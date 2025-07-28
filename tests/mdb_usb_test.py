#!/usr/bin/env python3
"""
MDB Hybrid Pi HAT Test
Tests the MDB connection using text commands on GPIO UART
"""
import serial
import time
import logging
import os
import sys

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from config import config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mdb_usb_test.log')
    ]
)
logger = logging.getLogger(__name__)

def test_usb_mdb_connection():
    """Test Hybrid MDB Pi HAT connection using text commands"""
    logger.info("="*60)
    logger.info("HYBRID MDB PI HAT TEST - Text Commands")
    logger.info("="*60)
    
    # Check if device exists
    if not os.path.exists(config.mdb.serial_port):
        logger.error(f"Device {config.mdb.serial_port} does not exist!")
        logger.info("Available serial devices:")
        import glob
        for pattern in ['/dev/ttyACM*', '/dev/ttyAMA*', '/dev/ttyUSB*']:
            devices = glob.glob(pattern)
            for device in devices:
                logger.info(f"  Found: {device}")
        return False
    
    try:
        logger.info(f"Testing connection to {config.mdb.serial_port}")
        logger.info(f"Using baud rate: {config.mdb.baud_rate}")
        logger.info(f"Using timeout: {config.mdb.timeout}")
        
        # Create serial connection exactly as specified by user
        ser = serial.Serial()
        ser.baudrate = 115200  # Set the appropriate BaudRate
        ser.timeout = 50  # The maximum timeout that the program waits for a reply
        ser.port = config.mdb.serial_port  # Use configured device file descriptor
        
        logger.info("Opening serial connection...")
        ser.open()  # Open the serial connection
        
        # Allow time for connection to stabilize
        time.sleep(1.0)
        
        logger.info("Sending version command 'V\\n'...")
        ser.write(b'V\n')  # Write the version command "V\n" encoded in Binary
        
        logger.info("Reading response...")
        s = ser.readline()  # Read the response
        
        if s:
            version_info = s.decode('ascii').strip()
            logger.info(f"✓ SUCCESS: Version: {version_info}")
            print(f'Version: {version_info}')
            
            # Test additional commands
            test_commands = [
                ('R', 'Reset'),
                ('S', 'Setup'),
                ('P', 'Poll'),
                ('T', 'Status')
            ]
            
            for cmd, name in test_commands:
                logger.info(f"Testing {name} command '{cmd}\\n'...")
                ser.write(f'{cmd}\n'.encode('ascii'))
                response = ser.readline()
                if response:
                    response_text = response.decode('ascii').strip()
                    logger.info(f"  {name} response: {response_text}")
                else:
                    logger.warning(f"  No response to {name} command")
            
            ser.close()
            logger.info("✓ Hybrid MDB Pi HAT test completed successfully!")
            return True
            
        else:
            logger.error("✗ No response to version command")
            ser.close()
            return False
            
    except serial.SerialException as e:
        logger.error(f"Serial error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.exception("Full traceback:")
        return False

def test_with_mdb_controller():
    """Test using the updated MDB Controller"""
    logger.info("="*60)
    logger.info("TESTING WITH UPDATED MDB CONTROLLER")
    logger.info("="*60)
    
    try:
        from mdb_controller import MDBController
        
        logger.info("Creating MDB Controller instance...")
        mdb = MDBController()
        
        logger.info("Initializing MDB Controller...")
        success = mdb.initialize()
        
        if success:
            logger.info("✓ MDB Controller initialized successfully!")
            
            # Test basic functionality
            status = mdb.get_status()
            logger.info(f"Status: {status}")
            
            # Test connection health
            health = mdb.check_connection()
            logger.info(f"Connection health: {health}")
            
            # Test device info
            if 'device_info' in status:
                logger.info(f"Device info: {status['device_info']}")
            
            mdb.close()
            logger.info("✓ MDB Controller test completed successfully!")
            return True
        else:
            logger.error("✗ MDB Controller initialization failed")
            return False
            
    except Exception as e:
        logger.error(f"MDB Controller test failed: {e}")
        logger.exception("Full traceback:")
        return False

def check_permissions():
    """Check permissions for device access"""
    logger.info("="*60)
    logger.info("CHECKING DEVICE PERMISSIONS")
    logger.info("="*60)
    
    try:
        device = config.mdb.serial_port
        if os.path.exists(device):
            stat_info = os.stat(device)
            permissions = oct(stat_info.st_mode)
            logger.info(f"Device: {device}")
            logger.info(f"Permissions: {permissions}")
            
            # Check if device is readable/writable
            readable = os.access(device, os.R_OK)
            writable = os.access(device, os.W_OK)
            
            logger.info(f"Readable: {readable}")
            logger.info(f"Writable: {writable}")
            
            if readable and writable:
                logger.info("✓ Device permissions look good")
                return True
            else:
                logger.warning("✗ Device permission issues detected")
                logger.info("Try: sudo usermod -a -G dialout $USER")
                logger.info("Then logout and login again")
                return False
        else:
            logger.error(f"Device {device} does not exist")
            return False
            
    except Exception as e:
        logger.error(f"Permission check failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("Starting Hybrid MDB Pi HAT testing...")
    
    print("HYBRID MDB PI HAT TEST")
    print("="*50)
    print(f"Testing device: {config.mdb.serial_port}")
    print(f"Baud rate: {config.mdb.baud_rate}")
    print("Setup: GPIO UART with text commands")
    
    # Test 1: Check permissions
    print("\n1. Checking permissions...")
    perm_ok = check_permissions()
    
    # Test 2: Direct connection test
    print("\n2. Testing direct connection...")
    direct_ok = test_usb_mdb_connection()
    
    # Test 3: MDB Controller test
    print("\n3. Testing with MDB Controller...")
    controller_ok = test_with_mdb_controller()
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Permissions:     {'✓ PASS' if perm_ok else '✗ FAIL'}")
    print(f"Direct Test:     {'✓ PASS' if direct_ok else '✗ FAIL'}")
    print(f"MDB Controller:  {'✓ PASS' if controller_ok else '✗ FAIL'}")
    
    if direct_ok and controller_ok:
        print("\n🎉 All tests passed! Hybrid MDB Pi HAT is working correctly.")
        return True
    elif direct_ok:
        print("\n⚠️ Direct connection works but controller has issues - check implementation.")
        return False
    else:
        print("\n❌ Tests failed - check hardware and configuration.")
        print(f"\nDevice being tested: {config.mdb.serial_port}")
        print("Make sure your Hybrid MDB Pi HAT is connected and powered on.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 