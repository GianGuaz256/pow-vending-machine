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
        
    def initialize(self) -> bool:
        """Initialize MDB connection"""
        try:
            self.serial_port = serial.Serial(
                port=config.mdb.serial_port,
                baudrate=config.mdb.baud_rate,
                timeout=config.mdb.timeout,
                bytesize=serial.EIGHTBITS,  # Use 8-bit, handle 9th bit in software
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            # Test connection
            if self._send_command(MDBCommand.RESET.value):
                self.is_connected = True
                self.state = VendState.ENABLED
                self._start_polling()
                logger.info("MDB controller initialized successfully")
                return True
            else:
                logger.error("Failed to establish MDB communication")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize MDB controller: {e}")
            return False
    
    def _send_command(self, command: int, data: bytes = b'') -> bool:
        """Send command to MDB device"""
        if not self.serial_port or not self.serial_port.is_open:
            return False
            
        try:
            with self._lock:
                # Construct MDB packet
                packet = bytes([command]) + data
                checksum = sum(packet) & 0xFF
                packet += bytes([checksum])
                
                # Send packet
                self.serial_port.write(packet)
                self.serial_port.flush()
                
                # Wait for ACK
                response = self.serial_port.read(1)
                return len(response) > 0 and response[0] == 0x00  # ACK
                
        except Exception as e:
            logger.error(f"Failed to send MDB command: {e}")
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
        """Poll MDB device for status updates"""
        try:
            # Send poll command
            if self._send_command(MDBCommand.POLL.value):
                response = self._read_response()
                if response:
                    self._process_poll_response(response)
                    
        except Exception as e:
            logger.error(f"Error polling MDB device: {e}")
    
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
        """Check if MDB connection is healthy"""
        try:
            # Send a simple poll command to test connection
            return self._send_command(MDBCommand.POLL.value)
        except Exception as e:
            logger.error(f"MDB connection check failed: {e}")
            self.is_connected = False
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current MDB status"""
        return {
            'state': self.state.value,
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