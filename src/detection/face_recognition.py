"""
Face Recognition - Mengenali wajah dari foto yang terdeteksi
"""

import cv2
import face_recognition
import numpy as np
import pickle
import logging
import os
from typing import List, Dict, Tuple, Optional
from datetime import datetime


class FaceRecognition:
    """Kelas untuk pengenalan wajah menggunakan face_recognition library"""
    
    def __init__(self, faces_dir: str = "data/faces", tolerance: float = 0.6):
        """
        Inisialisasi Face Recognition
        
        Args:
            faces_dir: Direktori untuk menyimpan encoding wajah
            tolerance: Toleransi untuk pengenalan wajah (0.0-1.0)
        """
        self.faces_dir = faces_dir
        self.tolerance = tolerance
        self.known_face_encodings: List[np.ndarray] = []
        self.known_face_names: List[str] = []
        self.encoding_file = os.path.join(faces_dir, "face_encodings.pkl")
        
        self.logger = logging.getLogger(__name__)
        
        # Buat direktori jika belum ada
        os.makedirs(faces_dir, exist_ok=True)
        
        # Load encoding yang sudah tersimpan
        self.load_encodings()
    
    def load_encodings(self):
        """Load encoding wajah dari file"""
        try:
            if os.path.exists(self.encoding_file):
                with open(self.encoding_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data['encodings']
                    self.known_face_names = data['names']
                self.logger.info(f"Berhasil load {len(self.known_face_names)} encoding wajah")
            else:
                self.logger.info("Belum ada encoding wajah yang tersimpan")
        except Exception as e:
            self.logger.error(f"Error load encoding wajah: {str(e)}")
    
    def save_encodings(self):
        """Save encoding wajah ke file"""
        try:
            data = {
                'encodings': self.known_face_encodings,
                'names': self.known_face_names
            }
            with open(self.encoding_file, 'wb') as f:
                pickle.dump(data, f)
            self.logger.info(f"Berhasil save {len(self.known_face_names)} encoding wajah")
        except Exception as e:
            self.logger.error(f"Error save encoding wajah: {str(e)}")
    
    def encode_face(self, face_image: np.ndarray) -> Optional[np.ndarray]:
        """
        Encode wajah dari gambar
        
        Args:
            face_image: Gambar wajah (BGR format)
            
        Returns:
            Array encoding wajah atau None jika gagal
        """
        try:
            # Convert BGR ke RGB (face_recognition butuh RGB)
            rgb_face = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
            
            # Encode wajah
            face_encodings = face_recognition.face_encodings(rgb_face)
            
            if len(face_encodings) > 0:
                return face_encodings[0]
            else:
                self.logger.warning("Tidak ada wajah terdeteksi dalam gambar")
                return None
                
        except Exception as e:
            self.logger.error(f"Error encode wajah: {str(e)}")
            return None
    
    def add_face(self, name: str, face_image: np.ndarray, save_image: bool = True) -> bool:
        """
        Menambahkan wajah baru ke database
        
        Args:
            name: Nama orang
            face_image: Gambar wajah (BGR format)
            save_image: Simpan gambar wajah ke disk
            
        Returns:
            True jika berhasil, False jika gagal
        """
        try:
            # Encode wajah
            encoding = self.encode_face(face_image)
            
            if encoding is None:
                self.logger.error(f"Gagal encode wajah untuk {name}")
                return False
            
            # Cek apakah nama sudah ada
            if name in self.known_face_names:
                # Update encoding untuk nama yang sudah ada
                idx = self.known_face_names.index(name)
                self.known_face_encodings[idx] = encoding
                self.logger.info(f"Update encoding wajah untuk {name}")
            else:
                # Tambah encoding baru
                self.known_face_encodings.append(encoding)
                self.known_face_names.append(name)
                self.logger.info(f"Tambah wajah baru: {name}")
            
            # Save gambar wajah jika diinginkan
            if save_image:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                image_path = os.path.join(self.faces_dir, f"{name}_{timestamp}.jpg")
                cv2.imwrite(image_path, face_image)
                self.logger.info(f"Gambar wajah disimpan ke {image_path}")
            
            # Save encoding ke file
            self.save_encodings()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error menambahkan wajah: {str(e)}")
            return False
    
    def add_face_from_file(self, name: str, image_path: str) -> bool:
        """
        Menambahkan wajah dari file gambar
        
        Args:
            name: Nama orang
            image_path: Path ke file gambar
            
        Returns:
            True jika berhasil, False jika gagal
        """
        try:
            # Load gambar
            image = cv2.imread(image_path)
            
            if image is None:
                self.logger.error(f"Gagal load gambar dari {image_path}")
                return False
            
            # Deteksi wajah
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_image)
            
            if len(face_locations) == 0:
                self.logger.error("Tidak ada wajah terdeteksi dalam gambar")
                return False
            
            # Ambil wajah pertama yang terdeteksi
            top, right, bottom, left = face_locations[0]
            face_image = image[top:bottom, left:right]
            
            # Tambah ke database
            return self.add_face(name, face_image, save_image=False)
            
        except Exception as e:
            self.logger.error(f"Error menambahkan wajah dari file: {str(e)}")
            return False
    
    def remove_face(self, name: str) -> bool:
        """
        Menghapus wajah dari database
        
        Args:
            name: Nama orang yang akan dihapus
            
        Returns:
            True jika berhasil, False jika gagal
        """
        try:
            if name in self.known_face_names:
                idx = self.known_face_names.index(name)
                self.known_face_names.pop(idx)
                self.known_face_encodings.pop(idx)
                self.save_encodings()
                self.logger.info(f"Wajah {name} berhasil dihapus")
                return True
            else:
                self.logger.warning(f"Wajah {name} tidak ditemukan")
                return False
        except Exception as e:
            self.logger.error(f"Error menghapus wajah: {str(e)}")
            return False
    
    def recognize_face(self, face_image: np.ndarray) -> Tuple[Optional[str], float]:
        """
        Mengenali wajah dari gambar
        
        Args:
            face_image: Gambar wajah (BGR format)
            
        Returns:
            Tuple (nama, distance) atau (None, 1.0) jika tidak dikenali
        """
        try:
            if len(self.known_face_encodings) == 0:
                return None, 1.0
            
            # Encode wajah input
            encoding = self.encode_face(face_image)
            
            if encoding is None:
                return None, 1.0
            
            # Compare dengan database
            face_distances = face_recognition.face_distance(
                self.known_face_encodings, 
                encoding
            )
            
            if len(face_distances) == 0:
                return None, 1.0
            
            # Cari match terbaik
            best_match_index = np.argmin(face_distances)
            distance = face_distances[best_match_index]
            
            # Cek apakah match valid berdasarkan tolerance
            if distance <= self.tolerance:
                name = self.known_face_names[best_match_index]
                return name, distance
            else:
                return None, distance
                
        except Exception as e:
            self.logger.error(f"Error mengenali wajah: {str(e)}")
            return None, 1.0
    
    def recognize_faces(self, faces: List[np.ndarray]) -> List[Dict[str, any]]:
        """
        Mengenali multiple wajah
        
        Args:
            faces: List gambar wajah
            
        Returns:
            List dict dengan nama, distance, dan status
        """
        results = []
        
        for i, face in enumerate(faces):
            name, distance = self.recognize_face(face)
            
            if name:
                status = "known"
                display_name = name
            else:
                status = "unknown"
                display_name = "Unknown"
            
            results.append({
                'index': i,
                'name': name,
                'display_name': display_name,
                'distance': distance,
                'status': status
            })
        
        return results
    
    def get_all_names(self) -> List[str]:
        """
        Mendapatkan semua nama yang tersimpan
        
        Returns:
            List nama-nama orang
        """
        return self.known_face_names.copy()
    
    def get_face_count(self) -> int:
        """
        Mendapatkan jumlah wajah yang tersimpan
        
        Returns:
            Jumlah wajah
        """
        return len(self.known_face_names)
    
    def get_face_images(self, name: str) -> List[str]:
        """
        Mendapatkan semua gambar wajah untuk nama tertentu
        
        Args:
            name: Nama orang
            
        Returns:
            List path ke gambar-gambar wajah
        """
        try:
            images = []
            for filename in os.listdir(self.faces_dir):
                if filename.startswith(name) and filename.endswith('.jpg'):
                    images.append(os.path.join(self.faces_dir, filename))
            return images
        except Exception as e:
            self.logger.error(f"Error mendapatkan gambar wajah: {str(e)}")
            return []
    
    def clear_database(self) -> bool:
        """
        Menghapus semua data wajah
        
        Returns:
            True jika berhasil
        """
        try:
            self.known_face_encodings.clear()
            self.known_face_names.clear()
            self.save_encodings()
            self.logger.info("Database wajah dibersihkan")
            return True
        except Exception as e:
            self.logger.error(f"Error membersihkan database: {str(e)}")
            return False
