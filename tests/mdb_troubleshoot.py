#!/usr/bin/env python3
"""
MDB Hardware Troubleshooting Script for Raspberry Pi 5 + MDB Pi Hat
Comprehensive diagnosis of MDB connection issues
"""
import serial
import time
import logging
import os
import sys
import subprocess
import glob

# Enhanced logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mdb_troubleshoot.log')
    ]
)
logger = logging.getLogger(__name__)

def check_raspberry_pi_info():
    """Check Raspberry Pi model and OS info"""
    logger.info("="*60)
    logger.info("RASPBERRY PI SYSTEM INFORMATION")
    logger.info("="*60)
    
    try:
        # Check Pi model
        with open('/proc/device-tree/model', 'r') as f:
            pi_model = f.read().strip('\x00')
        logger.info(f"Raspberry Pi Model: {pi_model}")
        
        # Check OS info
        with open('/etc/os-release', 'r') as f:
            os_info = f.read()
        for line in os_info.split('\n'):
            if line.startswith('PRETTY_NAME='):
                os_name = line.split('=')[1].strip('"')
                logger.info(f"Operating System: {os_name}")
                break
        
        # Check kernel version
        kernel_version = subprocess.check_output(['uname', '-r']).decode().strip()
        logger.info(f"Kernel Version: {kernel_version}")
        
    except Exception as e:
        logger.warning(f"Could not get system info: {e}")

