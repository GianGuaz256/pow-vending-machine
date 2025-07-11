"""
MDB Controller for Qibixx MDB Pi HAT
Handles communication with the vending machine MDB board
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
    """MDB command constants"""
    RESET = 0x00
    SETUP = 0x01
    POLL = 0x02
    VEND = 0x03
    READER = 0x04
    REVALUE = 0x05
    EXPANSION = 0x07

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
    """Controller for MDB communication via Qibixx MDB Pi HAT"""
    
    def __init__(self):
        self.serial_port = None
        self.is_connected = False
        self.state = VendState.DISABLED
        self.session_data = {}
        self._lock = threading.Lock()
        self._running = False
        self._poll_thread = None
        # Initialize baud_rate from config to prevent AttributeError
        self.baud_rate = config.mdb.baud_rate
        
    def initialize(self) -> bool:
        """Initialize MDB connection"""
        try:
            logger.info("Initializing Qibixx MDB Pi HAT connection...")
            
            # Qibixx MDB Pi HAT serial parameters:
            # Baudrate: 38400, Parity: None, Data Bits: 8, Stop Bits: 1
            self.serial_port = serial.Serial(
                port=config.mdb.serial_port,
                baudrate=config.mdb.baud_rate,  # 38400 for Qibixx MDB Pi HAT
                timeout=config.mdb.timeout,
                bytesize=serial.EIGHTBITS,     # 8 data bits
                parity=serial.PARITY_NONE,     # No parity
                stopbits=serial.STOPBITS_ONE   # 1 stop bit
            )
            
            # Allow HAT time to stabilize after serial port opening
            logger.info("Allowing HAT to stabilize...")
            time.sleep(1.0)
            
            # Test connection with adaptive baud rate detection
            if self._test_qibixx_connection():
                self.is_connected = True
                self.state = VendState.ENABLED
                self._start_polling()
                logger.info(f"✓ Qibixx MDB Pi Hat initialized successfully at {self.baud_rate} baud")
                return True
            else:
                logger.error("Failed to establish communication with Qibixx MDB Pi Hat")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize MDB controller: {e}")
            return False
    
    def _send_command(self, command: int, data: bytes = b'') -> bool:
        """Send command to Qibixx MDB Pi Hat"""
        if not self.serial_port or not self.serial_port.is_open:
            return False
            
        try:
            with self._lock:
                # For Qibixx MDB Pi Hat, use text-based commands
                if command == MDBCommand.RESET.value:
                    qibixx_cmd = b'R\r'
                elif command == MDBCommand.SETUP.value:
                    qibixx_cmd = b'S\r'
                elif command == MDBCommand.POLL.value:
                    qibixx_cmd = b'P\r'
                else:
                    # Fallback to raw MDB command for testing
                    packet = bytes([command]) + data
                    checksum = sum(packet) & 0xFF
                    qibixx_cmd = packet + bytes([checksum])
                
                # Send command
                self.serial_port.write(qibixx_cmd)
                self.serial_port.flush()
                
                # Wait for response
                time.sleep(0.1)
                response = self.serial_port.read(100)  # Read more data
                
                # Check for valid response (not 0xFF NAK)
                return len(response) > 0 and response != b'\xff'
                
        except Exception as e:
            logger.error(f"Failed to send command to Qibixx hat: {e}")
            return False
    
    def _test_qibixx_connection(self) -> bool:
        """Test connection to Qibixx MDB Pi Hat with adaptive baud rate detection"""
        if not self.serial_port:
            return False
            
        # Baud rates to try (HAT responds at different rates in different states)
        baud_rates = [38400, 19200, 9600]  # Order based on troubleshooting results
        test_commands = [
            (b'\x01', "SETUP"),      # SETUP command
            (b'\x08', "POLL"),       # POLL command  
            (b'\x00', "RESET"),      # RESET command
            (b'\x0f', "EXPANSION"),  # EXPANSION ID command
        ]
        
        # Close current connection to change baud rate
        original_baud = self.baud_rate
        
        for baud_rate in baud_rates:
            logger.info(f"Testing Qibixx connection at {baud_rate} baud...")
            
            try:
                # Close and reopen with new baud rate
                if self.serial_port.is_open:
                    self.serial_port.close()
                    
                self.serial_port.baudrate = baud_rate
                self.serial_port.open()
                
                # Test multiple commands at this baud rate
                for cmd_bytes, cmd_name in test_commands:
                    try:
                        with self._lock:
                            # Clear buffers
                            self.serial_port.reset_input_buffer()
                            self.serial_port.reset_output_buffer()
                            time.sleep(0.1)
                            
                            # Send command
                            self.serial_port.write(cmd_bytes)
                            self.serial_port.flush()
                            
                            # Wait for response
                            time.sleep(0.5)
                            response = self.serial_port.read(100)
                            
                            # Check if we got any response
                            if len(response) > 0:
                                logger.info(f"✓ Qibixx connection successful at {baud_rate} baud!")
                                logger.info(f"  Command: {cmd_name} ({cmd_bytes.hex()}) → Response: {response.hex()}")
                                
                                # Update our baud rate to the working one
                                self.baud_rate = baud_rate
                                return True
                                
                    except Exception as e:
                        logger.debug(f"Command {cmd_name} failed at {baud_rate} baud: {e}")
                        continue
                        
                logger.debug(f"No responses at {baud_rate} baud")
                
            except Exception as e:
                logger.debug(f"Failed to test {baud_rate} baud: {e}")
                continue
                
        # Restore original baud rate if all failed
        try:
            if self.serial_port.is_open:
                self.serial_port.close()
            self.serial_port.baudrate = original_baud
            self.serial_port.open()
        except Exception as e:
            logger.error(f"Failed to restore original baud rate: {e}")
            
        logger.warning("No response from Qibixx hat at any tested baud rate")
        return False
    
    def _read_response(self, timeout: float = 1.0) -> Optional[bytes]:
        """Read response from MDB device"""
        if not self.serial_port or not self.serial_port.is_open:
            return None
            
        try:
            start_time = time.time()
            response = b''
            
            while time.time() - start_time < timeout:
                if self.serial_port.in_waiting > 0:
                    byte = self.serial_port.read(1)
                    if byte:
                        response += byte
                        # For now, read until no more data or timeout
                        # In real MDB implementation, 9th bit handling would be needed
                        if self.serial_port.in_waiting == 0:
                            time.sleep(0.01)  # Small delay to check for more data
                            if self.serial_port.in_waiting == 0:
                                break
                time.sleep(0.01)
            
            return response if response else None
            
        except Exception as e:
            logger.error(f"Failed to read MDB response: {e}")
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
                time.sleep(0.1)  # Poll every 100ms
                
            except Exception as e:
                logger.error(f"Error in MDB poll loop: {e}")
                time.sleep(1.0)
    
    def _poll_device(self):
        """Poll Qibixx MDB Pi Hat for status updates"""
        try:
            # Send POLL command using binary protocol (more reliable)
            if self._send_command(MDBCommand.POLL.value):
                response = self._read_response()
                if response:
                    self._process_poll_response(response)
                    
        except Exception as e:
            logger.error(f"Error polling Qibixx hat: {e}")
    
    def _send_qibixx_command(self, command: bytes) -> bool:
        """Send raw command to Qibixx hat"""
        if not self.serial_port or not self.serial_port.is_open:
            return False
            
        try:
            with self._lock:
                self.serial_port.write(command)
                self.serial_port.flush()
                time.sleep(0.1)
                return True
                
        except Exception as e:
            logger.error(f"Failed to send Qibixx command: {e}")
            return False
    
    def _process_poll_response(self, response: bytes):
        """Process poll response from MDB device"""
        if not response:
            return
            
        try:
            # Parse response based on first byte
            cmd = response[0] & 0x7F  # Remove mode bit
            
            if cmd == 0x01:  # Vend request
                self._handle_vend_request(response)
            elif cmd == 0x02:  # Session begin
                self._handle_session_begin(response)
            elif cmd == 0x03:  # Session cancel
                self._handle_session_cancel()
            elif cmd == 0x04:  # Session complete
                self._handle_session_complete()
            else:
                logger.debug(f"Unknown MDB response: {response.hex()}")
                
        except Exception as e:
            logger.error(f"Error processing MDB response: {e}")
    
    def _handle_vend_request(self, response: bytes):
        """Handle vend request from MDB"""
        try:
            if len(response) >= 5:
                # Parse vend request
                item_price = int.from_bytes(response[1:3], 'big') / 100.0  # Price in cents
                item_number = response[3]
                
                self.session_data = {
                    'item_price': item_price,
                    'item_number': item_number,
                    'timestamp': time.time()
                }
                
                self.state = VendState.VEND_REQUEST
                logger.info(f"Vend request: Item {item_number}, Price ${item_price:.2f}")
                
        except Exception as e:
            logger.error(f"Error handling vend request: {e}")
    
    def _handle_session_begin(self, response: bytes):
        """Handle session begin"""
        self.state = VendState.SESSION_IDLE
        logger.info("MDB session began")
    
    def _handle_session_cancel(self):
        """Handle session cancellation"""
        self.state = VendState.ENABLED
        self.session_data.clear()
        logger.info("MDB session cancelled")
    
    def _handle_session_complete(self):
        """Handle session completion"""
        self.state = VendState.SESSION_COMPLETE
        logger.info("MDB session completed")
    
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
                
            # Send vend approved command
            if self._send_command(MDBCommand.VEND.value, b'\x01'):
                self.state = VendState.VEND_APPROVED
                logger.info("Vend approved")
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
                
            # Send vend denied command
            if self._send_command(MDBCommand.VEND.value, b'\x00'):
                self.state = VendState.VEND_DENIED
                logger.info("Vend denied")
                return True
            else:
                logger.error("Failed to send vend denial")
                return False
                
        except Exception as e:
            logger.error(f"Error denying vend: {e}")
            return False
    
    def end_session(self) -> bool:
        """End current session"""
        try:
            # Send session end command
            if self._send_command(MDBCommand.READER.value, b'\x04'):
                self.state = VendState.ENABLED
                self.session_data.clear()
                logger.info("Session ended")
                return True
            else:
                logger.error("Failed to end session")
                return False
                
        except Exception as e:
            logger.error(f"Error ending session: {e}")
            return False
    
    def check_connection(self) -> bool:
        """Check if Qibixx MDB Pi Hat connection is healthy"""
        try:
            # Use adaptive connection test if not connected, quick test if already connected
            if not self.is_connected:
                # Do full adaptive baud rate detection
                connection_result = self._test_qibixx_connection()
                self.is_connected = connection_result
                return connection_result
            else:
                # Quick health check with current settings
                if not self.serial_port or not self.serial_port.is_open:
                    self.is_connected = False
                    return False
                    
                with self._lock:
                    # Clear buffers
                    self.serial_port.reset_input_buffer()
                    self.serial_port.reset_output_buffer()
                    time.sleep(0.1)
                    
                    # Send SETUP command (quick test)
                    self.serial_port.write(b'\x01')
                    self.serial_port.flush()
                    time.sleep(0.5)
                    
                    # Check for response
                    response = self.serial_port.read(100)
                    if len(response) > 0:
                        logger.debug(f"Connection check successful. Response: {response.hex()}")
                        return True
                    else:
                        logger.warning("Connection lost - no response during health check")
                        self.is_connected = False
                        return False
                        
        except Exception as e:
            logger.error(f"Qibixx connection check failed: {e}")
            self.is_connected = False
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current MDB status"""
        return {
            'state': self.state.value if self.state else 'unknown',
            'is_connected': self.is_connected,
            'last_activity': time.time(),
            'session_data': self.session_data.copy() if self.session_data else {}
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