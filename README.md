# Bitcoin Lightning Vending Machine

<img src="public/vending.jpg" alt="Bitcoin Lightning Vending Machine" width="100%" />

A complete Python application for Raspberry Pi 5 that enables Bitcoin Lightning Network payments in vending machines. This system integrates with BTCPay Server for payment processing, uses an LCD touchscreen for user interface, and communicates with vending machine hardware via MDB protocol.

## Features

- **Bitcoin Lightning Network Payments**: Fast, low-fee Bitcoin payments via BTCPay Server
- **Touch Screen Interface**: 3.5" Waveshare LCD with intuitive user interface
- **MDB Protocol Support**: Communication with vending machine hardware via Qibixx MDB Pi HAT
- **Real-time Payment Monitoring**: Automatic payment confirmation and vending
- **QR Code Generation**: Dynamic Lightning invoice QR codes for mobile payments
- **System Health Monitoring**: Automatic component status checking and error recovery
- **Logging & Diagnostics**: Comprehensive logging for troubleshooting

## Hardware Requirements

### Core Components
- **Raspberry Pi 5 8GB** (Quad-Core ARM76 64-bit, 2.4 GHz)
- **Waveshare 3.5 inch Touch Screen IPS TFT LCD** (320x480 resolution)
- **Qibixx MDB Pi HAT** (for MDB communication with vending machine)
- **27W USB-C PD Power Supply** for Raspberry Pi 5

### Connections
- LCD connects via SPI interface
- MDB HAT communicates via UART
- Standard vending machine MDB connection

## Software Requirements

- **Raspberry Pi OS** (64-bit recommended)
- **Python 3.9+**
- **BTCPay Server** (self-hosted or hosted)
- **Lightning Network Node** (connected to BTCPay Server)

## Installation

### 1. Clone Repository
```bash
git clone <repository-url>
cd pow-vending-machine
```

### 2. Run Installation Script
```bash
cd scripts
chmod +x install.sh
./install.sh
```

The installation script will:
- Update system packages
- Install required dependencies
- Enable SPI and UART interfaces
- Create Python virtual environment
- Install Python packages
- Set up systemd service
- Configure logging

### 3. Configure BTCPay Server

Create environment configuration from template:
```bash
cp config/env_template.txt .env
nano .env
```

Fill in your BTCPay Server details:
```bash
BTCPAY_SERVER_URL=https://your-btcpay-server.com
BTCPAY_STORE_ID=your-store-id
BTCPAY_API_KEY=your-api-key
BTCPAY_WEBHOOK_SECRET=your-webhook-secret
```

### 4. Test Installation
```bash
source venv/bin/activate
python main.py
```

### 5. Enable Service (Optional)
```bash
sudo systemctl enable bitcoin-vending.service
sudo systemctl start bitcoin-vending.service
```

## Quick Start

### For Mac Development
```bash
# Setup development environment
cd scripts && make setup-mac

# Run tests
make test-mac

# Run simulator
make simulate
```

### For Raspberry Pi Production  
```bash
# Full installation
cd scripts && make setup

# Run tests
make test

# Deploy as service
make deploy
```

### Manual Operation
```bash
# Direct execution
python main.py

# Or using source path
python src/vending_machine.py

# Run individual tests
python tests/test_components.py
python tests/test_mac.py
python tests/simulator.py
```

## Configuration

### Display Settings
Edit `config.py` to adjust display parameters:
```python
@dataclass
class DisplayConfig:
    width: int = 320
    height: int = 480
    orientation: int = 90  # Rotation in degrees
```

### MDB Settings
Configure MDB communication:
```python
@dataclass
class MDBConfig:
    serial_port: str = "/dev/ttyAMA0"
    baud_rate: int = 9600
    timeout: float = 1.0
```

