# 🎥 CCTV AI Telegram Bot - Sistem Deteksi Orang dengan Pengenalan Wajah

Sistem CCTV cerdas dengan integrasi Telegram bot untuk kamera V380 IP. Sistem ini dapat mendeteksi orang, mengenali wajah, dan mengirimkan notifikasi langsung ke Telegram.

**Dikembangkan oleh Riftech © 2026**

---

## ✨ Fitur Utama

### 🔌 **Koneksi Kamera IP V380**
- Koneksi otomatis ke kamera CCTV V380
- IP: 10.26.27.196
- User: admin, Password: admin
- Auto-reconnect jika koneksi terputus

### 👁️ **Deteksi Orang Real-time**
- Mendeteksi keberadaan orang secara otomatis
- Menggunakan model YOLOv8n (ringan dan cepat)
- Confidence threshold yang dapat diatur

### 👤 **Pengenalan Wajah**
- Mengenali dan menyimpan nama orang yang terdeteksi
- Database wajah yang dikelola melalui Telegram
- Support untuk banyak orang

### 📸 **Fitur Notifikasi Lanjutan**
- **Kirim 2 Foto**: Full frame + Zoom wajah
- **Reply untuk Tambah Nama**: Tambah wajah dari foto notifikasi
- **Enhance Kualitas**: Perjelas foto dengan satu command

### 📱 **Kontrol Penuh via Telegram**
- Semua konfigurasi melalui chat
- Tambah/hapus wajah dengan mudah
- Aktifkan/nonaktifkan fitur
- Status dan statistik realtime

### 🚨 **Notifikasi Instan**
- Kirimkan foto dan info deteksi langsung ke Telegram
- Informasi lengkap: waktu, jumlah orang, status pengenalan
- Perintah reply yang praktis

### 📊 **Monitoring 24/7**
- Berjalan terus-menerus di Ubuntu server
- Auto-restart dengan systemd
- Logging lengkap

### 🗃️ **Database Wajah**
- Simpan dan kelola database wajah orang yang dikenal
- Support export/import (future)
- Backup otomatis

### ⚙️ **Konfigurasi Fleksibel**
- Pengaturan mudah melalui file config dan Telegram
- Banyak opsi yang dapat disesuaikan
- Hot-reload konfigurasi

---

## 📁 Struktur Direktori

```
cam_ai_telebot/
├── README.md                 # Dokumentasi utama
├── requirements.txt          # Dependensi Python
├── .gitignore               # File untuk git
├── config/                  # Konfigurasi sistem
│   ├── config.yaml.template  # Template konfigurasi utama
│   └── telegram_config.json.template  # Template konfigurasi Telegram
├── src/                     # Source code utama
│   ├── main.py             # Entry point aplikasi
│   ├── camera/             # Modul kamera
│   │   ├── __init__.py
│   │   └── camera_manager.py
│   ├── detection/          # Modul deteksi
│   │   ├── __init__.py
│   │   ├── face_detector.py
│   │   ├── person_detector.py
│   │   └── face_recognition.py
│   ├── telegram_bot/       # Modul Telegram bot
│   │   ├── __init__.py
│   │   ├── bot_handler.py
│   │   ├── commands.py
│   │   └── messages.py
│   └── database/           # Modul database
│       └── __init__.py
├── data/                   # Data aplikasi
│   ├── faces/             # Foto wajah yang tersimpan
│   ├── detections/        # Log deteksi
│   └── recordings/        # Rekaman (opsional)
├── logs/                   # File log aplikasi
└── scripts/                # Script instalasi
    ├── install.sh         # Script instalasi Ubuntu
    ├── setup_camera.sh    # Setup kamera
    ├── setup_bot.sh       # Setup Telegram bot
    └── setup_service.sh  # Setup systemd service
```

---

## 🚀 Instalasi

### Persyaratan Sistem
- Ubuntu Server (Proxmox VM)
- Python 3.8+
- Akses internet (untuk download model dan dependensi)
- Kamera IP V380 di jaringan yang sama
- Telegram Bot Token dan Chat ID

### Langkah-langkah Instalasi

#### 1. Clone/Download Repository
```bash
cd /opt
# Jika menggunakan git:
git clone https://github.com/riftech22/cam_ai_telebot.git
cd cam_ai_telebot
# Atau jika sudah ada:
cd /opt/cam_ai_telebot
```

#### 2. Jalankan Script Instalasi
```bash
chmod +x scripts/install.sh
sudo ./scripts/install.sh
```

Script ini akan:
- Install Python 3.8+ (jika belum ada)
- Install pip dan dependensi sistem
- Install Python virtual environment
- Install semua dependensi Python
- Buat direktori yang diperlukan
- Download model YOLOv8n

