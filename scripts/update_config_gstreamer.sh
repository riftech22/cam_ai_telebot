#!/bin/bash
# Script untuk update config.yaml dengan GStreamer settings

set -e

CONFIG_FILE="/opt/cam_ai_telebot/config/config.yaml"

echo "=========================================="
echo "Update Config untuk GStreamer RTSP Proxy"
echo "=========================================="
echo ""

if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Config file tidak ditemukan: $CONFIG_FILE"
    exit 1
fi

echo "✅ Config file ditemukan: $CONFIG_FILE"
echo ""

# Backup config
BACKUP_FILE="${CONFIG_FILE}.backup.$(date +%Y%m%d_%H%M%S)"
cp "$CONFIG_FILE" "$BACKUP_FILE"
echo "✅ Backup dibuat: $BACKUP_FILE"
echo ""

# Update config dengan sed
echo "Updating config.yaml..."
sed -i 's/use_vlc_proxy: true/use_vlc_proxy: false/g' "$CONFIG_FILE"
sed -i 's/use_vlc_proxy: .*true$/use_vlc_proxy: false/' "$CONFIG_FILE"
sed -i 's/use_http_stream: true/use_http_stream: false/g' "$CONFIG_FILE"
sed -i 's/use_http_stream: .*true$/use_http_stream: false/' "$CONFIG_FILE"

# Tambah use_gstreamer_proxy jika belum ada
if ! grep -q "use_gstreamer_proxy:" "$CONFIG_FILE"; then
    echo "Menambahkan use_gstreamer_proxy: true"
    sed -i '/vlc_http_port:/a \  use_gstreamer_proxy: true' "$CONFIG_FILE"
    sed -i '/use_gstreamer_proxy:/a \  gstreamer_rtsp_port: 8554' "$CONFIG_FILE"
else
    # Update jika sudah ada
    sed -i 's/use_gstreamer_proxy: .*false$/use_gstreamer_proxy: true/' "$CONFIG_FILE"
    sed -i 's/use_gstreamer_proxy: .*$/use_gstreamer_proxy: true/' "$CONFIG_FILE"
fi

echo "✅ Config berhasil diupdate!"
echo ""

# Tampilkan config yang relevan
echo "=========================================="
echo "CONFIG YANG DIUPDATE:"
echo "=========================================="
grep -A 10 "camera:" "$CONFIG_FILE" | grep -E "(use_vlc_proxy|use_http_stream|use_gstreamer_proxy|vlc_rtsp_port|vlc_http_port|gstreamer_rtsp_port)"
echo ""

echo "=========================================="
echo "SUCCESS!"
echo "=========================================="
echo ""
echo "Config telah diupdate untuk menggunakan GStreamer RTSP Proxy!"
echo ""
echo "Next step:"
echo "1. Cek config: nano $CONFIG_FILE"
echo "2. Pastikan settings:"
echo "   - use_vlc_proxy: false"
echo "   - use_http_stream: false"
echo "   - use_gstreamer_proxy: true"
echo "   - gstreamer_rtsp_port: 8554"
echo "3. Restart bot: sudo systemctl restart cctv-ai-bot"
echo ""