### Payment Settings
Adjust payment parameters:
```python
@dataclass
class VendingConfig:
    max_price: float = 100.0
    min_price: float = 0.50
    currency: str = "EUR"
    payment_confirmation_time: int = 30
```

## Operation Flow

1. **System Initialization**
   - Check all hardware components
   - Connect to BTCPay Server
   - Display system status

2. **Ready State**
   - Wait for vend request from MDB
   - Display "Ready" message

3. **Vend Request**
   - Receive item price from vending machine
   - Create Lightning invoice via BTCPay Server
   - Display QR code for payment

4. **Payment Processing**
   - Monitor Lightning invoice status
   - Update display with payment progress
   - Handle payment timeout/errors

5. **Payment Confirmed**
   - Send approval to vending machine
   - Trigger item dispensing
   - Display success message

6. **Complete Transaction**
   - End MDB session
   - Return to ready state

## Hardware Setup

This section covers the complete setup procedure for both the MDB Pi HAT and 3.5" LCD display on Raspberry Pi running Ubuntu 24.04.

### Prerequisites

- Raspberry Pi 3B+, 4, or 5 (recommended: Pi 5 8GB)
- Ubuntu 24.04 LTS (64-bit) for Raspberry Pi
- Qibixx MDB Pi HAT
- Waveshare 3.5" RPi LCD (C) - 480x320 touchscreen
- Internet connection for driver installation
- SSH access or external HDMI display for initial setup

### 1. MDB Pi HAT UART Configuration

The MDB Pi HAT uses the Raspberry Pi's UART interface for communication. This requires specific system configuration to work properly with Ubuntu.

#### 1.1 Disable Console Serial Access

For **Ubuntu 24.04** on Raspberry Pi, edit the boot configuration:

```bash
sudo nano /boot/firmware/config.txt
```

Add these lines at the end:
```bash
# MDB Pi HAT Configuration
# Indicates which kernel
kernel=vmlinuz
# Overrides console login
initramfs initrd.img followkernel
# Disables bluetooth overlay
dtoverlay=disable-bt
enable_uart=1

# For Raspberry Pi 5, also add:
dtparam=uart0=on
```

#### 1.2 Disable Serial Console

Edit the command line parameters:
```bash
sudo nano /boot/firmware/nobtcmd.txt
```

Remove this entry (leave the rest of the line intact):
```bash
console=ttyAMA0,115200
```

#### 1.3 Disable Bluetooth UART Assignment

Disable the HCI UART service:
```bash
sudo systemctl disable hciuart
```

#### 1.4 UART Interface Parameters

The MDB Pi HAT communicates with these settings:
- **Baud Rate**: 115200
- **Parity**: None
- **Data Bits**: 8
- **Stop Bits**: 1
- **Device**: `/dev/ttyAMA0`

#### 1.5 Test UART Communication

Install and test with minicom:
```bash
sudo apt-get update
sudo apt-get install minicom

# Test connection
sudo minicom -b 115200 -D /dev/ttyAMA0
```

In minicom:
1. Press `CTRL+A`, then `Z`, then `E` to enable local echo
2. Type `V+` and press Enter (command must be uppercase)
3. You should see a response from the MDB Pi HAT

#### 1.6 GPIO Pin Usage

The MDB Pi HAT uses these GPIO pins:
- **GPIO 5 (BCM5)**: Communication signaling (SPI mode only)
- **GPIO 6 (BCM6)**: Reset control (must be HIGH or input for normal operation)
- **GPIO 13 (BCM13)**: Communication signaling (SPI mode only)
- **GPIO 8,9,10,11**: SPI interface (reserved, do not initialize)

### 2. Waveshare 3.5" LCD Setup

#### 2.1 Hardware Connection

The LCD connects to the Raspberry Pi's 40-pin header. The display has 26 pins, so align them correctly:

