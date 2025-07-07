"""
Enhanced Simple MDB Test
Low-level MDB hardware communication test with comprehensive logging
"""
import serial
import time
import logging
import os
import sys

# Set up enhanced logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('simple_mdb_test.log')
    ]
)
logger = logging.getLogger(__name__)

def test_serial_ports():
    """Test available serial ports"""
    logger.info("="*50)
    logger.info("SIMPLE MDB HARDWARE TEST")
    logger.info("="*50)
    
    # Common MDB serial ports
    test_ports = ['/dev/ttyAMA0', '/dev/ttyUSB0', '/dev/ttyS0', '/dev/mdb0']
    
    logger.info("Checking for available serial ports...")
    available_ports = []
    
    for port in test_ports:
        logger.debug(f"Checking port: {port}")
        if os.path.exists(port):
            try:
                stat_info = os.stat(port)
                logger.info(f"✓ Port {port} exists - permissions: {oct(stat_info.st_mode)}")
                available_ports.append(port)
            except Exception as e:
                logger.warning(f"✗ Port {port} exists but cannot access: {e}")
        else:
            logger.debug(f"✗ Port {port} does not exist")
    
    if not available_ports:
        logger.error("No MDB serial ports found!")
        return None
    
    logger.info(f"Available ports: {available_ports}")
    return available_ports[0]  # Use first available port

def test_mdb_communication(port):
    """Test basic MDB communication"""
    logger.info(f"Testing MDB communication on {port}")
    
    # Common MDB baud rates to try
    baud_rates = [9600, 19200, 38400, 115200]
    
    for baud_rate in baud_rates:
        logger.info(f"Trying baud rate: {baud_rate}")
        
        try:
            # Open serial connection
            logger.debug(f"Opening serial port {port} at {baud_rate} baud")
            ser = serial.Serial(
                port=port,
                baudrate=baud_rate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=2.0
            )
            
            logger.info(f"Serial port opened successfully")
            logger.debug(f"Port settings: {ser.get_settings()}")
            
            # Clear any existing data
            ser.flushInput()
            ser.flushOutput()
            time.sleep(0.1)
            
            # Track if we get any responses
            response_received = False
            
            # Test 1: Send RESET command
            logger.info("Test 1: Sending RESET command (0x00)")
            reset_cmd = b'\x00'
            ser.write(reset_cmd)
            logger.debug(f"Sent: {reset_cmd.hex()}")
            
            # Wait for response
            time.sleep(0.5)
            
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                logger.info(f"Received response: {response.hex()} ({len(response)} bytes)")
                response_received = True
                
                # Check for ACK (0x00) or other expected responses
                if response == b'\x00':
                    logger.info("✓ Received ACK - MDB device responded correctly!")
                else:
                    logger.info(f"Received non-ACK response: {response.hex()}")
            else:
                logger.warning("No response received to RESET command")
            
            # Test 2: Send SETUP command
            logger.info("Test 2: Sending SETUP command (0x01)")
            setup_cmd = b'\x01'
            ser.write(setup_cmd)
            logger.debug(f"Sent: {setup_cmd.hex()}")
            
            time.sleep(0.5)
            
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                logger.info(f"Setup response: {response.hex()} ({len(response)} bytes)")
                response_received = True
            else:
                logger.warning("No response to SETUP command")
            
            # Test 3: Send STATUS request
            logger.info("Test 3: Sending STATUS request (0x02)")
            status_cmd = b'\x02'
            ser.write(status_cmd)
            logger.debug(f"Sent: {status_cmd.hex()}")
            
            time.sleep(0.5)
            
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                logger.info(f"Status response: {response.hex()} ({len(response)} bytes)")
                response_received = True
            else:
                logger.warning("No response to STATUS command")
            
            # Test 4: Check for any spontaneous data
            logger.info("Test 4: Listening for spontaneous data...")
            time.sleep(2.0)
            
            if ser.in_waiting > 0:
                response = ser.read(ser.in_waiting)
                logger.info(f"Spontaneous data: {response.hex()} ({len(response)} bytes)")
                response_received = True
            else:
                logger.info("No spontaneous data received")
            
            ser.close()
            
            # Only return True if we actually received responses from MDB device
            if response_received:
                logger.info(f"✓ Successfully communicated with MDB device on {port} at {baud_rate} baud")
                return True
            else:
                logger.warning(f"✗ Serial port {port} opened but no MDB device responded at {baud_rate} baud")
                # Continue to next baud rate
                continue
            
        except serial.SerialException as e:
            logger.error(f"Serial error at {baud_rate} baud: {e}")
            try:
                ser.close()
            except:
                pass
        except Exception as e:
            logger.error(f"Unexpected error at {baud_rate} baud: {e}")
            try:
                ser.close()
            except:
                pass
    
    logger.error(f"❌ Failed to communicate with MDB device on {port} - no responses received at any baud rate")
    return False

def check_permissions():
    """Check permissions for serial port access"""
    logger.info("Checking user permissions for serial access...")
    
    # Check user groups
    try:
        import grp
        import pwd
        
        username = pwd.getpwuid(os.getuid()).pw_name
        user_groups = [g.gr_name for g in grp.getgrall() if username in g.gr_mem]
        primary_group = grp.getgrgid(pwd.getpwuid(os.getuid()).pw_gid).gr_name
        all_groups = [primary_group] + user_groups
        
        logger.info(f"Current user: {username}")
        logger.info(f"User groups: {all_groups}")
        
        # Check for common serial groups
        serial_groups = ['dialout', 'tty', 'uucp', 'serial']
        has_serial_access = any(group in all_groups for group in serial_groups)
        
        if has_serial_access:
            logger.info("✓ User has serial port access permissions")
        else:
            logger.warning("✗ User may not have serial port permissions")
            logger.warning(f"Consider adding user to one of: {serial_groups}")
            
    except Exception as e:
        logger.warning(f"Could not check permissions: {e}")

def main():
    """Main test function"""
    try:
        logger.info("Starting simple MDB hardware test")
        
        # Check system info
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        
        # Check permissions
        check_permissions()
        
        # Find available ports
        port = test_serial_ports()
        
        if port:
            # Test communication
            success = test_mdb_communication(port)
            
            if success:
                logger.info("🎉 MDB hardware test completed successfully!")
                print("\n✓ MDB hardware test PASSED - check simple_mdb_test.log for details")
            else:
                logger.error("❌ MDB hardware test failed")
                print("\n✗ MDB hardware test FAILED - check simple_mdb_test.log for details")
                return False
        else:
            logger.error("No MDB hardware ports available")
            print("\n✗ No MDB hardware detected - check simple_mdb_test.log for details")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        logger.exception("Full exception traceback:")
        print(f"\n✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)