#!/bin/bash
# Auto-update config.yaml untuk MediaTX settings

set -e

CONFIG_FILE="/opt/cam_ai_telebot/config/config.yaml"
BACKUP_FILE="/opt/cam_ai_telebot/config/config.yaml.backup.$(date +%Y%m%d_%H%M%S)"

echo "=========================================="
echo "Update config untuk MediaTX"
echo "=========================================="
echo ""

# Cek file config ada
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Config file tidak ada: $CONFIG_FILE"
    exit 1
fi

# Backup config
echo "Backup config ke: $BACKUP_FILE"
cp "$CONFIG_FILE" "$BACKUP_FILE"
echo "✅ Backup created"
echo ""

# Update config
echo "Update config.yaml untuk MediaTX..."
echo ""

# Cek apakah use_vlc_proxy ada, jika tidak tambahkan
if grep -q "use_vlc_proxy:" "$CONFIG_FILE"; then
    echo "Update use_vlc_proxy: false"
    sed -i 's/use_vlc_proxy:.*/use_vlc_proxy: false/' "$CONFIG_FILE"
else
    echo "Add use_vlc_proxy: false"
    echo "" >> "$CONFIG_FILE"
    echo "use_vlc_proxy: false" >> "$CONFIG_FILE"
fi

# Cek apakah use_http_stream ada, jika tidak tambahkan
if grep -q "use_http_stream:" "$CONFIG_FILE"; then
    echo "Update use_http_stream: false"
    sed -i 's/use_http_stream:.*/use_http_stream: false/' "$CONFIG_FILE"
else
    echo "Add use_http_stream: false"
    echo "" >> "$CONFIG_FILE"
    echo "use_http_stream: false" >> "$CONFIG_FILE"
fi

# Cek apakah use_gstreamer_proxy ada, jika tidak tambahkan
if grep -q "use_gstreamer_proxy:" "$CONFIG_FILE"; then
    echo "Update use_gstreamer_proxy: true"
    sed -i 's/use_gstreamer_proxy:.*/use_gstreamer_proxy: true/' "$CONFIG_FILE"
else
    echo "Add use_gstreamer_proxy: true"
    echo "" >> "$CONFIG_FILE"
    echo "use_gstreamer_proxy: true" >> "$CONFIG_FILE"
fi

# Cek apakah gstreamer_rtsp_port ada, jika tidak tambahkan
if grep -q "gstreamer_rtsp_port:" "$CONFIG_FILE"; then
    echo "Update gstreamer_rtsp_port: 8554"
    sed -i 's/gstreamer_rtsp_port:.*/gstreamer_rtsp_port: 8554/' "$CONFIG_FILE"
else
    echo "Add gstreamer_rtsp_port: 8554"
    echo "" >> "$CONFIG_FILE"
    echo "gstreamer_rtsp_port: 8554" >> "$CONFIG_FILE"
fi

echo ""
echo "✅ Config updated successfully!"
echo ""

# Show updated config
echo "=========================================="
echo "UPDATED CONFIG"
echo "=========================================="
echo ""
cat "$CONFIG_FILE" | grep -E "use_vlc_proxy|use_http_stream|use_gstreamer_proxy|gstreamer_rtsp_port"
echo ""
echo "=========================================="
echo "DONE"
echo "=========================================="
echo ""
echo "Config telah diupdate untuk MediaTX + FFmpeg proxy"
echo ""
echo "Settings:"
echo "  use_vlc_proxy: false"
echo "  use_http_stream: false"
echo "  use_gstreamer_proxy: true"
echo "  gstreamer_rtsp_port: 8554"
echo ""
echo "Backup tersimpan di: $BACKUP_FILE"
echo ""
echo "Next steps:"
echo "1. Setup MediaTX: bash scripts/setup_mediatx_proxy.sh"
echo "2. Restart bot: sudo systemctl restart cctv-ai-bot"
echo ""