**Pin Connections:**
| LCD Pin | RPi Pin | Function |
|---------|---------|----------|
| 1, 17 | 1, 17 | 3.3V Power |
| 2, 4 | 2, 4 | 5V Power |
| 6, 9, 14, 20, 25 | 6, 9, 14, 20, 25 | Ground |
| 11 | 11 | Touch IRQ |
| 18 | 18 | LCD RS |
| 19 | 19 | LCD SI/Touch SI |
| 21 | 21 | Touch SO |
| 22 | 22 | Reset |
| 23 | 23 | LCD SCK/Touch SCK |
| 24 | 24 | LCD CS |
| 26 | 26 | Touch CS |

#### 2.2 Driver Installation

**Method 1: Automatic Installation (Recommended)**

Clone and install the LCD driver:
```bash
git clone https://github.com/waveshare/LCD-show.git
cd LCD-show/
chmod +x LCD35C-show
sudo ./LCD35C-show
```

The system will reboot automatically and the touchscreen should be active.

**Method 2: Manual Installation for Ubuntu 24.04**

For Ubuntu systems, you may need manual configuration. Refer to the Waveshare manual configuration guide if the automatic method doesn't work.

#### 2.3 Screen Orientation

To change screen rotation (0°, 90°, 180°, 270°):
```bash
cd LCD-show/
sudo ./LCD35C-show 90  # Replace 90 with desired rotation
```

#### 2.4 Touch Screen Calibration

Install calibration tool:
```bash
sudo apt-get update
sudo apt-get install xinput-calibrator
```

Run calibration:
```bash
xinput_calibrator
```

Follow the on-screen instructions to calibrate touch points.

Save calibration data:
```bash
sudo nano /etc/X11/xorg.conf.d/99-calibration.conf
```

#### 2.5 Virtual Keyboard (Optional)

Install virtual keyboard for touch input:
```bash
sudo apt-get update
sudo apt-get install matchbox-keyboard

# Create toggle script
sudo nano /usr/bin/toggle-matchbox-keyboard.sh
```

Add this content:
```bash
#!/bin/bash
# This script toggles the virtual keyboard
PID=`pidof matchbox-keyboard`
if [ ! -e $PID ]; then
    killall matchbox-keyboard
else
    matchbox-keyboard -s 50 extended&
fi
```

Make executable:
```bash
sudo chmod +x /usr/bin/toggle-matchbox-keyboard.sh
```

#### 2.6 Backlight Control

Control LCD backlight brightness via GPIO:
```bash
# Install GPIO utilities
sudo apt-get install wiringpi

# Set PWM mode
gpio -g mode 18 pwm
gpio pwmc 1000

# Control brightness (0-1024)
gpio -g pwm 18 512  # 50% brightness
gpio -g pwm 18 1024 # 100% brightness
gpio -g pwm 18 0    # Off
```

### 3. System Configuration

#### 3.1 Enable Required Interfaces

Enable SPI and I2C interfaces:
```bash
sudo raspi-config
```

Navigate to:
- Interfacing Options → SPI → Enable
- Interfacing Options → I2C → Enable

Or manually edit `/boot/firmware/config.txt`:
```bash
dtparam=spi=on
dtparam=i2c_arm=on
```

#### 3.2 Power Requirements

Ensure adequate power supply:
- **Raspberry Pi 5**: 27W USB-C PD power supply
- **Raspberry Pi 4**: Minimum 3A/5V power supply
- **LCD Power Consumption**: ~200mA

#### 3.3 Final Reboot

After all configurations:
```bash
sudo reboot
```

### 4. Testing Hardware Setup

#### 4.1 Test MDB Communication

```bash
# Check UART device
ls -la /dev/ttyAMA0

# Test with simple echo
echo "V+" > /dev/ttyAMA0
```

#### 4.2 Test LCD Display

The LCD should show the desktop after driver installation. Test touch functionality by interacting with the screen.

#### 4.3 GPIO Reset Test

