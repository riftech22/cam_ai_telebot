"""
Main Application - CCTV AI Telegram Bot
Entry point untuk aplikasi CCTV AI dengan deteksi orang dan pengenalan wajah
"""

import asyncio
import logging
import logging.handlers
import time
import yaml
import json
import signal
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from camera.camera_manager import CameraManager
from detection.face_detector import FaceDetector
from detection.person_detector import PersonDetector
from detection.face_recognition import FaceRecognition
from detection.motion_detector import MotionDetector
from telegram_bot.bot_handler import BotHandler


class CCTVTelebotApp:
    """Kelas utama untuk aplikasi CCTV AI Telegram Bot"""
    
    def __init__(self):
        """Inisialisasi aplikasi"""
        self.logger = self._setup_logging()
        
        # Komponen sistem
        self.camera = None
        self.face_detector = None
        self.person_detector = None
        self.face_recognition = None
        self.motion_detector = None
        self.bot_handler = None
        
        # Motion tracking
        self.last_motion_time = 0
        
        # Konfigurasi
        self.config = None
        self.telegram_config = None
        
        # Status
        self.running = False
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _setup_logging(self):
        """Setup logging untuk aplikasi"""
        # Buat direktori logs jika belum ada
        Path("logs").mkdir(exist_ok=True)
        
        # Setup root logger
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.handlers.RotatingFileHandler(
            'logs/app.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(console_format)
        logger.addHandler(file_handler)
        
        return logging.getLogger(__name__)
    
    def load_config(self):
        """Load konfigurasi dari file"""
        try:
            # Load config.yaml
            config_path = Path("config/config.yaml")
            if not config_path.exists():
                config_path = Path("config/config.yaml.template")
                self.logger.warning("config.yaml tidak ditemukan, menggunakan template")
            
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            
            self.logger.info("Konfigurasi berhasil dimuat")
            
            # Load telegram_config.json
            telegram_path = Path("config/telegram_config.json")
            if not telegram_path.exists():
                telegram_path = Path("config/telegram_config.json.template")
                self.logger.warning("telegram_config.json tidak ditemukan, menggunakan template")
            
            with open(telegram_path, 'r') as f:
                self.telegram_config = json.load(f)
            
            self.logger.info("Konfigurasi Telegram berhasil dimuat")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error load konfigurasi: {str(e)}")
            return False
    
    def initialize_components(self):
        """Inisialisasi semua komponen sistem"""
        try:
            self.logger.info("Menginisialisasi komponen sistem...")
            
            # Kamera - support old format (camera) and new format (cameras)
            camera_config = None
            if 'camera' in self.config:
                camera_config = self.config['camera']
            elif 'cameras' in self.config and len(self.config['cameras']) > 0:
                camera_config = self.config['cameras'][0]  # Ambil kamera pertama
            
            if camera_config is None:
                raise Exception("Konfigurasi kamera tidak ditemukan")
            
            self.camera = CameraManager(
                ip=camera_config['ip'],
                port=camera_config['port'],
                username=camera_config['username'],
                password=camera_config['password'],
                rtsp_port=camera_config.get('rtsp_port', 554),
                stream_url=camera_config.get('stream_url', '/1')
            )
            
            # Hubungkan ke kamera
            if not self.camera.connect():
                raise Exception("Gagal menghubungkan ke kamera")
            
            # Face Detector
            self.face_detector = FaceDetector()
            self.logger.info("Face detector diinisialisasi")
            
            # Person Detector dengan YOLOv8n
            self.person_detector = PersonDetector(
                confidence_threshold=self.config['detection']['min_confidence']
            )
            self.logger.info("Person detector (YOLOv8n) diinisialisasi")
            
            # Face Recognition
            self.face_recognition = FaceRecognition(
                tolerance=self.config['database']['face_encoding_tolerance']
            )
            self.logger.info("Face recognition diinisialisasi")
            
            # Motion Detector
            if self.config['detection'].get('motion_detection_enabled', False):
                motion_config = self.config.get('motion_detection', {})
                self.motion_detector = MotionDetector(
                    min_contour_area=motion_config.get('min_contour_area', 500),
                    sensitivity=motion_config.get('sensitivity', 25)
                )
                self.logger.info("Motion detector diinisialisasi")
            else:
                self.logger.info("Motion detector dinonaktifkan")
            
            # Telegram Bot
            self.bot_handler = BotHandler(
                bot_token=self.telegram_config['bot_token'],
                camera_manager=self.camera,
                face_detector=self.face_detector,
                person_detector=self.person_detector,
                face_recognition=self.face_recognition,
                config=self.config
            )
            
            # Handle admin_id - convert to int if provided and valid
            admin_id_str = self.telegram_config.get('admin_id')
            if admin_id_str and admin_id_str != "YOUR_ADMIN_ID_HERE":
                try:
                    admin_id = int(admin_id_str)
                except (ValueError, TypeError):
                    self.logger.warning("admin_id tidak valid, menggunakan None")
                    admin_id = None
            else:
                admin_id = None
            
            self.bot_handler.initialize(
                chat_id=int(self.telegram_config['chat_id']),
                admin_id=admin_id
            )
            self.logger.info("Telegram bot diinisialisasi")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error inisialisasi komponen: {str(e)}")
            return False
    
    async def run_detection_loop(self):
        """Loop utama untuk deteksi orang dan wajah"""
        self.logger.info("Memulai loop deteksi...")
        
        last_detection_time = time.time()
        detection_interval = self.config['detection']['detection_interval']
        
        last_camera_check = time.time()
        camera_check_interval = 30  # Cek kamera setiap 30 detik
        
        frame_count = 0  # Counter untuk debug
        
        while self.running:
            try:
                current_time = time.time()
                frame_count += 1
                
                # Log setiap 30 detik untuk memastikan loop berjalan
                if frame_count % 300 == 0:
                    self.logger.info(f"Detection loop running... Frame count: {frame_count}")
                
                # Cek status kamera
                if current_time - last_camera_check >= camera_check_interval:
                    self.logger.debug("Checking camera connection...")
                    if not self.camera.check_connection():
                        self.logger.warning("Kamera terputus, mencoba reconnect...")
                        await self.bot_handler.send_camera_disconnected_alert()
                        
                        if self.camera.reconnect():
                            await self.bot_handler.send_camera_reconnected_alert()
                    else:
                        self.logger.debug("Camera connection OK")
                    
                    last_camera_check = current_time
                
                # Cek apakah deteksi aktif
                if not self.config['detection']['enabled']:
                    self.logger.debug("Detection is disabled in config, skipping...")
                    await asyncio.sleep(1)
                    continue
                
                # Cek interval deteksi
                if current_time - last_detection_time >= detection_interval:
                    self.logger.debug(f"Attempting to read frame... (frame #{frame_count})")
                    
                    # Baca frame dari kamera
                    ret, frame = self.camera.read_frame()
                    
                    if ret and frame is not None:
                        self.logger.debug(f"Frame read successfully: {frame.shape}")
                        
                        # Deteksi gerakan (jika diaktifkan)
                        has_motion = False
                        motion_percentage = 0.0
                        if self.motion_detector is not None:
                            has_motion, motion_percentage, _ = self.motion_detector.detect_motion(frame)
                            self.logger.info(f"Motion detection: has_motion={has_motion}, percentage={motion_percentage:.2f}%")
                            
                            # Kirim notifikasi jika ada gerakan
                            motion_config = self.config.get('motion_detection', {})
                            cooldown = motion_config.get('cooldown_seconds', 5)
                            min_percentage = motion_config.get('min_motion_percentage', 2)
                            
                            if (has_motion and 
                                motion_percentage >= min_percentage and
                                current_time - self.last_motion_time >= cooldown):
                                
                                if self.config['notification'].get('send_on_motion', True):
                                    self.logger.info(f"Motion detected! Percentage: {motion_percentage:.2f}%")
                                    await self.bot_handler.send_motion_alert(frame, motion_percentage)
                                    self.last_motion_time = current_time
                        
                        # Deteksi orang
                        if self.config['detection']['person_detection_enabled']:
                            self.logger.debug("Starting person detection...")
                            detected_persons = self.person_detector.detect_persons(frame)
                            self.logger.info(f"Person detection result: {len(detected_persons)} persons detected")
                            
                            if len(detected_persons) > 0:
                                self.logger.info(f"Terdeteksi {len(detected_persons)} orang")
                                
                                # Deteksi wajah untuk zoom
                                face_crops = []
                                recognized_faces = []
                                if self.config['detection']['face_recognition_enabled']:
                                    faces = self.face_detector.detect_and_crop_faces(frame)
                                    
                                    if len(faces) > 0:
                                        face_images = [face[0] for face in faces]
                                        recognized_faces = self.face_recognition.recognize_faces(face_images)
                                        face_crops = faces  # (cropped_face, bbox, confidence)
                                
                                # Update statistik
                                if self.bot_handler.get_commands_instance():
                                    stats = self.bot_handler.get_commands_instance().detection_stats
                                    stats['total'] += len(detected_persons)
                                    for face in recognized_faces:
                                        if face['status'] == 'known':
                                            stats['known'] += 1
                                        else:
                                            stats['unknown'] += 1
                                    
                                # Kirim notifikasi SEGERA tanpa delay
                                self.logger.info("Sending detection alert to Telegram...")
                                await self.bot_handler.send_detection_alert(
                                    frame,
                                    detected_persons,
                                    recognized_faces,
                                    face_crops  # Tambahkan face crops untuk zoom
                                )
                                
                                # Reset timer agar deteksi berikutnya tidak perlu tunggu lama
                                last_detection_time = current_time
                        else:
                            self.logger.debug("Person detection is disabled")
                        
                        last_detection_time = current_time
                    else:
                        self.logger.warning(f"Failed to read frame (ret={ret}, frame={frame is not None})")
                
                # Tunggu sebentar sebelum loop berikutnya
                await asyncio.sleep(0.1)
                
            except Exception as e:
                self.logger.error(f"Error dalam loop deteksi: {str(e)}", exc_info=True)
                await asyncio.sleep(1)
    
    async def run(self):
        """Jalankan aplikasi"""
        try:
            self.logger.info("="*60)
            self.logger.info("CCTV AI Telegram Bot dimulai")
            self.logger.info("="*60)
            
            # Load konfigurasi
            if not self.load_config():
                return False
            
            # Inisialisasi komponen
            if not self.initialize_components():
                return False
            
            self.running = True
            
            # Mulai Telegram bot
            bot_task = asyncio.create_task(self.bot_handler.start_bot())
            
            # Mulai loop deteksi
            detection_task = asyncio.create_task(self.run_detection_loop())
            
            # Tunggu sampai selesai
            await asyncio.gather(bot_task, detection_task)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error menjalankan aplikasi: {str(e)}")
            return False
    
    async def stop(self):
        """Hentikan aplikasi"""
        self.logger.info("Menghentikan aplikasi...")
        
        self.running = False
        
        # Hentikan bot
        if self.bot_handler:
            await self.bot_handler.stop_bot()
        
        # Lepaskan kamera
        if self.camera:
            self.camera.release()
        
        self.logger.info("Aplikasi dihentikan")
    
    def _signal_handler(self, signum, frame):
        """Handler untuk sinyal SIGINT dan SIGTERM"""
        self.logger.info(f"Sinyal {signum} diterima, menghentikan aplikasi...")
        self.running = False


async def main():
    """Fungsi main"""
    app = CCTVTelebotApp()
    
    try:
        success = await app.run()
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)
            
    except KeyboardInterrupt:
        await app.stop()
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    # Import logging.handlers di sini untuk menghindari circular import
    import logging.handlers
    
    asyncio.run(main())
