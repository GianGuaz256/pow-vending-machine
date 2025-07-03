"""
Main Vending Machine Application
Coordinates LCD display, MDB board, and BTCPay Server for Bitcoin Lightning payments
"""
import time
import logging
import threading
import signal
import sys
from typing import Optional, Dict, Any
from enum import Enum

from config import config
from lcd_display import LCDDisplay
from mdb_controller import MDBController, VendState
from btcpay_client import BTCPayClient, InvoiceStatus

# Set up logging
logging.basicConfig(
    level=getattr(logging, config.system.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.system.log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VendingMachineState(Enum):
    """Main application states"""
    INITIALIZING = "initializing"
    READY = "ready"
    VEND_REQUEST = "vend_request"
    PAYMENT_PENDING = "payment_pending"
    PAYMENT_CONFIRMED = "payment_confirmed"
    DISPENSING = "dispensing"
    ERROR = "error"
    SHUTDOWN = "shutdown"

class VendingMachine:
    """Main vending machine application"""
    
    def __init__(self):
        self.state = VendingMachineState.INITIALIZING
        self.display = LCDDisplay()
        self.mdb = MDBController()
        self.btcpay = BTCPayClient()
        
        self.current_invoice = None
        self.current_vend_request = None
        self.running = False
        self._state_lock = threading.Lock()
        
        # Component status
        self.component_status = {
            'display': False,
            'mdb': False,
            'btcpay': False
        }
        
    def initialize(self) -> bool:
        """Initialize all components"""
        logger.info("Initializing Bitcoin Vending Machine...")
        
        try:
            # Validate configuration
            if not config.validate():
                logger.error("Configuration validation failed")
                return False
            
            # Initialize display first
            self.component_status['display'] = self.display.initialize()
            if not self.component_status['display']:
                logger.error("Failed to initialize display")
                return False
            
            self.display.show_message("Initializing...", "Starting system components")
            
            # Initialize MDB controller
            self.component_status['mdb'] = self.mdb.initialize()
            if not self.component_status['mdb']:
                logger.error("Failed to initialize MDB controller")
                self.display.show_error("MDB Controller Error")
                return False
            
            # Initialize BTCPay client
            self.component_status['btcpay'] = self.btcpay.initialize()
            if not self.component_status['btcpay']:
                logger.error("Failed to initialize BTCPay client")
                self.display.show_error("BTCPay Server Error")
                return False
            
            # Show system status
            self.display.show_system_status(
                self.component_status['mdb'],
                self.component_status['btcpay'],
                self.component_status['display']
            )
            time.sleep(3)
            
            self.state = VendingMachineState.READY
            self.display.show_message("Ready", "Bitcoin Vending Machine")
            
            logger.info("Vending machine initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            self.display.show_error(f"Initialization Error: {str(e)}")
            return False
    
    def run(self):
        """Main application loop"""
        if not self.initialize():
            logger.error("Failed to initialize, exiting")
            return
        
        self.running = True
        logger.info("Starting main application loop")
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            while self.running:
                self._process_state()
                time.sleep(0.1)  # Main loop delay
                
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            self.state = VendingMachineState.ERROR
            self.display.show_error(f"System Error: {str(e)}")
        
        finally:
            self._shutdown()
    
    def _process_state(self):
        """Process current state"""
        try:
            if self.state == VendingMachineState.READY:
                self._handle_ready_state()
            elif self.state == VendingMachineState.VEND_REQUEST:
                self._handle_vend_request_state()
            elif self.state == VendingMachineState.PAYMENT_PENDING:
                self._handle_payment_pending_state()
            elif self.state == VendingMachineState.PAYMENT_CONFIRMED:
                self._handle_payment_confirmed_state()
            elif self.state == VendingMachineState.DISPENSING:
                self._handle_dispensing_state()
            elif self.state == VendingMachineState.ERROR:
                self._handle_error_state()
                
        except Exception as e:
            logger.error(f"Error processing state {self.state}: {e}")
            self._set_state(VendingMachineState.ERROR)
    
    def _handle_ready_state(self):
        """Handle ready state - waiting for vend request"""
        # Check for vend request from MDB
        vend_request = self.mdb.get_vend_request()
        if vend_request:
            self.current_vend_request = vend_request
            logger.info(f"Received vend request: {vend_request}")
            self._set_state(VendingMachineState.VEND_REQUEST)
    
    def _handle_vend_request_state(self):
        """Handle vend request - create invoice and show QR code"""
        if not self.current_vend_request:
            self._set_state(VendingMachineState.READY)
            return
        
        try:
            amount = self.current_vend_request['item_price']
            currency = config.vending.currency
            
            # Validate amount
            if amount < config.vending.min_price or amount > config.vending.max_price:
                logger.error(f"Invalid amount: {amount}")
                self.mdb.deny_vend()
                self.display.show_error("Invalid Price")
                time.sleep(3)
                self._reset_to_ready()
                return
            
            # Create invoice
            self.current_invoice = self.btcpay.create_invoice(
                amount=amount,
                currency=currency,
                description=f"Vending Machine Item #{self.current_vend_request['item_number']}"
            )
            
            if not self.current_invoice:
                logger.error("Failed to create invoice")
                self.mdb.deny_vend()
                self.display.show_error("Payment System Error")
                time.sleep(3)
                self._reset_to_ready()
                return
            
            # Register payment callback
            invoice_id = self.current_invoice['invoice_id']
            self.btcpay.register_payment_callback(invoice_id, self._payment_status_callback)
            
            # Show QR code
            lightning_invoice = self.current_invoice['lightning_invoice']
            if lightning_invoice:
                self.display.show_qr_code(
                    lightning_invoice,
                    f"Pay {amount:.2f} {currency}"
                )
            else:
                self.display.show_payment_status(amount, currency, "waiting")
            
            self._set_state(VendingMachineState.PAYMENT_PENDING)
            
            # Start payment timeout timer
            self._start_payment_timeout()
            
        except Exception as e:
            logger.error(f"Error handling vend request: {e}")
            self.mdb.deny_vend()
            self.display.show_error("System Error")
            time.sleep(3)
            self._reset_to_ready()
    
    def _handle_payment_pending_state(self):
        """Handle payment pending state"""
        if not self.current_invoice:
            self._reset_to_ready()
            return
        
        # Check if payment is confirmed
        invoice_id = self.current_invoice['invoice_id']
        if self.btcpay.is_invoice_paid(invoice_id):
            self._set_state(VendingMachineState.PAYMENT_CONFIRMED)
    
    def _handle_payment_confirmed_state(self):
        """Handle payment confirmed state"""
        try:
            # Approve vend on MDB
            if self.mdb.approve_vend():
                amount = self.current_invoice['amount']
                currency = self.current_invoice['currency']
                self.display.show_payment_status(amount, currency, "paid")
                time.sleep(2)
                self._set_state(VendingMachineState.DISPENSING)
            else:
                logger.error("Failed to approve vend on MDB")
                self.display.show_error("Vending Error")
                time.sleep(3)
                self._reset_to_ready()
                
        except Exception as e:
            logger.error(f"Error confirming payment: {e}")
            self.display.show_error("System Error")
            time.sleep(3)
            self._reset_to_ready()
    
    def _handle_dispensing_state(self):
        """Handle dispensing state"""
        try:
            item_number = self.current_vend_request.get('item_number', 'Unknown')
            self.display.show_dispensing(f"Item #{item_number}")
            
            # Wait for dispensing to complete
            time.sleep(5)  # Adjust based on actual dispensing time
            
            # End MDB session
            self.mdb.end_session()
            
            logger.info("Item dispensed successfully")
            self.display.show_message("Complete", "Thank you!")
            time.sleep(3)
            
            self._reset_to_ready()
            
        except Exception as e:
            logger.error(f"Error during dispensing: {e}")
            self.display.show_error("Dispensing Error")
            time.sleep(3)
            self._reset_to_ready()
    
    def _handle_error_state(self):
        """Handle error state"""
        # Try to recover by checking component status
        self._check_component_status()
        
        if all(self.component_status.values()):
            logger.info("All components healthy, returning to ready state")
            self._reset_to_ready()
        else:
            # Show error status
            self.display.show_system_status(
                self.component_status['mdb'],
                self.component_status['btcpay'],
                self.component_status['display']
            )
            time.sleep(10)
    
    def _payment_status_callback(self, status_info: Dict[str, Any]):
        """Callback for payment status updates"""
        try:
            status = status_info.get('status', '')
            logger.info(f"Payment status update: {status}")
            
            if self.current_invoice:
                amount = self.current_invoice['amount']
                currency = self.current_invoice['currency']
                
                if status in [InvoiceStatus.PAID.value, InvoiceStatus.CONFIRMED.value]:
                    self.display.show_payment_status(amount, currency, "paid")
                elif status == InvoiceStatus.EXPIRED.value:
                    self.display.show_payment_status(amount, currency, "expired")
                    self._payment_expired()
                elif status == InvoiceStatus.INVALID.value:
                    self.display.show_payment_status(amount, currency, "error")
                    self._payment_failed()
                    
        except Exception as e:
            logger.error(f"Error in payment status callback: {e}")
    
    def _start_payment_timeout(self):
        """Start payment timeout timer"""
        def timeout_handler():
            time.sleep(config.btcpay.payment_timeout)
            
            if (self.state == VendingMachineState.PAYMENT_PENDING and 
                self.current_invoice):
                logger.warning("Payment timeout reached")
                self._payment_expired()
        
        timeout_thread = threading.Thread(target=timeout_handler, daemon=True)
        timeout_thread.start()
    
    def _payment_expired(self):
        """Handle payment expiration"""
        logger.info("Payment expired")
        self.mdb.deny_vend()
        self.display.show_error("Payment Expired")
        time.sleep(3)
        self._reset_to_ready()
    
    def _payment_failed(self):
        """Handle payment failure"""
        logger.error("Payment failed")
        self.mdb.deny_vend()
        self.display.show_error("Payment Failed")
        time.sleep(3)
        self._reset_to_ready()
    
    def _check_component_status(self):
        """Check status of all components"""
        self.component_status['mdb'] = self.mdb.check_connection()
        self.component_status['btcpay'] = self.btcpay.check_connection()
        self.component_status['display'] = self.display.is_initialized
    
    def _set_state(self, new_state: VendingMachineState):
        """Set new state with thread safety"""
        with self._state_lock:
            if self.state != new_state:
                logger.info(f"State change: {self.state.value} -> {new_state.value}")
                self.state = new_state
    
    def _reset_to_ready(self):
        """Reset to ready state"""
        self.current_invoice = None
        self.current_vend_request = None
        self._set_state(VendingMachineState.READY)
        self.display.show_message("Ready", "Bitcoin Vending Machine")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def _shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down vending machine...")
        self._set_state(VendingMachineState.SHUTDOWN)
        
        try:
            # Cancel any pending invoice
            if self.current_invoice:
                self.btcpay.cancel_invoice(self.current_invoice['invoice_id'])
            
            # Deny any pending vend
            if self.mdb.state == VendState.VEND_REQUEST:
                self.mdb.deny_vend()
            
            # Close components
            self.display.show_message("Shutting Down", "Please wait...")
            time.sleep(2)
            
            self.mdb.close()
            self.display.close()
            
            logger.info("Shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

def main():
    """Main entry point"""
    try:
        vending_machine = VendingMachine()
        vending_machine.run()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 