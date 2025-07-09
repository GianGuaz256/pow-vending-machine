"""
Bitcoin Vending Machine Simulator for Development and Testing
LCD display + terminal-based simulator optimized for Raspberry Pi
"""
import threading
import time
import sys
import os
import logging
import pygame
from typing import Optional, Dict, Any

# Add project root and src to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

# Set up enhanced logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('simulator.log')
    ]
)
logger = logging.getLogger(__name__)

# Log system information
logger.info("="*60)
logger.info("VENDING MACHINE SIMULATOR SESSION STARTED")
logger.info("="*60)
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Project root: {project_root}")

try:
    from config import config
    from lcd_display import LCDDisplay
    from btcpay_client import BTCPayClient, InvoiceStatus
    BTCPAY_AVAILABLE = True
    logger.info("All components successfully imported")
except ImportError as e:
    BTCPAY_AVAILABLE = False
    logger.error(f"Component import failed: {e}")
    sys.exit(1)

def wait_for_display(duration: float) -> bool:
    """Wait while processing pygame events - essential for display updates"""
    if duration <= 0:
        return True
        
    clock = pygame.time.Clock()
    elapsed = 0
    
    while elapsed < duration * 1000:  # Convert to milliseconds
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logger.info("Display window closed by user")
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    logger.info("Simulator terminated by user (ESC key)")
                    return False
        
        clock.tick(60)  # 60 FPS
        elapsed += clock.get_time()
    
    return True

