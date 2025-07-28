# 🔌 MDB Interface Setup Guide

Complete guide for setting up MDB interfaces with your Raspberry Pi for the POW Vending Machine project.

This guide covers **Qibixx MDB Pi HAT** (GPIO-based), **Qibixx MDB USB Interface**, and **Hybrid Pi HAT** approaches.

## 📋 Prerequisites

- Raspberry Pi 4/5 Model B with Raspberry Pi OS
- **One of:**
  - Qibixx MDB Pi HAT v4.0.2+ (GPIO-based)
  - Qibixx MDB USB Interface (USB-based)
  - **Hybrid Pi HAT** (GPIO hardware with USB-style commands) **← YOUR SETUP**
- MDB-compatible vending machine or bill acceptor
- SD card with fresh Raspberry Pi OS installation
- SSH or direct access to the Pi

---

## 🔄 **Choose Your MDB Interface Type**

### **Option A: USB Interface**
- **Port:** `/dev/ttyACM0`
- **Baud Rate:** 115200
- **Commands:** Text-based (`V\n`, `R\n`, etc.)
- **Connection:** USB cable

### **Option B: Hybrid Pi HAT (YOUR SETUP)** ⭐
- **Port:** `/dev/ttyAMA0` (GPIO UART)  
- **Baud Rate:** 115200
- **Commands:** Text-based (`V\n`, `R\n`, etc.) **← Like USB but on GPIO**
- **Connection:** GPIO pins
- **Advantages:** Best of both worlds - GPIO control with simple text commands

### **Option C: Traditional Pi HAT**
- **Port:** `/dev/ttyAMA0`  
- **Baud Rate:** 38400 (auto-detected)
- **Commands:** Binary MDB protocol
- **Connection:** GPIO pins

---

## 🔧 Hardware Setup

### **USB Interface Setup (Option A)**

1. **Connect USB MDB Interface**
   - Connect Qibixx MDB USB Interface to Pi via USB
   - Connect MDB cable from interface to vending machine
   - Power on both devices

2. **Verify USB Connection**
   ```bash
   # Check if device appears
   ls -la /dev/ttyACM*
   
   # Should show: /dev/ttyACM0
   ```

### **Pi HAT Setup (Options B & C)**

1. **Physical Installation**
   - Power down Raspberry Pi completely
   - Mount the MDB Pi HAT on GPIO pins 1-40
   - Connect MDB cable from HAT to vending machine
   - Power up the Raspberry Pi

2. **GPIO Pin Usage**
   - **GPIO 6**: Reset control for HAT communication
   - **GPIO 14/15**: UART TX/RX (pins 8/10)
   - **Power pins**: 5V and GND from Pi

---

## ⚙️ **Raspberry Pi UART Configuration**

### **Pi and UARTs - Official Qibixx Instructions**

The MDB Pi HAT interface provides a UART which the device uses for communication. However, with recent additions to the RPi line, UART usage requires specific configuration.

⚠️ **Warning**: Older Raspbian versions work differently. Ensure you have the latest available version!

ℹ️ **Note**: Different Pi models and operating systems need specific configurations. If in doubt, use the MDB-USB Interface instead.

### **Setup Pi HAT - Raspbian/Raspberry Pi OS**

#### **Step 1: Disable Console Login on Serial Port**

**Method A: Using raspi-config (Recommended)**
```bash
sudo raspi-config
```

1. Select **Interface Options** (usually option 3)
2. Select **Serial Port** (P6)
3. **"Would you like a login shell to be accessible over serial?"** → Select **"No"**
4. **"Would you like the serial port hardware to be enabled?"** → Select **"Yes"**

**Method B: Manual Configuration**

Edit the boot command line:

⚠️ **Raspberry Pi 5**: Use `/boot/firmware/cmdline.txt`  
⚠️ **Raspberry Pi 1-4**: Use `/boot/cmdline.txt`

```bash
# For Pi 5
sudo nano /boot/firmware/cmdline.txt

# For Pi 1-4  
sudo nano /boot/cmdline.txt
```

**Remove this text** (keep the rest of the line intact):
```
console=serial0,115200
```

ℹ️ **Important**: After editing, ensure the file remains as one single line!

#### **Step 2: Disable Bluetooth Handler**

```bash
sudo systemctl disable hciuart
```

#### **Step 3: Disable Bluetooth UART Assignment**

First, check which overlay to use:
```bash
ls -la /boot/overlays/ | grep disable
```

You'll see either `disable-bt.dtbo` or `pi3-disable-bt.dtbo`. Use the filename without `.dtbo`.

