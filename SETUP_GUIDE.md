# 🚀 Panduan Setup Lengkap - CCTV AI Telegram Bot

Panduan lengkap untuk menginstal dan mengkonfigurasi sistem CCTV AI dengan deteksi orang dan pengenalan wajah untuk kamera V380 IP Anda.

---

## 📋 Prasyarat Sistem

- **OS**: Ubuntu 22.04 LTS
- **Python**: 3.10 atau lebih tinggi
- **RAM**: Minimal 4GB (disarankan 8GB untuk performa lebih baik)
- **Storage**: Minimal 10GB ruang kosong
- **Network**: Koneksi internet untuk download dan akses kamera IP
- **Kamera**: V380 IP Camera dengan RTSP support

---

## 🎯 Konfigurasi Kamera Default

- **IP Address**: 10.26.27.196
- **Username**: admin
- **Password**: Kuncong0203
- **Port RTSP**: 554

---

## 📝 Langkah-langkah Instalasi

### 1️⃣ Clone atau Download Project

```bash
cd /home/riftech/projeck/
# Jika menggunakan git
git clone https://github.com/username/cam_ai_telebot.git
cd cam_ai_telebot

# Atau jika sudah ada
cd cam_ai_telebot
```

### 2️⃣ Jalankan Script Instalasi

```bash
chmod +x scripts/*.sh
sudo ./scripts/install.sh
```

Script ini akan:
- ✅ Update sistem Ubuntu
- ✅ Install semua dependensi (OpenCV, dlib, dll)
- ✅ Setup virtual environment Python
- ✅ Install Python packages
- ✅ Buat file konfigurasi dari template

**Proses ini mungkin memakan waktu 30-60 menit tergantung kecepatan internet dan spesifikasi server.**

### 3️⃣ Konfigurasi Kamera

Edit file konfigurasi kamera:

```bash
nano config/config.yaml
```

Pastikan konfigurasi kamera sudah benar:
```yaml
camera:
  ip: "10.26.27.196"        # IP kamera V380
  port: 80                    # Port HTTP
  username: "admin"            # Username
  password: "Kuncong0203"       # Password
  model: "v380"                # Model kamera
  rtsp_port: 554               # Port RTSP
  stream_url: "/1"              # URL stream
```

### 4️⃣ Setup Telegram Bot

```bash
chmod +x scripts/setup_bot.sh
./scripts/setup_bot.sh
```

Ikuti panduan di script untuk:
1. Mendapatkan bot token dari @BotFather
2. Mendapatkan Chat ID dari @userinfobot
3. Mengedit file `config/telegram_config.json`

**Contoh konfigurasi Telegram:**
```json
{
  "bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
  "chat_id": "123456789",
  "admin_id": "123456789",
  "notification_settings": {
    "enable_sound": true,
    "enable_preview": true,
    "notification_interval": 60
  }
}
```

### 5️⃣ Test Koneksi Kamera

```bash
chmod +x scripts/setup_camera.sh
./scripts/setup_camera.sh
```

Script ini akan:
- ✅ Test koneksi ke kamera V380
- ✅ Ambil satu test frame
- ✅ Simpan test image ke `/tmp/camera_test.jpg`
- ✅ Tampilkan informasi resolusi dan FPS

Jika test gagal:
- Cek IP kamera
- Pastikan kamera dalam jaringan yang sama
- Verifikasi username dan password
- Cek apakah kamera mendukung RTSP

### 6️⃣ Test Aplikasi (Manual)

```bash
# Activate virtual environment
source venv/bin/activate

# Jalankan aplikasi
python3 src/main.py
```

Aplikasi akan:
- ✅ Connect ke kamera
- ✅ Load model YOLOv8n
- ✅ Start Telegram bot
- ✅ Mulai loop deteksi

**Test dengan Telegram:**
1. Buka Telegram
2. Cari bot Anda
3. Kirim `/start`
4. Kirim `/status` untuk cek status
5. Kirim `/screenshot` untuk test kamera

### 7️⃣ Install sebagai Systemd Service

Setelah aplikasi berjalan dengan baik, install sebagai service agar otomatis start pada boot:

```bash
chmod +x scripts/setup_service.sh
sudo ./scripts/setup_service.sh
```

Script ini akan:
- ✅ Create user `cctvbot` untuk security
- ✅ Setup systemd service
- ✅ Enable autostart on boot
- ✅ Auto-restart jika crash

**Manage Service:**