class VendingMachineSimulator:
    """Enhanced Vending Machine Simulator for Raspberry Pi"""
    
    def __init__(self):
        logger.info("Initializing Vending Machine Simulator")
        
        # Initialize components
        self.display = None
        self.btcpay = None
        self.running = False
        
        # Vending state
        self.current_invoice = None
        self.current_vend_request = None
        
        # Product catalog (low prices for simulation testing)
        self.products = {
            "1": {"name": "Coca Cola", "price": 0.01},
            "2": {"name": "Sprite", "price": 0.01}, 
            "3": {"name": "Water", "price": 0.01},
            "4": {"name": "Coffee", "price": 0.01},
            "5": {"name": "Sandwich", "price": 0.01},
            "6": {"name": "Chips", "price": 0.01},
            "7": {"name": "Chocolate", "price": 0.01},
            "8": {"name": "Energy Drink", "price": 0.01},
        }
        
        # Test results tracking
        self.test_results = {}
        self.simulator_events = []
        
    def initialize_components(self):
        """Initialize all simulator components"""
        logger.info("Initializing simulator components")
        
        # Initialize LCD Display
        try:
            logger.debug("Initializing LCD display")
            self.display = LCDDisplay()
            if self.display.initialize():
                logger.info("✓ LCD display initialized successfully")
                self.display.show_message("Bitcoin Vending Machine", "Simulator Ready")
                wait_for_display(2)
                return True
            else:
                logger.error("✗ LCD display initialization failed")
                return False
        except Exception as e:
            logger.error(f"✗ LCD display error: {e}")
            return False
    
    def initialize_btcpay(self):
        """Initialize BTCPay client"""
        if not BTCPAY_AVAILABLE:
            logger.warning("BTCPay not available - using simulation mode")
            return False
            
        try:
            logger.debug("Initializing BTCPay client")
            self.btcpay = BTCPayClient()
            logger.info("✓ BTCPay client initialized")
            return True
        except Exception as e:
            logger.error(f"✗ BTCPay initialization failed: {e}")
            return False
    
    def show_main_menu(self):
        """Display main menu on LCD and terminal"""
        # Show welcome message on display
        self.display.show_message("Welcome!", "Select your product")
        wait_for_display(1)
        
        # Show product menu in terminal
        print("\n" + "="*50)
        print("🍕 BITCOIN VENDING MACHINE SIMULATOR")
        print("="*50)
        print("Available Products:")
        print("-"*30)
        
        for num, product in self.products.items():
            print(f"  {num}. {product['name']:<15} €{product['price']:.2f}")
        
        print("-"*30)
        print("  9. Test Mode")
        print("  0. Exit")
        print("="*50)
        print("💡 Visual output shows on your miniHDMI display")
        print("📱 QR codes for payment will appear on the display")
        print("⌨️  Use terminal for product selection")
    
    def get_user_selection(self) -> str:
        """Get user input from terminal"""
        try:
            selection = input("\nEnter your selection (0-9): ").strip()
            return selection
        except KeyboardInterrupt:
            logger.info("Simulator interrupted by user")
            return "0"
        except Exception as e:
            logger.error(f"Input error: {e}")
            return ""
    
    def process_product_selection(self, selection: str):
        """Process selected product"""
        if selection == "0":
            logger.info("Exit selected")
            return False
        elif selection == "9":
            self.run_test_mode()
            return True
        elif selection in self.products:
            product = self.products[selection]
            logger.info(f"Product selected: {product['name']} - €{product['price']}")
            self.process_vending(product)
            return True
        else:
            print("❌ Invalid selection. Please try again.")
            self.display.show_error("Invalid Selection")
            wait_for_display(2)
            return True
    
    def process_vending(self, product: Dict[str, Any]):
        """Process vending transaction"""
        logger.info(f"Starting vending process for {product['name']}")
        
        # Show product selected
        self.display.show_message(
            f"Selected: {product['name']}", 
            f"Price: €{product['price']:.2f}"
        )
        wait_for_display(3)
        
        # Create invoice if BTCPay available
        if self.btcpay:
            self.create_real_invoice(product)
        else:
            self.simulate_payment(product)
    
    def create_real_invoice(self, product: Dict[str, Any]):
        """Create real BTCPay invoice"""
        try:
            logger.info(f"Creating BTCPay invoice for {product['name']}")
            
            # Show creating invoice message
            self.display.show_message("Creating Invoice...", "Please wait")
            wait_for_display(2)
            
            # Create invoice
            invoice_data = self.btcpay.create_invoice(
                amount=product['price'],
                currency='EUR',
                description=f"Vending: {product['name']}"
            )
            
            if invoice_data:
                self.current_invoice = invoice_data
                logger.info(f"✓ Invoice created: {invoice_data['invoice_id']}")
                
                # Get Lightning invoice for QR code
                lightning_invoice = invoice_data.get('lightning_invoice')
                payment_url = invoice_data.get('payment_url')
                
                # Debug: Show what we received
                logger.debug(f"Lightning invoice available: {bool(lightning_invoice)}")
                logger.debug(f"Payment URL available: {bool(payment_url)}")
                if lightning_invoice:
                    logger.debug(f"Lightning invoice starts with: {lightning_invoice[:20]}...")
                
                if lightning_invoice:
                    # Show Lightning invoice QR code - this is what wallets scan directly
                    self.display.show_qr_code(lightning_invoice, f"Pay €{product['price']:.2f}")
                    
                    print(f"\n⚡ LIGHTNING PAYMENT REQUIRED")
                    print(f"Product: {product['name']}")
                    print(f"Amount: €{product['price']:.2f}")
                    print(f"Invoice ID: {invoice_data['invoice_id']}")
                    print(f"Lightning Invoice: {lightning_invoice[:50]}...")
                    if payment_url:
                        print(f"Web Checkout (fallback): {payment_url}")
                    print(f"\n📱 Scan Lightning QR code on display with your wallet")
                    print(f"💡 This is a real Lightning Network invoice")
                elif payment_url:
                    # Fallback to web checkout if Lightning invoice unavailable
                    self.display.show_qr_code(payment_url, "Scan to Pay")
                    print(f"\n💳 WEB PAYMENT (Lightning unavailable)")
                    print(f"Payment URL: {payment_url}")
                    print(f"⚠️ Please use web checkout")
                else:
                    print(f"\n❌ No payment method available")
                    self.display.show_error("No Payment Method")
                    wait_for_display(3)
                    return
                
                # Monitor payment for any valid payment method
                self.monitor_payment(product)
            else:
                logger.error("Failed to create invoice")
                self.display.show_error("Payment System Error")
                wait_for_display(3)
                
        except Exception as e:
            logger.error(f"Invoice creation failed: {e}")
            self.display.show_error("Payment Error")
            wait_for_display(3)
    
    def monitor_payment(self, product: Dict[str, Any]):
        """Monitor payment status"""
        logger.info("Monitoring payment status")
        
        if not self.current_invoice:
            return
            
        invoice_id = self.current_invoice['invoice_id']
        timeout = 300  # 5 minutes
        check_interval = 5  # Check every 5 seconds
        elapsed = 0
        
        print(f"\n⏰ Waiting for payment (timeout: {timeout}s)")
        
        while elapsed < timeout:
            try:
                # Update payment status display
                remaining = timeout - elapsed
                self.display.show_payment_status(
                    product['price'], 
                    'EUR', 
                    f"Waiting ({remaining}s)"
                )
                
                # Check payment status
                if self.btcpay.is_invoice_paid(invoice_id):
                    logger.info("🎉 Payment received!")
                    print("\n✅ PAYMENT RECEIVED!")
                    self.handle_payment_success(product)
                    return
                
                # Check for expired/invalid status
                status_info = self.btcpay.get_invoice_status(invoice_id)
                if status_info:
                    status = status_info.get('status', '')
                    logger.debug(f"Payment status: {status}")
                    
                    if status in [InvoiceStatus.EXPIRED.value, InvoiceStatus.INVALID.value]:
                        logger.warning(f"Payment failed: {status}")
                        print(f"\n❌ Payment {status}")
                        self.display.show_error(f"Payment {status}")
                        wait_for_display(3)
                        return
                
                # Wait and check again
                if not wait_for_display(check_interval):
                    return
                elapsed += check_interval
                
                # Show countdown
                print(f"⏱ Checking payment... ({elapsed}/{timeout}s)", end='\r')
                
            except KeyboardInterrupt:
                logger.info("Payment monitoring cancelled by user")
                print("\n\n⚠️ Payment monitoring cancelled")
                self.cancel_current_invoice()
                return
            except Exception as e:
                logger.error(f"Payment monitoring error: {e}")
                break
        
        # Timeout reached
        logger.warning("Payment timeout reached")
        print(f"\n⏰ Payment timeout ({timeout}s)")
        self.display.show_error("Payment Timeout")
        wait_for_display(3)
        self.cancel_current_invoice()
    
    def handle_payment_success(self, product: Dict[str, Any]):
        """Handle successful payment"""
        logger.info(f"Processing successful payment for {product['name']}")
        
        # Show payment success
        self.display.show_payment_status(product['price'], 'EUR', 'PAID')
        wait_for_display(3)
        
        # Show dispensing
        self.display.show_dispensing(product['name'])
        print(f"\n🎉 Dispensing {product['name']}!")
        print("📦 Please collect your item")
        wait_for_display(5)
        
        # Show completion
        self.display.show_message("Enjoy!", "Thank you for your purchase")
        wait_for_display(3)
        
        # Clean up
        self.current_invoice = None
    
    def cancel_current_invoice(self):
        """Cancel current invoice"""
        if self.current_invoice and self.btcpay:
            try:
                invoice_id = self.current_invoice['invoice_id']
                self.btcpay.cancel_invoice(invoice_id)
                logger.info(f"Invoice {invoice_id} cancelled")
            except Exception as e:
                logger.error(f"Failed to cancel invoice: {e}")
        
        self.current_invoice = None
    
    def simulate_payment(self, product: Dict[str, Any]):
        """Simulate payment when BTCPay not available"""
        logger.info("Running payment simulation")
        
        # Show fake QR code
        fake_url = f"bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh?amount={product['price']/50000:.8f}"
        self.display.show_qr_code(fake_url, "Scan to Pay (SIMULATION)")
        
        print(f"\n🧪 SIMULATION MODE")
        print(f"Product: {product['name']}")
        print(f"Amount: €{product['price']:.2f}")
        print(f"Fake Bitcoin URL: {fake_url}")
        
        # Simulate payment process
        for i in range(10, 0, -1):
            self.display.show_payment_status(product['price'], 'EUR', f'Waiting ({i}s)')
            print(f"⏱ Simulating payment... {i}s", end='\r')
            if not wait_for_display(1):
                return
        
        # Simulate success
        print("\n✅ SIMULATED PAYMENT SUCCESS!")
        self.handle_payment_success(product)
    
    def run_test_mode(self):
        """Run systematic component tests"""
        logger.info("Starting test mode")
        
        print("\n🧪 TEST MODE")
        print("="*30)
        
        tests = [
            ("Display Test", self.test_display),
            ("QR Code Test", self.test_qr_codes),
            ("Payment Status Test", self.test_payment_status),
            ("BTCPay Test", self.test_btcpay_connection),
        ]
        
        for test_name, test_func in tests:
            print(f"\n▶️ Running {test_name}...")
            try:
                success = test_func()
                status = "✅ PASS" if success else "❌ FAIL"
                print(f"{status}: {test_name}")
            except Exception as e:
                print(f"❌ ERROR: {test_name} - {e}")
                logger.error(f"Test {test_name} failed: {e}")
        
        print("\n🏁 Test mode completed")
        input("\nPress Enter to return to main menu...")
    
    def test_display(self) -> bool:
        """Test display functionality"""
        self.display.show_message("Display Test", "Testing text display")
        wait_for_display(2)
        return True
    
    def test_qr_codes(self) -> bool:
        """Test QR code generation"""
        test_data = "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh?amount=0.001"
        self.display.show_qr_code(test_data, "QR Code Test")
        wait_for_display(3)
        return True
    
    def test_payment_status(self) -> bool:
        """Test payment status displays"""
        statuses = ["waiting", "paid", "expired"]
        for status in statuses:
            self.display.show_payment_status(2.50, "EUR", status)
            wait_for_display(2)
        return True
    
    def test_btcpay_connection(self) -> bool:
        """Test BTCPay server connection"""
        if not self.btcpay:
            self.display.show_message("BTCPay Test", "Not configured")
            wait_for_display(2)
            return False
        
        try:
            # Test connection
            self.display.show_message("BTCPay Test", "Testing connection...")
            wait_for_display(1)
            
            # Create and cancel test invoice
            invoice = self.btcpay.create_invoice(0.01, 'EUR', 'Test invoice')
            if invoice:
                self.btcpay.cancel_invoice(invoice['invoice_id'])
                self.display.show_message("BTCPay Test", "✅ Connection OK")
                wait_for_display(2)
                return True
            else:
                self.display.show_message("BTCPay Test", "❌ Connection Failed")
                wait_for_display(2)
                return False
        except Exception as e:
            logger.error(f"BTCPay test failed: {e}")
            self.display.show_message("BTCPay Test", "❌ Error")
            wait_for_display(2)
            return False
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Cleaning up simulator resources")
        
        # Cancel any pending invoice
        self.cancel_current_invoice()
        
        # Close display
        if self.display:
            self.display.close()
            logger.info("Display closed")
        
        logger.info("Simulator cleanup completed")
    
    def run(self):
        """Main simulator loop"""
        logger.info("Starting simulator main loop")
        
        try:
            # Initialize components
            if not self.initialize_components():
                print("❌ Failed to initialize display")
                return
            
            # Initialize BTCPay (optional)
            btcpay_ok = self.initialize_btcpay()
            if btcpay_ok:
                print("✅ BTCPay client available - real payments enabled")
            else:
                print("⚠️ BTCPay not available - simulation mode only")
            
            self.running = True
            
            # Main interaction loop
            while self.running:
                try:
                    self.show_main_menu()
                    selection = self.get_user_selection()
                    
                    if not self.process_product_selection(selection):
                        break
                        
                except KeyboardInterrupt:
                    logger.info("Simulator interrupted by user")
                    break
                except Exception as e:
                    logger.error(f"Main loop error: {e}")
                    print(f"❌ Error: {e}")
                    wait_for_display(2)
            
        except Exception as e:
            logger.error(f"Simulator failed: {e}")
            print(f"❌ Simulator error: {e}")
        finally:
            self.cleanup()
        
        print("\n👋 Simulator stopped")
        logger.info("Simulator session ended")

def main():
    """Main entry point"""
    print("Bitcoin Vending Machine Simulator")
    print("="*50)
    
    if not BTCPAY_AVAILABLE:
        print("⚠️ Some components not available - limited functionality")
    else:
        print("✅ All components available")
    
    print("\nFeatures:")
    print("• Real LCD display via miniHDMI")
    print("• Terminal-based product selection")
    print("• Real BTCPay integration with genuine QR codes")
    print("• Comprehensive testing mode")
    print("• Enhanced logging and diagnostics")
    
    input("\nPress Enter to start simulator...")
    
    try:
        simulator = VendingMachineSimulator()
        simulator.run()
    except Exception as e:
        logger.error(f"Failed to start simulator: {e}")
        print(f"❌ Failed to start simulator: {e}")

if __name__ == "__main__":
    main() 