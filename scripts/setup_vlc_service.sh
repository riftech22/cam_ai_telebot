#!/bin/bash
# VLC RTSP Proxy Systemd Service Setup Script

set -e

echo "=========================================="
echo "VLC RTSP Proxy Service Setup"
echo "=========================================="
echo ""

# Konfigurasi
CAMERA_IP=${1:-"10.26.27.196"}
CAMERA_USER=${2:-"admin"}
CAMERA_PASS=${3:-"Kuncong0203"}
RTSP_PORT=${4:-554}
STREAM_URL=${5:-"/1"}
LOCAL_RTSP_PORT=${6:-8554}

echo "=========================================="
echo "KONFIGURASI"
echo "=========================================="
echo "Kamera IP: $CAMERA_IP"
echo "Kamera User: $CAMERA_USER"
echo "RTSP Port: $RTSP_PORT"
echo "Stream URL: $STREAM_URL"
echo "Local RTSP Port: $LOCAL_RTSP_PORT"
echo ""

# Cek VLC terinstall
if ! command -v vlc &> /dev/null; then
    echo "❌ VLC tidak terinstall"
    echo "Install dengan:"
    echo "sudo apt update && sudo apt install -y vlc"
    exit 1
fi

echo "✅ VLC terinstall: $(vlc --version | head -1)"
echo ""

# Buat VLC user untuk menjalankan service
echo "=========================================="
echo "MEMBUAT VLC USER"
echo "=========================================="
echo ""

if ! id "vlc-user" &>/dev/null; then
    sudo useradd -r -s /bin/false vlc-user
    echo "✅ VLC user created: vlc-user"
else
    echo "✅ VLC user already exists: vlc-user"
fi

echo ""

# Buat systemd service
echo "=========================================="
echo "MEMBUAT SYSTEMD SERVICE"
echo "=========================================="
echo ""

SERVICE_FILE="/etc/systemd/system/vlc-rtsp-proxy.service"

# Build RTSP URL dan VLC command untuk menghindari escaping issues
RTSP_SOURCE="rtsp://${CAMERA_USER}:${CAMERA_PASS}@${CAMERA_IP}:${RTSP_PORT}${STREAM_URL}?rtsp_transport=tcp&latency=0"
RTSP_DEST="rtsp://127.0.0.1:${LOCAL_RTSP_PORT}/camera"

sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=VLC RTSP Proxy for CCTV AI Bot
After=network.target

[Service]
Type=simple
User=vlc-user
Group=vlc-user
Restart=always
RestartSec=10
WorkingDirectory=/tmp

ExecStart=/usr/bin/vlc -I dummy \
    --no-sout-rtp-sap \
    --no-sout-standard-sap \
    --ttl=1 \
    --sout="#transcode{vcodec=h264,acodec=none}:rtp{sdp=${RTSP_DEST}}" \
    "${RTSP_SOURCE}"

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Service file created: $SERVICE_FILE"
echo ""

# Reload systemd
echo "Reload systemd daemon..."
sudo systemctl daemon-reload
echo "✅ Systemd daemon reloaded"
echo ""

# Enable service
echo "Enable VLC RTSP proxy service..."
sudo systemctl enable vlc-rtsp-proxy.service
echo "✅ VLC RTSP proxy service enabled"
echo ""

# Start service
echo "Start VLC RTSP proxy service..."
sudo systemctl start vlc-rtsp-proxy.service
echo "✅ VLC RTSP proxy service started"
echo ""

# Check status
echo "=========================================="
echo "SERVICE STATUS"
echo "=========================================="
echo ""
sudo systemctl status vlc-rtsp-proxy.service --no-pager

echo ""
echo "=========================================="
echo "SUCCESS!"
echo "=========================================="
echo ""
echo "VLC RTSP Proxy service telah diinstall dan dijalankan!"
echo ""
echo "Local RTSP URL:"
echo "rtsp://127.0.0.1:$LOCAL_RTSP_PORT/camera"
echo ""
echo "Untuk menggunakan VLC proxy di CCTV AI Bot:"
echo "1. Edit config: nano /opt/cam_ai_telebot/config/config.yaml"
echo "2. Set: use_vlc_proxy: true"
echo "3. Set: vlc_rtsp_port: $LOCAL_RTSP_PORT"
echo "4. Restart bot: sudo systemctl restart cctv-ai-bot"
echo ""
echo "Service management:"
echo "• Check status: sudo systemctl status vlc-rtsp-proxy"
echo "• Start: sudo systemctl start vlc-rtsp-proxy"
echo "• Stop: sudo systemctl stop vlc-rtsp-proxy"
echo "• Restart: sudo systemctl restart vlc-rtsp-proxy"
echo "• Disable: sudo systemctl disable vlc-rtsp-proxy"
echo ""