Test MDB Pi HAT reset functionality:
```bash
# Export GPIO 6 for reset control
echo "6" > /sys/class/gpio/export
echo "out" > /sys/class/gpio/gpio6/direction

# Reset the HAT
echo "0" > /sys/class/gpio/gpio6/value
sleep 1
echo "in" > /sys/class/gpio/gpio6/direction
```

### 5. Troubleshooting Hardware Issues

#### UART Issues
- Verify `/dev/ttyAMA0` exists and is accessible
- Check that Bluetooth is disabled with `sudo systemctl status hciuart`
- Ensure `enable_uart=1` is in `/boot/firmware/config.txt`

#### LCD Issues
- If screen is blank, try connecting via SSH and reinstalling drivers
- For Ubuntu, use SSH or external HDMI during initial setup
- Check SPI is enabled: `lsmod | grep spi`

#### Power Issues
- Monitor `dmesg` for undervoltage warnings
- Use adequate power supply (27W for Pi 5)
- Check LED indicators: PWR should be solid, ACT should blink

#### Driver Conflicts
- If `apt-get upgrade` breaks the display, edit `/boot/firmware/config.txt` and remove `dtoverlay=ads7846`
- Reboot after configuration changes

### 6. MDB Wiring

Standard MDB connection to vending machine:
- **Pin 1**: +12V DC
- **Pin 2**: Ground  
- **Pin 3**: Data High
- **Pin 4**: Data Low

**Warning**: Ensure proper voltage levels and grounding before connecting to vending machine hardware.

## Troubleshooting

### Common Issues

**Display not working:**
- Check SPI is enabled: `sudo raspi-config`
- Verify LCD connections
- Check display initialization logs

**MDB communication failed:**
- Verify UART is enabled
- Check MDB cable connections
- Test with multimeter for proper voltages

**BTCPay Server connection issues:**
- Verify network connectivity
- Check API key permissions
- Confirm store ID is correct

### Log Files
```bash
# Application logs
tail -f /var/log/vending_machine.log

# System service logs
sudo journalctl -u bitcoin-vending.service -f
```

### Debug Mode
Run with increased logging:
```bash
python vending_machine.py --log-level DEBUG
```

## Security Considerations

- Keep BTCPay Server API keys secure
- Use HTTPS for BTCPay Server communication
- Regular system updates
- Network firewall configuration
- Physical security of Raspberry Pi

## API Integration

### BTCPay Server API
The system uses BTCPay Server's REST API:
- Invoice creation
- Payment monitoring
- Status updates

### Required Permissions
API key needs these permissions:
- `btcpay.store.cancreateinvoice` - Required to create new invoices for vending machine purchases
- `btcpay.store.canviewinvoices` - Required to monitor invoice status and payment confirmation
- `btcpay.store.canmodifyinvoices` - Required to cancel invoices when necessary

**Note:** For testing and troubleshooting, you may also want:
- `btcpay.store.webhooks.canmodifywebhooks` - For webhook management (optional)
- `btcpay.store.canviewstoresettings` - For advanced store configuration (optional)

## Development

### Project Structure
```
pow-vending-machine/
├── src/                   # Main application source code
│   ├── __init__.py
│   ├── vending_machine.py # Main application
│   ├── config.py          # Configuration settings
│   ├── lcd_display.py     # LCD controller
│   ├── mdb_controller.py  # MDB communication
│   └── btcpay_client.py   # BTCPay Server integration
├── tests/                 # Testing and simulation
│   ├── test_components.py # Component tests
│   ├── test_mac.py        # Mac compatibility tests
│   └── simulator.py       # GUI simulator
├── scripts/               # Installation and deployment
│   ├── install.sh         # Installation script
│   └── Makefile           # Build commands
├── config/                # Configuration files
│   ├── requirements.txt   # Pi dependencies
│   ├── requirements-mac.txt # Mac dependencies
│   └── env_template.txt   # Environment template
└── README.md              # Documentation
```