Edit the boot configuration:

⚠️ **Raspberry Pi 5**: Use `/boot/firmware/config.txt`  
⚠️ **Raspberry Pi 1-4**: Use `/boot/config.txt`

```bash
# For Pi 5
sudo nano /boot/firmware/config.txt

# For Pi 1-4
sudo nano /boot/config.txt
```

**Add these lines to the end:**

**For Raspberry Pi 1, 2, 3, and 4:**
```bash
dtoverlay=disable-bt
enable_uart=1
```

**For Raspberry Pi 5:**
```bash
dtoverlay=disable-bt
enable_uart=1
dtparam=uart0=on
```

#### **Step 4: Reboot**
```bash
sudo reboot
```

✅ **Success**: After reboot, the full UART (PL011) should be connected to the Pi HAT!

---

## 🎛️ **GPIO Control Setup**

### **GPIO 6 Control Using pinctrl (Recommended)**

The MDB Pi HAT requires GPIO 6 control for proper operation. Use `pinctrl` from the `raspi-utils` package:

#### **Install pinctrl (if needed)**
```bash
sudo apt install raspi-utils
```

#### **GPIO 6 Control Commands**
```bash
# Set GPIO 6 (BCM numbering) as output and drive LOW
sudo pinctrl set 6 op dl

# Set GPIO 6 HIGH  
sudo pinctrl set 6 op dh

# Set GPIO 6 as input
sudo pinctrl set 6 ip

# Check GPIO 6 status
pinctrl get 6
```

ℹ️ **Note**: This uses BCM pin numbers directly and works on Pi 5 without sysfs issues.

---

## ⚙️ Software Configuration

### **For Hybrid Pi HAT (YOUR SETUP)** ⭐

Your setup uses a **Qibixx MDB Pi HAT** with **text-based commands** at **115200 baud** on `/dev/ttyAMA0`.

#### **Configure Environment**
Create/edit `.env` file:
```bash
nano .env
```

Add your hybrid configuration:
```bash
# Hybrid Pi HAT Configuration (GPIO + Text Commands)
MDB_SERIAL_PORT=/dev/ttyAMA0
MDB_BAUD_RATE=115200
MDB_TIMEOUT=50.0
```

#### **Set Permissions**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Logout and login again for changes to take effect
```

### **For USB Interface (Option A)**

#### **Configure Environment**
```bash
# MDB USB Interface Configuration
MDB_SERIAL_PORT=/dev/ttyACM0
MDB_BAUD_RATE=115200
MDB_TIMEOUT=50.0
```

#### **Set Permissions**
```bash
sudo usermod -a -G dialout $USER
```

### **For Traditional Pi HAT (Option C)**

Follow the same UART setup steps above, then:

```bash
# Traditional Pi HAT Configuration
MDB_SERIAL_PORT=/dev/ttyAMA0
MDB_BAUD_RATE=38400
MDB_TIMEOUT=1.0
```

---

## 🧪 **Testing and Verification**

### **Step 1: Verify UART Device Exists**

After UART configuration and reboot:
```bash
ls -la /dev/ttyAMA*
```

You should see:
```
crw-rw---- 1 root dialout 204, 64 [date] /dev/ttyAMA0
```

### **Step 2: Test with Minicom (Official Method)**

**Install minicom:**
```bash
sudo apt-get install minicom
```

**Test the interface:**
```bash
sudo minicom -b 115200 -D /dev/ttyAMA0
```

**Enable local echo** (to see what you type):
- Press `CTRL+A` then `Z` then `E`

**Send test command:**
- Type `V` and press `Enter`
- You should see response like: `v,4.0.2.0,7de04655363231164c343132`

**Exit minicom:**
- Press `CTRL+A` then `X`

### **Step 3: Set GPIO 6 Control**

**Initialize GPIO 6 for HAT communication:**
```bash
# Set GPIO 6 as output and drive high (initialize HAT)
sudo pinctrl set 6 op dh

