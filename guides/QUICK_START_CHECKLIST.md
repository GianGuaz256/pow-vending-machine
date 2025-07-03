# Quick Start Checklist - Bitcoin Lightning Vending Machine

## Pre-Assembly Checklist

### ✅ Components Received
- [ ] Raspberry Pi 5 8GB (with heatsink/fan recommended)
- [ ] Waveshare 3.5" Touch Screen LCD (320x480)
- [ ] Qibixx MDB Pi HAT
- [ ] 27W USB-C PD Power Supply
- [ ] 32GB+ MicroSD Card (Class 10+)
- [ ] MDB cable (from vending machine)
- [ ] Jumper wires (male-female, female-female)
- [ ] Ethernet cable or WiFi credentials

### ✅ Tools Needed
- [ ] Computer with SD card reader
- [ ] Micro HDMI to HDMI cable (for initial setup)
- [ ] USB keyboard and mouse (for initial setup)
- [ ] Multimeter (for testing voltages)
- [ ] Small screwdriver set
- [ ] Anti-static wrist strap (recommended)

## Step-by-Step Assembly

### 🖥️ Step 1: Prepare Raspberry Pi (45 minutes)

#### Initial OS Setup
- [ ] **1.1** Flash Ubuntu Server 24.04 LTS (64-bit) to SD card using Raspberry Pi Imager
- [ ] **1.2** During imaging, enable SSH with username/password
- [ ] **1.3** Set username: `ubuntu` (or preferred name) and strong password
- [ ] **1.4** **DO NOT configure WiFi yet** (we'll do this via SSH)

#### Headless SSH Setup (No Monitor/Keyboard Needed)
- [ ] **1.5** Connect your laptop to WiFi network (WiFi-X)
- [ ] **1.6** Connect Raspberry Pi to ethernet cable (with internet)
- [ ] **1.7** Insert SD card and boot Pi (wait 2-3 minutes)
- [ ] **1.8** Find Pi's IP: `nmap -sn 192.168.1.0/24` or check router admin
- [ ] **1.9** SSH to Pi: `ssh ubuntu@192.168.1.XXX`

#### Configure WiFi via SSH
- [ ] **1.10** Configure WiFi: `sudo nmtui`
  - [ ] Select "Activate a connection"
  - [ ] Choose WiFi-X network
  - [ ] Enter WiFi password
  - [ ] Select "Activate" and exit
- [ ] **1.11** Verify WiFi: `ip addr show wlan0` (note the IP address)
- [ ] **1.12** Test internet: `ping 8.8.8.8`

#### Switch to WiFi-Only
- [ ] **1.13** Restart network: `sudo systemctl restart NetworkManager`
- [ ] **1.14** Unplug ethernet cable (wait 30 seconds first)
- [ ] **1.15** Reboot Pi: `sudo reboot`
- [ ] **1.16** Reconnect via WiFi: `ssh ubuntu@WIFI_IP_ADDRESS`

#### System Updates and Interfaces
- [ ] **1.17** Update system: `sudo apt update && sudo apt upgrade -y`
- [ ] **1.18** Enable SPI: `echo "dtparam=spi=on" | sudo tee -a /boot/firmware/config.txt`
- [ ] **1.19** Enable UART: `echo "enable_uart=1" | sudo tee -a /boot/firmware/config.txt`
- [ ] **1.20** Disable Bluetooth: `echo "dtoverlay=disable-bt" | sudo tee -a /boot/firmware/config.txt`
- [ ] **1.21** Install packages: `sudo apt install -y python3-pip python3-venv python3-dev python3-rpi.gpio git build-essential`
- [ ] **1.22** Add user to groups: `sudo usermod -a -G dialout,spi,i2c,gpio $USER`
- [ ] **1.23** Reboot Pi: `sudo reboot`

### 🔌 Step 2: Install MDB Pi HAT (15 minutes)

⚠️ **POWER OFF THE PI FIRST**: `sudo shutdown -h now`

- [ ] **2.1** Disconnect power from Raspberry Pi
- [ ] **2.2** Ground yourself with anti-static strap
- [ ] **2.3** Align MDB HAT with GPIO header (all 40 pins)
- [ ] **2.4** Press HAT down firmly and evenly
- [ ] **2.5** Secure with provided standoffs/screws
- [ ] **2.6** Verify HAT is seated properly (no bent pins)

### 📺 Step 3: Connect LCD Display (20 minutes)

Choose your connection method:

#### Method A: Using HAT Passthrough (if available)
- [ ] **3.1** Check if MDB HAT has GPIO passthrough pins on top
- [ ] **3.2** Connect LCD directly to passthrough pins using this mapping:
  - [ ] LCD VCC → HAT 3.3V pin
  - [ ] LCD GND → HAT GND pin  
  - [ ] LCD DIN → HAT GPIO 10 (Pin 19)
  - [ ] LCD CLK → HAT GPIO 11 (Pin 23)
  - [ ] LCD CS → HAT GPIO 8 (Pin 24)
  - [ ] LCD DC → HAT GPIO 24 (Pin 18)
  - [ ] LCD RST → HAT GPIO 25 (Pin 22)
  - [ ] LCD BL → HAT GPIO 18 (Pin 12)

#### Method B: Using Jumper Wires (if no passthrough)
- [ ] **3.1** Use female-to-female jumper wires
- [ ] **3.2** Connect to accessible pins on HAT sides/back
- [ ] **3.3** Use same pin mapping as Method A
- [ ] **3.4** Secure wires to prevent disconnection

### 🔧 Step 4: Configure System (15 minutes)

- [ ] **4.1** Reconnect via SSH if needed: `ssh ubuntu@WIFI_IP_ADDRESS`
- [ ] **4.2** Edit boot configuration: `sudo nano /boot/firmware/config.txt`
- [ ] **4.3** Verify/add these lines (some may already exist from Step 1):
```ini
# Enable SPI for LCD
dtparam=spi=on

# Enable UART for MDB
enable_uart=1
dtparam=uart=on

# Disable Bluetooth to free up UART
dtoverlay=disable-bt

# LCD Configuration
dtoverlay=spi0-1cs,cs0_pin=8
dtparam=cs0_spidev=on

# Increase GPU memory
gpu_mem=128
```
- [ ] **4.4** Save and exit (`Ctrl+X`, then `Y`, then `Enter`)
- [ ] **4.5** Check cmdline: `cat /boot/firmware/cmdline.txt` (should NOT contain `console=serial0,115200`)
- [ ] **4.6** If serial console present, remove it: `sudo sed -i 's/console=serial0,115200 //' /boot/firmware/cmdline.txt`
- [ ] **4.7** Reboot: `sudo reboot`

### 🧪 Step 5: Test Hardware (10 minutes)

#### Test MDB Communication
- [ ] **5.1** Check MDB device exists: `ls -la /dev/ttyAMA*`
- [ ] **5.2** Should see `/dev/ttyAMA0`
- [ ] **5.3** Test permissions: `groups` (should include `dialout`)
- [ ] **5.4** If not in dialout: `sudo usermod -a -G dialout $USER` then logout/login

#### Test LCD Display  
- [ ] **5.5** Check SPI device: `ls -la /dev/spi*`
- [ ] **5.6** Should see `/dev/spidev0.0`
- [ ] **5.7** Test SPI: 
```bash
sudo python3 -c "
import spidev
spi = spidev.SpiDev()
spi.open(0, 0)
print('✓ SPI working!')
spi.close()
"
```

### 📦 Step 6: Install Software (20 minutes)

- [ ] **6.1** Clone repository: `git clone <your-repo-url>`
- [ ] **6.2** Navigate to project: `cd pow-vending-machine`
- [ ] **6.3** Run installer: `cd scripts && chmod +x install.sh && ./install.sh`
- [ ] **6.4** Wait for installation to complete (will take 10-15 minutes)

### ⚙️ Step 7: Configure Application (10 minutes)

- [ ] **7.1** Copy environment template: `cp config/env_template.txt .env`
- [ ] **7.2** Edit configuration: `nano .env`
- [ ] **7.3** Fill in BTCPay Server details:
  - [ ] `BTCPAY_SERVER_URL=https://your-btcpay-server.com`
  - [ ] `BTCPAY_STORE_ID=your-store-id`
  - [ ] `BTCPAY_API_KEY=your-api-key`
  - [ ] `BTCPAY_WEBHOOK_SECRET=your-webhook-secret`
- [ ] **7.4** Verify hardware settings:
  - [ ] `MDB_SERIAL_PORT=/dev/ttyAMA0`
  - [ ] `DISPLAY_WIDTH=320`
  - [ ] `DISPLAY_HEIGHT=480`
- [ ] **7.5** Save and exit

### 🧪 Step 8: Test Installation (10 minutes)

- [ ] **8.1** Activate virtual environment: `source venv/bin/activate`
- [ ] **8.2** Test components: `python tests/test_components.py`
- [ ] **8.3** Expected results:
  - [ ] ✓ Configuration loaded
  - [ ] ✓ MDB device detected  
  - [ ] ✓ SPI interface working
  - [ ] ✓ LCD display initialized
- [ ] **8.4** If any failures, check connections and repeat previous steps

### 🚀 Step 9: Run Application (5 minutes)

#### Option A: Manual Test
- [ ] **9.1** Run manually: `python main.py`
- [ ] **9.2** Check display shows "Initializing..." then "Ready"
- [ ] **9.3** Verify no error messages in console
- [ ] **9.4** Stop with `Ctrl+C`

#### Option B: Service Mode (Production)
- [ ] **9.1** Enable service: `sudo systemctl enable bitcoin-vending.service`
- [ ] **9.2** Start service: `sudo systemctl start bitcoin-vending.service`
- [ ] **9.3** Check status: `sudo systemctl status bitcoin-vending.service`
- [ ] **9.4** Monitor logs: `tail -f /var/log/vending_machine.log`

### 🔌 Step 10: Connect to Vending Machine (10 minutes)

⚠️ **Only do this step when ready for production use**

- [ ] **10.1** Ensure vending machine is powered off
- [ ] **10.2** Connect MDB cable from vending machine to MDB connector on HAT
- [ ] **10.3** Verify cable polarity (check vending machine manual)
- [ ] **10.4** Power on vending machine
- [ ] **10.5** Check for 24V power with multimeter (optional but recommended)
- [ ] **10.6** Power on Pi and test communication

## Troubleshooting Quick Checks

### ❌ SSH Connection Issues
- [ ] Wait 3-5 minutes after Pi boots
- [ ] Check Pi has ethernet connection and link light
- [ ] Scan for Pi IP: `nmap -sn 192.168.1.0/24`
- [ ] Try password auth: `ssh -o PreferredAuthentications=password ubuntu@IP`
- [ ] Check router admin panel for "ubuntu" device

### ❌ Pi Won't Boot
- [ ] Check power supply (must be 27W for Pi 5)
- [ ] Check SD card is properly inserted
- [ ] Try different HDMI cable/monitor (if not headless)
- [ ] Re-flash SD card with correct Ubuntu image

### ❌ MDB Not Working  
- [ ] Check `/dev/ttyAMA*` exists
- [ ] Verify user in `dialout` group
- [ ] Check UART enabled in `/boot/config.txt`
- [ ] Test with multimeter for 24V from vending machine

### ❌ LCD Not Working
- [ ] Check all SPI connections (8 wires total)
- [ ] Verify SPI enabled: `ls /dev/spi*`
- [ ] Check power connections (3.3V, GND)
- [ ] Test with multimeter for voltage on LCD pins

### ❌ Software Errors
- [ ] Check Python virtual environment is activated
- [ ] Verify all dependencies installed: `pip list`
- [ ] Check log files: `tail -f /var/log/vending_machine.log`
- [ ] Check service status: `systemctl status bitcoin-vending.service`

## Essential Commands Reference

```bash
# SSH connection (replace with your WiFi IP)
ssh ubuntu@192.168.1.XXX

# Check hardware
ls /dev/ttyAMA* /dev/spi*

# Network troubleshooting
ip addr show
sudo nmtui
sudo systemctl restart NetworkManager

# Monitor logs  
tail -f /var/log/vending_machine.log

# Control service
sudo systemctl start bitcoin-vending.service
sudo systemctl stop bitcoin-vending.service
sudo systemctl status bitcoin-vending.service

# Test components
source venv/bin/activate
python tests/test_components.py

# Manual run
python main.py
```

## Expected Timeline

- **Total setup time**: 2.5-3.5 hours for first-time headless setup
- **Experienced setup**: 60-90 minutes
- **SSH setup portion**: 20-30 minutes
- **Testing and troubleshooting**: Additional 30-60 minutes

## Success Indicators

### ✅ System Ready When:
- [ ] LCD displays "Bitcoin Vending Machine" and "Ready"
- [ ] No error messages in logs
- [ ] MDB communication established (if connected to vending machine)
- [ ] BTCPay Server connection successful
- [ ] Service runs without crashes for 10+ minutes

### 🎉 Congratulations! 
Your Bitcoin Lightning Vending Machine is now ready for operation!

---

**Need Help?** 
- Check the detailed `HARDWARE_SETUP.md` guide
- Review logs: `tail -f /var/log/vending_machine.log`
- Test individual components: `python tests/test_components.py` 