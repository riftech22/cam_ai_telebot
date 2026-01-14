"""
Face Detector - Mendeteksi wajah dari frame kamera
"""

import cv2
import logging
import numpy as np
from typing import List, Tuple, Optional


class FaceDetector:
    """Kelas untuk mendeteksi wajah menggunakan OpenCV Haar Cascade"""
    
    def __init__(self, scale_factor: float = 1.1, min_neighbors: int = 5, 
                 min_size: Tuple[int, int] = (30, 30)):
        """
        Inisialisasi Face Detector
        
        Args:
            scale_factor: Faktor skala untuk pyramid image
            min_neighbors: Jumlah minimum neighbor untuk deteksi
            min_size: Ukuran minimum wajah (width, height)
        """
        self.scale_factor = scale_factor
        self.min_neighbors = min_neighbors
        self.min_size = min_size
        self.face_cascade = None
        self.logger = logging.getLogger(__name__)
        
        self._load_cascade()
    
    def _load_cascade(self):
        """Memuat model Haar Cascade untuk deteksi wajah"""
        try:
            # Coba load cascade dari OpenCV
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            if self.face_cascade.empty():
                raise Exception("Gagal memuat model face cascade")
                
            self.logger.info("Model face detector berhasil dimuat")
            
        except Exception as e:
            self.logger.error(f"Error memuat face cascade: {str(e)}")
            # Coba path alternatif
            alt_paths = [
                '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml',
                '/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml',
                'haarcascade_frontalface_default.xml'
            ]
            
            for path in alt_paths:
                self.face_cascade = cv2.CascadeClassifier(path)
                if not self.face_cascade.empty():
                    self.logger.info(f"Model dimuat dari: {path}")
                    break
            
            if self.face_cascade.empty():
                self.logger.error("Gagal memuat face cascade dari semua path")
    
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Mendeteksi wajah dalam frame
        
        Args:
            frame: Frame dari kamera (numpy array)
            
        Returns:
            List koordinat wajah [(x, y, w, h), ...]
        """
        if self.face_cascade is None or self.face_cascade.empty():
            self.logger.warning("Face cascade tidak dimuat")
            return []
        
        try:
            # Convert ke grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Equalize histogram untuk meningkatkan deteksi
            gray = cv2.equalizeHist(gray)
            
            # Deteksi wajah
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=self.scale_factor,
                minNeighbors=self.min_neighbors,
                minSize=self.min_size
            )
            
            return faces.tolist()
            
        except Exception as e:
            self.logger.error(f"Error mendeteksi wajah: {str(e)}")
            return []
    
    def detect_and_crop_faces(self, frame: np.ndarray, 
                              padding: int = 10) -> List[Tuple[np.ndarray, Tuple[int, int, int, int]]]:
        """
        Mendeteksi wajah dan crop dari frame
        
        Args:
            frame: Frame dari kamera
            padding: Padding tambahan di sekitar wajah
            
        Returns:
            List (cropped_face, coordinates)
        """
        faces = self.detect_faces(frame)
        result = []
        
        for (x, y, w, h) in faces:
            try:
                # Tambahkan padding
                x1 = max(0, x - padding)
                y1 = max(0, y - padding)
                x2 = min(frame.shape[1], x + w + padding)
                y2 = min(frame.shape[0], y + h + padding)
                
                # Crop wajah
                face = frame[y1:y2, x1:x2]
                
                if face.size > 0:
                    result.append((face, (x, y, w, h)))
                    
            except Exception as e:
                self.logger.error(f"Error cropping wajah: {str(e)}")
                continue
        
        return result
    
    def draw_faces(self, frame: np.ndarray, 
                   faces: List[Tuple[int, int, int, int]],
                   names: Optional[List[str]] = None,
                   color: Tuple[int, int, int] = (0, 255, 0)) -> np.ndarray:
        """
        Menggambar kotak di sekitar wajah yang terdeteksi
        
        Args:
            frame: Frame asli
            faces: List koordinat wajah
            names: Nama-nama orang (opsional)
            color: Warna kotak (B, G, R)
            
        Returns:
            Frame dengan kotak wajah
        """
        result = frame.copy()
        
        for i, (x, y, w, h) in enumerate(faces):
            # Gambar kotak
            cv2.rectangle(result, (x, y), (x + w, y + h), color, 2)
            
            # Tambahkan nama jika tersedia
            if names and i < len(names) and names[i]:
                text = names[i]
                
                # Background text
                (text_width, text_height) = cv2.getTextSize(
                    text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
                cv2.rectangle(
                    result, 
                    (x, y - text_height - 10),
                    (x + text_width, y),
                    color,
                    -1
                )
                
                # Text
                cv2.putText(
                    result,
                    text,
                    (x, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    2
                )
        
        return result
    
    def extract_face_features(self, face: np.ndarray) -> Optional[np.ndarray]:
        """
        Ekstrak fitur dari wajah (untuk pengenalan)
        
        Args:
            face: Gambar wajah yang sudah di-crop
            
        Returns:
            Array fitur atau None jika gagal
        """
        try:
            # Resize ke ukuran standar
            face_resized = cv2.resize(face, (100, 100))
            
            # Convert ke grayscale
            gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
            
            # Normalize
            gray = gray.astype('float32') / 255.0
            
            return gray
            
        except Exception as e:
            self.logger.error(f"Error ekstrak fitur wajah: {str(e)}")
            return None
    
    def preprocess_face(self, face: np.ndarray) -> Optional[np.ndarray]:
        """
        Preprocess wajah untuk face recognition
        
        Args:
            face: Gambar wajah
            
        Returns:
            Wajah yang sudah di-preprocess
        """
        try:
            # Resize ke 128x128 (ukuran standar untuk face_recognition)
            face_resized = cv2.resize(face, (128, 128))
            
            # Apply histogram equalization
            if len(face_resized.shape) == 3:
                gray = cv2.cvtColor(face_resized, cv2.COLOR_BGR2GRAY)
                gray = cv2.equalizeHist(gray)
                face_resized = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            
            return face_resized
            
        except Exception as e:
            self.logger.error(f"Error preprocess wajah: {str(e)}")
            return None