# Verify setting
pinctrl get 6
```

### **Step 4: Test Again with Minicom**

Repeat the minicom test to ensure HAT communication is working properly.

### **Step 5: Test Your Hybrid Pi HAT Setup** ⭐

Your device should now be working! Run these tests:

#### **Quick Test (User's Exact Method)**
```bash
cd ~/pow-vending-machine
source venv/bin/activate
python tests/simple_usb_mdb_test.py
```

**Expected output:**
```
Version: v,4.0.2.0,7de04655363231164c343132
✓ SUCCESS: MDB interface is working!
```

#### **Comprehensive Test**
```bash
python tests/mdb_usb_test.py
```

**Expected output:**
```
🎉 All tests passed! Hybrid MDB Pi HAT is working correctly.
```

### **Test USB Interface**

Run the USB-specific test:
```bash
cd ~/pow-vending-machine
source venv/bin/activate
python tests/mdb_usb_test.py
```

### **Test Traditional Pi HAT**

Run the HAT-specific test:
```bash
python tests/mdb_troubleshoot.py
```

### **Test Main Controller**

Test the updated MDB controller:
```bash
python tests/test_mdb.py
```

---

## 🔍 **Serial Interface Parameters**

The MDB Pi HAT communicates using these parameters:
- **Baudrate**: 115200
- **Parity**: None  
- **Data Bits**: 8
- **Stop Bits**: 1

---

## 📊 **Understanding the Differences**

| Feature | USB Interface | Hybrid Pi HAT | Traditional Pi HAT |
|---------|---------------|---------------|-------------------|
| **Connection** | `/dev/ttyACM0` | `/dev/ttyAMA0` | `/dev/ttyAMA0` |
| **Baud Rate** | 115200 | 115200 | 38400 (adaptive) |
| **Commands** | Text (`V\n`) | Text (`V\n`) | Binary (`0x01`) |
| **Setup Complexity** | Low | Medium | High |
| **GPIO Requirements** | None | UART + GPIO6 | UART + GPIO6 |
| **Response Format** | ASCII text | ASCII text | Binary data |

### **Command Examples**

**USB Interface & Hybrid Pi HAT:**
```python
import serial
ser = serial.Serial('/dev/ttyAMA0', 115200, timeout=50)
ser.write(b'V\n')  # Version command
response = ser.readline().decode('ascii')
```

**Traditional Pi HAT:**
```python
import serial
ser = serial.Serial('/dev/ttyAMA0', 38400, timeout=1)
ser.write(b'\x01')  # SETUP command
response = ser.read(100)  # Binary response
```

---

## 🚨 Troubleshooting

### **UART Issues**

**Problem: `No such file or directory: '/dev/ttyAMA0'`**
1. Check UART is enabled in boot config
2. Verify Bluetooth is disabled  
3. Reboot the Pi
4. Check device exists: `ls -la /dev/ttyAMA*`

**Problem: `Permission denied`**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Check permissions
ls -la /dev/ttyAMA0

# Logout and login again
```

### **GPIO Issues**

**Problem: GPIO 6 control fails**
```bash
# Install raspi-utils if needed
sudo apt install raspi-utils

# Set GPIO 6 high
sudo pinctrl set 6 op dh

# Check status
pinctrl get 6
```

### **Pi HAT Issues**

**Problem: `No response from device`**
- Check GPIO6 control with `pinctrl`
- Verify UART configuration
- Test with minicom first
- Ensure HAT is properly seated

**Problem: `Bluetooth interference`**
- Disable Bluetooth services: `sudo systemctl disable hciuart`
- Check `/boot/firmware/config.txt` for `dtoverlay=disable-bt`

---

## ✅ **Quick Start Checklist**

### **USB Interface** ✅
- [ ] USB MDB device connected and visible at `/dev/ttyACM0`
- [ ] User added to `dialout` group
- [ ] Environment configured with `MDB_SERIAL_PORT=/dev/ttyACM0`
- [ ] Test passes: `python tests/mdb_usb_test.py`

### **Hybrid Pi HAT** ✅  
- [ ] HAT physically mounted on GPIO pins
- [ ] UART enabled in boot config
- [ ] Bluetooth disabled
- [ ] Serial console removed from cmdline.txt
- [ ] GPIO 6 control working: `sudo pinctrl set 6 op dh`
- [ ] Minicom test successful: `sudo minicom -b 115200 -D /dev/ttyAMA0`
- [ ] Test passes: `python tests/simple_usb_mdb_test.py`

### **Traditional Pi HAT** ✅  
- [ ] Same UART setup as Hybrid
- [ ] GPIO6 accessible
- [ ] Test passes: `python tests/mdb_troubleshoot.py`

---

## 🚀 Next Steps

Once MDB setup is complete:

1. **Test Full System**: `python main.py`
2. **Configure BTCPay**: Set up payment processing
3. **Test Vending Operations**: Try coin insertion and vending
4. **Monitor Logs**: Watch `logs/vending_machine.log`

The Hybrid Pi HAT approach is **recommended** for new installations due to its combination of GPIO control and simple text-based commands. 