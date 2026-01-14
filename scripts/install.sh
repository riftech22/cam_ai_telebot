#!/bin/bash
#
# Script instalasi CCTV AI Telegram Bot untuk Ubuntu 22.04
# Dijalankan sebagai root atau dengan sudo
#

set -e

echo "========================================"
echo "CCTV AI Telegram Bot - Instalasi"
echo "========================================"
echo ""

# Cek apakah dijalankan sebagai root
if [ "$EUID" -ne 0 ]; then 
    echo "Harap jalankan script ini dengan sudo atau sebagai root"
    exit 1
fi

# Update sistem
echo "[1/8] Mengupdate sistem..."
apt update && apt upgrade -y

# Install dependensi sistem
echo "[2/8] Menginstall dependensi sistem..."
apt install -y \
    python3.10 \
    python3-pip \
    python3-venv \
    build-essential \
    cmake \
    pkg-config \
    libx11-dev \
    libgtk-3-dev \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    libtbb2 \
    libtbb-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libv4l-dev \
    v4l-utils \
    libxvidcore-dev \
    libx264-dev \
    libx264-163 \
    yasm \
    libopenexr-dev \
    libatlas-base-dev \
    wget \
    curl \
    git \
    unzip

# Install boost python (needed for dlib)
echo "[3/8] Menginstall boost-python..."
apt install -y libboost-python-dev

# Buat virtual environment
echo "[4/8] Membuat virtual environment..."
cd /home/riftech/projeck/cam_ai_telebot
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "[5/8] Mengupgrade pip..."
pip install --upgrade pip

# Install Python packages (dlib included)
echo "[6/8] Menginstall Python packages..."
pip install -r requirements.txt

# Download YOLOv8n model (akan otomatis dilakukan saat pertama kali dijalankan)
echo "[7/7] Model YOLOv8n akan didownload otomatis saat aplikasi dijalankan pertama kali"

# Setup konfigurasi
echo ""
echo "========================================"
echo "Setup Konfigurasi"
echo "========================================"

# Copy template config jika belum ada
if [ ! -f config/config.yaml ]; then
    cp config/config.yaml.template config/config.yaml
    echo "✓ config.yaml dibuat dari template"
    echo "  Silakan edit config/config.yaml untuk mengubah konfigurasi kamera"
fi

if [ ! -f config/telegram_config.json ]; then
    cp config/telegram_config.json.template config/telegram_config.json
    echo "✓ telegram_config.json dibuat dari template"
    echo "  Silakan edit config/telegram_config.json untuk mengisi bot token dan chat ID"
fi

# Buat direktori data
mkdir -p data/faces
mkdir -p data/detections
mkdir -p data/recordings
mkdir -p logs

echo "✓ Direktori data dibuat"

# Set permissions
chmod -R 755 data
chmod -R 755 logs
chmod +x scripts/*.sh

echo ""
echo "========================================"
echo "Instalasi Selesai!"
echo "========================================"
echo ""
echo "Langkah selanjutnya:"
echo ""
echo "1. Edit konfigurasi kamera:"
echo "   nano config/config.yaml"
echo ""
echo "2. Edit konfigurasi Telegram:"
echo "   nano config/telegram_config.json"
echo ""
echo "   Untuk mendapatkan bot token:"
echo "   - Chat dengan @BotFather di Telegram"
echo "   - Buat bot baru dan dapatkan token"
echo ""
echo "   Untuk mendapatkan chat ID:"
echo "   - Chat dengan @userinfobot di Telegram"
echo "   - Kirim pesan untuk mendapatkan chat ID"
echo ""
echo "3. Jalankan script setup kamera:"
echo "   ./scripts/setup_camera.sh"
echo ""
echo "4. Jalankan aplikasi untuk test:"
echo "   source venv/bin/activate"
echo "   python3 src/main.py"
echo ""
echo "5. Setelah berhasil, install sebagai service:"
echo "   sudo ./scripts/setup_service.sh"
echo ""
echo "========================================"
