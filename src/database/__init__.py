"""
Modul Database - Mengelola database sistem
"""

import logging
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class DetectionLogger:
    """Kelas untuk logging deteksi orang dan wajah"""
    
    def __init__(self, log_dir: str = "data/detections"):
        """
        Inisialisasi Detection Logger
        
        Args:
            log_dir: Direktori untuk menyimpan log deteksi
        """
        self.log_dir = Path(log_dir)
        self.logger = logging.getLogger(__name__)
        
        # Buat direktori jika belum ada
        self.log_dir.mkdir(parents=True, exist_ok=True)
    
    def log_detection(self, person_count: int, detected_persons: List, 
                     recognized_faces: List, frame_path: Optional[str] = None):
        """
        Log deteksi ke file JSON
        
        Args:
            person_count: Jumlah orang yang terdeteksi
            detected_persons: List deteksi orang
            recognized_faces: List wajah yang dikenali
            frame_path: Path ke frame yang disimpan (opsional)
        """
        try:
            timestamp = datetime.now()
            date_str = timestamp.strftime("%Y-%m-%d")
            time_str = timestamp.strftime("%H:%M:%S")
            
            # Buat log entry
            log_entry = {
                'timestamp': timestamp.isoformat(),
                'date': date_str,
                'time': time_str,
                'person_count': person_count,
                'persons': [
                    {
                        'x': int(p[0]),
                        'y': int(p[1]),
                        'width': int(p[2]),
                        'height': int(p[3]),
                        'confidence': float(p[4])
                    }
                    for p in detected_persons
                ],
                'faces': [
                    {
                        'name': f['name'],
                        'display_name': f['display_name'],
                        'distance': float(f['distance']),
                        'status': f['status']
                    }
                    for f in recognized_faces
                ],
                'frame_path': frame_path
            }
            
            # Simpan ke file per tanggal
            log_file = self.log_dir / f"detections_{date_str}.json"
            
            # Load existing logs
            existing_logs = []
            if log_file.exists():
                try:
                    with open(log_file, 'r') as f:
                        existing_logs = json.load(f)
                except:
                    existing_logs = []
            
            # Append new log
            existing_logs.append(log_entry)
            
            # Save logs
            with open(log_file, 'w') as f:
                json.dump(existing_logs, f, indent=2)
            
            self.logger.debug(f"Log deteksi disimpan ke {log_file}")
            
        except Exception as e:
            self.logger.error(f"Error logging deteksi: {str(e)}")
    
    def get_detections_by_date(self, date: Optional[str] = None) -> List[Dict]:
        """
        Mendapatkan log deteksi untuk tanggal tertentu
        
        Args:
            date: Tanggal dalam format YYYY-MM-DD (default: hari ini)
            
        Returns:
            List log deteksi
        """
        try:
            if date is None:
                date = datetime.now().strftime("%Y-%m-%d")
            
            log_file = self.log_dir / f"detections_{date}.json"
            
            if not log_file.exists():
                return []
            
            with open(log_file, 'r') as f:
                logs = json.load(f)
            
            return logs
            
        except Exception as e:
            self.logger.error(f"Error getting detections: {str(e)}")
            return []
    
    def get_detection_stats(self, days: int = 7) -> Dict:
        """
        Mendapatkan statistik deteksi untuk beberapa hari terakhir
        
        Args:
            days: Jumlah hari untuk statistik
            
        Returns:
            Dictionary statistik
        """
        try:
            stats = {
                'total_detections': 0,
                'total_persons': 0,
                'total_known_faces': 0,
                'total_unknown_faces': 0,
                'daily_stats': []
            }
            
            for i in range(days):
                date = datetime.now().strftime("%Y-%m-%d")
                logs = self.get_detections_by_date(date)
                
                if logs:
                    daily_persons = sum(log['person_count'] for log in logs)
                    daily_known = sum(
                        len([f for f in log['faces'] if f['status'] == 'known'])
                        for log in logs
                    )
                    daily_unknown = sum(
                        len([f for f in log['faces'] if f['status'] == 'unknown'])
                        for log in logs
                    )
                    
                    stats['total_detections'] += len(logs)
                    stats['total_persons'] += daily_persons
                    stats['total_known_faces'] += daily_known
                    stats['total_unknown_faces'] += daily_unknown
                    
                    stats['daily_stats'].append({
                        'date': date,
                        'detections': len(logs),
                        'persons': daily_persons,
                        'known_faces': daily_known,
                        'unknown_faces': daily_unknown
                    })
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Error getting detection stats: {str(e)}")
            return {}
    
    def cleanup_old_logs(self, days: int = 30):
        """
        Hapus log deteksi lama
        
        Args:
            days: Jumlah hari untuk menyimpan log
        """
        try:
            cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
            
            for log_file in self.log_dir.glob("detections_*.json"):
                if log_file.stat().st_mtime < cutoff_date:
                    log_file.unlink()
                    self.logger.info(f"Log lama dihapus: {log_file}")
                    
        except Exception as e:
            self.logger.error(f"Error cleanup old logs: {str(e)}")


class SystemStats:
    """Kelas untuk menyimpan statistik sistem"""
    
    def __init__(self, stats_file: str = "data/system_stats.json"):
        """
        Inisialisasi System Stats
        
        Args:
            stats_file: Path ke file statistik sistem
        """
        self.stats_file = Path(stats_file)
        self.logger = logging.getLogger(__name__)
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict:
        """Load statistik dari file"""
        try:
            if self.stats_file.exists():
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            else:
                return {
                    'total_start_time': datetime.now().isoformat(),
                    'total_detections': 0,
                    'total_persons_detected': 0,
                    'total_faces_recognized': 0,
                    'start_count': 0,
                    'last_start_time': None
                }
        except Exception as e:
            self.logger.error(f"Error loading stats: {str(e)}")
            return {}
    
    def save_stats(self):
        """Simpan statistik ke file"""
        try:
            self.stats['last_update'] = datetime.now().isoformat()
            
            # Buat direktori jika belum ada
            self.stats_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving stats: {str(e)}")
    
    def increment_detection(self, person_count: int):
        """
        Increment counter deteksi
        
        Args:
            person_count: Jumlah orang yang terdeteksi
        """
        self.stats['total_detections'] += 1
        self.stats['total_persons_detected'] += person_count
        self.save_stats()
    
    def increment_face_recognition(self, count: int = 1):
        """
        Increment counter pengenalan wajah
        
        Args:
            count: Jumlah wajah yang dikenali
        """
        self.stats['total_faces_recognized'] += count
        self.save_stats()
    
    def record_start(self):
        """Record aplikasi start"""
        self.stats['start_count'] += 1
        self.stats['last_start_time'] = datetime.now().isoformat()
        self.save_stats()
    
    def get_stats(self) -> Dict:
        """Mendapatkan statistik sistem"""
        return self.stats.copy()
    
    def reset_stats(self):
        """Reset semua statistik"""
        self.stats = {
            'total_start_time': datetime.now().isoformat(),
            'total_detections': 0,
            'total_persons_detected': 0,
            'total_faces_recognized': 0,
            'start_count': 0,
            'last_start_time': None
        }
        self.save_stats()