#### 3. Konfigurasi Kamera
```bash
chmod +x scripts/setup_camera.sh
./scripts/setup_camera.sh
```

Atau edit manual:
```bash
nano config/config.yaml
```

Isi dengan:
```yaml
camera:
  ip: "10.26.27.196"
  port: 80
  username: "admin"
  password: "Kuncong0203"
  model: "v380"

detection:
  enabled: true
  person_detection_enabled: true
  face_recognition_enabled: true
  min_confidence: 0.5
  detection_interval: 1  # Detik

notification:
  alert_on_known: true
  alert_on_unknown: true

database:
  face_encoding_tolerance: 0.6
```

#### 4. Setup Telegram Bot
```bash
chmod +x scripts/setup_bot.sh
./scripts/setup_bot.sh
```

Atau edit manual:
```bash
nano config/telegram_config.json
```

Isi dengan:
```json
{
  "bot_token": "YOUR_BOT_TOKEN_FROM_BOTFATHER",
  "chat_id": "YOUR_CHAT_ID",
  "admin_id": "YOUR_TELEGRAM_USER_ID"
}
```

**Cara mendapatkan Bot Token:**
1. Chat dengan @BotFather di Telegram
2. Kirim `/newbot`
3. Ikuti instruksi untuk membuat bot
4. Copy token yang diberikan

**Cara mendapatkan Chat ID:**
1. Chat dengan @userinfobot di Telegram
2. Kirim pesan apapun
3. Copy Chat ID yang ditampilkan

#### 5. Jalankan sebagai Service
```bash
chmod +x scripts/setup_service.sh
sudo ./scripts/setup_service.sh
sudo systemctl start cctv-ai-bot
sudo systemctl enable cctv-ai-bot
```

#### 6. Cek Status
```bash
sudo systemctl status cctv-ai-bot
```

Lihat log:
```bash
tail -f logs/app.log
```

---

## 📱 Perintah Telegram Bot

### Perintah Dasar

| Perintah | Deskripsi | Contoh |
|----------|-----------|---------|
| `/start` | Memulai bot, pesan selamat datang lengkap | `/start` |
| `/help` | Panduan lengkap dengan FAQ | `/help` |
| `/status` | Cek status sistem (kamera, deteksi, wajah) | `/status` |
| `/stats` | Lihat statistik deteksi | `/stats` |

### Monitoring

| Perintah | Deskripsi | Contoh |
|----------|-----------|---------|
| `/screenshot` | Ambil foto kamera saat ini | `/screenshot` |

### Manajemen Wajah

| Perintah | Deskripsi | Contoh |
|----------|-----------|---------|
| `/addface [nama]` | Tambah wajah baru dengan upload foto | `/addface Budi` |
| `/listfaces` | Lihat daftar semua wajah terdaftar | `/listfaces` |
| `/delface [nama]` | Hapus wajah dari database | `/delface Budi` |
| `/reply_name [nama]` | Tambah nama dari foto reply | `/reply_name Ahmad` |

### Enhancement

| Perintah | Deskripsi | Contoh |
|----------|-----------|---------|
| `/enhance` | Perjelas kualitas foto reply | `/enhance` |

### Pengaturan

| Perintah | Deskripsi | Contoh |
|----------|-----------|---------|
| `/settings` | Buka menu pengaturan lengkap | `/settings` |
| `/toggle_detection` | Aktifkan/nonaktifkan deteksi | `/toggle_detection` |

### Command Tambahan

| Perintah | Deskripsi | Contoh |
|----------|-----------|---------|
| `/cancel` | Batalkan proses tambah wajah | `/cancel` |

---

## 💡 Cara Penggunaan Fitur Baru

### 1. Tambah Wajah dengan Upload Foto (Cara Lama)

```bash
# Di Telegram:
1. Kirim: /addface Budi
2. Upload foto wajah Budi
3. Selesai! Bot akan menyimpan wajah
```

### 2. Tambah Wajah dari Foto Notifikasi (Cara Baru - REKOMENDASI)

```bash
# Saat bot mengirim notifikasi deteksi:
1. Bot mengirim 2 foto:
   - Foto 1/2: Full frame
   - Foto 2/2: Zoom wajah

2. Reply salah satu foto + ketik: /reply_name Budi

3. Bot akan:
   - Deteksi wajah dari foto reply
   - Tambah "Budi" ke database
   - Kirim konfirmasi sukses

4. Selesai! Sekarang Budi akan dikenali otomatis
```

### 3. Perjelas Kualitas Foto (Enhancement)

