#!/bin/bash
#
# Script untuk setup Telegram Bot
#

echo "========================================"
echo "Setup Telegram Bot"
echo "========================================"
echo ""

# Cek apakah file konfigurasi ada
if [ ! -f config/telegram_config.json ]; then
    if [ -f config/telegram_config.json.template ]; then
        cp config/telegram_config.json.template config/telegram_config.json
        echo "✓ File konfigurasi dibuat dari template"
    else
        echo "Error: Template konfigurasi tidak ditemukan!"
        exit 1
    fi
fi

echo ""
echo "Panduan Setup Telegram Bot:"
echo "========================================"
echo ""
echo "1. MENDAPATKAN BOT TOKEN"
echo "========================================"
echo "   a. Buka Telegram dan cari @BotFather"
echo "   b. Kirim /newbot"
echo "   c. Ikuti instruksi untuk membuat bot baru"
echo "   d. Pilih nama untuk bot Anda"
echo "   e. Pilih username untuk bot (harus diakhiri dengan 'bot')"
echo "   f. Copy bot token yang diberikan"
echo ""
echo "   Contoh bot token:"
echo "   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
echo ""
echo "2. MENDAPATKAN CHAT ID"
echo "========================================"
echo "   a. Buka Telegram dan cari @userinfobot"
echo "   b. Kirim pesan apapun ke bot"
echo "   c. Bot akan membalas dengan Chat ID Anda"
echo "   d. Copy Chat ID tersebut"
echo ""
echo "   Contoh Chat ID:"
echo "   123456789"
echo ""
echo "3. EDIT FILE KONFIGURASI"
echo "========================================"
echo "   Edit file: config/telegram_config.json"
echo ""
echo "   Isi bagian berikut:"
echo "   - bot_token: Token dari @BotFather"
echo "   - chat_id: Chat ID Anda untuk notifikasi"
echo "   - admin_id: (Opsional) Chat ID admin untuk kontrol penuh"
echo ""
echo "   Contoh:"
echo '   {'
echo '     "bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",'
echo '     "chat_id": "123456789",'
echo '     "admin_id": "123456789"'
echo '   }'
echo ""
echo "4. TEST BOT"
echo "========================================"
echo "   Setelah mengedit konfigurasi:"
echo "   a. Start bot: python3 src/main.py"
echo "   b. Buka Telegram"
echo "   c. Cari bot Anda dengan username yang dibuat"
echo "   d. Kirim /start"
echo ""
echo "========================================"
echo ""

# Tanya apakah ingin langsung edit
read -p "Apakah ingin langsung edit file konfigurasi sekarang? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    nano config/telegram_config.json
    echo ""
    echo "✓ File konfigurasi diedit"
    echo ""
fi

echo "========================================"
echo "Setup Selesai!"
echo "========================================"
echo ""
echo "Langkah selanjutnya:"
echo ""
echo "1. Pastikan bot_token dan chat_id sudah benar"
echo "2. Jalankan aplikasi untuk test:"
echo "   source venv/bin/activate"
echo "   python3 src/main.py"
echo ""
echo "3. Jika berhasil, install sebagai service:"
echo "   sudo ./scripts/setup_service.sh"
echo ""
echo "========================================"