```bash
# Start service
sudo systemctl start cctv-ai-bot

# Stop service
sudo systemctl stop cctv-ai-bot

# Restart service
sudo systemctl restart cctv-ai-bot

# Enable autostart on boot
sudo systemctl enable cctv-ai-bot

# Check status
sudo systemctl status cctv-ai-bot

# View logs
sudo journalctl -u cctv-ai-bot -f
```

---

## 📱 Menggunakan Telegram Bot

### Perintah Dasar

| Perintah | Deskripsi |
|----------|-----------|
| `/start` | Memulai bot dan menampilkan menu utama |
| `/help` | Menampilkan bantuan lengkap |
| `/status` | Cek status sistem (kamera, deteksi, database) |
| `/screenshot` | Ambil foto dari kamera saat ini |
| `/stats` | Lihat statistik deteksi |

### Manajemen Wajah

**Tambah Wajah Baru:**
```bash
/addface NamaOrang
```
Kemudian kirim foto wajah orang tersebut.

**Lihat Daftar Wajah:**
```bash
/listfaces
```

**Hapus Wajah:**
```bash
/delface NamaOrang
```

### Pengaturan

| Perintah | Deskripsi |
|----------|-----------|
| `/settings` | Menu pengaturan lengkap |
| `/toggle_detection` | Aktifkan/nonaktifkan deteksi |
| `/stats` | Statistik deteksi |

---

## 🔧 Troubleshooting

### Kamera Tidak Terhubung

**Masalah**: Gagal connect ke kamera

**Solusi**:
```bash
# Test koneksi network
ping 10.26.27.196

# Cek apakah port RTSP terbuka
telnet 10.26.27.196 554

# Test RTSP stream secara manual
ffplay rtsp://admin:Kuncong0203@10.26.27.196:554/1
```

### Bot Tidak Merespon

**Masalah**: Bot tidak merespon perintah

**Solusi**:
```bash
# Check service status
sudo systemctl status cctv-ai-bot

# View logs
sudo journalctl -u cctv-ai-bot -n 50

# Restart service
sudo systemctl restart cctv-ai-bot
```

### Wajah Tidak Terdeteksi

**Masalah**: Sistem tidak mengenali wajah

**Solusi**:
- Pastikan foto wajah jelas dan terang
- Wajah harus menghadap kamera
- Tidak ada shadow pada wajah
- Tambahkan multiple foto untuk orang yang sama
- Sesuaikan `face_encoding_tolerance` di config

### Deteksi Tidak Akurat

**Masalah**: YOLOv8n tidak mendeteksi orang dengan baik

**Solusi**:
- Adjust `min_confidence` di config (coba 0.4-0.6)
- Pastikan pencahayaan kamera cukup
- Check resolusi kamera (minimal 640x480)

---

## 📊 Monitoring dan Maintenance

### View Logs

```bash
# Real-time logs dari systemd
sudo journalctl -u cctv-ai-bot -f

# Application logs
tail -f logs/app.log

# Detection logs
tail -f logs/detection.log

# Telegram logs
tail -f logs/telegram.log
```

### Backup Database

```bash
# Backup face encodings
cp data/faces/face_encodings.pkl backup/

# Backup semua data wajah
tar -czf faces_backup_$(date +%Y%m%d).tar.gz data/faces/
```

### Update System

```bash
# Stop service
sudo systemctl stop cctv-ai-bot

# Update code
git pull

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Start service
sudo systemctl start cctv-ai-bot
```

---

## 🔒 Security Best Practices

1. **Change Default Passwords**: Ubah password default kamera
2. **Network Segmentation**: Pisahkan kamera CCTV dari network lain
3. **Firewall**: Batasi akses port RTSP (554) hanya dari server
4. **Regular Updates**: Update sistem dan dependencies secara teratur
5. **Monitor Logs**: Pantau logs untuk aktivitas mencurigakan

---

## 📞 Support

Jika mengalami masalah:

1. Cek logs: `sudo journalctl -u cctv-ai-bot -n 100`
2. Baca documentation di `README.md`
3. Cek troubleshooting section di atas

---

## 🎉 Selesai!

Sistem CCTV AI Telegram Bot Anda sekarang siap digunakan!

**Fitur yang aktif:**
- ✅ Deteksi orang real-time dengan YOLOv8n
- ✅ Pengenalan wajah otomatis
- ✅ Notifikasi instan ke Telegram
- ✅ Konfigurasi penuh via Telegram
- ✅ Monitoring 24/7 sebagai systemd service

**Selamat menggunakan sistem CCTV AI Anda! 🎥🔍**
