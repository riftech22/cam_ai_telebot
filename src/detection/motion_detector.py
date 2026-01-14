"""
Motion Detector - Mendeteksi gerakan dalam frame menggunakan OpenCV
"""

import cv2
import numpy as np
import logging
from typing import Tuple, Optional


class MotionDetector:
    """Kelas untuk mendeteksi gerakan menggunakan OpenCV"""
    
    def __init__(self, min_contour_area: int = 500, sensitivity: int = 25):
        """
        Inisialisasi Motion Detector
        
        Args:
            min_contour_area: Minimum area kontur untuk dianggap gerakan
            sensitivity: Sensitivitas deteksi (semakin rendah = semakin sensitif)
        """
        self.min_contour_area = min_contour_area
        self.sensitivity = sensitivity
        self.previous_frame = None
        self.logger = logging.getLogger(__name__)
        
    def detect_motion(self, frame: np.ndarray) -> Tuple[bool, float, np.ndarray]:
        """
        Mendeteksi gerakan dalam frame
        
        Args:
            frame: Input frame (numpy array)
            
        Returns:
            Tuple (has_motion, motion_percentage, motion_mask)
            - has_motion: True jika ada gerakan
            - motion_percentage: Persentase frame yang berubah (0-100)
            - motion_mask: Frame mask yang menunjukkan area gerakan
        """
        try:
            # Convert ke grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Blur untuk reduksi noise
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            # Jika belum ada frame sebelumnya, simpan sekarang
            if self.previous_frame is None:
                self.previous_frame = gray
                return False, 0.0, np.zeros_like(frame)
            
            # Hitung perbedaan absolute antar frame
            frame_delta = cv2.absdiff(self.previous_frame, gray)
            
            # Threshold untuk binarization
            thresh = cv2.threshold(frame_delta, self.sensitivity, 255, cv2.THRESH_BINARY)[1]
            
            # Dilasi untuk menghubungkan area yang berubah
            thresh = cv2.dilate(thresh, None, iterations=2)
            
            # Hitung kontur
            contours, _ = cv2.findContours(
                thresh.copy(), 
                cv2.RETR_EXTERNAL, 
                cv2.CHAIN_APPROX_SIMPLE
            )
            
            # Filter kontur berdasarkan area
            motion_contours = [c for c in contours if cv2.contourArea(c) > self.min_contour_area]
            
            # Update frame sebelumnya
            self.previous_frame = gray
            
            # Cek apakah ada gerakan
            has_motion = len(motion_contours) > 0
            
            # Hitung persentase gerakan
            motion_pixels = cv2.countNonZero(thresh)
            total_pixels = thresh.shape[0] * thresh.shape[1]
            motion_percentage = (motion_pixels / total_pixels) * 100 if total_pixels > 0 else 0.0
            
            # Buat motion mask untuk visualisasi (convert ke BGR)
            motion_mask = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)
            
            # Gambar kotak di sekitar kontur gerakan
            if has_motion:
                for contour in motion_contours:
                    (x, y, w, h) = cv2.boundingRect(contour)
                    cv2.rectangle(motion_mask, (x, y), (x + w, y + h), (0, 0, 255), 2)
            
            self.logger.debug(
                f"Motion detection: has_motion={has_motion}, "
                f"percentage={motion_percentage:.2f}%, contours={len(motion_contours)}"
            )
            
            return has_motion, motion_percentage, motion_mask
            
        except Exception as e:
            self.logger.error(f"Error deteksi gerakan: {str(e)}")
            return False, 0.0, np.zeros_like(frame)
    
    def draw_motion(self, frame: np.ndarray, 
                    motion_mask: np.ndarray,
                    color: Tuple[int, int, int] = (0, 0, 255)) -> np.ndarray:
        """
        Menggamabarkan area gerakan ke frame
        
        Args:
            frame: Frame asli
            motion_mask: Mask gerakan
            color: Warna area gerakan (B, G, R)
            
        Returns:
            Frame dengan overlay gerakan
        """
        # Blend mask dengan frame asli
        alpha = 0.3  # Transparansi mask
        result = cv2.addWeighted(frame, 1 - alpha, motion_mask, alpha, 0)
        
        return result
    
    def reset(self):
        """Reset frame sebelumnya (untuk handle perubahan scene)"""
        self.previous_frame = None
        self.logger.debug("Motion detector reset")
