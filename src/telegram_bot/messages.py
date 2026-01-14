"""
Messages - Template pesan untuk Telegram Bot dalam bahasa Indonesia
"""

class Messages:
    """Kelas untuk menyimpan semua template pesan Telegram"""
    
    # Pesan selamat datang
    WELCOME = """
🎥 **CCTV AI TELEGRAM BOT**
*Dikembangkan oleh Riftech*

━━━━━━━━━━━━━━━━━━━━━━━━

🎉 **Selamat Datang!**

Sistem keamanan canggih dengan deteksi orang dan pengenalan wajah otomatis. Kirim notifikasi instan ke Telegram Anda!

━━━━━━━━━━━━━━━━━━━━━━━━

📋 **DAFTAR COMMAND**

━━━━━━━━━━━━━━━━━━━━━━━━

📊 **INFORMASI SISTEM**
/start - Menampilkan pesan ini
/status - Cek status sistem
/stats - Lihat statistik deteksi

📸 **MONITORING**
/screenshot - Ambil foto kamera saat ini

👤 **MANAJEMEN WAJAH**
/addface [nama] - Tambah wajah baru
  Contoh: /addface Budi
/listfaces - Lihat daftar wajah terdaftar
/delface [nama] - Hapus wajah dari database
  Contoh: /delface Budi
/reply_name [nama] - Tambah nama dari foto reply
  Contoh: /reply_name Ahmad

🔧 **ENHANCEMENT**
/enhance - Perjelas kualitas foto reply

⚙️ **PENGATURAN**
/settings - Buka menu pengaturan
/toggle_detection - Aktif/nonaktif deteksi

❓ **BANTUAN**
/help - Panduan lengkap

━━━━━━━━━━━━━━━━━━━━━━━━

💡 **CARA PENGGUNAAN**

1️⃣ **Tambah Wajah:**
   - Kirim: /addface NamaOrang
   - Upload foto wajah orang tersebut
   - Selesai! Bot otomatis mengenali

2️⃣ **Reply Foto untuk Tambah Nama:**
   - Reply foto notifikasi + /reply_name Nama
   - Bot otomatis tambah wajah

3️⃣ **Perjelas Foto:**
   - Reply foto + /enhance
   - Bot akan perjelas kualitas

━━━━━━━━━━━━━━━━━━━━━━━━

🚀 **FITUR UTAMA**

✅ Deteksi orang real-time (YOLOv8n)
✅ Pengenalan wajah otomatis
✅ Notifikasi instan ke Telegram
✅ Kirim 2 foto (full + zoom wajah)
✅ Kontrol penuh via chat
✅ Auto-reconnect jika kamera terputus

━━━━━━━━━━━━━━━━━━━━━━━━

📱 **SUPPORT & INFO**

📧 Email: info@riftech.com
🌐 Website: www.riftech.com

━━━━━━━━━━━━━━━━━━━━━━━━

👨‍💻 **CCTV AI Telegram Bot v1.0**
*Developed by Riftech © 2026*

━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    HELP = """
📖 **Bantuan Lengkap - CCTV AI Bot**

━━━━━━━━━━━━━━━━━━━━━━━━

📋 **DAFTAR COMMAND LENGKAP**

━━━━━━━━━━━━━━━━━━━━━━━━

📊 **INFORMASI SISTEM**
━━━━━━━━━━━━━━━━━━━━━━━━
/start - Menampilkan pesan selamat datang
/status - Cek status sistem (kamera, deteksi, wajah)
/stats - Lihat statistik deteksi lengkap

📸 **MONITORING**
━━━━━━━━━━━━━━━━━━━━━━━━
/screenshot - Ambil foto kamera saat ini
  → Bot akan kirim foto live dari kamera

👤 **MANAJEMEN WAJAH**
━━━━━━━━━━━━━━━━━━━━━━━━
/addface [nama] - Tambah wajah baru dengan upload foto
  Contoh: /addface Budi
  → Kirim perintah, lalu upload foto wajah

/listfaces - Lihat semua wajah yang terdaftar
  → Menampilkan list nama semua wajah di database

/delface [nama] - Hapus wajah dari database
  Contoh: /delface Budi
  → Wajah tidak akan lagi dikenali sistem

/reply_name [nama] - Tambah nama dari foto reply
  Contoh: /reply_name Ahmad
  → Reply foto notifikasi + command ini untuk tambah wajah

🔧 **ENHANCEMENT**
━━━━━━━━━━━━━━━━━━━━━━━━
/enhance - Perjelas kualitas foto reply
  → Reply foto + command ini untuk enhance
  → Foto akan diterang, dipertajam, dan diperbaiki kontrasnya

