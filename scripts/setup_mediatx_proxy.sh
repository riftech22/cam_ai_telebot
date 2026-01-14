#!/bin/bash
# MediaTX (rtsp-simple-server) + FFmpeg RTSP Proxy Setup Script
# MediaTX = Simple and Reliable RTSP Server
# FFmpeg = Powerful Transcoding (H.265 to H.264)

set -e

echo "=========================================="
echo "MediaTX + FFmpeg RTSP Proxy Setup"
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

# Cek vlc-user sudah ada
if ! id "vlc-user" &>/dev/null; then
    echo "❌ vlc-user tidak ada!"
    echo "Buat dulu vlc-user: sudo useradd -r -s /bin/false vlc-user"
    exit 1
fi

echo "✅ vlc-user sudah ada"
echo ""

# Install mediamtx jika belum ada
if ! command -v mediamtx &> /dev/null; then
    echo "MediaTX tidak terinstall. Installing..."
    
    # Download mediamtx
    cd /tmp
    wget -q https://github.com/bluenviron/mediamtx/releases/download/v1.8.0/mediamtx_v1.8.0_linux_amd64.tar.gz
    
    # Extract dan install
    tar xzf mediamtx_v1.8.0_linux_amd64.tar.gz
    sudo mv mediamtx /usr/local/bin/
    sudo chmod +x /usr/local/bin/mediamtx
    
    # Cleanup
    rm -rf mediamtx_v1.8.0_linux_amd64.tar.gz README.md LICENSE mediamtx.yml
    
    echo "✅ MediaTX installed: $(mediamtx --version 2>&1 | head -1)"
else
    echo "✅ MediaTX terinstalled: $(mediamtx --version 2>&1 | head -1)"
fi

# Cek ffmpeg terinstall
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg tidak terinstall"
    echo "Install dengan:"
    echo "sudo apt update && sudo apt install -y ffmpeg"
    exit 1
fi

echo "✅ FFmpeg terinstalled: $(ffmpeg -version 2>&1 | head -1)"
echo ""

# Buat mediamtx config
echo "=========================================="
echo "MEMBUKAM MEDIAMTX CONFIG"
echo "=========================================="
echo ""

CONFIG_DIR="/etc/mediamtx"
sudo mkdir -p $CONFIG_DIR

sudo tee $CONFIG_DIR/mediamtx.yml > /dev/null <<EOF
# MediaTX Configuration for CCTV AI Bot
# Simple and Reliable RTSP Server

logLevel: info

# RTSP Server
rtsp:
  address: 127.0.0.1
  port: $LOCAL_RTSP_PORT

# Read from TCP (receive from FFmpeg)
paths:
  camera:
    source: tcp://127.0.0.1:1554
EOF

echo "✅ MediaTX config created: $CONFIG_DIR/mediamtx.yml"
echo ""

# Buat systemd service untuk MediaTX
echo "=========================================="
echo "MEMBUKAM SYSTEMD SERVICE - MEDIATX"
echo "=========================================="
echo ""

MEDIA_TX_SERVICE="/etc/systemd/system/mediatx-proxy.service"

sudo tee $MEDIA_TX_SERVICE > /dev/null <<EOF
[Unit]
Description=MediaTX RTSP Proxy for CCTV AI Bot
After=network.target

[Service]
Type=simple
User=vlc-user
Group=vlc-user
Restart=always
RestartSec=10
WorkingDirectory=/tmp

ExecStart=/usr/local/bin/mediamtx $CONFIG_DIR/mediamtx.yml

[Install]
WantedBy=multi-user.target
EOF

echo "✅ MediaTX service file created: $MEDIA_TX_SERVICE"
echo ""

# Buat systemd service untuk FFmpeg
echo "=========================================="
echo "MEMBUKAM SYSTEMD SERVICE - FFMPEG"
echo "=========================================="
echo ""

FFMPEG_SERVICE="/etc/systemd/system/ffmpeg-proxy.service"

