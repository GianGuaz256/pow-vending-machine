#!/bin/bash

# Bitcoin Lightning Vending Machine Installation Script
# For Ubuntu Server with Waveshare LCD and Qibixx MDB Pi HAT

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Error handler
error_exit() {
    log_error "$1"
    exit 1
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   error_exit "This script should not be run as root. Please run as a regular user with sudo privileges."
fi

# Check sudo privileges
log "Testing sudo access..."
if ! sudo -v; then
    error_exit "This script requires sudo privileges. Please ensure you can run sudo commands."
fi

echo "Bitcoin Lightning Vending Machine - Installation Script (Ubuntu)"
echo "================================================================="
log "Starting installation process..."

# Validate Ubuntu version
if ! grep -q "Ubuntu" /etc/os-release 2>/dev/null; then
    log_warning "This script is designed for Ubuntu"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    UBUNTU_VERSION=$(grep VERSION_ID /etc/os-release | cut -d'"' -f2)
    log "Detected Ubuntu $UBUNTU_VERSION"
fi

# Check minimum requirements
log "Checking system requirements..."

# Check Python 3 version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    log "Python version: $PYTHON_VERSION"
    
    # Check if Python version is 3.8 or higher
    if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
        log_warning "Python 3.8+ recommended, found $PYTHON_VERSION"
    fi
else
    log "Python 3 not found - will be installed"
fi

# Check available disk space (minimum 2GB)
AVAILABLE_SPACE=$(df . | tail -1 | awk '{print $4}')
if [ $AVAILABLE_SPACE -lt 2000000 ]; then
    log_warning "Low disk space detected. At least 2GB recommended."
fi

# Check memory (minimum 1GB)
TOTAL_MEM=$(free -m | awk 'NR==2{print $2}')
if [ $TOTAL_MEM -lt 1000 ]; then
    log_warning "Low memory detected. At least 1GB recommended."
fi

# Update system
log "Updating system packages..."
if ! sudo apt update; then
    error_exit "Failed to update package lists"
fi

log "Upgrading system packages..."
if ! sudo apt upgrade -y; then
    log_warning "Some packages failed to upgrade, continuing..."
fi

# Install system dependencies
log "Installing system dependencies..."
SYSTEM_PACKAGES=(
    python3
    python3-pip
    python3-venv
    python3-dev
    git
    curl
    wget
    libffi-dev
    libssl-dev
    libjpeg-dev
    zlib1g-dev
    libfreetype6-dev
    liblcms2-dev
    libopenjp2-7
    libtiff6
    libtiff-dev
    libatlas-base-dev
    libxcb1-dev
    pkg-config
    build-essential
    udev
    systemd
)

for package in "${SYSTEM_PACKAGES[@]}"; do
    if ! dpkg -l | grep -q "^ii  $package "; then
        log "Installing $package..."
        if ! sudo apt install -y "$package"; then
            log_warning "Failed to install $package, continuing..."
        fi
    else
        log "Package $package already installed"
    fi
done

# Detect hardware architecture
ARCHITECTURE=$(uname -m)
log "Detected architecture: $ARCHITECTURE"

# Configure hardware interfaces
log "Configuring hardware interfaces..."

# Check if we're on a Raspberry Pi
if [ -f /proc/device-tree/model ] && grep -q "Raspberry Pi" /proc/device-tree/model; then
    log "Raspberry Pi detected"
    
    # Enable SPI and UART interfaces
    if command -v raspi-config >/dev/null 2>&1; then
        log "Enabling SPI interface..."
        sudo raspi-config nonint do_spi 0
        
        log "Enabling UART interface..."
        sudo raspi-config nonint do_serial 0
    else
        log_warning "raspi-config not available. Manual SPI/UART configuration may be needed."
    fi
    
    # Configure boot config
    if [ -f /boot/config.txt ]; then
        log "Configuring /boot/config.txt..."
        
        if ! grep -q "dtparam=spi=on" /boot/config.txt; then
            echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
            log "Added SPI configuration"
        fi

        if ! grep -q "enable_uart=1" /boot/config.txt; then
            echo "enable_uart=1" | sudo tee -a /boot/config.txt
            log "Added UART configuration"
        fi
    fi
else
    log "Generic Ubuntu system detected - hardware configuration may need manual setup"
fi

# Create project directory and virtual environment
log "Setting up Python environment..."
cd "$(dirname "$0")/.."
PROJECT_DIR=$(pwd)
log "Project directory: $PROJECT_DIR"

if [ -d "venv" ]; then
    log_warning "Virtual environment already exists, removing..."
    rm -rf venv
fi

log "Creating Python virtual environment..."
if ! python3 -m venv venv; then
    error_exit "Failed to create virtual environment"
fi

log "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
log "Upgrading pip..."
if ! pip install --upgrade pip; then
    log_warning "Failed to upgrade pip, continuing..."
fi

# Install Python dependencies based on architecture
log "Installing Python dependencies..."

if [[ "$ARCHITECTURE" =~ ^(arm|aarch64) ]]; then
    # ARM-based system (likely Raspberry Pi), try full requirements first
    log "ARM system detected - installing hardware requirements..."
    
    if pip install -r config/requirements.txt; then
        log_success "All dependencies installed successfully"
    else
        log_warning "Some hardware-specific packages failed. Installing core dependencies..."
        
        # Install core dependencies individually
        CORE_PACKAGES=(
            "requests>=2.31.0"
            "qrcode[pil]>=7.4.2"
            "Pillow>=10.0.0"
            "pygame>=2.5.0"
            "pyserial>=3.5"
            "python-dotenv>=1.0.0"
            "flask>=2.3.0"
            "colorlog>=6.7.0"
        )
        
        for package in "${CORE_PACKAGES[@]}"; do
            log "Installing $package..."
            pip install "$package" || log_warning "Failed to install $package"
        done
    fi
else
    # x86/x64 system, use compatible requirements
    log "x86/x64 system detected - installing compatible dependencies..."
    
    if pip install -r config/requirements-mac.txt; then
        log_success "Compatible dependencies installed successfully"
    else
        log_warning "Some packages failed to install. Installing manually..."
        
        # Install core packages individually
        CORE_PACKAGES=(
            "requests>=2.31.0"
            "qrcode[pil]>=7.4.2"
            "Pillow>=10.0.0"
            "pygame>=2.5.0"
            "pyserial>=3.5"
            "python-dotenv>=1.0.0"
            "flask>=2.3.0"
            "colorlog>=6.7.0"
        )
        
        for package in "${CORE_PACKAGES[@]}"; do
            log "Installing $package..."
            pip install "$package" || log_warning "Failed to install $package"
        done
    fi
fi

# Create environment file from template
log "Setting up configuration..."
if [ ! -f .env ]; then
    log "Creating environment configuration file..."
    if [ -f config/env_template.txt ]; then
        cp config/env_template.txt .env
        log_success "Environment file created from template"
        log_warning "Please edit .env file with your BTCPay Server configuration"
    else
        log_warning "Environment template not found. Creating basic .env file..."
        cat > .env << EOF
# BTCPay Server Configuration
BTCPAY_SERVER_URL=https://your-btcpay-server.com
BTCPAY_STORE_ID=your-store-id
BTCPAY_API_KEY=your-api-key
BTCPAY_WEBHOOK_SECRET=your-webhook-secret

# Vending Machine Configuration
VENDING_CURRENCY=EUR
VENDING_MIN_PRICE=0.50
VENDING_MAX_PRICE=100.00

# Display Configuration
DISPLAY_WIDTH=320
DISPLAY_HEIGHT=480

# MDB Configuration
MDB_SERIAL_PORT=/dev/ttyAMA0
MDB_BAUD_RATE=9600

# System Configuration
LOG_LEVEL=INFO
LOG_FILE=/var/log/vending_machine.log
EOF
        log_success "Basic .env file created"
    fi
else
    log "Environment file already exists"
fi

# Create log directory with proper permissions
log "Setting up logging..."
sudo mkdir -p /var/log/bitcoin-vending
sudo touch /var/log/bitcoin-vending/vending_machine.log
sudo chown -R $USER:$USER /var/log/bitcoin-vending
sudo chmod 755 /var/log/bitcoin-vending
sudo chmod 644 /var/log/bitcoin-vending/vending_machine.log
log_success "Log directory created"

# Set up logrotate
log "Configuring log rotation..."
sudo tee /etc/logrotate.d/bitcoin-vending > /dev/null <<EOF
/var/log/bitcoin-vending/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    copytruncate
    create 644 $USER $USER
}
EOF

