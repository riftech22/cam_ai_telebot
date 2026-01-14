#!/bin/bash
#
# Script untuk menginstall CCTV AI Bot sebagai systemd service
#

set -e

echo "========================================"
echo "Setup Systemd Service"
echo "========================================"
echo ""

# Cek apakah dijalankan sebagai root
if [ "$EUID" -ne 0 ]; then 
    echo "Harap jalankan script ini dengan sudo atau sebagai root"
    exit 1
fi

# Path instalasi (dynamic path detection)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/.." && pwd )"
INSTALL_DIR="${SCRIPT_DIR}"
SERVICE_NAME="cctv-ai-bot"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# Cek apakah konfigurasi sudah ada
if [ ! -f "${INSTALL_DIR}/config/config.yaml" ]; then
    echo "Error: config/config.yaml tidak ditemukan!"
    echo "Jalankan setup konfigurasi terlebih dahulu"
    exit 1
fi

if [ ! -f "${INSTALL_DIR}/config/telegram_config.json" ]; then
    echo "Error: telegram_config.json tidak ditemukan!"
    echo "Jalankan setup konfigurasi terlebih dahulu"
    exit 1
fi

# Cek apakah virtual environment ada
if [ ! -d "${INSTALL_DIR}/venv" ]; then
    echo "Error: Virtual environment tidak ditemukan!"
    echo "Jalankan ./scripts/install.sh terlebih dahulu"
    exit 1
fi

# Buat user service jika belum ada
echo "[1/4] Setup user service..."
if ! id "cctvbot" &>/dev/null; then
    echo "Membuat user cctvbot..."
    useradd -r -s /bin/false cctvbot
    echo "✓ User cctvbot dibuat"
else
    echo "✓ User cctvbot sudah ada"
fi

# Set ownership direktori
echo "[2/4] Set permissions..."
chown -R cctvbot:cctvbot ${INSTALL_DIR}
echo "✓ Ownership direktori diubah ke cctvbot"

# Buat systemd service file
echo "[3/4] Membuat systemd service file..."
cat > ${SERVICE_FILE} << EOF
[Unit]
Description=CCTV AI Telegram Bot - Sistem deteksi orang dengan pengenalan wajah
After=network.target
Wants=network.target

[Service]
Type=simple
User=cctvbot
Group=cctvbot
WorkingDirectory=${INSTALL_DIR}
Environment="PATH=${INSTALL_DIR}/venv/bin"
ExecStart=${INSTALL_DIR}/venv/bin/python ${INSTALL_DIR}/src/main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=cctv-ai-bot

# Security
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Service file dibuat: ${SERVICE_FILE}"

# Reload systemd daemon
echo "[4/4] Reload systemd daemon..."
systemctl daemon-reload
echo "✓ Systemd daemon reloaded"

echo ""
echo "========================================"
echo "Service Setup Selesai!"
echo "========================================"
echo ""
echo "Service commands:"
echo ""
echo "Start service:"
echo "  sudo systemctl start ${SERVICE_NAME}"
echo ""
echo "Stop service:"
echo "  sudo systemctl stop ${SERVICE_NAME}"
echo ""
echo "Restart service:"
echo "  sudo systemctl restart ${SERVICE_NAME}"
echo ""
echo "Enable service (autostart on boot):"
echo "  sudo systemctl enable ${SERVICE_NAME}"
echo ""
echo "Disable service:"
echo "  sudo systemctl disable ${SERVICE_NAME}"
echo ""
echo "Check status:"
echo "  sudo systemctl status ${SERVICE_NAME}"
echo ""
echo "View logs:"
echo "  sudo journalctl -u ${SERVICE_NAME} -f"
echo ""
echo "View logs file:"
echo "  tail -f ${INSTALL_DIR}/logs/app.log"
echo ""
echo "========================================"
echo ""

# Tanya apakah ingin langsung start service
read -p "Apakah ingin langsung start service sekarang? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Starting service..."
    systemctl start ${SERVICE_NAME}
    systemctl status ${SERVICE_NAME}
    echo ""
    echo "Service started! Check logs untuk memantau aktivitas:"
    echo "  sudo journalctl -u ${SERVICE_NAME} -f"
else
    echo ""
    echo "Service tidak di-start. Anda bisa start manual nanti:"
    echo "  sudo systemctl start ${SERVICE_NAME}"
fi
