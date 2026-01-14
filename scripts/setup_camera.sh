#!/bin/bash
#
# Script untuk test koneksi kamera
#

echo "========================================"
echo "Test Koneksi Kamera"
echo "========================================"
echo ""

# Load konfigurasi
if [ ! -f config/config.yaml ]; then
    echo "Error: config/config.yaml tidak ditemukan!"
    echo "Jalankan ./scripts/install.sh terlebih dahulu"
    exit 1
fi

# Activate virtual environment
if [ -d venv ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment tidak ditemukan!"
    echo "Jalankan ./scripts/install.sh terlebih dahulu"
    exit 1
fi

# Buat script test Python
cat > /tmp/test_camera.py << 'EOF'
import cv2
import yaml
import sys

# Load config
with open('config/config.yaml', 'r') as f:
    config = yaml.safe_load(f)

camera_config = config['camera']

# Build RTSP URL
rtsp_url = f"rtsp://{camera_config['username']}:{camera_config['password']}@{camera_config['ip']}:{camera_config.get('rtsp_port', 554)}{camera_config.get('stream_url', '/1')}"

print(f"Menghubungkan ke kamera...")
print(f"IP: {camera_config['ip']}")
print(f"Port: {camera_config.get('rtsp_port', 554)}")
print(f"Username: {camera_config['username']}")
print(f"Stream: {camera_config.get('stream_url', '/1')}")
print("")

try:
    # Coba koneksi
    cap = cv2.VideoCapture(rtsp_url)
    
    if not cap.isOpened():
        print("❌ Gagal membuka koneksi ke kamera")
        sys.exit(1)
    
    print("✓ Berhasil terkoneksi ke kamera")
    
    # Baca satu frame
    ret, frame = cap.read()
    
    if ret and frame is not None:
        height, width = frame.shape[:2]
        print(f"✓ Resolusi: {width}x{height}")
        print(f"✓ Berhasil membaca frame")
        
        # Simpan test image
        cv2.imwrite('/tmp/camera_test.jpg', frame)
        print("✓ Test image disimpan ke /tmp/camera_test.jpg")
        
        # Cek properti
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"✓ FPS: {fps}")
        
        print("")
        print("========================================")
        print("✓ Kamera berhasil terkoneksi!")
        print("========================================")
        
    else:
        print("❌ Gagal membaca frame dari kamera")
        sys.exit(1)
    
    cap.release()
    
except Exception as e:
    print(f"❌ Error: {str(e)}")
    sys.exit(1)

EOF

# Jalankan test
python3 /tmp/test_camera.py

# Cek hasil
if [ $? -eq 0 ]; then
    echo ""
    echo "Test kamera berhasil!"
    echo ""
    echo "Anda dapat melihat test image:"
    echo "  eog /tmp/camera_test.jpg"
    echo ""
    echo "Atau jika ada perbaikan yang diperlukan:"
    echo "  nano config/config.yaml"
    echo ""
else
    echo ""
    echo "Test kamera gagal!"
    echo ""
    echo "Periksa konfigurasi kamera:"
    echo "  nano config/config.yaml"
    echo ""
    echo "Pastikan:"
    echo "  - IP kamera benar"
    echo "  - Kamera dalam jaringan yang sama"
    echo "  - Username dan password benar"
    echo "  - Port RTSP benar"
    echo "  - Kamera mendukung RTSP"
    echo ""
    exit 1
fi

# Cleanup
rm /tmp/test_camera.py