### Testing

Quick setup and testing:
```bash
# Mac development setup
cd scripts && make setup-mac

# Run Mac compatibility tests
cd scripts && make test-mac

# Run full simulator
cd scripts && make simulate

# Raspberry Pi setup
cd scripts && make setup

# Run component tests
cd scripts && make test
```

Individual component testing:
```bash
# Test all components
python tests/test_components.py

# Test specific components
python -c "
import sys; sys.path.insert(0, 'src')
from src.lcd_display import LCDDisplay
d = LCDDisplay(); d.initialize()
"
```

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create GitHub issue
- Check troubleshooting section
- Review log files

## Version History

- v1.0.0 - Initial release with core functionality
- Lightning Network payment integration
- MDB protocol support
- Touch screen interface

## Resources

### Bitcoin & Lightning Network
- [BTCPay Server Documentation](https://docs.btcpayserver.org/) - Payment processing server setup and API
- [Lightning Network Specifications](https://github.com/lightning/bolts) - Lightning Network protocol specifications
- [Lightning Labs Documentation](https://docs.lightning.engineering/) - Lightning Network development resources
- [Bitcoin Developer Resources](https://developer.bitcoin.org/) - Bitcoin protocol and development guides

### Hardware Documentation
- [Qibixx MDB Pi HAT Documentation](https://docs.qibixx.com/mdb-products/mdb-pi-hat-firststeps) - MDB communication setup guide
- [Waveshare 3.5" LCD Documentation](https://www.waveshare.com/wiki/3.5inch_RPi_LCD_(C)) - LCD driver installation and configuration
- [Raspberry Pi Official Documentation](https://www.raspberrypi.org/documentation/) - Complete Raspberry Pi setup guides
- [MDB Protocol Specification](https://www.coinopexpress.com/products/product_downloads/MDBVersion3.pdf) - Multi-Drop Bus protocol standard

### Development Tools
- [Python GPIO Libraries](https://gpiozero.readthedocs.io/) - Raspberry Pi GPIO control
- [PySerial Documentation](https://pyserial.readthedocs.io/) - Serial communication library
- [Pygame Documentation](https://www.pygame.org/docs/) - Graphics and display library
- [Requests Documentation](https://docs.python-requests.org/) - HTTP library for API calls

### Operating System
- [Ubuntu Server for Raspberry Pi](https://ubuntu.com/download/raspberry-pi) - Ubuntu installation for Raspberry Pi
- [Raspberry Pi OS](https://www.raspberrypi.org/software/) - Official Raspberry Pi operating system
- [Ubuntu Touch Setup Guide](https://ubuntu.com/tutorials/how-to-install-ubuntu-on-your-raspberry-pi) - Installation tutorial

### Community & Support
- [BTCPay Server Community](https://chat.btcpayserver.org/) - Support and community discussions
- [Lightning Network Community](https://discord.gg/lightningnetwork) - Lightning development community
- [Raspberry Pi Forums](https://www.raspberrypi.org/forums/) - Hardware and software support
- [Bitcoin Stack Exchange](https://bitcoin.stackexchange.com/) - Bitcoin technical Q&A

### Related Projects
- [LNBits](https://lnbits.com/) - Lightning Network wallet and payment tools
- [Raspiblitz](https://github.com/rootzoll/raspiblitz) - Bitcoin Lightning Node on Raspberry Pi
- [Umbrel](https://umbrel.com/) - Personal Bitcoin and Lightning node
- [BTCPay Server Docker](https://github.com/btcpayserver/btcpayserver-docker) - Containerized BTCPay deployment

### Vending Machine Integration
- [National Automatic Merchandising Association](https://www.vending.org/) - Vending industry standards
- [Coinco MDB Resources](https://www.coinco.com/) - MDB hardware and documentation
- [Vending Machine Manufacturers](https://www.vendingmarketwatch.com/) - Industry news and resources