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

### **Pi HAT Setup (Option B)**

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

## ⚙️ Software Configuration

### **For Hybrid Pi HAT (YOUR SETUP)** ⭐

Your setup uses a **Qibixx MDB Pi HAT** with **text-based commands** at **115200 baud** on `/dev/ttyAMA0`.

#### 1. **Enable UART Communication**
Edit the boot configuration:
```bash
sudo nano /boot/firmware/config.txt
```

Add these lines:
```bash
# Enable UART for MDB HAT
enable_uart=1
dtparam=uart=on
dtparam=uart0=on

# Disable Bluetooth to free up UART
dtoverlay=disable-bt
dtoverlay=uart0
```

#### 2. **Disable Serial Console**
```bash
sudo nano /boot/firmware/cmdline.txt
```

Remove these parts if present:
```bash
console=serial0,115200 console=ttyAMA0,115200
```

#### 3. **Configure Environment**
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

#### 4. **Set Permissions**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Logout and login again for changes to take effect
```

#### 5. **Reboot**
```bash
sudo reboot
```

### **For USB Interface (Option A)**

#### 1. **Install Dependencies**
```bash
cd ~/pow-vending-machine
pip install -r requirements.txt
```

#### 2. **Configure Environment**
Create/edit `.env` file:
```bash
nano .env
```

Add USB MDB configuration:
```bash
# MDB USB Interface Configuration
MDB_SERIAL_PORT=/dev/ttyACM0
MDB_BAUD_RATE=115200
MDB_TIMEOUT=50.0
```

#### 3. **Set Permissions**
```bash
# Add user to dialout group for USB access
sudo usermod -a -G dialout $USER

# Logout and login again for changes to take effect
```

### **For Traditional Pi HAT (Option C)**

---

## 🧪 Testing and Verification

### **Test Your Hybrid Pi HAT Setup** ⭐

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
🎉 All tests passed! MDB interface is working correctly.
```

#### **Manual Test with Minicom**
```bash
sudo minicom -b 115200 -D /dev/ttyAMA0
```

Type `V` and press Enter. You should see:
```
v,4.0.2.0,7de04655363231164c343132
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

## 📊 **Understanding the Differences**

| Feature | USB Interface | Pi HAT |
|---------|---------------|---------|
| **Connection** | `/dev/ttyACM0` | `/dev/ttyAMA0` |
| **Baud Rate** | 115200 | 38400 (adaptive) |
| **Commands** | Text (`V\n`) | Binary (`0x01`) |
| **Setup Complexity** | Low | Medium |
| **GPIO Requirements** | None | UART + GPIO6 |
| **Response Format** | ASCII text | Binary data |

### **Command Examples**

**USB Interface:**
```python
import serial
ser = serial.Serial('/dev/ttyACM0', 115200, timeout=50)
ser.write(b'V\n')  # Version command
response = ser.readline().decode('ascii')
```

**Pi HAT:**
```python
import serial
ser = serial.Serial('/dev/ttyAMA0', 38400, timeout=1)
ser.write(b'\x01')  # SETUP command
response = ser.read(100)  # Binary response
```

---

## 🚨 Troubleshooting

### **USB Interface Issues**

**Problem: `No such file or directory: '/dev/ttyACM0'`**
```bash
# Check available USB devices
ls -la /dev/ttyACM*
ls -la /dev/ttyUSB*

# Check USB connections
lsusb
```

**Problem: `Permission denied`**
```bash
# Add user to dialout group
sudo usermod -a -G dialout $USER

# Check permissions
ls -la /dev/ttyACM0

# Logout and login again
```

### **Pi HAT Issues**

**Problem: `No response from device`**
- Check GPIO6 control
- Verify UART configuration
- Test different baud rates (38400, 19200, 9600)

**Problem: `Bluetooth interference`**
- Disable Bluetooth services
- Check `/boot/firmware/config.txt`

---

## ✅ **Quick Start Checklist**

### **USB Interface** ✅
- [ ] USB MDB device connected and visible at `/dev/ttyACM0`
- [ ] User added to `dialout` group
- [ ] Environment configured with `MDB_SERIAL_PORT=/dev/ttyACM0`
- [ ] Test passes: `python tests/mdb_usb_test.py`

### **Pi HAT** ✅  
- [ ] HAT physically mounted on GPIO pins
- [ ] UART enabled in `/boot/firmware/config.txt`
- [ ] Bluetooth disabled
- [ ] Serial console removed from cmdline.txt
- [ ] GPIO6 accessible
- [ ] Test passes: `python tests/mdb_troubleshoot.py`

---

## 🚀 Next Steps

Once MDB setup is complete:

1. **Test Full System**: `python main.py`
2. **Configure BTCPay**: Set up payment processing
3. **Test Vending Operations**: Try coin insertion and vending
4. **Monitor Logs**: Watch `logs/vending_machine.log`

The new USB interface approach is **recommended** for new installations due to its simplicity and reliability. 