# Create systemd service
log "Creating systemd service..."
SERVICE_FILE="/etc/systemd/system/bitcoin-vending.service"

sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Bitcoin Lightning Vending Machine
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=$PROJECT_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin
Environment=PYTHONPATH=$PROJECT_DIR/src
ExecStart=$PROJECT_DIR/venv/bin/python src/vending_machine.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=bitcoin-vending

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$PROJECT_DIR /var/log/bitcoin-vending
CapabilityBoundingSet=

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
log_success "Systemd service created"

# Set up udev rules for MDB device
log "Configuring MDB device access..."
sudo tee /etc/udev/rules.d/99-bitcoin-vending-mdb.rules > /dev/null <<EOF
# Qibixx MDB Pi HAT
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", SYMLINK+="mdb0", GROUP="dialout", MODE="0664"

# Generic USB serial devices for MDB
SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", GROUP="dialout", MODE="0664"
SUBSYSTEM=="tty", ATTRS{idVendor}=="067b", ATTRS{idProduct}=="2303", GROUP="dialout", MODE="0664"
EOF

sudo udevadm control --reload-rules
sudo udevadm trigger
log_success "MDB device rules configured"

# Add user to required groups
log "Configuring user permissions..."
sudo usermod -a -G dialout,gpio,spi,i2c $USER 2>/dev/null || true
log_success "User added to hardware access groups"