⚙️ **PENGATURAN**
━━━━━━━━━━━━━━━━━━━━━━━━
/settings - Buka menu pengaturan lengkap
  → Melihat semua pengaturan aktif

/toggle_detection - Aktifkan/nonaktifkan deteksi
  → On/off deteksi orang

━━━━━━━━━━━━━━━━━━━━━━━━

💡 **PANDUAN MENAMBAH WAJAH**

**Cara 1: Upload Foto**
1. Kirim: /addface NamaOrang
2. Upload foto wajah orang tersebut
3. Sistem otomatis tambah ke database

**Cara 2: Reply Foto (Rekomendasi)**
1. Bot kirim notifikasi deteksi
2. Reply salah satu foto + /reply_name Nama
3. Sistem otomatis tambah dari foto reply

💡 **PANDUAN ENHANCE FOTO**
1. Bot kirim foto notifikasi
2. Reply salah satu foto + /enhance
3. Bot akan perjelas kualitas:
   • Increase brightness (+20%)
   • Sharpen edges (+30%)
   • Improve contrast (+15%)
4. Kirim foto yang sudah di-enhance

━━━━━━━━━━━━━━━━━━━━━━━━

📌 **TIPS PENTING**

• Gunakan foto yang JELAS dan TERANG
• Wajah harus MENGHADAP kamera
• Pastikan PENCAHAYAAN cukup
• Hanya SATU WAJAH dalam foto (untuk /addface)
• Foto dari kamera lebih akurat (untuk /reply_name)

━━━━━━━━━━━━━━━━━━━━━━━━

❓ **PERTANYAAN SERING DITANYAKAN**

**Q: Bagaimana cara tambah wajah dengan cepat?**
A: Gunakan /reply_name dengan reply foto notifikasi

**Q: Foto terlalu gelap/diburamkan?**
A: Reply foto + /enhance untuk perjelas

**Q: Apakah bisa tambah wajah tanpa foto baru?**
A: Ya, reply foto notifikasi + /reply_name Nama

**Q: Berapa wajah maksimal yang bisa disimpan?**
A: Tidak ada batas, tapi rekomendasi <50 untuk performa terbaik

**Q: Apakah sistem kirim notifikasi 24 jam?**
A: Ya, tapi bisa diatur di /settings

━━━━━━━━━━━━━━━━━━━━━━━━

📱 **BUTUH BANTUAN LAIN?**

Email: info@riftech.com
Website: www.riftech.com

━━━━━━━━━━━━━━━━━━━━━━━━

👨‍💻 **CCTV AI Telegram Bot v1.0**
*Developed by Riftech © 2026*

━━━━━━━━━━━━━━━━━━━━━━━━
"""
    
    STATUS = """
📊 **Status Sistem**

**Kamera:**
🔌 Status: {camera_status}
📡 IP: {camera_ip}
📐 Resolusi: {resolution}
⚡ FPS: {fps}

**Deteksi:**
👥 Deteksi Orang: {person_detection}
👤 Pengenalan Wajah: {face_recognition}
🎯 Confidence Threshold: {confidence}

**Database Wajah:**
📁 Total Wajah: {face_count}
👥 Orang Terdaftar: {person_count}

**Telegram Bot:**
✅ Bot Online
📱 Chat ID: {chat_id}

**Waktu Terakhir Update:**
{timestamp}
"""
    
    SETTINGS = """
⚙️ **Pengaturan Sistem**

Pilih pengaturan yang ingin diubah:

1. **Deteksi Orang** - {person_detection_status}
   Command: /toggle_person_detection

2. **Pengenalan Wajah** - {face_recognition_status}
   Command: /toggle_face_recognition

3. **Interval Deteksi** - {detection_interval} detik
   Command: /set_detection_interval [detik]

4. **Confidence Threshold** - {confidence}
   Command: /set_confidence [0.0-1.0]

5. **Toleransi Pengenalan Wajah** - {tolerance}
   Command: /set_tolerance [0.0-1.0]

6. **Notifikasi Orang Dikenali** - {known_alert}
   Command: /toggle_known_alert

7. **Notifikasi Orang Tidak Dikenali** - {unknown_alert}
   Command: /toggle_unknown_alert

Gunakan perintah yang sesuai untuk mengubah pengaturan.
"""
    
    FACE_ADDED = """
✅ **Wajah Berhasil Ditambahkan!**

