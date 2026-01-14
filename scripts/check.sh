#!/bin/bash
# Script Cek CCTV AI Telegram Bot
# Memverifikasi semua komponen dan status aplikasi

echo "=========================================="
echo "  CCTV AI Telegram Bot - System Check"
echo "=========================================="
echo ""

# Warna untuk output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Direktori aplikasi
APP_DIR="/opt/cam_ai_telebot"
SERVICE_NAME="cctv-ai-bot"

# Counter untuk hasil
PASS=0
FAIL=0
WARN=0

# Fungsi cek
check() {
    local name="$1"
    local command="$2"
    local expected="$3"
    
    echo -n "Checking $name... "
    
    eval "$command" > /dev/null 2>&1
    local result=$?
    
    if [ $result -eq 0 ]; then
        if [ -n "$expected" ]; then
            local actual=$(eval "$command")
            if echo "$actual" | grep -q "$expected"; then
                echo -e "${GREEN}✓ PASS${NC}"
                ((PASS++))
            else
                echo -e "${RED}✗ FAIL${NC} (Expected: $expected)"
                ((FAIL++))
            fi
        else
            echo -e "${GREEN}✓ PASS${NC}"
            ((PASS++))
        fi
    else
        echo -e "${RED}✗ FAIL${NC}"
        ((FAIL++))
    fi
}

# Fungsi cek dengan warning
check_warn() {
    local name="$1"
    local command="$2"
    
    echo -n "Checking $name... "
    
    eval "$command" > /dev/null 2>&1
    local result=$?
    
    if [ $result -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC}"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠ WARN${NC}"
        ((WARN++))
    fi
}

echo "=== SYSTEM CHECK ==="
echo ""

# 1. Cek service systemd
check "Systemd service" "systemctl is-active $SERVICE_NAME" "active"

# 2. Cek direktori aplikasi
check "Application directory" "[ -d $APP_DIR ]"

# 3. Cek Python virtual environment
check "Virtual environment" "[ -d $APP_DIR/venv ]"

# 4. Cek log directory
check "Log directory" "[ -d $APP_DIR/logs ]"

# 5. Cek config file
check "Config file exists" "[ -f $APP_DIR/config/config.yaml ]"

# 6. Cek data directories
check "Data directory" "[ -d $APP_DIR/data ]"
check "Faces directory" "[ -d $APP_DIR/data/faces ]"

# 7. Cek source files
check "Main source file" "[ -f $APP_DIR/src/main.py ]"
check "Motion detector" "[ -f $APP_DIR/src/detection/motion_detector.py ]"
check "Person detector" "[ -f $APP_DIR/src/detection/person_detector.py ]"
check "Face detector" "[ -f $APP_DIR/src/detection/face_detector.py ]"
check "Face recognition" "[ -f $APP_DIR/src/detection/face_recognition.py ]"
check "Bot handler" "[ -f $APP_DIR/src/telegram_bot/bot_handler.py ]"

# 8. Cek config template
check "Config template" "[ -f $APP_DIR/config/config.yaml.template ]"

echo ""
echo "=== CONFIGURATION CHECK ==="
echo ""

# 9. Cek git status
echo -n "Checking git status... "
cd $APP_DIR
git status --porcelain > /dev/null 2>&1
if [ $? -eq 0 ]; then
    git diff --quiet && git diff --cached --quiet
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ PASS${NC} (Clean)"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠ WARN${NC} (Uncommitted changes)"
        ((WARN++))
    fi
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAIL++))
fi

# 10. Cek branch
check "Git branch" "git rev-parse --abbrev-ref HEAD" "main"

# 11. Cek remote connection
check_warn "Git remote connection" "git fetch --dry-run"

echo ""
echo "=== DEPENDENCIES CHECK ==="
echo ""

# 12. Cek Python syntax
if [ -d "$APP_DIR/venv" ]; then
    source $APP_DIR/venv/bin/activate
    
    # Cek import
    check "OpenCV (cv2)" "python3 -c 'import cv2'"
    check "NumPy" "python3 -c 'import numpy'"
    check "PyYAML" "python3 -c 'import yaml'"
    check "Telegram Bot" "python3 -c 'from telegram import Bot'"
    check "YOLO (ultralytics)" "python3 -c 'from ultralytics import YOLO'"
    
    deactivate
else
    echo -e "${YELLOW}Virtual environment not found, skipping dependency checks${NC}"
fi

echo ""
echo "=== RUNNING STATUS CHECK ==="
echo ""

