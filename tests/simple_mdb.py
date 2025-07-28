"""
Enhanced Simple MDB Test
Text-based MDB communication test for Hybrid Pi HAT setup
"""
import serial
import time
import logging
import os
import sys

# Add project root to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

from config import config

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
    logger.info("SIMPLE MDB HARDWARE TEST - HYBRID PI HAT")
    logger.info("="*50)
    
    # Check configured port
    if os.path.exists(config.mdb.serial_port):
        logger.info(f"✓ Configured port {config.mdb.serial_port} exists")
        return config.mdb.serial_port
    
    # Common MDB serial ports as fallback
    test_ports = ['/dev/ttyAMA0', '/dev/ttyUSB0', '/dev/ttyACM0', '/dev/ttyS0']
    
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
    """Test MDB communication using text commands (Hybrid Pi HAT)"""
    logger.info(f"Testing MDB communication on {port}")
    
    # Test text-based commands at 115200 baud (your working setup)
    logger.info("Testing Hybrid Pi HAT setup: 115200 baud with text commands")
    
    try:
        # Open serial connection with your working parameters
        logger.debug(f"Opening serial port {port} at 115200 baud")
        ser = serial.Serial(
            port=port,
            baudrate=115200,  # Your working baud rate
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=50.0  # High timeout like your setup
        )
        
        logger.info(f"Serial port opened successfully")
        logger.debug(f"Port settings: {ser.get_settings()}")
        
        # Clear any existing data
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        time.sleep(0.1)
        
        # Track if we get any responses
        response_received = False
        
        # Test text commands (your working setup)
        text_commands = [
            ('V\n', 'VERSION'),
            ('R\n', 'RESET'),
            ('S\n', 'SETUP'), 
            ('P\n', 'POLL'),
            ('T\n', 'STATUS')
        ]
        
        for cmd_text, cmd_name in text_commands:
            logger.info(f"Test: Sending {cmd_name} command ('{cmd_text.strip()}')")
            cmd_bytes = cmd_text.encode('ascii')
            ser.write(cmd_bytes)
            logger.debug(f"Sent: {cmd_bytes}")
            
            # Wait for response
            time.sleep(0.5)
            
            if ser.in_waiting > 0:
                response = ser.readline()
                if response:
                    response_text = response.decode('ascii').strip()
                    logger.info(f"✓ Received response: '{response_text}'")
                    response_received = True
                    
                    # Check for expected responses
                    if cmd_name == 'VERSION' and response_text.startswith('v,'):
                        logger.info("✓ Version response format correct!")
                    elif 'NACK' in response_text.upper() or 'OK' in response_text.upper():
                        logger.info("✓ Valid MDB response format!")
                else:
                    logger.warning(f"Empty response to {cmd_name} command")
            else:
                logger.warning(f"No response to {cmd_name} command")
        
        ser.close()
        
        if response_received:
            logger.info(f"✓ Successfully communicated with MDB device on {port} using text commands")
            return True
        else:
            logger.warning(f"✗ No responses received from MDB device")
            return False
            
    except serial.SerialException as e:
        logger.error(f"Serial error: {e}")
        try:
            ser.close()
        except:
            pass
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        try:
            ser.close()
        except:
            pass
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
        logger.info("Starting simple MDB hardware test for Hybrid Pi HAT")
        
        # Check system info
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Configured MDB port: {config.mdb.serial_port}")
        logger.info(f"Configured baud rate: {config.mdb.baud_rate}")
        
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
                print("✓ Your Hybrid Pi HAT is working with text commands at 115200 baud")
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