# Test installation
log "Testing installation..."
source venv/bin/activate

# Test Python imports
if python -c "
import sys
import os
sys.path.insert(0, '.')
sys.path.insert(0, 'src')
try:
    from config import config
    print('✓ Configuration module loaded')
    from lcd_display import LCDDisplay
    print('✓ LCD display module loaded')
    from mdb_controller import MDBController
    print('✓ MDB controller module loaded')
    from btcpay_client import BTCPayClient
    print('✓ BTCPay client module loaded')
    print('✓ All core modules imported successfully')
except Exception as e:
    print(f'✗ Import error: {e}')
    sys.exit(1)
"; then
    log_success "All core modules imported successfully"
else
    error_exit "Module import test failed"
fi

# Create test runner script
log "Creating test runner scripts..."
cat > run_tests.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

echo "Bitcoin Vending Machine - Component Tests"
echo "========================================="

echo
echo "1. Testing LCD Display Component..."
python tests/test_lcd.py

echo
echo "2. Testing MDB Controller Component..."
python tests/test_mdb.py

echo
echo "3. Testing BTCPay Server Component..."
python tests/test_btcpay.py

echo
echo "All component tests completed!"
EOF

chmod +x run_tests.sh

cat > run_enhanced_tests.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate

echo "Bitcoin Vending Machine - Enhanced Tests"
echo "========================================"
python tests/test_enhanced_components.py
EOF

chmod +x run_enhanced_tests.sh

log_success "Test runner scripts created"

# Final validation
log "Performing final validation..."

# Check if all required files exist
REQUIRED_FILES=(
    "src/config.py"
    "src/lcd_display.py"
    "src/mdb_controller.py"
    "src/btcpay_client.py"
    "src/vending_machine.py"
    "tests/test_lcd.py"
    "tests/test_mdb.py"
    "tests/test_btcpay.py"
    ".env"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        log "✓ $file exists"
    else
        log_warning "✗ $file missing"
    fi
done

echo ""
log_success "Installation completed successfully!"
echo "=================================================================="
echo ""
echo "🚀 NEXT STEPS:"
echo ""
echo "1. 📝 Configure your BTCPay Server settings:"
echo "   nano .env"
echo ""
echo "2. 🧪 Test individual components:"
echo "   ./run_tests.sh"
echo ""
echo "3. 🔄 Run enhanced integration tests:"
echo "   ./run_enhanced_tests.sh"
echo ""
echo "4. 🚀 Start the application manually:"
echo "   source venv/bin/activate"
echo "   python src/vending_machine.py"
echo ""
echo "5. 🔧 Enable and start the systemd service:"
echo "   sudo systemctl enable bitcoin-vending.service"
echo "   sudo systemctl start bitcoin-vending.service"
echo ""
echo "6. 📊 Monitor the application:"
echo "   sudo systemctl status bitcoin-vending.service"
echo "   sudo journalctl -u bitcoin-vending.service -f"
echo "   tail -f /var/log/bitcoin-vending/vending_machine.log"
echo ""
echo "⚠️  IMPORTANT NOTES:"
echo "   • Reboot required if using GPIO/SPI interfaces"
echo "   • Edit .env file with your BTCPay Server details"
echo "   • Ensure user is in dialout group: groups $USER"
echo "   • Check hardware connections before starting service"
echo ""
log_success "Installation guide complete!" 