# 13. Cek log terbaru
echo -n "Checking recent logs... "
if [ -f "$APP_DIR/logs/app.log" ]; then
    recent_logs=$(tail -20 $APP_DIR/logs/app.log)
    if echo "$recent_logs" | grep -q "Detection loop running"; then
        echo -e "${GREEN}✓ PASS${NC} (Detection loop active)"
        ((PASS++))
    elif echo "$recent_logs" | grep -q "Error\|Exception\|Failed"; then
        echo -e "${RED}✗ FAIL${NC} (Errors found in logs)"
        ((FAIL++))
    else
        echo -e "${YELLOW}⚠ WARN${NC} (Unable to determine status)"
        ((WARN++))
    fi
else
    echo -e "${YELLOW}⚠ WARN${NC} (Log file not found)"
    ((WARN++))
fi

# 14. Cek motion detector initialization
echo -n "Checking motion detector init... "
if [ -f "$APP_DIR/logs/app.log" ]; then
    if grep -q "Motion detector diinisialisasi" $APP_DIR/logs/app.log; then
        echo -e "${GREEN}✓ PASS${NC} (Initialized)"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠ WARN${NC} (Not initialized or not found in logs)"
        ((WARN++))
    fi
else
    echo -e "${YELLOW}⚠ WARN${NC} (Log file not found)"
    ((WARN++))
fi

# 15. Cek telegram bot initialization
echo -n "Checking telegram bot init... "
if [ -f "$APP_DIR/logs/app.log" ]; then
    if grep -q "Telegram Bot berjalan" $APP_DIR/logs/app.log; then
        echo -e "${GREEN}✓ PASS${NC} (Running)"
        ((PASS++))
    else
        echo -e "${YELLOW}⚠ WARN${NC} (Not running or not found in logs)"
        ((WARN++))
    fi
else
    echo -e "${YELLOW}⚠ WARN${NC} (Log file not found)"
    ((WARN++))
fi

echo ""
echo "=== NETWORK CHECK ==="
echo ""

# 16. Cek koneksi kamera
echo -n "Checking camera connection... "
if grep -q "camera:" $APP_DIR/config/config.yaml; then
    IP=$(grep -A 1 "^  ip:" $APP_DIR/config/config.yaml | head -n 1 | awk '{print $2}' | tr -d '"')
    if [ -n "$IP" ]; then
        ping -c 1 -W 2 $IP > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ PASS${NC} (Camera at $IP is reachable)"
            ((PASS++))
        else
            echo -e "${RED}✗ FAIL${NC} (Camera at $IP not reachable)"
            ((FAIL++))
        fi
    else
        echo -e "${YELLOW}⚠ WARN${NC} (IP not found in config)"
        ((WARN++))
    fi
else
    echo -e "${YELLOW}⚠ WARN${NC} (Camera config not found)"
    ((WARN++))
fi

# 17. Cek internet connection
echo -n "Checking internet connection... "
ping -c 1 -W 2 8.8.8.8 > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASS++))
else
    echo -e "${YELLOW}⚠ WARN${NC} (No internet)"
    ((WARN++))
fi

echo ""
echo "=========================================="
echo "  CHECK RESULTS"
echo "=========================================="
echo -e "${GREEN}PASSED: $PASS${NC}"
echo -e "${YELLOW}WARNINGS: $WARN${NC}"
echo -e "${RED}FAILED: $FAIL${NC}"
echo ""

TOTAL=$((PASS + FAIL + WARN))
SUCCESS_RATE=$((PASS * 100 / TOTAL))

echo "Success Rate: $SUCCESS_RATE%"
echo ""

if [ $FAIL -eq 0 ] && [ $WARN -le 2 ]; then
    echo -e "${GREEN}✓ SYSTEM HEALTHY - All critical checks passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Test motion detection: Gerakkan tangan di depan kamera"
    echo "2. Test person detection: Berdiri di depan kamera"
    echo "3. Check Telegram for notifications"
    echo "4. Monitor logs: tail -f $APP_DIR/logs/app.log"
    exit 0
elif [ $FAIL -eq 0 ]; then
    echo -e "${YELLOW}⚠ SYSTEM OKAY - Minor warnings detected${NC}"
    echo "System is running but some non-critical issues found"
    echo ""
    echo "Review warnings and fix if needed"
    exit 0
else
    echo -e "${RED}✗ SYSTEM ISSUES DETECTED${NC}"
    echo ""
    echo "Failed checks:"
    echo "1. Review error messages above"
    echo "2. Check logs: sudo journalctl -u $SERVICE_NAME -n 50"
    echo "3. Check app logs: tail -50 $APP_DIR/logs/app.log"
    echo ""
    echo "Common fixes:"
    echo "- Install missing dependencies: pip install -r requirements.txt"
    echo "- Fix config file: nano $APP_DIR/config/config.yaml"
    echo "- Restart service: sudo systemctl restart $SERVICE_NAME"
    exit 1
fi
