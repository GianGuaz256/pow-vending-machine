#!/bin/bash

# Bitcoin Lightning Vending Machine Installation Script
# For Raspberry Pi 5 with Waveshare LCD and Qibixx MDB Pi HAT
#
# NOTE: For cleaner installation, consider using the simplified scripts:
#   - install-minimal.sh: Minimal dependencies, LCD setup separate
#   - fix-lcd-64bit.sh: Fix architecture issues on 64-bit OS
# See guides/SIMPLIFIED_INSTALL.md for details

set -e

echo "Bitcoin Lightning Vending Machine - Installation Script"
echo "======================================================="

# Fix locale issues
export LC_ALL=C
export LANG=C

# Check if running on Raspberry Pi or Raspberry Pi OS
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null && ! grep -q "BCM" /proc/cpuinfo 2>/dev/null; then
    # Also check for Raspberry Pi OS via os-release
    if [ -f /etc/os-release ]; then
        if ! grep -q -E "(raspbian|raspberry)" /etc/os-release 2>/dev/null; then
            echo "Warning: This script is designed for Raspberry Pi"
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                exit 1
            fi
        fi
    else
        echo "Warning: This script is designed for Raspberry Pi"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
fi

# Update system
echo "Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install system dependencies
echo "Installing system dependencies..."
# Core Python requirements
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    git \
    build-essential

# Pygame dependencies (required for LCD display via pygame)
# Note: These are needed because the LCD code uses pygame
echo "Installing display dependencies for pygame..."
sudo apt install -y \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libjpeg-dev \
    libportmidi-dev \
    python3-pygame

# Enable SPI and UART interfaces
echo "Enabling SPI and UART interfaces..."
# Check if raspi-config is available
if command -v raspi-config &> /dev/null; then
    sudo raspi-config nonint do_spi 0
    sudo raspi-config nonint do_serial 0
else
    echo "raspi-config not found, please enable SPI and UART manually"
fi

# Create virtual environment
echo "Creating Python virtual environment..."
cd "$(dirname "$0")/.."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r config/requirements.txt

# Create environment file from template
if [ ! -f .env ]; then
    echo "Creating environment configuration file..."
    cp config/env_template.txt .env
    echo "Please edit .env file with your BTCPay Server configuration"
fi

# Create log directory
echo "Creating log directory..."
sudo mkdir -p /var/log
sudo touch /var/log/vending_machine.log
sudo chown $USER:$USER /var/log/vending_machine.log

# Create systemd service
echo "Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/bitcoin-vending.service"
WORKING_DIR=$(pwd)

sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Bitcoin Lightning Vending Machine
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORKING_DIR
Environment=PATH=$WORKING_DIR/venv/bin
ExecStart=$WORKING_DIR/venv/bin/python src/vending_machine.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
sudo systemctl daemon-reload

# Set up udev rules for MDB device
echo "Setting up udev rules for MDB device..."
sudo tee /etc/udev/rules.d/99-mdb-device.rules > /dev/null <<EOF
# Qibixx MDB Pi HAT
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", SYMLINK+="mdb0", GROUP="dialout", MODE="0664"
EOF

sudo udevadm control --reload-rules

# Add user to dialout group for serial access
echo "Adding user to dialout group..."
sudo usermod -a -G dialout $USER

# Configure display settings
echo "Configuring display settings..."
# Check for both possible config locations
CONFIG_FILE="/boot/config.txt"
if [ ! -f "$CONFIG_FILE" ] && [ -f "/boot/firmware/config.txt" ]; then
    CONFIG_FILE="/boot/firmware/config.txt"
fi

if [ -f "$CONFIG_FILE" ]; then
    if ! grep -q "dtparam=spi=on" "$CONFIG_FILE"; then
        echo "dtparam=spi=on" | sudo tee -a "$CONFIG_FILE"
    fi

    if ! grep -q "enable_uart=1" "$CONFIG_FILE"; then
        echo "enable_uart=1" | sudo tee -a "$CONFIG_FILE"
    fi
else
    echo "Warning: Could not find boot config file. Please enable SPI and UART manually."
fi

# Test installation
echo "Testing installation..."
source venv/bin/activate
python -c "
import sys
sys.path.insert(0, 'src')
from src.config import config
print('✓ Configuration loaded successfully')
"

echo ""
echo "Installation completed successfully!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your BTCPay Server configuration:"
echo "   nano .env"
echo ""
echo "2. Test individual components:"
echo "   python tests/test_components.py"
echo ""
echo "3. Run the application:"
echo "   source venv/bin/activate"
echo "   python src/vending_machine.py"
echo ""
echo "4. Enable service to start on boot:"
echo "   sudo systemctl enable bitcoin-vending.service"
echo "   sudo systemctl start bitcoin-vending.service"
echo ""
echo "5. Monitor logs:"
echo "   tail -f /var/log/vending_machine.log"
echo "   sudo journalctl -u bitcoin-vending.service -f"
echo ""
echo "Note: Reboot required for interface changes to take effect" 