# 🔌 MDB Pi HAT Setup Guide

Complete guide for setting up the Qibixx MDB Pi HAT with your Raspberry Pi 4 for the POW Vending Machine project.

## 📋 Prerequisites

- Raspberry Pi 4 Model B with Raspberry Pi OS
- Qibixx MDB Pi HAT v4.0.2+ 
- MDB-compatible vending machine or bill acceptor
- SD card with fresh Raspberry Pi OS installation
- SSH or direct access to the Pi

---

## 🔧 Hardware Setup

### 1. **Physical Installation**

1. **Power down** your Raspberry Pi completely
2. **Mount the MDB Pi HAT** on GPIO pins 1-40
3. **Connect MDB cable** from HAT to your vending machine/bill acceptor
4. **Power up** the Raspberry Pi

### 2. **GPIO Pin Usage**

The Qibixx MDB Pi HAT uses:
- **GPIO 6**: Reset control for HAT communication
- **GPIO 14/15**: UART TX/RX (pins 8/10)
- **Power pins**: 5V and GND from Pi

⚠️ **Important**: Do not connect other devices to GPIO 6, 14, or 15 while using the MDB HAT.

---

## ⚙️ Raspberry Pi Configuration

### 1. **Enable UART Communication**

Edit the boot configuration:
```bash
sudo nano /boot/firmware/config.txt
```

Add these lines (or verify they exist):
```bash
# Enable UART for MDB HAT
enable_uart=1
dtparam=uart=on
dtparam=uart0=on

# Disable Bluetooth to free up UART
dtoverlay=disable-bt

# For Raspberry Pi 4, explicitly enable UART
dtoverlay=uart0

# Enable SPI for potential LCD use
dtparam=spi=on

# Optional: Increase GPU memory
gpu_mem=128
```

### 2. **Disable Serial Console**

Remove serial console from boot parameters:
```bash
sudo nano /boot/firmware/cmdline.txt
```

Remove these parts if present:
```bash
console=serial0,115200 console=ttyAMA0,115200
```

### 3. **Disable Bluetooth Services**

```bash
# Disable Bluetooth services
sudo systemctl disable hciuart
sudo systemctl disable bluetooth

# Stop them immediately
sudo systemctl stop hciuart
sudo systemctl stop bluetooth
```

### 4. **Configure GPIO Access**

Add your user to the GPIO group:
```bash
sudo usermod -a -G dialout,gpio $USER
```

### 5. **Reboot**

```bash
sudo reboot
```

---

## 🖥️ Software Configuration

### 1. **Verify UART Device**

After reboot, check that the UART device exists:
```bash
ls -la /dev/ttyAMA*
```

You should see:
```
crw-rw---- 1 root dialout 204, 64 [date] /dev/ttyAMA0
```

### 2. **Install Project Dependencies**

```bash
cd ~/pow-vending-machine
pip install -r requirements.txt
```

### 3. **Configure Environment**

Create/edit `.env` file:
```bash
nano .env
```

Add MDB configuration:
```bash
# MDB Configuration
MDB_SERIAL_PORT=/dev/ttyAMA0
MDB_BAUD_RATE=38400
MDB_TIMEOUT=1.0
MDB_RETRIES=3
```

**Note**: The software now automatically detects the correct baud rate (38400, 19200, or 9600) based on HAT state.

---

## 🧪 Testing and Verification

### 1. **Hardware Detection Test**

Run the comprehensive hardware test:
```bash
cd ~/pow-vending-machine
source venv/bin/activate
python tests/mdb_troubleshoot.py
```

**Expected output:**
```
🎉 MDB DEVICE DETECTED AND RESPONDING!
✓ SUCCESS: MDB device is communicating properly
```

### 2. **MDB Controller Test**

Test the main MDB controller:
```bash
python tests/test_mdb.py
```

**Expected output:**
```
✓ Qibixx MDB Pi Hat initialized successfully at [XXXX] baud
✓ PASS: MDB Initialization
```

### 3. **Pi HAT Updater Test**

Test the Qibixx updater tool:
```bash
cd ~/Desktop
sudo ./pihatupdater
```

**Expected output:**
```
Current Version: v,4.0.2.0,[firmware_hash]
```

---

## 🔄 Understanding Baud Rate Behavior

### **Why Different Baud Rates?**

The Qibixx MDB Pi HAT operates in different communication modes depending on its internal state:

| HAT State | Baud Rate | Commands That Respond |
|-----------|-----------|----------------------|
| **Fresh Boot** | 38400 | SETUP → `000000` |
| **Active Mode** | 19200 | EXPANSION → `0000` |
| **Standard MDB** | 9600 | RESET, POLL → `0000` |

### **Adaptive Detection**

Our software automatically:
1. **Tests multiple baud rates** (38400 → 19200 → 9600)
2. **Tries multiple commands** (SETUP, POLL, RESET, EXPANSION)
3. **Switches to working configuration** automatically
4. **Logs the successful connection** for debugging

---

## 🚨 Troubleshooting

### **Problem: `/dev/ttyAMA0: no such file or directory`**

**Solution:**
1. Check UART is enabled in `/boot/firmware/config.txt`
2. Verify Bluetooth is disabled
3. Reboot the Pi
4. Check device exists: `ls -la /dev/ttyAMA*`

### **Problem: `Permission denied` accessing serial port**

**Solution:**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Check permissions
ls -la /dev/ttyAMA0

# Logout and login again
```

### **Problem: `open /sys/class/gpio/gpio6/value: no such file or directory`**

**Solutions:**

**Option 1 - Export GPIO6:**
```bash
echo "518" | sudo tee /sys/class/gpio/export  # GPIO6 = 512 + 6 = 518
echo "out" | sudo tee /sys/class/gpio/gpio518/direction
echo "1" | sudo tee /sys/class/gpio/gpio518/value
```

**Option 2 - Use modern GPIO tools:**
```bash
# Install GPIO tools
sudo apt install gpiod

# Set GPIO6 high
gpioset gpiochip0 6=1
```

### **Problem: MDB tests still run in simulation mode**

**Diagnostic steps:**
1. Run `python tests/mdb_troubleshoot.py` to verify hardware
2. Check if any responses are received at any baud rate
3. Verify HAT power and connections
4. Check for GPIO conflicts

### **Problem: Inconsistent responses at different times**

**This is normal!** The HAT changes communication modes. Our adaptive detection handles this automatically.

### **Problem: Pi HAT updater shows old version**

**Solution:**
```bash
# Update HAT firmware
sudo ./pihatupdater

# If GPIO6 error, set it first:
gpioset gpiochip0 6=1 &
sudo ./pihatupdater
```

---

## 📊 Monitoring and Debugging

### **Check Real-time Communication**

Monitor MDB communication:
```bash
# Watch MDB controller logs
tail -f logs/vending_machine.log | grep mdb_controller

# Test specific commands
python -c "
import serial
ser = serial.Serial('/dev/ttyAMA0', 38400, timeout=1)
ser.write(b'\\x01')  # SETUP command
response = ser.read(100)
print(f'Response: {response.hex()}')
ser.close()
"
```

### **GPIO Status Check**

```bash
# Check GPIO status
cat /sys/kernel/debug/gpio | grep -A5 -B5 "GPIO6"

# Check UART status  
dmesg | grep -i uart

# Check for conflicts
lsof /dev/ttyAMA0
```

---

## ✅ Success Checklist

- [ ] `/dev/ttyAMA0` device exists and is accessible
- [ ] `mdb_troubleshoot.py` shows "MDB DEVICE DETECTED AND RESPONDING!"
- [ ] `test_mdb.py` shows "MDB Initialization ✓ PASS" (not simulation)
- [ ] Pi HAT updater shows current firmware version
- [ ] GPIO6 can be controlled (no permission errors)
- [ ] No Bluetooth interference (services disabled)
- [ ] MDB controller auto-detects correct baud rate

---

## 🚀 Next Steps

Once MDB setup is complete:

1. **Test Full System**: `python main.py`
2. **Configure BTCPay**: Set up payment processing
3. **Test Vending Operations**: Try coin insertion and vending
4. **Monitor Logs**: Watch `logs/vending_machine.log`

---

## 📞 Support

If you encounter issues not covered here:

1. **Check logs**: `tail -f logs/vending_machine.log`
2. **Run diagnostics**: `python tests/mdb_troubleshoot.py`
3. **Verify connections**: Physical and software configuration
4. **Update firmware**: Use latest Pi HAT updater

The adaptive baud rate detection should handle most communication issues automatically. If problems persist, the issue is likely hardware-related (connections, power, or HAT malfunction). 