"""
Person Detector - Mendeteksi keberadaan orang dalam frame menggunakan YOLOv8n
"""

import cv2
import logging
import numpy as np
from typing import List, Tuple, Optional
from ultralytics import YOLO


class PersonDetector:
    """Kelas untuk mendeteksi orang menggunakan YOLOv8n"""
    
    def __init__(self, confidence_threshold: float = 0.5, model_size: str = "yolov8n"):
        """
        Inisialisasi Person Detector dengan YOLOv8n
        
        Args:
            confidence_threshold: Threshold untuk confidence detection (0.0-1.0)
            model_size: Ukuran model YOLO (yolov8n, yolov8s, yolov8m, yolov8l, yolov8x)
        """
        self.confidence_threshold = confidence_threshold
        self.model_size = model_size
        self.model = None
        self.person_class_id = 0  # ID class 'person' di COCO dataset
        self.logger = logging.getLogger(__name__)
        
        self._load_model()
    
    def _load_model(self):
        """Memuat model YOLOv8n untuk deteksi orang"""
        try:
            # Load model YOLOv8n (nano model - tercepat dan paling ringan)
            self.logger.info(f"Memuat model YOLO{self.model_size[5:]}...")
            self.model = YOLO(f"{self.model_size}.pt")
            
            self.logger.info(f"Model YOLO{self.model_size[5:]} berhasil dimuat")
            
        except Exception as e:
            self.logger.error(f"Error memuat model YOLO: {str(e)}")
            self.logger.info("Mencoba download model dari Ultralytics...")
            try:
                self.model = YOLO(self.model_size)
                self.logger.info("Model berhasil didownload dan dimuat")
            except Exception as e2:
                self.logger.error(f"Gagal memuat model YOLO: {str(e2)}")
    
    def detect_persons(self, frame: np.ndarray, 
                       verbose: bool = False) -> List[Tuple[int, int, int, int, float]]:
        """
        Mendeteksi orang dalam frame menggunakan YOLOv8n
        
        Args:
            frame: Frame dari kamera
            verbose: Tampilkan informasi deteksi
            
        Returns:
            List koordinat dan confidence orang [(x, y, w, h, confidence), ...]
        """
        if self.model is None:
            self.logger.warning("Model YOLO tidak dimuat")
            return []
        
        try:
            # Jalankan inference dengan YOLO
            results = self.model(frame, verbose=verbose, conf=self.confidence_threshold)
            
            # Ekstrak deteksi orang
            detections = []
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # Filter hanya class 'person' (class_id = 0)
                    if int(box.cls) == self.person_class_id:
                        # Dapatkan koordinat bounding box
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = float(box.conf[0])
                        
                        # Convert ke (x, y, w, h) format
                        x = int(x1)
                        y = int(y1)
                        w = int(x2 - x1)
                        h = int(y2 - y1)
                        
                        detections.append((x, y, w, h, confidence))
            
            # YOLO sudah memiliki NMS built-in, jadi tidak perlu tambahan
            return detections
            
        except Exception as e:
            self.logger.error(f"Error mendeteksi orang: {str(e)}")
            return []
    
    
    def draw_persons(self, frame: np.ndarray,
                     persons: List[Tuple[int, int, int, int, float]],
                     color: Tuple[int, int, int] = (255, 0, 0)) -> np.ndarray:
        """
        Menggambar kotak di sekitar orang yang terdeteksi
        
        Args:
            frame: Frame asli
            persons: List koordinat orang [(x, y, w, h, confidence), ...]
            color: Warna kotak (B, G, R)
            
        Returns:
            Frame dengan kotak orang
        """
        result = frame.copy()
        
        for x, y, w, h, confidence in persons:
            # Gambar kotak dengan warna berdasarkan confidence
            if confidence >= 0.8:
                box_color = (0, 255, 0)  # Hijau untuk confidence tinggi
            elif confidence >= 0.6:
                box_color = (0, 255, 255)  # Kuning untuk confidence sedang
            else:
                box_color = (0, 0, 255)  # Merah untuk confidence rendah
            
            cv2.rectangle(result, (x, y), (x + w, y + h), box_color, 2)
            
            # Label dengan confidence
            label = f"Person {confidence:.2f}"
            
            # Background text
            (text_width, text_height) = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(
                result, 
                (x, y - text_height - 10),
                (x + text_width, y),
                box_color,
                -1
            )
            
            # Text
            cv2.putText(
                result,
                label,
                (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2
            )
        
        return result
    
    def count_persons(self, frame: np.ndarray) -> int:
        """
        Menghitung jumlah orang dalam frame
        
        Args:
            frame: Frame dari kamera
            
        Returns:
            Jumlah orang yang terdeteksi
        """
        persons = self.detect_persons(frame)
        return len(persons)
    
    def get_person_count(self, persons: List[Tuple[int, int, int, int, float]]) -> int:
        """
        Mendapatkan jumlah orang dari list deteksi
        
        Args:
            persons: List koordinat orang
            
        Returns:
            Jumlah orang
        """
        return len(persons)
    
    def get_high_confidence_persons(self, frame: np.ndarray, 
                                    min_confidence: float = 0.7) -> List[Tuple[int, int, int, int, float]]:
        """
        Mendapatkan deteksi orang dengan confidence tinggi
        
        Args:
            frame: Frame dari kamera
            min_confidence: Minimum confidence threshold
            
        Returns:
            List deteksi dengan confidence tinggi
        """
        all_persons = self.detect_persons(frame)
        return [p for p in all_persons if p[4] >= min_confidence]
    
    def is_person_present(self, frame: np.ndarray) -> bool:
        """
        Cek apakah ada orang dalam frame
        
        Args:
            frame: Frame dari kamera
            
        Returns:
            True jika ada orang, False jika tidak
        """
        return self.count_persons(frame) > 0
