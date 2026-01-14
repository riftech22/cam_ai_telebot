#!/bin/bash
# VLC RTSP Proxy Setup Script
# Menggunakan VLC sebagai RTSP proxy untuk koneksi kamera yang lebih stabil

set -e

echo "=========================================="
echo "VLC RTSP Proxy Setup"
echo "=========================================="
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

# RTSP URL asli
RTSP_URL="rtsp://${CAMERA_USER}:${CAMERA_PASS}@${CAMERA_IP}:${RTSP_PORT}${STREAM_URL}"

echo "=========================================="
echo "MULAI VLC RTSP PROXY"
echo "=========================================="
echo ""
echo "RTSP Asli: rtsp://${CAMERA_USER}:****@${CAMERA_IP}:${RTSP_PORT}${STREAM_URL}"
echo "Local RTSP: rtsp://127.0.0.1:${LOCAL_RTSP_PORT}/camera"
echo ""
echo "VLC akan:"
echo "1. Connect ke kamera (lebih stabil)"
echo "2. Re-stream ke local RTSP port $LOCAL_RTSP_PORT"
echo "3. OpenCV connect ke local RTSP (stabil)"
echo ""
echo "=========================================="
echo ""

# Jalankan VLC sebagai RTSP proxy
# Menggunakan VLC untuk stream dan re-stream ke local RTSP
vlc -I dummy \
    --rtsp-tcp \
    --rtsp-frame-buffer-size=100000 \
    --no-sout-rtp-sap \
    --no-sout-standard-sap \
    --ttl=1 \
    --sout="#transcode{vcodec=h264,acodec=none}:rtp{sdp=rtsp://127.0.0.1:${LOCAL_RTSP_PORT}/camera}" \
    "$RTSP_URL" \
    vlc://quit

echo ""
echo "=========================================="
echo "VLC RTSP Proxy berjalan!"
echo "=========================================="
echo ""
echo "Untuk stop VLC proxy, tekan Ctrl+C"
echo ""
echo "Gunakan local RTSP di config:"
echo "rtsp://127.0.0.1:${LOCAL_RTSP_PORT}/camera"
echo ""
