"""
Bot Handler - Handler utama untuk Telegram Bot
"""

import logging
import asyncio
from telegram import Bot
from telegram.ext import Application, ContextTypes
from .commands import BotCommands
from .messages import Messages


class BotHandler:
    """Kelas untuk mengelola Telegram Bot"""
    
    def __init__(self, bot_token: str, camera_manager, face_detector, 
                 person_detector, face_recognition, config):
        """
        Inisialisasi Bot Handler
        
        Args:
            bot_token: Token Telegram Bot
            camera_manager: Instance CameraManager
            face_detector: Instance FaceDetector
            person_detector: Instance PersonDetector
            face_recognition: Instance FaceRecognition
            config: Konfigurasi sistem
        """
        self.bot_token = bot_token
        self.camera = camera_manager
        self.face_detector = face_detector
        self.person_detector = person_detector
        self.face_recognition = face_recognition
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.messages = Messages()
        
        # Telegram application
        self.application = None
        self.commands = None
        
        # Chat ID untuk notifikasi
        self.chat_id = None
        self.admin_id = None
        
    async def send_detection_alert(self, frame, detected_persons, recognized_faces, face_crops=None):
        """
        Kirim notifikasi deteksi ke Telegram dengan zoom wajah
        
        Args:
            frame: Frame dari kamera
            detected_persons: List orang yang terdeteksi
            recognized_faces: List wajah yang dikenali
            face_crops: List wajah yang di-crop untuk zoom (opsional)
        """
        try:
            if not self.chat_id:
                self.logger.warning("Chat ID tidak tersedia")
                return
            
            import cv2
            import os
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            person_count = len(detected_persons)
            
            # Kirim foto full frame dulu (SEGERA)
            temp_frame_path = f"/tmp/detection_{timestamp}.jpg"
            cv2.imwrite(temp_frame_path, frame)
            
            # Buat pesan
            face_info = ""
            if recognized_faces and len(recognized_faces) > 0:
                face_list = "\n".join([
                    f"• {face['display_name']} (Conf: {face['distance']:.2f})"
                    for face in recognized_faces
                ])
                face_info = self.messages.FACE_DETECTED_INFO.format(face_list=face_list)
            
            message = self.messages.DETECTION_ALERT.format(
                timestamp=current_time,
                person_count=person_count,
                face_info=face_info
            )
            
            # Kirim foto full frame dengan caption
            await self.application.bot.send_photo(
                chat_id=self.chat_id,
                photo=open(temp_frame_path, 'rb'),
                caption=message,
                parse_mode='Markdown'
            )
            self.logger.info(f"Foto full frame terkirim ke {self.chat_id}")
            
            # Hapus temporary file
            os.remove(temp_frame_path)
            
            # Kirim zoom wajah jika ada
            if face_crops and len(face_crops) > 0:
                for i, (face_crop, bbox, confidence) in enumerate(face_crops):
                    # Simpan zoom wajah
                    temp_face_path = f"/tmp/face_zoom_{timestamp}_{i}.jpg"
                    cv2.imwrite(temp_face_path, face_crop)
                    
                    # Kirim zoom wajah
                    face_label = "Wajah Terdeteksi"
                    if i < len(recognized_faces):
                        face = recognized_faces[i]
                        if face['status'] == 'known':
                            face_label = f"👤 {face['display_name']}"
                        else:
                            face_label = "❓ Wajah Tidak Dikenal"
                    
                    await self.application.bot.send_photo(
                        chat_id=self.chat_id,
                        photo=open(temp_face_path, 'rb'),
                        caption=f"🔍 {face_label}\n📊 Confidence: {confidence:.2f}",
                        parse_mode='Markdown'
                    )
                    
                    self.logger.info(f"Zoom wajah #{i} terkirim")
                    
                    # Hapus temporary file
                    os.remove(temp_face_path)
            
            self.logger.info(f"Notifikasi deteksi terkirim ke {self.chat_id}")
            
        except Exception as e:
            self.logger.error(f"Error kirim notifikasi deteksi: {str(e)}", exc_info=True)
    
    async def send_camera_disconnected_alert(self):
        """Kirim notifikasi kamera terputus"""
        try:
            if not self.chat_id:
                return
            
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            message = self.messages.CAMERA_DISCONNECTED.format(
                ip=self.camera.ip,
                timestamp=timestamp
            )
            
            await self.application.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error kirim notifikasi kamera terputus: {str(e)}")
    
    async def send_camera_reconnected_alert(self):
        """Kirim notifikasi kamera terhubung kembali"""
        try:
            if not self.chat_id:
                return
            
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            message = self.messages.CAMERA_RECONNECTED.format(
                ip=self.camera.ip,
                timestamp=timestamp
            )
            
            await self.application.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error kirim notifikasi kamera reconnect: {str(e)}")
    
    async def send_system_started(self):
        """Kirim notifikasi sistem dimulai"""
        try:
            if not self.chat_id:
                return
            
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            message = self.messages.SYSTEM_STARTED.format(
                ip=self.camera.ip,
                timestamp=timestamp
            )
            
            await self.application.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            
        except Exception as e:
            self.logger.error(f"Error kirim notifikasi sistem dimulai: {str(e)}")
    
    def initialize(self, chat_id: int, admin_id: int = None):
        """
        Inisialisasi Telegram Bot
        
        Args:
            chat_id: Chat ID untuk notifikasi
            admin_id: Admin ID (opsional)
        """
        try:
            self.chat_id = chat_id
            self.admin_id = admin_id
            
            # Create application
            self.application = Application.builder().token(self.bot_token).build()
            
            # Create commands handler
            self.commands = BotCommands(
                self.camera,
                self.face_detector,
                self.person_detector,
                self.face_recognition,
                self.config
            )
            
            # Add handlers
            for handler in self.commands.get_handlers():
                self.application.add_handler(handler)
            
            self.logger.info("Telegram Bot berhasil diinisialisasi")
            
        except Exception as e:
            self.logger.error(f"Error inisialisasi bot: {str(e)}")
            raise
    
    async def start_bot(self):
        """Mulai Telegram Bot"""
        try:
            # Run bot
            self.logger.info("Memulai Telegram Bot...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            
            # Kirim notifikasi sistem dimulai
            await self.send_system_started()
            
            self.logger.info("Telegram Bot berjalan")
            
        except Exception as e:
            self.logger.error(f"Error memulai bot: {str(e)}")
            raise
    
    async def stop_bot(self):
        """Hentikan Telegram Bot"""
        try:
            if self.application:
                await self.application.updater.stop()
                await self.application.stop()
                await self.application.shutdown()
                
                # Kirim notifikasi sistem berhenti
                if self.chat_id:
                    await self.application.bot.send_message(
                        chat_id=self.chat_id,
                        text=self.messages.SYSTEM_STOPPED,
                        parse_mode='Markdown'
                    )
                
                self.logger.info("Telegram Bot berhenti")
                
        except Exception as e:
            self.logger.error(f"Error menghentikan bot: {str(e)}")
    
    def get_commands_instance(self) -> BotCommands:
        """Mendapatkan instance commands"""
        return self.commands
    
    def is_initialized(self) -> bool:
        """Cek apakah bot sudah diinisialisasi"""
        return self.application is not None
    
    def is_running(self) -> bool:
        """Cek apakah bot sedang berjalan"""
        if self.application and self.application.updater:
            return self.application.updater.is_running()
        return False
