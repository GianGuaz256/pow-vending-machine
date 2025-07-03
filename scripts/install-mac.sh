#!/bin/bash

# Bitcoin Lightning Vending Machine Installation Script
# For macOS development and testing

set -e

echo "Bitcoin Lightning Vending Machine - Installation Script (macOS)"
echo "==============================================================="

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "Warning: This script is designed for macOS"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3 from https://python.org or using Homebrew:"
    echo "  brew install python"
    exit 1
fi

# Check for pip
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is required but not installed."
    echo "Please install pip3 or reinstall Python 3."
    exit 1
fi

# Create virtual environment
echo "Creating Python virtual environment..."
cd "$(dirname "$0")/.."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r config/requirements-mac.txt

# Create environment file from template
if [ ! -f .env ]; then
    echo "Creating environment configuration file..."
    cp config/env_template.txt .env
    echo "Please edit .env file with your BTCPay Server configuration"
fi

# Create log directory
echo "Creating log directory..."
mkdir -p logs
touch logs/vending_machine.log

# Test installation
echo "Testing installation..."
python -c "
import sys
import os
sys.path.insert(0, '.')
sys.path.insert(0, 'src')
from config import config
print('✓ Configuration loaded successfully')
print('✓ All imports working correctly')
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
echo "   source venv/bin/activate"
echo "   python tests/test_components.py"
echo ""
echo "3. Run the application (simulator mode):"
echo "   source venv/bin/activate" 
echo "   python src/vending_machine.py"
echo ""
echo "4. Run tests:"
echo "   source venv/bin/activate"
echo "   python -m pytest tests/ -v"
echo ""
echo "Note: This installation is for development/testing only."
echo "Hardware-specific features (GPIO, SPI, real MDB) will be simulated." 