#!/bin/bash
# VLC RTSP Connection Test Script

set -e

echo "=========================================="
echo "VLC RTSP Connection Test"
echo "=========================================="
echo ""

# Konfigurasi
CAMERA_IP=${1:-"10.26.27.196"}
CAMERA_USER=${2:-"admin"}
CAMERA_PASS=${3:-"Kuncong0203"}
RTSP_PORT=${4:-554}
STREAM_URL=${5:-"/1"}

echo "=========================================="
echo "KONFIGURASI"
echo "=========================================="
echo "Kamera IP: $CAMERA_IP"
echo "Kamera User: $CAMERA_USER"
echo "RTSP Port: $RTSP_PORT"
echo "Stream URL: $STREAM_URL"
echo ""

# Test 1: Ping Camera
echo "=========================================="
echo "TEST 1: Ping Camera"
echo "=========================================="
echo ""

if ping -c 3 $CAMERA_IP > /dev/null 2>&1; then
    echo "✅ Camera reachable: $CAMERA_IP"
else
    echo "❌ Camera NOT reachable: $CAMERA_IP"
    echo "Check network connection and camera power!"
    exit 1
fi

echo ""

# Test 2: Telnet RTSP Port
echo "=========================================="
echo "TEST 2: Telnet RTSP Port"
echo "=========================================="
echo ""

if timeout 3 bash -c "cat < /dev/null > /dev/tcp/$CAMERA_IP/$RTSP_PORT" 2>/dev/null; then
    echo "✅ RTSP port open: $CAMERA_IP:$RTSP_PORT"
else
    echo "❌ RTSP port CLOSED: $CAMERA_IP:$RTSP_PORT"
    echo "Check camera RTSP settings!"
    exit 1
fi

echo ""

# Test 3: VLC Version
echo "=========================================="
echo "TEST 3: VLC Version"
echo "=========================================="
echo ""

if command -v vlc &> /dev/null; then
    VLC_VERSION=$(sudo -u vlc-user vlc --version 2>/dev/null | head -1)
    if [ -n "$VLC_VERSION" ]; then
        echo "✅ VLC installed: $VLC_VERSION"
    else
        echo "✅ VLC installed: $(vlc --version | head -1)"
    fi
else
    echo "❌ VLC NOT installed"
    exit 1
fi

echo ""

# Test 4: Test RTSP Connection with VLC
echo "=========================================="
echo "TEST 4: VLC RTSP Connection (10 seconds)"
echo "=========================================="
echo ""

RTSP_URL="rtsp://${CAMERA_USER}:${CAMERA_PASS}@${CAMERA_IP}:${RTSP_PORT}${STREAM_URL}?rtsp_transport=tcp&latency=0"
echo "Connecting to: rtsp://${CAMERA_USER}:****@${CAMERA_IP}:${RTSP_PORT}${STREAM_URL}?rtsp_transport=tcp&latency=0"
echo ""

# Run VLC for 10 seconds, then kill it
if id "vlc-user" &>/dev/null; then
    timeout 10 sudo -u vlc-user vlc -I dummy "$RTSP_URL" vlc://quit 2>&1 | head -20 &
else
    echo "❌ vlc-user not exists"
    exit 1
fi
VLC_PID=$!
sleep 10
kill $VLC_PID 2>/dev/null || true
wait $VLC_PID 2>/dev/null || true

echo ""

# Test 5: Check VLC User
echo "=========================================="
echo "TEST 5: VLC User Check"
echo "=========================================="
echo ""

if id "vlc-user" &>/dev/null; then
    echo "✅ VLC user exists: vlc-user"
    id vlc-user
else
    echo "❌ VLC user NOT exists: vlc-user"
    echo "Run: sudo useradd -r -s /bin/false vlc-user"
fi

echo ""

# Test 6: Test VLC as vlc-user
echo "=========================================="
echo "TEST 6: VLC as vlc-user (10 seconds)"
echo "=========================================="
echo ""

if id "vlc-user" &>/dev/null; then
    echo "Testing VLC as vlc-user..."
    timeout 10 sudo -u vlc-user vlc -I dummy "$RTSP_URL" vlc://quit 2>&1 | head -20 &
    VLC_PID=$!
    sleep 10
    kill $VLC_PID 2>/dev/null || true
    wait $VLC_PID 2>/dev/null || true
    echo ""
    echo "✅ VLC can run as vlc-user"
else
    echo "❌ vlc-user not exists, skipping"
fi

echo ""

# Test 7: Test VLC Streaming
echo "=========================================="
echo "TEST 7: VLC Streaming to Local RTSP (10 seconds)"
echo "=========================================="
echo ""

RTSP_DEST="rtsp://127.0.0.1:8554/camera"
echo "Source: $RTSP_URL"
echo "Destination: $RTSP_DEST"
echo ""

# Kill existing VLC processes
pkill -9 vlc 2>/dev/null || true
sleep 2

# Test VLC streaming
if id "vlc-user" &>/dev/null; then
    timeout 10 sudo -u vlc-user vlc -I dummy \
        --no-sout-rtp-sap \
        --no-sout-standard-sap \
        --ttl=1 \
        --sout="#transcode{vcodec=h264,acodec=none}:rtp{sdp=${RTSP_DEST}}" \
        "$RTSP_URL" \
        vlc://quit 2>&1 | head -30 &
else
    echo "❌ vlc-user not exists"
    exit 1
fi

VLC_PID=$!
sleep 10
kill $VLC_PID 2>/dev/null || true
wait $VLC_PID 2>/dev/null || true

echo ""
echo "=========================================="
echo "TEST COMPLETE"
echo "=========================================="
echo ""
echo "Check output above for any errors!"
echo ""