👤 Nama: {name}
📊 Confidence: {confidence:.2f}
🕐 Waktu: {timestamp}

Sekarang sistem dapat mengenali orang ini!
"""
    
    FACE_ADDED_ERROR = """
❌ **Gagal Menambahkan Wajah**

Terjadi kesalahan saat menambahkan wajah:
{error}

Pastikan:
• Foto jelas dan terang
• Wajah terlihat dengan baik
• Tidak ada wajah ganda dalam foto

Coba kirim ulang foto yang lebih baik.
"""
    
    FACE_REMOVED = """
✅ **Wajah Berhasil Dihapus!**

👤 Nama: {name}
🕐 Waktu: {timestamp}

Wajah ini tidak akan lagi dikenali oleh sistem.
"""
    
    FACE_NOT_FOUND = """
❌ **Wajah Tidak Ditemukan**

Nama "{name}" tidak ditemukan dalam database.

Gunakan /listfaces untuk melihat semua wajah yang tersimpan.
"""
    
    FACE_LIST = """
📋 **Daftar Wajah Terdaftar**

Total: {count} orang

{faces_list}

Gunakan /delface [nama] untuk menghapus wajah.
"""
    
    NO_FACES = """
📋 **Daftar Wajah Terdaftar**

Belum ada wajah yang terdaftar.

Gunakan /addface [nama] untuk menambahkan wajah baru.
"""
    
    DETECTION_ALERT = """
🚨 **Deteksi Orang!**

📸 Foto terlampir
🕐 Waktu: {timestamp}
👥 Jumlah Orang: {person_count}

{face_info}
"""
    
    FACE_DETECTED_INFO = """
**Wajah Terdeteksi:**
{face_list}
"""
    
    SCREENSHOT_SUCCESS = """
📸 **Screenshot Berhasil!**

Foto dari kamera saat ini.
🕐 Waktu: {timestamp}
"""
    
    SCREENSHOT_ERROR = """
❌ **Gagal Mengambil Screenshot**

Terjadi kesalahan: {error}

Pastikan kamera terkoneksi dengan baik.
"""
    
    TOGGLE_DETECTION_ON = """
✅ **Deteksi Diaktifkan**

Sekarang sistem akan mendeteksi orang dan mengirim notifikasi.
"""
    
    TOGGLE_DETECTION_OFF = """
⏸️ **Deteksi Dinonaktifkan**

Sistem tidak akan mendeteksi orang sampai diaktifkan kembali.
Gunakan /toggle_detection untuk mengaktifkan.
"""
    
    SET_INTERVAL_SUCCESS = """
✅ **Interval Deteksi Diubah**

Interval deteksi: {interval} detik
"""
    
    SET_CONFIDENCE_SUCCESS = """
✅ **Confidence Threshold Diubah**

Confidence threshold: {confidence}
"""
    
    SET_TOLERANCE_SUCCESS = """
✅ **Toleransi Pengenalan Diubah**

Toleransi pengenalan wajah: {tolerance}
"""
    
    INVALID_INPUT = """
❌ **Input Tidak Valid**

Input yang Anda berikan tidak valid.
Format yang benar: {format}

Contoh: {example}
"""
    
    ERROR_OCCURRED = """
❌ **Terjadi Kesalahan**

Terjadi kesalahan dalam sistem:
{error}

Silakan coba lagi nanti atau hubungi administrator.
"""
    
    LOG_ENTRY = """
📝 **Log Terakhir**

{log_content}
"""
    
    STATS = """
📊 **Statistik Deteksi**

**Total Deteksi:** {total_detections}
**Orang Dikenali:** {known_count}
**Orang Tidak Dikenali:** {unknown_count}
**Rata-rata Confidence:** {avg_confidence:.2f}

**Wajah Terdaftar:** {face_count}

**Waktu Terakhir Update:** {timestamp}
"""
    
    ADD_FACE_INSTRUCTION = """
📸 **Menambah Wajah Baru**

Silakan kirim foto wajah untuk: {name}

Pastikan:
• Wajah terlihat jelas
• Pencahayaan cukup
• Wajah menghadap kamera
• Hanya satu wajah dalam foto

Kirim /cancel untuk membatalkan.
"""
    
    CANCEL_ADD_FACE = """
❌ **Penambahan Wajah Dibatalkan**

Tidak ada wajah yang ditambahkan.
"""
    
    CAMERA_DISCONNECTED = """
⚠️ **Peringatan: Kamera Terputus**

Koneksi ke kamera terputus. Sistem mencoba reconnect...

IP: {ip}
Waktu: {timestamp}

