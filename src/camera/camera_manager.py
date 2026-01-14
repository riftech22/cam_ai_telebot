"""
Camera Manager - Mengelola koneksi dan streaming dari kamera IP V380
"""

import cv2
import requests
import logging
from typing import Optional, Tuple
import time


class CameraManager:
    """Kelas untuk mengelola koneksi kamera IP V380"""
    
    def __init__(self, ip: str, port: int, username: str, password: str, 
                 rtsp_port: int = 554, stream_url: str = "/1",
                 buffer_size: int = 3, fps: int = 15, 
                 timeout: int = 10, max_retries: int = 5,
                 use_vlc_proxy: bool = False, vlc_rtsp_port: int = 8554, 
                 vlc_rtsp_path: str = "/camera"):
        """
        Inisialisasi Camera Manager
        
        Args:
            ip: IP address kamera
            port: Port HTTP kamera
            username: Username login kamera
            password: Password login kamera
            rtsp_port: Port RTSP untuk streaming
            stream_url: URL stream tambahan
            buffer_size: Buffer size untuk VideoCapture (default: 3)
            fps: FPS target untuk streaming (default: 15)
            timeout: Timeout untuk koneksi (default: 10 detik)
            max_retries: Maksimal percobaan reconnect (default: 5)
            use_vlc_proxy: Gunakan VLC RTSP proxy (default: False)
            vlc_rtsp_port: Local RTSP port dari VLC proxy (default: 8554)
            vlc_rtsp_path: RTSP path dari VLC proxy (default: /camera)
        """
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.rtsp_port = rtsp_port
        self.stream_url = stream_url
        self.buffer_size = buffer_size
        self.fps = fps
        self.timeout = timeout
        self.max_retries = max_retries
        self.use_vlc_proxy = use_vlc_proxy
        self.vlc_rtsp_port = vlc_rtsp_port
        self.vlc_rtsp_path = vlc_rtsp_path
        self.cap: Optional[cv2.VideoCapture] = None
        self.is_connected = False
        self.last_frame_time = time.time()
        self.consecutive_failures = 0
        
        self.logger = logging.getLogger(__name__)
        
    def build_rtsp_url(self) -> str:
        """
        Membangun URL RTSP untuk streaming dengan parameter optimasi
        
        Returns:
            URL RTSP lengkap
        """
        if self.use_vlc_proxy:
            # Gunakan VLC RTSP proxy (lebih stabil)
            rtsp_url = f"rtsp://127.0.0.1:{self.vlc_rtsp_port}{self.vlc_rtsp_path}"
            self.logger.info(f"RTSP URL (VLC Proxy): rtsp://127.0.0.1:{self.vlc_rtsp_port}{self.vlc_rtsp_path}")
            self.logger.info(f"VLC proxy menjalankan stream dari kamera {self.ip}")
        else:
            # Format RTSP untuk V380 dengan parameter optimasi
            # rtsp_transport: tcp (lebih stabil dari udp)
            # latency: 0 (real-time, no buffering)
            rtsp_url = f"rtsp://{self.username}:{self.password}@{self.ip}:{self.rtsp_port}{self.stream_url}?rtsp_transport=tcp&latency=0"
            self.logger.info(f"RTSP URL (Direct): rtsp://{self.username}:****@{self.ip}:{self.rtsp_port}{self.stream_url}")
        
        return rtsp_url
    
    def connect(self) -> bool:
        """
        Membuka koneksi ke kamera dengan timeout dan retry
        
        Returns:
            True jika berhasil terkoneksi, False jika gagal
        """
        try:
            rtsp_url = self.build_rtsp_url()
            self.logger.info(f"Menghubungkan ke kamera {self.ip} (timeout: {self.timeout}s)...")
            
            # Mencoba koneksi dengan parameter optimasi
            self.cap = cv2.VideoCapture(rtsp_url)
            
            # Set buffer size dan fps untuk stabilitas
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, self.buffer_size)
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'H264'))
            
            # Test koneksi dengan membaca beberapa frame
            success_count = 0
            for i in range(5):  # Coba 5 frame untuk memastikan stabil
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    success_count += 1
                    if success_count >= 3:  # Minimal 3 frame sukses
                        self.is_connected = True
                        self.consecutive_failures = 0
                        self.last_frame_time = time.time()
                        self.logger.info(f"Berhasil terkoneksi ke kamera {self.ip}")
                        self.logger.info(f"Resolusi: {frame.shape[1]}x{frame.shape[0]}, FPS: {self.fps}, Buffer: {self.buffer_size}")
                        return True
                time.sleep(0.1)  # Tunggu 100ms antar frame
            
            # Jika kurang dari 3 frame sukses
            self.logger.error(f"Gagal membaca frame yang stabil dari kamera {self.ip}")
            self.release()
            return False
                
        except Exception as e:
            self.logger.error(f"Error saat menghubungkan ke kamera: {str(e)}", exc_info=True)
            self.release()
            return False
    
    def read_frame(self) -> Tuple[bool, Optional[cv2.typing.MatLike]]:
        """
        Membaca satu frame dari kamera dengan health check
        
        Returns:
            Tuple (success, frame) dimana success adalah bool dan frame adalah numpy array atau None
        """
        if not self.is_connected or self.cap is None:
            self.logger.warning("Kamera tidak terkoneksi, mencoba reconnect...")
            self.reconnect()
            return False, None
        
        try:
            ret, frame = self.cap.read()
            
            if ret and frame is not None:
                # Update timestamp dan reset failure counter
                self.last_frame_time = time.time()
                self.consecutive_failures = 0
                return True, frame
            else:
                # Increment failure counter
                self.consecutive_failures += 1
                self.logger.warning(f"Gagal membaca frame (consecutive failures: {self.consecutive_failures})")
                
                # Cek jika perlu reconnect
                if self.consecutive_failures >= 3:
                    self.logger.error("Terlalu banyak kegagalan, mencoba reconnect...")
                    return self.reconnect()
                
                return False, None
                
        except Exception as e:
            self.consecutive_failures += 1
            self.logger.error(f"Error saat membaca frame: {str(e)}")
            
            # Cek jika perlu reconnect
            if self.consecutive_failures >= 3:
                self.logger.error("Terlalu banyak error, mencoba reconnect...")
                return self.reconnect()
            
            return False, None
    
    def reconnect(self, max_retries: int = None) -> bool:
        """
        Mencoba reconnect ke kamera dengan exponential backoff
        
        Args:
            max_retries: Maksimal percobaan reconnect (default: self.max_retries)
            
        Returns:
            True jika berhasil reconnect, False jika gagal
        """
        if max_retries is None:
            max_retries = self.max_retries
        
        self.release()
        self.consecutive_failures = 0
        
        for attempt in range(max_retries):
            # Exponential backoff: 2s, 4s, 8s, 16s, 32s
            backoff_time = min(2 ** attempt, 30)  # Max 30 detik
            self.logger.info(f"Percobaan reconnect {attempt + 1}/{max_retries} (menunggu {backoff_time}s)...")
            
            time.sleep(backoff_time)
            
            if self.connect():
                self.logger.info("Reconnect berhasil!")
                return True
        
        self.logger.error(f"Gagal melakukan reconnect ke kamera setelah {max_retries} percobaan")
        return False
    
    def get_properties(self) -> dict:
        """
        Mendapatkan properti kamera
        
        Returns:
            Dictionary berisi properti kamera
        """
        if not self.is_connected or self.cap is None:
            return {}
        
        try:
            width = self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
            height = self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            
            return {
                'width': int(width),
                'height': int(height),
                'fps': int(fps) if fps > 0 else 15,
                'ip': self.ip,
                'port': self.port
            }
        except Exception as e:
            self.logger.error(f"Error mendapatkan properti kamera: {str(e)}")
            return {}
    
    def capture_photo(self, filename: Optional[str] = None) -> Optional[cv2.typing.MatLike]:
        """
        Mengambil satu foto dari kamera
        
        Args:
            filename: Nama file untuk menyimpan foto (opsional)
            
        Returns:
            Frame yang diambil atau None jika gagal
        """
        ret, frame = self.read_frame()
        
        if ret and frame is not None:
            if filename:
                try:
                    cv2.imwrite(filename, frame)
                    self.logger.info(f"Foto disimpan ke {filename}")
                except Exception as e:
                    self.logger.error(f"Error menyimpan foto: {str(e)}")
            return frame
        return None
    
    def check_connection(self) -> bool:
        """
        Mengecek status koneksi kamera
        
        Returns:
            True jika kamera terkoneksi, False jika tidak
        """
        if self.cap is None or not self.is_connected:
            return False
        
        try:
            # Cek apakah masih bisa membaca frame
            ret, frame = self.cap.read()
            return ret and frame is not None
        except:
            return False
    
    def release(self):
        """Membebaskan resource kamera"""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            self.is_connected = False
            self.logger.info("Koneksi kamera dilepaskan")
    
    def __del__(self):
        """Destructor untuk memastikan resource dibebaskan"""
        self.release()
    
    @staticmethod
    def test_http_connection(ip: str, port: int, username: str, password: str) -> bool:
        """
        Test koneksi HTTP ke kamera
        
        Args:
            ip: IP address kamera
            port: Port HTTP
            username: Username
            password: Password
            
        Returns:
            True jika koneksi berhasil, False jika gagal
        """
        try:
            url = f"http://{ip}:{port}"
            response = requests.get(url, auth=(username, password), timeout=5)
            return response.status_code == 200
        except:
            return False
