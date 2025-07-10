"""
Simplified Vending Machine Simulator
Provides interactive testing capabilities without hardware conflicts
"""
import threading
import time
import sys
import os
import logging
import pygame
from typing import Optional, Dict, Any

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

from lcd_display import LCDDisplay
from btcpay_client import BTCPayClient, InvoiceStatus

logger = logging.getLogger(__name__)

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
    """Simplified Vending Machine Simulator - no MDB controller conflicts"""
    
    def __init__(self):
        logger.info("Initializing Vending Machine Simulator")
        
        # Initialize components (LCD only, no MDB)
        self.display = None
        self.btcpay = None
        self.running = False
        
        # Vending state
        self.current_invoice = None
        self.current_product = None
        
        # Product catalog (low prices for testing)
        self.products = {
            "1": {"name": "Coca Cola", "price": 0.05},
            "2": {"name": "Sprite", "price": 0.05}, 
            "3": {"name": "Water", "price": 0.03},
            "4": {"name": "Coffee", "price": 0.10},
            "5": {"name": "Snacks", "price": 0.08},
        }
        
    def initialize_components(self):
        """Initialize display component only"""
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
        try:
            logger.debug("Initializing BTCPay client")
            self.btcpay = BTCPayClient()
            if self.btcpay.initialize():
                logger.info("✓ BTCPay client initialized")
                return True
            else:
                logger.warning("BTCPay initialization failed - using simulation mode")
                return False
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
        print("🪙 BITCOIN VENDING MACHINE - SIMULATION MODE")
        print("="*50)
        print("Available Products:")
        print("-"*30)
        
        for num, product in self.products.items():
            print(f"  {num}. {product['name']:<15} €{product['price']:.2f}")
        
        print("-"*30)
        print("  8. Test BTCPay Connection")
        print("  9. Show Status")
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
        elif selection == "8":
            self.test_btcpay_connection()
            return True
        elif selection == "9":
            self.show_status()
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
        self.current_product = product
        
        print(f"\n🔄 Processing {product['name']} (€{product['price']:.2f})")
        
        # Try to create real invoice first
        if self.btcpay:
            self.create_real_invoice(product)
        else:
            self.simulate_payment(product)
    
    def create_real_invoice(self, product: Dict[str, Any]):
        """Create real BTCPay invoice"""
        try:
            logger.info(f"Creating invoice for {product['name']}")
            
            invoice = self.btcpay.create_invoice(
                amount=product['price'],
                currency='EUR',
                description=f"Vending Machine - {product['name']}"
            )
            
            if not invoice:
                logger.error("Failed to create invoice")
                print("❌ Failed to create payment request")
                self.display.show_error("Payment System Error")
                wait_for_display(3)
                return
            
            self.current_invoice = invoice
            logger.info(f"Invoice created: {invoice['invoice_id']}")
            
            # Display QR code - prioritize Lightning Network
            lightning_url = invoice.get('lightning_invoice')
            
            if lightning_url and lightning_url.startswith(('lnbc', 'lntb', 'lnbcrt')):
                # Real Lightning invoice found!
                qr_data = lightning_url
                qr_label = f"⚡ Lightning €{product['price']:.2f}"
                print(f"⚡ Lightning Network QR code displayed")
                print(f"💳 QR code displayed on screen")
                print(f"💰 Amount: €{product['price']:.2f}")
                print(f"🧾 Invoice ID: {invoice['invoice_id']}")
                print(f"📱 Lightning Invoice: {qr_data[:50]}...")
                
                self.display.show_qr_code(qr_data, qr_label)
                
            elif invoice.get('payment_url'):
                # BTCPay checkout page as fallback
                qr_data = invoice['payment_url']
                qr_label = f"💳 BTCPay €{product['price']:.2f}"
                print(f"🌐 BTCPay checkout QR code displayed")
                print(f"💳 QR code displayed on screen")
                print(f"💰 Amount: €{product['price']:.2f}")
                print(f"🧾 Invoice ID: {invoice['invoice_id']}")
                print(f"📱 Checkout URL: {qr_data[:50]}...")
                
                self.display.show_qr_code(qr_data, qr_label)
                
            else:
                # No Lightning available - show error instead of Bitcoin fallback
                print(f"❌ Lightning Network not available from BTCPay Server")
                print(f"⚠️  Please ensure Lightning Network is properly configured on your BTCPay instance")
                print(f"💡 Falling back to simulation mode...")
                self.display.show_error("Lightning Network Unavailable")
                wait_for_display(3)
                
                # Cancel the real invoice and use simulation instead
                self.cancel_current_invoice()
                self.simulate_payment(product)
                return
            
            # Start monitoring payment
            self.monitor_payment(product)
            
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            print(f"❌ Error creating payment: {e}")
            self.display.show_error("Payment Error")
            wait_for_display(3)
    
    def monitor_payment(self, product: Dict[str, Any]):
        """Monitor payment status"""
        if not self.current_invoice:
            return
        
        invoice_id = self.current_invoice['invoice_id']
        timeout = 120  # 2 minutes timeout
        check_interval = 2  # Check every 2 seconds
        
        # Get the QR data that was used
        qr_data = self._get_payment_qr_data(product)
        
        print("\n⏳ Waiting for payment...")
        print("Press Ctrl+C to cancel")
        
        try:
            for elapsed in range(0, timeout, check_interval):
                # Update display with QR code AND status
                remaining = timeout - elapsed
                self.display.show_qr_with_status(
                    qr_data, 
                    product['price'], 
                    'EUR', 
                    f'waiting ({remaining}s)',
                    f"Pay €{product['price']:.2f}"
                )
                
                # Check payment status
                if self.btcpay.is_invoice_paid(invoice_id):
                    print("\n✅ PAYMENT CONFIRMED!")
                    # Show final success with QR
                    self.display.show_qr_with_status(
                        qr_data, 
                        product['price'], 
                        'EUR', 
                        'PAID ✓',
                        f"Payment Complete"
                    )
                    wait_for_display(2)
                    self.handle_payment_success(product)
                    return
                
                # Wait with progress indicator
                print(f"⏱ Checking payment... {remaining}s remaining", end='\r')
                
                if not wait_for_display(check_interval):
                    break
            
            # Payment timeout
            print("\n⏰ Payment timeout")
            self.display.show_payment_status(product['price'], 'EUR', 'expired')
            wait_for_display(3)
            
        except KeyboardInterrupt:
            print("\n❌ Payment cancelled by user")
            self.display.show_message("Cancelled", "Payment cancelled")
            wait_for_display(2)
        finally:
            self.cancel_current_invoice()
    
    def _get_payment_qr_data(self, product: Dict[str, Any]) -> str:
        """Get the QR data for the current payment"""
        if self.current_invoice:
            # Try to get the actual Lightning invoice first
            lightning_url = self.current_invoice.get('lightning_invoice')
            if lightning_url and lightning_url.startswith(('lnbc', 'lntb', 'lnbcrt')):
                return lightning_url
            elif self.current_invoice.get('payment_url'):
                return self.current_invoice['payment_url']
        
        # Fallback to fake Lightning invoice for testing
        return f"lnbc{int(product['price']*100000)}u1pwx7h5xpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqdq5xysxxatsyp3k7enxv4jsxqzpurzjq0nvpwkq20uuz2lgzuzjx5rhrxyzpjm6r62grsaetnjm9tgnewdltvp2rwqy0rptqfcrj73wk2xhhszqqqqqrqq9qwxlg8m0qqqqqqgqjq4qvwx"
    
    def handle_payment_success(self, product: Dict[str, Any]):
        """Handle successful payment"""
        logger.info(f"Payment successful for {product['name']}")
        
        # Show success on display
        self.display.show_payment_status(product['price'], 'EUR', 'paid')
        wait_for_display(2)
        
        # Simulate dispensing
        print(f"🎯 Dispensing {product['name']}...")
        self.display.show_dispensing(f"Dispensing {product['name']}")
        wait_for_display(3)
        
        # Complete transaction
        print("✅ Transaction completed!")
        self.display.show_message("Complete", "Thank you!")
        wait_for_display(3)
        
        # Reset state
        self.current_invoice = None
        self.current_product = None
    
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
        
        # Create a fake Lightning invoice for testing (this is what a real one looks like)
        # This is just for visual testing - not a real payment
        fake_lightning_invoice = f"lnbc{int(product['price']*100000)}u1pwx7h5xpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqdq5xysxxatsyp3k7enxv4jsxqzpurzjq0nvpwkq20uuz2lgzuzjx5rhrxyzpjm6r62grsaetnjm9tgnewdltvp2rwqy0rptqfcrj73wk2xhhszqqqqqrqq9qwxlg8m0qqqqqqgqjq4qvwx"
        
        print(f"\n🧪 SIMULATION MODE - NO REAL PAYMENT")
        print(f"Product: {product['name']}")
        print(f"Amount: €{product['price']:.2f}")
        print(f"⚡ Lightning Network QR code displayed (SIMULATION)")
        print(f"📱 Fake Lightning Invoice: {fake_lightning_invoice[:50]}...")
        print(f"⚠️  This is a test - no real payment required")
        
        # Simulate payment process with shorter timeout for testing
        print(f"\n⏳ Auto-completing payment in 5 seconds...")
        for i in range(5, 0, -1):
            # Show QR code with countdown status
            self.display.show_qr_with_status(
                fake_lightning_invoice, 
                product['price'], 
                'EUR', 
                f'SIMULATION ({i}s)',
                f"⚡ TEST MODE €{product['price']:.2f}"
            )
            print(f"⏱ Simulating payment... {i}s", end='\r')
            if not wait_for_display(1):
                return
        
        # Show success with QR
        print("\n✅ SIMULATED PAYMENT SUCCESS!")
        self.display.show_qr_with_status(
            fake_lightning_invoice, 
            product['price'], 
            'EUR', 
            'PAID ✓ (SIMULATION)',
            "⚡ Payment Complete"
        )
        wait_for_display(2)
        self.handle_payment_success(product)
    
    def test_btcpay_connection(self):
        """Test BTCPay server connection"""
        print("\n🔧 Testing BTCPay Connection...")
        self.display.show_message("BTCPay Test", "Testing connection...")
        
        if not self.btcpay:
            print("❌ BTCPay client not initialized")
            self.display.show_message("BTCPay Test", "Not configured")
            wait_for_display(3)
            return
        
        try:
            # Create and cancel test invoice
            test_invoice = self.btcpay.create_invoice(0.01, 'EUR', 'Connection test')
            if test_invoice:
                self.btcpay.cancel_invoice(test_invoice['invoice_id'])
                print("✅ BTCPay connection successful")
                self.display.show_message("BTCPay Test", "✅ Connection OK")
            else:
                print("❌ BTCPay connection failed")
                self.display.show_message("BTCPay Test", "❌ Connection Failed")
        except Exception as e:
            print(f"❌ BTCPay test error: {e}")
            self.display.show_message("BTCPay Test", "❌ Error")
            logger.error(f"BTCPay test failed: {e}")
        
        wait_for_display(3)
    
    def show_status(self):
        """Show system status"""
        print("\n" + "="*40)
        print("📊 SYSTEM STATUS")
        print("="*40)
        print(f"Display: {'✅ OK' if self.display and self.display.is_initialized else '❌ Error'}")
        print(f"BTCPay: {'✅ OK' if self.btcpay else '❌ Not available'}")
        
        if self.current_invoice:
            print(f"\nActive Invoice: {self.current_invoice.get('invoice_id', 'N/A')}")
            print(f"Amount: €{self.current_invoice.get('amount', 0):.2f}")
        
        if self.current_product:
            print(f"\nCurrent Product: {self.current_product['name']}")
        
        print("="*40)
        input("Press Enter to continue...")
    
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
    """Main entry point for simulation mode"""
    print("🚀 Starting Bitcoin Vending Machine Simulator...")
    print("This mode provides interactive testing without requiring MDB hardware.\n")
    
    print("Features:")
    print("• Real LCD display via miniHDMI")
    print("• Terminal-based product selection") 
    print("• Real BTCPay integration with genuine QR codes")
    print("• No MDB controller conflicts")
    
    try:
        simulator = VendingMachineSimulator()
        simulator.run()
        
    except KeyboardInterrupt:
        print("\n\nSimulator stopped by user")
    except Exception as e:
        logger.error(f"Simulator error: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 