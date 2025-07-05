# Installation Guide

Simple setup guide for Bitcoin Lightning Vending Machine on Raspberry Pi.

## Requirements

- Raspberry Pi with fresh Raspberry Pi OS
- Waveshare 3.5" LCD (B v2 or similar)
- Qibixx MDB Pi HAT
- Internet connection

## Installation

### Step 1: Clone and Setup

```bash
git clone [your-repo-url] pow-vending-machine
cd pow-vending-machine
chmod +x setup.sh
./setup.sh
```

### Step 2: Reboot

```bash
sudo reboot
```

### Step 3: Install LCD Driver

After reboot:

```bash
git clone https://github.com/waveshare/LCD-show.git
cd LCD-show
chmod +x LCD35B-show-V2
sudo ./LCD35B-show-V2
```

Note: Use `LCD35C-show` for C version, or check LCD-show folder for your model.

The Pi will reboot again automatically.

### Step 4: Configure

After LCD reboot:

```bash
cd pow-vending-machine
nano .env
```

Add your BTCPay Server details:
- BTCPAY_URL=https://your-btcpay-server.com
- BTCPAY_API_KEY=your-api-key
- STORE_ID=your-store-id

### Step 5: Run

```bash
source venv/bin/activate
python main.py
```

## Troubleshooting

### LCD Issues on 64-bit OS

If LCD installation fails with architecture errors, the setup script already handles this. If you still have issues:

```bash
sudo dpkg --add-architecture armhf
sudo apt update
sudo apt --fix-broken install
```

### Serial Port Access

If you get permission errors:

```bash
# Log out and back in, or:
newgrp dialout
```

### LCD Not Displaying

Check if LCD is detected:
```bash
ls /dev/fb*  # Should show fb0 and fb1
```

If pygame can't find display:
```bash
export SDL_FBDEV=/dev/fb1
```

## That's it!

Your vending machine should now be running with the LCD display and MDB board ready to accept Lightning payments. 