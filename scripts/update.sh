#!/bin/bash
# Script Update Otomatis CCTV AI Telegram Bot
# Gunakan script ini untuk update aplikasi ke versi terbaru

echo "=========================================="
echo "  CCTV AI Telegram Bot - Update Script"
echo "=========================================="
echo ""

# Warna untuk output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Cek apakah berjalan sebagai root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Error: Script ini harus dijalankan sebagai root${NC}"
    echo "Gunakan: sudo bash scripts/update.sh"
    exit 1
fi

# Direktori aplikasi
APP_DIR="/opt/cam_ai_telebot"
SERVICE_NAME="cctv-ai-bot"

# Step 1: Stop service
echo -e "${YELLOW}[1/7] Menghentikan service...${NC}"
systemctl stop $SERVICE_NAME
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Service berhasil dihentikan${NC}"
else
    echo -e "${RED}✗ Gagal menghentikan service${NC}"
fi
echo ""

# Step 2: Backup config lama
echo -e "${YELLOW}[2/7] Backup konfigurasi lama...${NC}"
if [ -f "$APP_DIR/config/config.yaml" ]; then
    cp $APP_DIR/config/config.yaml $APP_DIR/config/config.yaml.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✓ Config berhasil di-backup${NC}"
else
    echo -e "${YELLOW}⚠ Config tidak ditemukan, skip backup${NC}"
fi
echo ""

# Step 3: Pull update dari GitHub
echo -e "${YELLOW}[3/7] Pulling update dari GitHub...${NC}"
cd $APP_DIR
git fetch origin main
if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Gagal fetch dari GitHub${NC}"
    exit 1
fi

git pull origin main
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Update berhasil di-pull${NC}"
else
    echo -e "${RED}✗ Gagal pull update${NC}"
    exit 1
fi
echo ""

# Step 4: Copy config template baru (jika config tidak ada)
echo -e "${YELLOW}[4/7] Memeriksa konfigurasi...${NC}"
if [ ! -f "$APP_DIR/config/config.yaml" ]; then
    cp $APP_DIR/config/config.yaml.template $APP_DIR/config/config.yaml
    echo -e "${YELLOW}⚠ Config tidak ditemukan, menggunakan template${NC}"
    echo -e "${YELLOW}⚠ Silakan edit $APP_DIR/config/config.yaml sesuai kebutuhan${NC}"
else
    echo -e "${GREEN}✓ Config sudah ada, tidak diubah${NC}"
fi
echo ""

# Step 5: Update dependencies
echo -e "${YELLOW}[5/7] Memeriksa dependencies...${NC}"
if [ -d "$APP_DIR/venv" ]; then
    source $APP_DIR/venv/bin/activate
    pip install -q -r $APP_DIR/requirements.txt
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Dependencies berhasil di-update${NC}"
    else
        echo -e "${RED}✗ Gagal update dependencies${NC}"
    fi
    deactivate
else
    echo -e "${YELLOW}⚠ Virtual environment tidak ditemukan${NC}"
    echo -e "${YELLOW}⚠ Jalankan script instalasi terlebih dahulu${NC}"
fi
echo ""

# Step 6: Restart service
echo -e "${YELLOW}[6/7] Memulai service...${NC}"
systemctl start $SERVICE_NAME
sleep 2
echo ""

# Step 7: Cek status service
echo -e "${YELLOW}[7/7] Memeriksa status service...${NC}"
if systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${GREEN}✓ Service berjalan dengan baik${NC}"
    systemctl status $SERVICE_NAME --no-pager | head -n 5
else
    echo -e "${RED}✗ Service tidak berjalan${NC}"
    echo ""
    echo "Error log:"
    journalctl -u $SERVICE_NAME -n 20 --no-pager
    exit 1
fi
echo ""

# Tampilkan informasi
echo "=========================================="
echo -e "${GREEN}  UPDATE SELESAI!${NC}"
echo "=========================================="
echo ""
echo "Langkah selanjutnya:"
echo "1. Cek log aplikasi:"
echo "   tail -f $APP_DIR/logs/app.log"
echo ""
echo "2. Test motion detection:"
echo "   - Gerakkan tangan di depan kamera"
echo "   - Cek Telegram untuk notifikasi"
echo ""
echo "3. Test person detection:"
echo "   - Berdiri di depan kamera"
echo "   - Cek Telegram untuk foto + zoom wajah"
echo ""
echo "4. Test commands di Telegram:"
echo "   /status"
echo "   /stats"
echo "   /screenshot"
echo ""
echo "5. Jika ada error, cek log:"
echo "   sudo journalctl -u $SERVICE_NAME -n 50"
echo ""
