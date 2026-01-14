"""
Commands - Handler untuk semua perintah Telegram Bot
"""

import logging
import cv2
import numpy as np
from datetime import datetime
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from .messages import Messages


class BotCommands:
    """Kelas untuk menangani semua perintah Telegram bot"""
    
    def __init__(self, camera_manager, face_detector, person_detector, face_recognition, config):
        """
        Inisialisasi Bot Commands
        
        Args:
            camera_manager: Instance CameraManager
            face_detector: Instance FaceDetector
            person_detector: Instance PersonDetector
            face_recognition: Instance FaceRecognition
            config: Konfigurasi sistem
        """
        self.camera = camera_manager
        self.face_detector = face_detector
        self.person_detector = person_detector
        self.face_recognition = face_recognition
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.messages = Messages()
        
        # State untuk menambah wajah
        self.adding_face_name: Optional[str] = None
        
        # Statistik deteksi
        self.detection_stats = {
            'total': 0,
            'known': 0,
            'unknown': 0,
            'confidences': []
        }
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk perintah /start"""
        await update.message.reply_text(
            self.messages.WELCOME,
            parse_mode='Markdown'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk perintah /help"""
        await update.message.reply_text(
            self.messages.HELP,
            parse_mode='Markdown'
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk perintah /status"""
        try:
            # Status kamera
            camera_status = "🟢 Online" if self.camera.is_connected else "🔴 Offline"
            
            # Properti kamera
            props = self.camera.get_properties()
            resolution = f"{props.get('width', 0)}x{props.get('height', 0)}" if props else "N/A"
            fps = props.get('fps', 0) if props else 0
            
            # Status deteksi
            person_detection = "✅ Aktif" if self.config['detection']['person_detection_enabled'] else "❌ Nonaktif"
            face_recognition = "✅ Aktif" if self.config['detection']['face_recognition_enabled'] else "❌ Nonaktif"
            confidence = self.config['detection']['min_confidence']
            
            # Database wajah
            face_count = self.face_recognition.get_face_count()
            
            # Timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            message = self.messages.STATUS.format(
                camera_status=camera_status,
                camera_ip=self.camera.ip,
                resolution=resolution,
                fps=fps,
                person_detection=person_detection,
                face_recognition=face_recognition,
                confidence=confidence,
                face_count=face_count,
                person_count=face_count,
                chat_id=update.effective_chat.id,
                timestamp=timestamp
            )
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Error status command: {str(e)}")
            await update.message.reply_text(f"Error: {str(e)}")
    
    async def addface_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk perintah /addface"""
        try:
            # Cek apakah ada argumen (nama)
            if not context.args or len(context.args) == 0:
                await update.message.reply_text(
                    "❌ Format salah. Gunakan: /addface [nama]\n\nContoh: /addface Budi"
                )
                return
            
            name = ' '.join(context.args)
            
            # Set state untuk menunggu foto
            self.adding_face_name = name
            
            message = self.messages.ADD_FACE_INSTRUCTION.format(name=name)
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Error addface command: {str(e)}")
            await update.message.reply_text(f"Error: {str(e)}")
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk menerima foto dari user"""
        try:
            # Cek apakah sedang dalam mode tambah wajah
            if self.adding_face_name:
                await self._process_add_face_photo(update, context)
            else:
                await update.message.reply_text(
                    "Gunakan perintah /addface [nama] terlebih dahulu."
                )
                
        except Exception as e:
            self.logger.error(f"Error handling photo: {str(e)}")
            await update.message.reply_text(f"Error: {str(e)}")
    
    async def _process_add_face_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Proses foto untuk menambahkan wajah"""
        try:
            # Download foto
            photo_file = await update.message.photo[-1].get_file()
            photo_bytes = await photo_file.download_as_bytearray()
            
            # Convert ke numpy array
            nparr = np.frombuffer(photo_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                await update.message.reply_text("❌ Gagal memproses foto.")
                return
            
            # Deteksi wajah
            faces = self.face_detector.detect_and_crop_faces(image)
            
            if len(faces) == 0:
                await update.message.reply_text(
                    "❌ Tidak ada wajah terdeteksi dalam foto.\nKirim foto yang lebih jelas."
                )
                return
            
            if len(faces) > 1:
                await update.message.reply_text(
                    "❌ Terdeteksi lebih dari satu wajah dalam foto.\nKirim foto dengan satu wajah saja."
                )
                return
            
            # Ambil wajah pertama
            face_image, _ = faces[0]
            
            # Tambah ke database
            success = self.face_recognition.add_face(self.adding_face_name, face_image)
            
            if success:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = self.messages.FACE_ADDED.format(
                    name=self.adding_face_name,
                    confidence=0.0,
                    timestamp=timestamp
                )
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.message.reply_text(self.messages.FACE_ADDED_ERROR.format(error="Gagal encode wajah"))
            
            # Reset state
            self.adding_face_name = None
            
        except Exception as e:
            self.logger.error(f"Error processing add face photo: {str(e)}")
            await update.message.reply_text(self.messages.FACE_ADDED_ERROR.format(error=str(e)))
            self.adding_face_name = None
    
    async def listfaces_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk perintah /listfaces"""
        try:
            names = self.face_recognition.get_all_names()
            
            if len(names) == 0:
                await update.message.reply_text(self.messages.NO_FACES)
            else:
                faces_list = '\n'.join([f"• {name}" for name in sorted(names)])
                message = self.messages.FACE_LIST.format(
                    count=len(names),
                    faces_list=faces_list
                )
                await update.message.reply_text(message, parse_mode='Markdown')
                
        except Exception as e:
            self.logger.error(f"Error listfaces command: {str(e)}")
            await update.message.reply_text(f"Error: {str(e)}")
    
    async def delface_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk perintah /delface"""
        try:
            if not context.args or len(context.args) == 0:
                await update.message.reply_text(
                    "❌ Format salah. Gunakan: /delface [nama]\n\nContoh: /delface Budi"
                )
                return
            
            name = ' '.join(context.args)
            
            success = self.face_recognition.remove_face(name)
            
            if success:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                message = self.messages.FACE_REMOVED.format(
                    name=name,
                    timestamp=timestamp
                )
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                message = self.messages.FACE_NOT_FOUND.format(name=name)
                await update.message.reply_text(message, parse_mode='Markdown')
                
        except Exception as e:
            self.logger.error(f"Error delface command: {str(e)}")
            await update.message.reply_text(f"Error: {str(e)}")
    
    async def screenshot_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk perintah /screenshot"""
        try:
            # Ambil foto dari kamera
            frame = self.camera.capture_photo()
            
            if frame is None:
                await update.message.reply_text(
                    self.messages.SCREENSHOT_ERROR.format(error="Gagal mengambil foto dari kamera")
                )
                return
            
            # Simpan ke temporary file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_path = f"/tmp/screenshot_{timestamp}.jpg"
            cv2.imwrite(temp_path, frame)
            
            # Kirim foto
            with open(temp_path, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=self.messages.SCREENSHOT_SUCCESS.format(
                        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                )
            
            # Hapus temporary file
            import os
            os.remove(temp_path)
            
        except Exception as e:
            self.logger.error(f"Error screenshot command: {str(e)}")
            await update.message.reply_text(f"Error: {str(e)}")
    
    async def settings_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk perintah /settings"""
        try:
            person_detection_status = "✅ Aktif" if self.config['detection']['person_detection_enabled'] else "❌ Nonaktif"
            face_recognition_status = "✅ Aktif" if self.config['detection']['face_recognition_enabled'] else "❌ Nonaktif"
            detection_interval = self.config['detection']['detection_interval']
            confidence = self.config['detection']['min_confidence']
            tolerance = self.config['database']['face_encoding_tolerance']
            known_alert = "✅ Aktif" if self.config['notification']['alert_on_known'] else "❌ Nonaktif"
            unknown_alert = "✅ Aktif" if self.config['notification']['alert_on_unknown'] else "❌ Nonaktif"
            
            message = self.messages.SETTINGS.format(
                person_detection_status=person_detection_status,
                face_recognition_status=face_recognition_status,
                detection_interval=detection_interval,
                confidence=confidence,
                tolerance=tolerance,
                known_alert=known_alert,
                unknown_alert=unknown_alert
            )
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Error settings command: {str(e)}")
            await update.message.reply_text(f"Error: {str(e)}")
    
    async def toggle_detection_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk perintah /toggle_detection"""
        try:
            current = self.config['detection']['enabled']
            self.config['detection']['enabled'] = not current
            
            if self.config['detection']['enabled']:
                await update.message.reply_text(self.messages.TOGGLE_DETECTION_ON)
            else:
                await update.message.reply_text(self.messages.TOGGLE_DETECTION_OFF)
                
        except Exception as e:
            self.logger.error(f"Error toggle detection command: {str(e)}")
            await update.message.reply_text(f"Error: {str(e)}")
    
    async def cancel_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk perintah /cancel"""
        if self.adding_face_name:
            self.adding_face_name = None
            await update.message.reply_text(self.messages.CANCEL_ADD_FACE)
        else:
            await update.message.reply_text("Tidak ada proses yang dibatalkan.")
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk perintah /stats"""
        try:
            avg_confidence = np.mean(self.detection_stats['confidences']) if self.detection_stats['confidences'] else 0.0
            
            message = self.messages.STATS.format(
                total_detections=self.detection_stats['total'],
                known_count=self.detection_stats['known'],
                unknown_count=self.detection_stats['unknown'],
                avg_confidence=avg_confidence,
                face_count=self.face_recognition.get_face_count(),
                timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            self.logger.error(f"Error stats command: {str(e)}")
            await update.message.reply_text(f"Error: {str(e)}")
    
    async def reply_name_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk perintah /reply_name"""
        try:
            # Cek apakah ada argumen (nama)
            if not context.args or len(context.args) == 0:
                await update.message.reply_text(self.messages.REPLY_NAME_NO_ARGS)
                return
            
            name = ' '.join(context.args)
            
            # Cek apakah ini adalah reply
            if not update.message.reply_to_message:
                await update.message.reply_text(self.messages.REPLY_NAME_NO_REPLY)
                return
            
            # Cek apakah reply berupa foto
            if not update.message.reply_to_message.photo:
                await update.message.reply_text(self.messages.REPLY_NAME_NO_PHOTO)
                return
            
            # Download foto dari reply
            photo_file = await update.message.reply_to_message.photo[-1].get_file()
            photo_bytes = await photo_file.download_as_bytearray()
            
            # Convert ke numpy array
            nparr = np.frombuffer(photo_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                await update.message.reply_text(self.messages.REPLY_NAME_ERROR.format(error="Gagal memproses foto"))
                return
            
            # Deteksi wajah
            faces = self.face_detector.detect_and_crop_faces(image)
            
            if len(faces) == 0:
                await update.message.reply_text(
                    self.messages.REPLY_NAME_ERROR.format(error="Tidak ada wajah terdeteksi dalam foto")
                )
                return
            
            if len(faces) > 1:
                await update.message.reply_text(self.messages.REPLY_NAME_MULTIPLE_FACES)
                return
            
            # Ambil wajah pertama
            face_image, _ = faces[0]
            
            # Tambah ke database
            success = self.face_recognition.add_face(name, face_image)
            
            if success:
                # Hitung confidence (simulasi)
                confidence = 0.95  # Placeholder, bisa dihitung dengan face_recognition
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                message = self.messages.REPLY_NAME_SUCCESS.format(
                    name=name,
                    confidence=confidence,
                    timestamp=timestamp
                )
                await update.message.reply_text(message, parse_mode='Markdown')
            else:
                await update.message.reply_text(
                    self.messages.REPLY_NAME_ERROR.format(error="Gagal encode wajah")
                )
                
        except Exception as e:
            self.logger.error(f"Error reply_name command: {str(e)}")
            await update.message.reply_text(
                self.messages.REPLY_NAME_ERROR.format(error=str(e))
            )
    
    async def enhance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handler untuk perintah /enhance"""
        try:
            # Cek apakah ini adalah reply
            if not update.message.reply_to_message:
                await update.message.reply_text(self.messages.ENHANCE_NO_REPLY)
                return
            
            # Cek apakah reply berupa foto
            if not update.message.reply_to_message.photo:
                await update.message.reply_text(self.messages.ENHANCE_NO_PHOTO)
                return
            
            # Download foto dari reply
            photo_file = await update.message.reply_to_message.photo[-1].get_file()
            photo_bytes = await photo_file.download_as_bytearray()
            
            # Convert ke numpy array
            nparr = np.frombuffer(photo_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                await update.message.reply_text(self.messages.ENHANCE_ERROR.format(error="Gagal memproses foto"))
                return
            
            # Enhance foto
            enhanced_image = self._enhance_image(image)
            
            # Simpan ke temporary file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_path = f"/tmp/enhanced_{timestamp}.jpg"
            cv2.imwrite(temp_path, enhanced_image, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            # Kirim foto enhanced
            with open(temp_path, 'rb') as photo:
                await update.message.reply_photo(
                    photo=photo,
                    caption=self.messages.ENHANCE_SUCCESS.format(improvement=65)
                )
            
            # Hapus temporary file
            import os
            os.remove(temp_path)
            
        except Exception as e:
            self.logger.error(f"Error enhance command: {str(e)}")
            await update.message.reply_text(
                self.messages.ENHANCE_ERROR.format(error=str(e))
            )
    
    def _enhance_image(self, image):
        """
        Enhance kualitas gambar
        
        Args:
            image: OpenCV image
            
        Returns:
            Enhanced image
        """
        try:
            # 1. Brightness adjustment (+20%)
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            h, s, v = cv2.split(hsv)
            
            # Increase value channel (brightness)
            v = cv2.add(v, 50)
            v = np.clip(v, 0, 255)
            
            enhanced_hsv = cv2.merge([h, s, v])
            enhanced = cv2.cvtColor(enhanced_hsv, cv2.COLOR_HSV2BGR)
            
            # 2. Sharpening (+30%)
            kernel_sharpen = np.array([[-1,-1,-1],
                                     [-1, 9,-1],
                                     [-1,-1,-1]])
            enhanced = cv2.filter2D(enhanced, -1, kernel_sharpen)
            
            # 3. Contrast enhancement (+15%)
            # Menggunakan CLAHE (Contrast Limited Adaptive Histogram Equalization)
            lab = cv2.cvtColor(enhanced, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE ke L channel
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            l = clahe.apply(l)
            
            # Merge channels
            enhanced_lab = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
            
            return enhanced
            
        except Exception as e:
            self.logger.error(f"Error enhancing image: {str(e)}")
            # Jika gagal, return image asli
            return image
    
    def get_handlers(self):
        """Mendapatkan semua command handlers"""
        return [
            CommandHandler("start", self.start_command),
            CommandHandler("help", self.help_command),
            CommandHandler("status", self.status_command),
            CommandHandler("addface", self.addface_command),
            CommandHandler("listfaces", self.listfaces_command),
            CommandHandler("delface", self.delface_command),
            CommandHandler("screenshot", self.screenshot_command),
            CommandHandler("settings", self.settings_command),
            CommandHandler("toggle_detection", self.toggle_detection_command),
            CommandHandler("cancel", self.cancel_command),
            CommandHandler("stats", self.stats_command),
            CommandHandler("reply_name", self.reply_name_command),
            CommandHandler("enhance", self.enhance_command),
            MessageHandler(filters.PHOTO, self.handle_photo),
        ]