def check_mdb_hat_detection():
    """Check if MDB Pi Hat is detected"""
    logger.info("="*60)
    logger.info("MDB PI HAT DETECTION")
    logger.info("="*60)
    
    # Check I2C devices (MDB hats often use I2C)
    try:
        result = subprocess.run(['i2cdetect', '-y', '1'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info("I2C Bus 1 devices:")
            logger.info(result.stdout)
        else:
            logger.warning("Could not scan I2C bus")
    except Exception as e:
        logger.warning(f"I2C detection failed: {e}")
    
    # Check USB devices
    try:
        result = subprocess.run(['lsusb'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            logger.info("USB devices:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    logger.info(f"  {line}")
        
        # Look for MDB-specific USB devices
        usb_devices = result.stdout.lower()
        if 'mdb' in usb_devices or 'vending' in usb_devices:
            logger.info("✓ Potential MDB device found in USB devices")
        else:
            logger.warning("✗ No obvious MDB device found in USB devices")
            
    except Exception as e:
        logger.warning(f"USB detection failed: {e}")

def check_serial_configuration():
    """Check serial port configuration"""
    logger.info("="*60)
    logger.info("SERIAL PORT CONFIGURATION")
    logger.info("="*60)
    
    # Check if serial is enabled in raspi-config
    try:
        with open('/boot/config.txt', 'r') as f:
            config_content = f.read()
        
        if 'enable_uart=1' in config_content:
            logger.info("✓ UART is enabled in /boot/config.txt")
        else:
            logger.warning("✗ UART may not be enabled - check /boot/config.txt")
            
        if 'dtoverlay=disable-bt' in config_content:
            logger.info("✓ Bluetooth is disabled (good for serial)")
        else:
            logger.warning("✗ Bluetooth may be interfering with serial - consider disabling")
            
    except Exception as e:
        logger.warning(f"Could not check /boot/config.txt: {e}")
    
    # Check cmdline.txt for console settings
    try:
        with open('/boot/cmdline.txt', 'r') as f:
            cmdline = f.read().strip()
        
        if 'console=serial0' in cmdline or 'console=ttyAMA0' in cmdline:
            logger.warning("✗ Serial console is enabled - this may interfere with MDB")
            logger.warning("  Consider removing console=serial0,115200 from /boot/cmdline.txt")
        else:
            logger.info("✓ Serial console appears to be disabled")
            
    except Exception as e:
        logger.warning(f"Could not check /boot/cmdline.txt: {e}")

def check_all_serial_ports():
    """Comprehensively check all available serial ports"""
    logger.info("="*60)
    logger.info("COMPREHENSIVE SERIAL PORT SCAN")
    logger.info("="*60)
    
    # Find all potential serial ports
    port_patterns = [
        '/dev/ttyAMA*',
        '/dev/ttyUSB*', 
        '/dev/ttyACM*',
        '/dev/ttyS*',
        '/dev/serial*',
        '/dev/mdb*'
    ]
    
    all_ports = []
    for pattern in port_patterns:
        ports = glob.glob(pattern)
        all_ports.extend(ports)
    
    logger.info(f"Found {len(all_ports)} potential serial ports:")
    
    for port in sorted(all_ports):
        try:
            stat_info = os.stat(port)
            permissions = oct(stat_info.st_mode)
            
            # Try to open the port briefly
            try:
                ser = serial.Serial(port, 9600, timeout=1)
                ser.close()
                status = "✓ ACCESSIBLE"
            except serial.SerialException as e:
                status = f"✗ ERROR: {e}"
            except Exception as e:
                status = f"✗ UNKNOWN ERROR: {e}"
                
            logger.info(f"  {port} - Permissions: {permissions} - Status: {status}")
            
        except Exception as e:
            logger.info(f"  {port} - ERROR: {e}")

def test_mdb_communication_detailed(port):
    """Detailed MDB communication test with more diagnostics"""
    logger.info("="*60)
    logger.info(f"DETAILED MDB TEST ON {port}")
    logger.info("="*60)
    
    # Test multiple MDB protocols and baud rates
    mdb_configs = [
        {'baud': 9600, 'name': 'Standard MDB'},
        {'baud': 19200, 'name': 'Fast MDB'},
        {'baud': 38400, 'name': 'High Speed MDB'},
        {'baud': 115200, 'name': 'USB MDB Bridge'}
    ]
    
    for config in mdb_configs:
        logger.info(f"Testing {config['name']} at {config['baud']} baud...")
        
        try:
            ser = serial.Serial(
                port=port,
                baudrate=config['baud'],
                bytesize=8,
                parity='N',
                stopbits=1,
                timeout=3.0,
                write_timeout=1.0
            )
            
            # Clear buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            time.sleep(0.1)
            
            # Try various MDB commands
            test_commands = [
                (b'\x00', 'RESET'),
                (b'\x01', 'SETUP'), 
                (b'\x02', 'STATUS'),
                (b'\x08', 'POLL'),
                (b'\x0F', 'EXPANSION ID'),
            ]
            
            responses_received = 0
            
            for cmd, name in test_commands:
                logger.info(f"  Sending {name} command: {cmd.hex()}")
                
                try:
                    ser.write(cmd)
                    ser.flush()
                    time.sleep(0.5)
                    
                    if ser.in_waiting > 0:
                        response = ser.read(ser.in_waiting)
                        logger.info(f"    Response: {response.hex()} ({len(response)} bytes)")
                        responses_received += 1
                    else:
                        logger.info(f"    No response")
                        
                except Exception as e:
                    logger.warning(f"    Error sending command: {e}")
            
            ser.close()
            
            if responses_received > 0:
                logger.info(f"✓ Received {responses_received} responses - MDB device detected!")
                return True
            else:
                logger.warning(f"✗ No responses received at {config['baud']} baud")
                
        except Exception as e:
            logger.error(f"  Failed to test {config['name']}: {e}")
    
    return False

def generate_recommendations():
    """Generate troubleshooting recommendations"""
    logger.info("="*60)
    logger.info("TROUBLESHOOTING RECOMMENDATIONS")
    logger.info("="*60)
    
    recommendations = [
        "1. HARDWARE CHECKS:",
        "   • Ensure MDB Pi Hat is properly seated on GPIO pins",
        "   • Check all connections are tight",
        "   • Verify MDB device (vending machine controller) is powered ON",
        "   • Check MDB cable connections (4-wire: +24V, GND, Data+, Data-)",
        "",
        "2. RASPBERRY PI CONFIGURATION:",
        "   • Enable UART: Add 'enable_uart=1' to /boot/config.txt",
        "   • Disable Bluetooth: Add 'dtoverlay=disable-bt' to /boot/config.txt", 
        "   • Remove serial console from /boot/cmdline.txt",
        "   • Reboot after configuration changes",
        "",
        "3. MDB PI HAT SPECIFIC:",
        "   • Check if hat requires specific drivers or overlays",
        "   • Verify hat documentation for correct serial port",
        "   • Some hats use USB interface instead of GPIO serial",
        "   • Check if hat has status LEDs indicating power/communication",
        "",
        "4. PERMISSIONS:",
        "   • Add user to dialout group: sudo usermod -a -G dialout $USER",
        "   • Log out and back in after group change",
        "",
        "5. ADVANCED DEBUGGING:",
        "   • Use oscilloscope to check for electrical signals on MDB lines",
        "   • Monitor /dev/ttyAMA0 with: cat /dev/ttyAMA0 | hexdump -C",
        "   • Check kernel logs: dmesg | grep -i serial",
        ""
    ]
    
    for rec in recommendations:
        logger.info(rec)

def main():
    """Main troubleshooting function"""
    logger.info("Starting comprehensive MDB hardware troubleshooting...")
    
    try:
        # System information
        check_raspberry_pi_info()
        
        # MDB Hat detection
        check_mdb_hat_detection()
        
        # Serial configuration
        check_serial_configuration()
        
        # Serial port scan
        check_all_serial_ports()
        
        # Test primary port if available
        if os.path.exists('/dev/ttyAMA0'):
            mdb_detected = test_mdb_communication_detailed('/dev/ttyAMA0')
            
            if mdb_detected:
                logger.info("🎉 MDB DEVICE DETECTED AND RESPONDING!")
                print("\n✓ SUCCESS: MDB device is communicating properly")
                return True
            else:
                logger.warning("❌ MDB device not responding")
        
        # Generate recommendations
        generate_recommendations()
        
        logger.info("❌ MDB TROUBLESHOOTING COMPLETED - ISSUES FOUND")
        print("\n✗ MDB device not detected - check mdb_troubleshoot.log for details")
        return False
        
    except Exception as e:
        logger.error(f"Troubleshooting failed: {e}")
        logger.exception("Full traceback:")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 