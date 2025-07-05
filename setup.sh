#!/bin/bash

# Bitcoin Lightning Vending Machine Setup
# For Raspberry Pi OS with Waveshare 3.5" LCD and MDB Board

set -e

echo "Bitcoin Lightning Vending Machine Setup"
echo "======================================"

# Update system
echo "Updating system..."
sudo apt update
sudo apt upgrade -y

# Install basic requirements
echo "Installing requirements..."
sudo apt install -y python3 python3-pip python3-venv git build-essential

# Fix 64-bit compatibility if needed
if [[ $(uname -m) == "aarch64" ]]; then
    echo "Setting up 64-bit compatibility..."
    sudo dpkg --add-architecture armhf
    sudo apt update
    sudo apt install -y libc6:armhf libstdc++6:armhf libx11-6:armhf
    sudo apt --fix-broken install -y || true
fi

# Enable hardware interfaces
echo "Enabling SPI and UART..."
sudo raspi-config nonint do_spi 0
sudo raspi-config nonint do_serial 0

# Setup Python environment
echo "Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r config/requirements.txt

# Create config file
[ ! -f .env ] && cp config/env_template.txt .env

# Add user to dialout group
sudo usermod -a -G dialout $USER

# LCD setup instructions
echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo ""
echo "1. REBOOT to apply hardware changes:"
echo "   sudo reboot"
echo ""
echo "2. After reboot, install LCD driver:"
echo "   git clone https://github.com/waveshare/LCD-show.git"
echo "   cd LCD-show"
echo "   chmod +x LCD35B-show-V2"
echo "   sudo ./LCD35B-show-V2"
echo ""
echo "3. After LCD reboot, configure BTCPay:"
echo "   nano .env"
echo ""
echo "4. Run the vending machine:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo "" 