```bash
# Saat bot mengirim notifikasi deteksi:
1. Bot mengirim 2 foto (full + zoom)

2. Jika foto terlalu gelap/buram:
   - Reply salah satu foto + ketik: /enhance

3. Bot akan:
   - Enhance kualitas foto:
     * Brightness +20%
     * Sharpening +30%
     * Contrast +15%
   - Kirim foto yang sudah diperjelas

4. Sekarang lebih mudah dikenali!
```

### 4. Alur Lengkap Penggunaan

```
Deteksi Orang
    ↓
Bot Kirim 2 Foto:
  - Foto 1/2: Full Frame
  - Foto 2/2: Zoom Wajah
    ↓
User Reply Foto:
  - /enhance → Perjelas dulu
  - /reply_name Nama → Tambah nama
    ↓
Bot:
  - Enhance (jika diminta)
  - Tambah nama ke database
  - Kirim konfirmasi
    ↓
Selesai!
```

---

## 🔧 Konfigurasi Melalui Telegram

### Semua Pengaturan Bisa Dilakukan via Chat

**Manajemen Wajah:**
- ✅ Tambah wajah baru
- ✅ Lihat semua wajah terdaftar
- ✅ Hapus wajah
- ✅ Reply foto notifikasi untuk tambah wajah

**Pengaturan Deteksi:**
- ✅ Aktifkan/nonaktifkan deteksi
- ✅ Aktifkan/nonaktifkan pengenalan wajah
- ✅ Ubah confidence threshold
- ✅ Ubah tolerance pengenalan

**Pengaturan Notifikasi:**
- ✅ Notifikasi orang dikenali
- ✅ Notifikasi orang tidak dikenali
- ✅ Ubah interval deteksi

**Monitoring:**
- ✅ Ambil screenshot kamera
- ✅ Cek status sistem
- ✅ Lihat statistik deteksi

---

## 📊 Fitur Deteksi

### Deteksi Orang
- **Model**: YOLOv8n (ultralytics/yolov8)
- **Akurasi**: Tinggi untuk deteksi manusia
- **Speed**: Cepat (~20-30 FPS di CPU)
- **Confidence**: Dapat diatur (default: 0.5)

### Pengenalan Wajah
- **Library**: face_recognition (dlib)
- **Metode**: 128-dimensional face encoding
- **Matching**: Cosine similarity
- **Tolerance**: Dapat diatur (default: 0.6)

### Enhancement Gambar
- **Brightness**: Histogram adjustment (+20%)
- **Sharpening**: Kernel-based sharpening (+30%)
- **Contrast**: CLAHE - Contrast Limited Adaptive Histogram Equalization (+15%)
- **Speed**: Cepat (<1 detik)

---

## 🛠️ Troubleshooting

### Kamera Tidak Terhubung

**Masalah:** Kamera tidak dapat terkoneksi

**Solusi:**
```bash
# 1. Cek koneksi jaringan
ping 10.26.27.196

# 2. Cek konfigurasi kamera
nano config/config.yaml
# Pastikan IP, username, password benar

# 3. Cek status kamera via browser
# Buka: http://10.26.27.196
# Login dengan: admin / Kuncong0203

# 4. Cek log
tail -f logs/app.log

# 5. Restart service
sudo systemctl restart cctv-ai-bot
```

### Bot Tidak Merespon

**Masalah:** Bot tidak membalas command

**Solusi:**
```bash
# 1. Cek bot token
nano config/telegram_config.json
# Pastikan token benar dari @BotFather

# 2. Cek chat_id
# Chat dengan @userinfobot untuk verifikasi

# 3. Cek service status
sudo systemctl status cctv-ai-bot

# 4. Lihat log
tail -f logs/telegram.log

# 5. Cek internet
ping api.telegram.org
```

### Deteksi Tidak Bekerja

**Masalah:** Tidak ada notifikasi meskipun ada orang

**Solusi:**
```bash
# 1. Cek apakah deteksi aktif
# Kirim: /status

# 2. Cek confidence threshold
# Jika terlalu tinggi, mungkin orang tidak terdeteksi
# Edit config/detection/min_confidence

# 3. Cek interval deteksi
# Jika terlalu lama, mungkin miss
# Edit config/detection/detection_interval

# 4. Cek log deteksi
tail -f logs/detection.log
```

### Wajah Tidak Dikenali

**Masalah:** Orang yang sudah ditambah tidak dikenali

**Solusi:**
```bash
# 1. Cek daftar wajah
# Kirim: /listfaces

# 2. Tambah wajah dengan foto yang lebih baik
# Gunakan foto jelas, terang, wajah menghadap kamera

# 3. Turunkan tolerance
# Edit config/database/face_encoding_tolerance
# Nilai lebih tinggi = lebih mudah match
# Nilai lebih rendah = lebih ketat

# 4. Coba fitur enhance
# Reply foto + /enhance
# Kemudian tambah wajah dari foto enhanced
```