sudo tee $FFMPEG_SERVICE > /dev/null <<EOF
[Unit]
Description=FFmpeg Transcoder for CCTV AI Bot (H.265 to H.264)
After=network.target
Before=mediatx-proxy.service

[Service]
Type=simple
User=vlc-user
Group=vlc-user
Restart=always
RestartSec=10
WorkingDirectory=/tmp

ExecStart=/usr/bin/ffmpeg -y \
  -rtsp_transport tcp \
  -stimeout 5000000 \
  -i rtsp://${CAMERA_USER}:${CAMERA_PASS}@${CAMERA_IP}:${RTSP_PORT}${STREAM_URL} \
  -c:v libx264 \
  -preset ultrafast \
  -tune zerolatency \
  -crf 23 \
  -pix_fmt yuv420p \
  -f mpegts \
  tcp://127.0.0.1:1554

# Note: FFmpeg Pipeline
# - Input: RTSP H.265 dari kamera
# - Output: MPEGTS ke TCP (127.0.0.1:1554)
# - MediaTX akan convert ke RTSP
# - H.265 -> H.264 transcoding dengan ultrafast preset
# - low latency untuk real-time detection

[Install]
WantedBy=multi-user.target
EOF

echo "✅ FFmpeg service file created: $FFMPEG_SERVICE"
echo ""

# Reload systemd
echo "Reload systemd daemon..."
sudo systemctl daemon-reload
echo "✅ Systemd daemon reloaded"
echo ""

# Enable dan start services
echo "=========================================="
echo "STARTING SERVICES"
echo "=========================================="
echo ""

echo "Start FFmpeg transcoder..."
sudo systemctl enable ffmpeg-proxy.service
sudo systemctl start ffmpeg-proxy.service
echo "✅ FFmpeg transcoder started"
echo ""

sleep 5

echo "Start MediaTX RTSP server..."
sudo systemctl enable mediatx-proxy.service
sudo systemctl start mediatx-proxy.service
echo "✅ MediaTX RTSP server started"
echo ""

# Check status
echo "=========================================="
echo "SERVICE STATUS"
echo "=========================================="
echo ""
echo "--- FFmpeg Service ---"
sudo systemctl status ffmpeg-proxy.service --no-pager
echo ""
echo "--- MediaTX Service ---"
sudo systemctl status mediatx-proxy.service --no-pager
echo ""

echo "=========================================="
echo "SUCCESS!"
echo "=========================================="
echo ""
echo "MediaTX + FFmpeg RTSP Proxy telah diinstall dan dijalankan!"
echo ""
echo "Architecture:"
echo "  1. FFmpeg: Ambil RTSP H.265 dari kamera"
echo "  2. FFmpeg: Transcode H.265 ke H.264 (ultrafast)"
echo "  3. FFmpeg: Stream via TCP (127.0.0.1:1554)"
echo "  4. MediaTX: Receive TCP stream"
echo "  5. MediaTX: Serve sebagai RTSP (127.0.0.1:$LOCAL_RTSP_PORT)"
echo ""
echo "Local RTSP URL:"
echo "rtsp://127.0.0.1:$LOCAL_RTSP_PORT"
echo ""
echo "Untuk menggunakan MediaTX proxy di CCTV AI Bot:"
echo "1. Edit config: nano /opt/cam_ai_telebot/config/config.yaml"
echo "2. Set: use_gstreamer_proxy: true"
echo "3. Set: gstreamer_rtsp_port: $LOCAL_RTSP_PORT"
echo "4. Restart bot: sudo systemctl restart cctv-ai-bot"
echo ""
echo "Service management:"
echo "• Check status: sudo systemctl status ffmpeg-proxy mediatx-proxy"
echo "• Start: sudo systemctl start ffmpeg-proxy mediatx-proxy"
echo "• Stop: sudo systemctl stop ffmpeg-proxy mediatx-proxy"
echo "• Restart: sudo systemctl restart ffmpeg-proxy mediatx-proxy"
echo "• Disable: sudo systemctl disable ffmpeg-proxy mediatx-proxy"
echo ""