Periksa koneksi jaringan dan status kamera.
"""
    
    CAMERA_RECONNECTED = """
✅ **Kamera Terhubung Kembali**

Berhasil reconnect ke kamera!
IP: {ip}
Waktu: {timestamp}
"""
    
    SYSTEM_STARTED = """
🚀 **Sistem Dimulai!**

CCTV AI Bot telah aktif dan siap mendeteksi.

Kamera: {ip}
Status: Online

Gunakan /status untuk cek status sistem.
"""
    
    SYSTEM_STOPPED = """
🛑 **Sistem Berhenti**

CCTV AI Bot telah berhenti.

Data dan konfigurasi tersimpan.
"""

    # Pesan untuk reply_name
    REPLY_NAME_SUCCESS = """
✅ **Wajah Berhasil Ditambahkan!**

👤 Nama: {name}
📊 Confidence: {confidence:.2f}
🕐 Waktu: {timestamp}

Sekarang sistem dapat mengenali orang ini!

━━━━━━━━━━━━━━━━━━━━━━━━
*Developed by Riftech*
"""

    REPLY_NAME_ERROR = """
❌ **Gagal Menambahkan Wajah**

Terjadi kesalahan: {error}

Pastikan:
• Reply berupa foto
• Foto mengandung wajah
• Nama tidak kosong
• Hanya satu wajah dalam foto

Coba lagi atau gunakan /addface [nama]

━━━━━━━━━━━━━━━━━━━━━━━━
*Developed by Riftech*
"""

    REPLY_NAME_NO_REPLY = """
❌ **Salah Penggunaan**

Anda harus REPLY foto untuk menambahkan nama.

Cara penggunaan:
1. Reply salah satu foto dari notifikasi deteksi
2. Ketik: /reply_name NamaOrang
3. Bot otomatis tambah wajah ke database

━━━━━━━━━━━━━━━━━━━━━━━━
*Developed by Riftech*
"""

    REPLY_NAME_NO_PHOTO = """
❌ **Reply Tidak Berupa Foto**

Reply Anda tidak mengandung foto.

Pastikan Anda reply salah satu foto dari notifikasi deteksi.

━━━━━━━━━━━━━━━━━━━━━━━━
*Developed by Riftech*
"""

    REPLY_NAME_NO_ARGS = """
❌ **Format Salih**

Format yang benar: /reply_name [nama]

Contoh:
/reply_name Ahmad
/reply_name Budi Santoso

━━━━━━━━━━━━━━━━━━━━━━━━
*Developed by Riftech*
"""

    REPLY_NAME_MULTIPLE_FACES = """
❌ **Terlalu Banyak Wajah**

Terdeteksi lebih dari satu wajah dalam foto.

Untuk menambahkan wajah, pastikan hanya SATU wajah dalam foto reply.

Atau gunakan /addface [nama] untuk upload foto tunggal.

━━━━━━━━━━━━━━━━━━━━━━━━
*Developed by Riftech*
"""

    # Pesan untuk enhance
    ENHANCE_SUCCESS = """
✅ **Foto Berhasil di-Enhance!**

📸 Foto telah diperjelas dan diperbaiki
✨ Kualitas meningkat +{improvement}%

Perubahan yang dilakukan:
• Brightness: +20%
• Sharpness: +30%
• Contrast: +15%

💡 Sekarang lebih mudah dikenali!

━━━━━━━━━━━━━━━━━━━━━━━━
*Developed by Riftech*
"""

    ENHANCE_ERROR = """
❌ **Gagal Enhance Foto**

Terjadi kesalahan: {error}

Pastikan:
• Reply berupa foto
• Foto valid
• Format file didukung (JPG, PNG)

Coba reply foto lain.

━━━━━━━━━━━━━━━━━━━━━━━━
*Developed by Riftech*
"""

    ENHANCE_NO_REPLY = """
❌ **Salah Penggunaan**

Anda harus REPLY foto untuk meng-enhance.

Cara penggunaan:
1. Reply salah satu foto dari notifikasi deteksi
2. Ketik: /enhance
3. Bot akan perjelas kualitas foto

━━━━━━━━━━━━━━━━━━━━━━━━
*Developed by Riftech*
"""

    ENHANCE_NO_PHOTO = """
❌ **Reply Tidak Berupa Foto**

Reply Anda tidak mengandung foto.

Pastikan Anda reply salah satu foto dari notifikasi deteksi.

━━━━━━━━━━━━━━━━━━━━━━━━
*Developed by Riftech*
"""
