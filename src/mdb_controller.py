"""
MDB Controller for Qibixx MDB USB Interface
Handles communication with the vending machine MDB board using USB interface
"""
import serial
import time
import threading
import logging
from typing import Optional, Dict, Any
from enum import Enum
from config import config

logger = logging.getLogger(__name__)

class MDBCommand(Enum):
    """MDB text command constants for USB interface"""
    VERSION = "V"
    RESET = "R"
    SETUP = "S"
    POLL = "P"
    ENABLE = "E"
    DISABLE = "D"
    STATUS = "T"

class VendState(Enum):
    """Vending machine states"""
    DISABLED = "disabled"
    ENABLED = "enabled"
    SESSION_IDLE = "session_idle"
    VEND_REQUEST = "vend_request"
    VEND_APPROVED = "vend_approved"
    VEND_DENIED = "vend_denied"
    SESSION_COMPLETE = "session_complete"
    ERROR = "error"

class MDBController:
    """Controller for MDB communication via Qibixx MDB USB Interface"""
    
    def __init__(self):
        self.serial_port = None
        self.is_connected = False
        self.state = VendState.DISABLED
        self.session_data = {}
        self._lock = threading.Lock()
        self._running = False
        self._poll_thread = None
        self.device_info = {}
        
    def initialize(self) -> bool:
        """Initialize MDB USB connection"""
        try:
            logger.info("Initializing Qibixx MDB USB Interface connection...")
            
            # Qibixx MDB USB Interface parameters:
            # Baudrate: 115200, Parity: None, Data Bits: 8, Stop Bits: 1
            self.serial_port = serial.Serial()
            self.serial_port.baudrate = 115200
            self.serial_port.timeout = 50  # High timeout as specified
            self.serial_port.port = config.mdb.serial_port
            self.serial_port.bytesize = serial.EIGHTBITS
            self.serial_port.parity = serial.PARITY_NONE
            self.serial_port.stopbits = serial.STOPBITS_ONE
            
            # Open the connection
            self.serial_port.open()
            
            # Allow interface time to stabilize
            logger.info("Allowing MDB USB interface to stabilize...")
            time.sleep(1.0)
            
            # Test connection with version command
            if self._test_connection():
                self.is_connected = True
                self.state = VendState.ENABLED
                self._start_polling()
                logger.info(f"✓ Qibixx MDB USB Interface initialized successfully on {config.mdb.serial_port}")
                return True
            else:
                logger.error("Failed to establish communication with Qibixx MDB USB Interface")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize MDB controller: {e}")
            if self.serial_port and self.serial_port.is_open:
                self.serial_port.close()
            return False
    
    def _test_connection(self) -> bool:
        """Test connection to Qibixx MDB USB Interface using version command"""
        if not self.serial_port or not self.serial_port.is_open:
            return False
            
        try:
            logger.info("Testing MDB USB connection with version command...")
            
            with self._lock:
                # Clear buffers
                self.serial_port.reset_input_buffer()
                self.serial_port.reset_output_buffer()
                time.sleep(0.1)
                
                # Send version command as specified
                self.serial_port.write(b'V\n')
                self.serial_port.flush()
                
                # Read response using readline()
                response = self.serial_port.readline()
                
                if response:
                    version_info = response.decode('ascii').strip()
                    logger.info(f"✓ MDB USB Interface Version: {version_info}")
                    
                    # Store device information
                    self.device_info['version'] = version_info
                    self.device_info['connection_type'] = 'USB'
                    self.device_info['baudrate'] = 115200
                    
                    return True
                else:
                    logger.warning("No response to version command")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to test MDB USB connection: {e}")
            return False
    
    def _send_command(self, command: str, data: str = '') -> Optional[str]:
        """Send text command to Qibixx MDB USB Interface"""
        if not self.serial_port or not self.serial_port.is_open:
            return None
            
        try:
            with self._lock:
                # Construct command with newline terminator
                full_command = f"{command}{data}\n"
                command_bytes = full_command.encode('ascii')
                
                # Send command
                self.serial_port.write(command_bytes)
                self.serial_port.flush()
                
                # Read response
                response = self.serial_port.readline()
                if response:
                    return response.decode('ascii').strip()
                return None
                
        except Exception as e:
            logger.error(f"Failed to send command to MDB USB interface: {e}")
            return None
    
    def _start_polling(self):
        """Start MDB polling thread"""
        self._running = True
        self._poll_thread = threading.Thread(target=self._poll_loop, daemon=True)
        self._poll_thread.start()
        logger.info("MDB polling started")
    
    def _poll_loop(self):
        """Main polling loop for MDB communication"""
        while self._running:
            try:
                if self.is_connected:
                    self._poll_device()
                time.sleep(0.5)  # Poll every 500ms for USB interface
                
            except Exception as e:
                logger.error(f"Error in MDB poll loop: {e}")
                time.sleep(2.0)
    
    def _poll_device(self):
        """Poll MDB USB Interface for status updates"""
        try:
            # Send POLL command
            response = self._send_command(MDBCommand.POLL.value)
            if response:
                self._process_poll_response(response)
                    
        except Exception as e:
            logger.error(f"Error polling MDB USB interface: {e}")
    
    def _process_poll_response(self, response: str):
        """Process poll response from MDB device"""
        if not response:
            return
            
        try:
            # Log the response for debugging
            logger.debug(f"Poll response: {response}")
            
            # Parse response - this will depend on your specific MDB device
            # Common responses might include status, coin insertion, vend requests, etc.
            
            if "COIN" in response.upper():
                self._handle_coin_insertion(response)
            elif "VEND" in response.upper():
                self._handle_vend_request(response)
            elif "BILL" in response.upper():
                self._handle_bill_insertion(response)
            elif "ERROR" in response.upper():
                self._handle_error(response)
            else:
                # Normal status or unknown response
                logger.debug(f"Normal poll response: {response}")
                
        except Exception as e:
            logger.error(f"Error processing MDB response: {e}")
    
    def _handle_coin_insertion(self, response: str):
        """Handle coin insertion"""
        try:
            logger.info(f"Coin insertion detected: {response}")
            # Parse coin value and update session
            # This depends on your specific MDB device response format
            
        except Exception as e:
            logger.error(f"Error handling coin insertion: {e}")
    
    def _handle_vend_request(self, response: str):
        """Handle vend request from MDB"""
        try:
            logger.info(f"Vend request: {response}")
            self.state = VendState.VEND_REQUEST
            
            # Parse vend request details from response
            # Store in session_data for processing
            self.session_data = {
                'vend_request': response,
                'timestamp': time.time()
            }
                
        except Exception as e:
            logger.error(f"Error handling vend request: {e}")
    
    def _handle_bill_insertion(self, response: str):
        """Handle bill/note insertion"""
        try:
            logger.info(f"Bill insertion detected: {response}")
            # Parse bill value and update session
            
        except Exception as e:
            logger.error(f"Error handling bill insertion: {e}")
    
    def _handle_error(self, response: str):
        """Handle error response"""
        try:
            logger.warning(f"MDB Error: {response}")
            self.state = VendState.ERROR
            
        except Exception as e:
            logger.error(f"Error handling MDB error: {e}")
    
    def get_vend_request(self) -> Optional[Dict[str, Any]]:
        """Get pending vend request"""
        if self.state == VendState.VEND_REQUEST:
            return self.session_data.copy()
        return None
    
    def approve_vend(self) -> bool:
        """Approve vend request"""
        try:
            if self.state != VendState.VEND_REQUEST:
                logger.warning("No vend request to approve")
                return False
                
            # Send enable/approve command
            response = self._send_command(MDBCommand.ENABLE.value)
            if response is not None:
                self.state = VendState.VEND_APPROVED
                logger.info(f"Vend approved: {response}")
                return True
            else:
                logger.error("Failed to send vend approval")
                return False
                
        except Exception as e:
            logger.error(f"Error approving vend: {e}")
            return False
    
    def deny_vend(self) -> bool:
        """Deny vend request"""
        try:
            if self.state != VendState.VEND_REQUEST:
                logger.warning("No vend request to deny")
                return False
                
            # Send disable/deny command
            response = self._send_command(MDBCommand.DISABLE.value)
            if response is not None:
                self.state = VendState.VEND_DENIED
                logger.info(f"Vend denied: {response}")
                return True
            else:
                logger.error("Failed to send vend denial")
                return False
                
        except Exception as e:
            logger.error(f"Error denying vend: {e}")
            return False
    
    def reset_device(self) -> bool:
        """Reset MDB device"""
        try:
            response = self._send_command(MDBCommand.RESET.value)
            if response is not None:
                logger.info(f"Device reset: {response}")
                self.state = VendState.ENABLED
                self.session_data.clear()
                return True
            return False
                
        except Exception as e:
            logger.error(f"Error resetting device: {e}")
            return False
    
    def get_device_status(self) -> Optional[str]:
        """Get device status"""
        try:
            return self._send_command(MDBCommand.STATUS.value)
        except Exception as e:
            logger.error(f"Error getting device status: {e}")
            return None
    
    def check_connection(self) -> bool:
        """Check if MDB USB Interface connection is healthy"""
        try:
            if not self.serial_port or not self.serial_port.is_open:
                self.is_connected = False
                return False
                
            # Quick health check with version command
            response = self._send_command(MDBCommand.VERSION.value)
            if response:
                logger.debug(f"Connection check successful. Version: {response}")
                self.is_connected = True
                return True
            else:
                logger.warning("Connection lost - no response to version command")
                self.is_connected = False
                return False
                        
        except Exception as e:
            logger.error(f"MDB connection check failed: {e}")
            self.is_connected = False
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current MDB status"""
        return {
            'state': self.state.value if self.state else 'unknown',
            'is_connected': self.is_connected,
            'last_activity': time.time(),
            'session_data': self.session_data.copy() if self.session_data else {},
            'device_info': self.device_info.copy() if self.device_info else {}
        }
    
    def close(self):
        """Close MDB connection"""
        self._running = False
        
        if self._poll_thread and self._poll_thread.is_alive():
            self._poll_thread.join(timeout=2.0)
            
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            
        self.is_connected = False
        logger.info("MDB controller closed") 