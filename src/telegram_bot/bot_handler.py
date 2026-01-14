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
        
    async def send_detection_alert(self, frame, detected_persons, recognized_faces):
        """
        Kirim notifikasi deteksi ke Telegram
        
        Args:
            frame: Frame dari kamera
            detected_persons: List orang yang terdeteksi
            recognized_faces: List wajah yang dikenali
        """
        try:
            if not self.chat_id:
                self.logger.warning("Chat ID tidak tersedia")
                return
            
            # Simpan frame ke temporary file
            import cv2
            import os
            from datetime import datetime
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_path = f"/tmp/detection_{timestamp}.jpg"
            cv2.imwrite(temp_path, frame)
            
            # Buat pesan
            from datetime import datetime
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            person_count = len(detected_persons)
            
            # Info wajah yang terdeteksi
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
            
            # Kirim pesan dan foto
            await self.application.bot.send_photo(
                chat_id=self.chat_id,
                photo=open(temp_path, 'rb'),
                caption=message,
                parse_mode='Markdown'
            )
            
            # Hapus temporary file
            os.remove(temp_path)
            
            self.logger.info(f"Notifikasi deteksi terkirim ke {self.chat_id}")
            
        except Exception as e:
            self.logger.error(f"Error kirim notifikasi deteksi: {str(e)}")
    
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
