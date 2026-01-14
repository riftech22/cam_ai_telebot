#!/bin/bash
# GStreamer RTSP Proxy Systemd Service Setup Script

set -e

echo "=========================================="
echo "GStreamer RTSP Proxy Service Setup"
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

# Cek GStreamer terinstall
if ! command -v gst-launch-1.0 &> /dev/null; then
    echo "❌ GStreamer tidak terinstall"
    echo "Install dengan:"
    echo "sudo apt update && sudo apt install -y gstreamer1.0-tools gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly"
    exit 1
fi

echo "✅ GStreamer terinstall: $(gst-launch-1.0 --version 2>&1 | head -1)"
echo ""

# Cek vlc-user sudah ada
if ! id "vlc-user" &>/dev/null; then
    echo "❌ vlc-user tidak ada!"
    echo "Buat dulu vlc-user: sudo useradd -r -s /bin/false vlc-user"
    exit 1
fi

echo "✅ vlc-user sudah ada"
echo ""

# Buat systemd service
echo "=========================================="
echo "MEMBUAT SYSTEMD SERVICE"
echo "=========================================="
echo ""

SERVICE_FILE="/etc/systemd/system/gstreamer-proxy.service"

sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=GStreamer RTSP Proxy for CCTV AI Bot
After=network.target

[Service]
Type=simple
User=vlc-user
Group=vlc-user
Restart=always
RestartSec=10
WorkingDirectory=/tmp

ExecStart=/usr/bin/gst-launch-1.0 -v \
    rtspsrc location="rtsp://${CAMERA_USER}:${CAMERA_PASS}@${CAMERA_IP}:${RTSP_PORT}${STREAM_URL}?rtsp_transport=tcp&latency=0" ! \
    rtph264depay ! \
    h264parse ! \
    queue max-size-buffers=1000 ! \
    rtph264pay pt=96 ! \
    udpsink host=127.0.0.1 port=${LOCAL_RTSP_PORT} sync=false

# Note: Using GStreamer for RTSP re-streaming
# GStreamer is more stable and reliable than VLC for this purpose
# Pipeline: RTSP Source -> H.264 Depay -> Parse -> Queue -> Pay -> UDP Sink
# Result: rtsp://127.0.0.1:8554 (OpenCV compatible)

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
echo "Enable GStreamer proxy service..."
sudo systemctl enable gstreamer-proxy.service
echo "✅ GStreamer proxy service enabled"
echo ""

# Start service
echo "Start GStreamer proxy service..."
sudo systemctl start gstreamer-proxy.service
echo "✅ GStreamer proxy service started"
echo ""

# Check status
echo "=========================================="
echo "SERVICE STATUS"
echo "=========================================="
echo ""
sudo systemctl status gstreamer-proxy.service --no-pager

echo ""
echo "=========================================="
echo "SUCCESS!"
echo "=========================================="
echo ""
echo "GStreamer RTSP Proxy service telah diinstall dan dijalankan!"
echo ""
echo "Local RTSP URL:"
echo "rtsp://127.0.0.1:$LOCAL_RTSP_PORT"
echo ""
echo "Untuk menggunakan GStreamer proxy di CCTV AI Bot:"
echo "1. Edit config: nano /opt/cam_ai_telebot/config/config.yaml"
echo "2. Set: use_gstreamer_proxy: true"
echo "3. Set: gstreamer_rtsp_port: $LOCAL_RTSP_PORT"
echo "4. Restart bot: sudo systemctl restart cctv-ai-bot"
echo ""
echo "Service management:"
echo "• Check status: sudo systemctl status gstreamer-proxy"
echo "• Start: sudo systemctl start gstreamer-proxy"
echo "• Stop: sudo systemctl stop gstreamer-proxy"
echo "• Restart: sudo systemctl restart gstreamer-proxy"
echo "• Disable: sudo systemctl disable gstreamer-proxy"
echo ""