### Service Tidak Start

**Masalah:** Systemd service gagal start

**Solusi:**
```bash
# 1. Cek error status
sudo systemctl status cctv-ai-bot

# 2. Cek log sistem
sudo journalctl -u cctv-ai-bot -n 50

# 3. Cek permission
ls -la scripts/
# Pastikan scripts executable: chmod +x scripts/*.sh

# 4. Run manual untuk debug
source venv/bin/activate
python3 src/main.py
```

---

## 📝 Log

Log tersimpan di `logs/` dengan format:

- **app.log** - Log aplikasi utama
  - Informasi startup
  - Error dan warning
  - Status koneksi

- **detection.log** - Log deteksi
  - Setiap kali orang terdeteksi
  - Informasi pengenalan wajah
  - Statistik deteksi

- **telegram.log** - Log aktivitas Telegram
  - Command yang diterima
  - Pesan yang dikirim
  - Error handler

### View Log Real-time
```bash
# Semua log
tail -f logs/app.log

# Deteksi log
tail -f logs/detection.log

# Telegram log
tail -f logs/telegram.log

# Semua log sekaligus
tail -f logs/*.log
```

---

## 🔐 Keamanan

- **Password kamera** disimpan aman di config
- **Bot hanya merespon admin** yang terdaftar
- **Enkripsi untuk komunikasi** Telegram (HTTPS)
- **Limit access** - hanya chat_id yang terdaftar
- **No hardcoded credentials** di source code

---

## 🚀 Performa dan Resource

### Resource Usage (Estimasi)
- **CPU**: 10-20% (Intel i5 atau sejenis)
- **RAM**: 500-800 MB
- **Disk**: 2-3 GB (termasuk model dan logs)
- **Network**: 100-200 MB/hour untuk notifikasi

### Optimalisasi
- YOLOv8n (nano model) untuk speed
- Face recognition hanya jika ada orang
- Interval deteksi yang dapat diatur
- Log rotation untuk menghemat disk

---

## 📄 Lisensi

MIT License - Bebas digunakan dan dimodifikasi

---

## 👨‍💻 Pengembang

Sistem ini dikembangkan untuk kebutuhan CCTV AI dengan integrasi Telegram.

**Dikembangkan oleh Riftech © 2026**

**Contact:**
- Email: info@riftech.com
- Website: www.riftech.com

---

## 🤝 Kontribusi

Kontribusi sangat diterima! Silakan buat pull request.

---

## 📖 Changelog

### Version 1.0 (2026-01-14)
- ✅ Deteksi orang real-time dengan YOLOv8n
- ✅ Pengenalan wajah otomatis
- ✅ Notifikasi Telegram lengkap
- ✅ Kirim 2 foto (full + zoom wajah)
- ✅ Reply untuk tambah nama wajah
- ✅ Enhancement kualitas foto (OpenCV-based)
- ✅ Kontrol penuh via Telegram
- ✅ Logging dan statistik
- ✅ Auto-reconnect kamera
- ✅ Systemd service untuk autostart

### Planned Features (Future)
- [ ] AI face enhancement (GFPGAN/CodeFormer)
- [ ] Video recording
- [ ] Multi-camera support
- [ ] Face tracking
- [ ] Export/import database
- [ ] Web dashboard

---

## 📞 Support

**Butuh bantuan?**

1. **Dokumentasi**: Baca file modul di `src/` untuk detail lebih
2. **Log**: Cek `logs/` untuk error dan warning
3. **Troubleshooting**: Lihat section troubleshooting di atas
4. **Contact**: Email info@riftech.com untuk support

---

## 🎓 Tips dan Best Practices

### Menambah Wajah
- Gunakan foto jelas dan terang
- Wajah harus menghadap kamera
- Pastikan pencahayaan cukup
- Gunakan fitur enhance untuk perbaiki foto
- Tambah beberapa foto untuk orang yang sama

### Konfigurasi
- Confidence threshold 0.5-0.7 untuk balance
- Detection interval 1-2 detik untuk real-time
- Tolerance 0.5-0.7 untuk pengenalan

### Monitoring
- Cek log secara berkala
- Monitor resource usage
- Backup database wajah
- Test command secara berkala

---

**Catatan**: Pastikan semua dependensi terinstal sebelum menjalankan sistem. Baca dokumentasi lengkap di setiap modul untuk informasi lebih detail.

**Selamat menggunakan CCTV AI Telegram Bot!** 🎉
