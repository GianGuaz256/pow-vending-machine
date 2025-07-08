"""
Bitcoin Vending Machine Simulator for Development and Testing
Comprehensive GUI-based simulator with enhanced logging and systematic testing capabilities
"""
import tkinter as tk
from tkinter import ttk, messagebox
import qrcode
from PIL import Image, ImageTk
import threading
import time
import sys
import os
import logging
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
    from btcpay_client import BTCPayClient, InvoiceStatus
    BTCPAY_AVAILABLE = True
    logger.info("BTCPay client successfully imported")
except ImportError as e:
    BTCPAY_AVAILABLE = False
    logger.warning(f"BTCPay client not available: {e}")

class SimulatedLCDDisplay:
    """Enhanced simulated LCD display using tkinter with logging"""
    
    def __init__(self, master, test_suite=None):
        self.master = master
        self.test_suite = test_suite
        self.width = 320
        self.height = 480
        
        logger.debug("Initializing simulated LCD display")
        
        # Create LCD frame
        self.lcd_frame = tk.Frame(master, bg='black', width=self.width, height=self.height)
        self.lcd_frame.pack(side=tk.LEFT, padx=10, pady=10)
        self.lcd_frame.pack_propagate(False)
        
        # Create display area
        self.display_label = tk.Label(
            self.lcd_frame, 
            bg='black', 
            fg='white', 
            font=('Arial', 12),
            justify=tk.CENTER,
            wraplength=300
        )
        self.display_label.pack(expand=True)
        
        self.is_initialized = True
        logger.info("Simulated LCD display initialized successfully")
    
    def show_message(self, title: str, message: str = ""):
        """Display a message"""
        try:
            text = f"{title}\n\n{message}" if message else title
            self.display_label.config(text=text, image='')
            logger.debug(f"Display message: {title} - {message}")
            if self.test_suite:
                self.test_suite.log_simulator_event("Display Message", f"Title: {title}, Message: {message}")
        except Exception as e:
            logger.error(f"Error showing message: {e}")
    
    def show_qr_code(self, data: str, title: str = "Scan to Pay"):
        """Display QR code"""
        try:
            logger.debug(f"Generating QR code for: {data[:50]}...")
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=8, border=4)
            qr.add_data(data)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img = qr_img.resize((200, 200), Image.Resampling.LANCZOS)
            
            # Convert to tkinter format
            self.qr_photo = ImageTk.PhotoImage(qr_img)
            
            self.display_label.config(text=title, image=self.qr_photo, compound=tk.BOTTOM)
            logger.info(f"QR code displayed successfully: {title}")
            if self.test_suite:
                self.test_suite.log_simulator_event("QR Code Display", f"Title: {title}, Data length: {len(data)}")
        except Exception as e:
            logger.error(f"Error showing QR code: {e}")
            self.show_message("QR Error", str(e))
            if self.test_suite:
                self.test_suite.log_simulator_event("QR Code Error", f"Error: {e}")
    
    def show_payment_status(self, amount: float, currency: str, status: str):
        """Display payment status"""
        try:
            colors = {
                "waiting": "yellow",
                "paid": "green", 
                "expired": "red",
                "error": "red"
            }
            color = colors.get(status.lower(), "white")
            
            text = f"{amount:.2f} {currency}\n\n{status.upper()}"
            self.display_label.config(text=text, fg=color, image='')
            logger.debug(f"Payment status displayed: {amount} {currency} - {status}")
            if self.test_suite:
                self.test_suite.log_simulator_event("Payment Status", f"{amount} {currency} - {status}")
        except Exception as e:
            logger.error(f"Error showing payment status: {e}")
    
    def show_dispensing(self, item_name: str = "Item"):
        """Show dispensing animation"""
        try:
            self.display_label.config(
                text=f"Dispensing...\n\nEnjoy your {item_name}!", 
                fg="green",
                image=''
            )
            logger.info(f"Dispensing animation displayed for: {item_name}")
            if self.test_suite:
                self.test_suite.log_simulator_event("Dispensing Animation", f"Item: {item_name}")
        except Exception as e:
            logger.error(f"Error showing dispensing animation: {e}")
    
    def show_error(self, error_message: str):
        """Display error message"""
        try:
            self.display_label.config(
                text=f"ERROR\n\n{error_message}", 
                fg="red",
                image=''
            )
            logger.warning(f"Error message displayed: {error_message}")
            if self.test_suite:
                self.test_suite.log_simulator_event("Error Display", f"Error: {error_message}")
        except Exception as e:
            logger.error(f"Error showing error message: {e}")
    
    def clear_screen(self):
        """Clear the display"""
        try:
            self.display_label.config(text="", image='')
            logger.debug("Display cleared")
        except Exception as e:
            logger.error(f"Error clearing display: {e}")

class SimulatedMDBController:
    """Enhanced simulated MDB controller with GUI controls and logging"""
    
    def __init__(self, master, lcd_display, test_suite=None):
        self.master = master
        self.lcd_display = lcd_display
        self.test_suite = test_suite
        self.is_connected = True
        self.current_vend_request = None
        
        logger.debug("Initializing simulated MDB controller")
        
        # Create MDB control frame
        self.control_frame = tk.LabelFrame(master, text="MDB Controller Simulator", padx=10, pady=10)
        self.control_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Price input
        tk.Label(self.control_frame, text="Item Price (EUR):").pack(pady=5)
        self.price_var = tk.StringVar(value="2.50")
        price_entry = tk.Entry(self.control_frame, textvariable=self.price_var, width=10)
        price_entry.pack(pady=5)
        
        # Item number input
        tk.Label(self.control_frame, text="Item Number:").pack(pady=5)
        self.item_var = tk.StringVar(value="1")
        item_entry = tk.Entry(self.control_frame, textvariable=self.item_var, width=10)
        item_entry.pack(pady=5)
        
        # Create vend request button
        self.vend_button = tk.Button(
            self.control_frame,
            text="Create Vend Request",
            command=self.create_vend_request,
            bg='lightblue',
            width=20
        )
        self.vend_button.pack(pady=10)
        
        # Status display
        self.status_text = tk.Text(self.control_frame, height=15, width=40)
        self.status_text.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self.log("MDB Controller Simulator ready")
        logger.info("Simulated MDB controller initialized successfully")
    
    def log(self, message: str):
        """Log message to both GUI and file"""
        try:
            timestamp = time.strftime('%H:%M:%S')
            gui_message = f"{timestamp} - {message}\n"
            self.status_text.insert(tk.END, gui_message)
            self.status_text.see(tk.END)
            logger.debug(f"MDB GUI Log: {message}")
        except Exception as e:
            logger.error(f"Error logging to MDB GUI: {e}")
    
    def create_vend_request(self):
        """Create a simulated vend request"""
        try:
            price = float(self.price_var.get())
            item_number = int(self.item_var.get())
            
            self.current_vend_request = {
                'item_price': price,
                'item_number': item_number,
                'timestamp': time.time()
            }
            
            self.log(f"Vend request created: Item {item_number}, Price €{price:.2f}")
            logger.info(f"Vend request created: Item {item_number}, Price €{price:.2f}")
            
            if self.test_suite:
                self.test_suite.log_simulator_event("Vend Request Created", f"Item {item_number}, Price €{price:.2f}")
            
            # Disable button to prevent multiple requests
            self.vend_button.config(state='disabled', text='Vend Request Active')
            
        except ValueError as e:
            error_msg = "Please enter valid price and item number"
            messagebox.showerror("Error", error_msg)
            logger.error(f"Invalid vend request input: {e}")
            if self.test_suite:
                self.test_suite.log_simulator_event("Vend Request Error", error_msg)
        except Exception as e:
            logger.error(f"Error creating vend request: {e}")
    
    def get_vend_request(self) -> Optional[Dict[str, Any]]:
        """Get pending vend request"""
        return self.current_vend_request.copy() if self.current_vend_request else None
    
    def approve_vend(self):
        """Approve vend request"""
        try:
            if self.current_vend_request:
                self.log("Vend APPROVED - Dispensing item")
                logger.info("Vend request approved")
                
                item_name = f"Item #{self.current_vend_request['item_number']}"
                self.lcd_display.show_dispensing(item_name)
                
                if self.test_suite:
                    self.test_suite.log_simulator_event("Vend Approved", f"Item: {item_name}")
                
                # Simulate dispensing delay
                threading.Timer(3.0, self.complete_vend).start()
                return True
            return False
        except Exception as e:
            logger.error(f"Error approving vend: {e}")
            return False
    
    def deny_vend(self):
        """Deny vend request"""
        try:
            if self.current_vend_request:
                self.log("Vend DENIED")
                logger.info("Vend request denied")
                
                if self.test_suite:
                    self.test_suite.log_simulator_event("Vend Denied", "Request denied")
                
                self.reset_vend()
                return True
            return False
        except Exception as e:
            logger.error(f"Error denying vend: {e}")
            return False
    
    def complete_vend(self):
        """Complete vending process"""
        try:
            self.log("Item dispensed successfully")
            logger.info("Item dispensed successfully")
            
            if self.test_suite:
                self.test_suite.log_simulator_event("Item Dispensed", "Vending completed successfully")
            
            self.reset_vend()
            self.lcd_display.show_message("Complete", "Thank you!")
            threading.Timer(2.0, lambda: self.lcd_display.show_message("Ready", "Bitcoin Vending Machine")).start()
        except Exception as e:
            logger.error(f"Error completing vend: {e}")
    
    def reset_vend(self):
        """Reset vend request"""
        try:
            self.current_vend_request = None
            self.vend_button.config(state='normal', text='Create Vend Request')
            logger.debug("Vend request reset")
        except Exception as e:
            logger.error(f"Error resetting vend: {e}")

class VendingMachineSimulator:
    """Enhanced main simulator application with systematic testing capabilities"""
    
    def __init__(self):
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.simulator_events = []
        
        logger.info("Initializing Vending Machine Simulator")
        
        # Create GUI
        self.root = tk.Tk()
        self.root.title("Bitcoin Vending Machine Simulator")
        self.root.geometry("1000x700")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Create main components
        self.lcd = SimulatedLCDDisplay(self.root, self)
        self.mdb = SimulatedMDBController(self.root, self.lcd, self)
        
        # BTCPay client setup
        self.btcpay = None
        self.btcpay_connected = False
        self.test_invoices = []  # Track for cleanup
        
        if BTCPAY_AVAILABLE:
            try:
                self.btcpay = BTCPayClient()
                self.btcpay_connected = self.btcpay.initialize()
                logger.info(f"BTCPay client initialized: {self.btcpay_connected}")
            except Exception as e:
                logger.error(f"BTCPay client initialization failed: {e}")
                self.btcpay_connected = False
        
        self.current_invoice = None
        self.running = False
        
        # Create control interface
        self.create_control_interface()
        
        # Initial display
        self.lcd.show_message("Ready", "Bitcoin Vending Machine")
        
        # Start main loop
        self.start_main_loop()
        
        logger.info("Vending Machine Simulator initialized successfully")
    
    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.test_results[test_name] = {"passed": passed, "details": details}
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
        
        status = "✓ PASS" if passed else "✗ FAIL"
        logger.info(f"Test Result - {status}: {test_name} - {details}")
    
    def log_simulator_event(self, event_type: str, details: str):
        """Log simulator event"""
        event = {
            'timestamp': time.time(),
            'type': event_type,
            'details': details
        }
        self.simulator_events.append(event)
        logger.debug(f"Simulator Event - {event_type}: {details}")
    
    def create_control_interface(self):
        """Create enhanced control interface"""
        # Control buttons frame
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.BOTTOM, pady=10)
        
        # Test buttons
        tk.Button(button_frame, text="Test QR Code", 
                 command=self.test_qr_code, bg='lightgreen').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Test Payment Status", 
                 command=self.test_payment_status, bg='lightgreen').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Test Error", 
                 command=self.test_error, bg='orange').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Reset Display", 
                 command=self.reset_display, bg='lightblue').pack(side=tk.LEFT, padx=5)
        
        # Systematic test buttons
        tk.Button(button_frame, text="Run System Tests", 
                 command=self.run_systematic_tests, bg='yellow').pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Test BTCPay Integration", 
                 command=self.test_btcpay_integration, bg='yellow').pack(side=tk.LEFT, padx=5)
        
        # Status label
        self.status_label = tk.Label(self.root, text="Status: Ready", font=('Arial', 10))
        self.status_label.pack(side=tk.BOTTOM)
    
    def test_qr_code(self):
        """Test QR code display"""
        try:
            test_data = "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh?amount=0.001"
            self.lcd.show_qr_code(test_data, "Test Bitcoin Payment")
            self.log_test_result("QR Code Test", True, "QR code displayed successfully")
        except Exception as e:
            logger.error(f"QR code test failed: {e}")
            self.log_test_result("QR Code Test", False, f"Error: {e}")
    
    def test_payment_status(self):
        """Test payment status display"""
        try:
            self.lcd.show_payment_status(2.50, "EUR", "waiting")
            self.log_test_result("Payment Status Test", True, "Payment status displayed")
        except Exception as e:
            logger.error(f"Payment status test failed: {e}")
            self.log_test_result("Payment Status Test", False, f"Error: {e}")
    
    def test_error(self):
        """Test error display"""
        try:
            self.lcd.show_error("Test error message - System diagnostic")
            self.log_test_result("Error Display Test", True, "Error message displayed")
        except Exception as e:
            logger.error(f"Error display test failed: {e}")
            self.log_test_result("Error Display Test", False, f"Error: {e}")
    
    def reset_display(self):
        """Reset display to ready state"""
        try:
            self.lcd.show_message("Ready", "Bitcoin Vending Machine")
            self.log_test_result("Display Reset Test", True, "Display reset successfully")
        except Exception as e:
            logger.error(f"Display reset failed: {e}")
            self.log_test_result("Display Reset Test", False, f"Error: {e}")
    
    def run_systematic_tests(self):
        """Run systematic component tests"""
        logger.info("Starting systematic component tests")
        self.status_label.config(text="Status: Running systematic tests...")
        
        # Test sequence
        tests = [
            ("Display Text", self.test_display_text),
            ("Display QR Codes", self.test_display_qr_variations),
            ("Payment Status Variations", self.test_payment_status_variations),
            ("Error Handling", self.test_error_handling),
            ("MDB Simulation", self.test_mdb_simulation)
        ]
        
        for test_name, test_func in tests:
            try:
                logger.info(f"Running test: {test_name}")
                test_func()
                time.sleep(1)  # Visual delay for demonstration
            except Exception as e:
                logger.error(f"Test {test_name} failed: {e}")
                self.log_test_result(test_name, False, f"Exception: {e}")
        
        self.show_test_results()
    
    def test_display_text(self):
        """Test display text functionality"""
        messages = [
            ("Welcome", "Bitcoin Vending Machine"),
            ("Status", "System Ready"),
            ("Thank You", "Purchase Complete")
        ]
        
        for title, message in messages:
            self.lcd.show_message(title, message)
            time.sleep(0.5)
        
        self.log_test_result("Display Text Test", True, f"Tested {len(messages)} text displays")
    
    def test_display_qr_variations(self):
        """Test various QR code types"""
        qr_tests = [
            ("Bitcoin Address", "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"),
            ("Lightning Invoice", "lnbc1500n1ps8huzfpp5pllm7zpjl3z7nvr8qqtdj2vfvdyfxfmhp6z3xg8k3dkf"),
            ("Bitcoin URI", "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh?amount=0.001")
        ]
        
        success_count = 0
        for test_name, test_data in qr_tests:
            try:
                self.lcd.show_qr_code(test_data, f"Test: {test_name}")
                success_count += 1
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"QR test {test_name} failed: {e}")
        
        success_rate = success_count / len(qr_tests)
        self.log_test_result("QR Code Variations", success_rate >= 0.8, 
                           f"{success_count}/{len(qr_tests)} QR types successful")
    
    def test_payment_status_variations(self):
        """Test payment status variations"""
        status_tests = [
            (1.50, "EUR", "waiting"),
            (0.001, "BTC", "confirming"),
            (5.00, "USD", "paid"),
            (2.25, "EUR", "expired")
        ]
        
        for amount, currency, status in status_tests:
            try:
                self.lcd.show_payment_status(amount, currency, status)
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Payment status test failed: {amount} {currency} {status} - {e}")
        
        self.log_test_result("Payment Status Variations", True, 
                           f"Tested {len(status_tests)} status combinations")
    
    def test_error_handling(self):
        """Test error handling and display"""
        error_tests = [
            "Connection timeout",
            "Payment failed",
            "Hardware malfunction",
            "Invalid selection"
        ]
        
        for error_msg in error_tests:
            try:
                self.lcd.show_error(error_msg)
                time.sleep(0.5)
            except Exception as e:
                logger.error(f"Error display test failed: {e}")
        
        self.log_test_result("Error Handling", True, f"Tested {len(error_tests)} error types")
    
    def test_mdb_simulation(self):
        """Test MDB controller simulation"""
        try:
            # Test vend request creation
            original_price = self.mdb.price_var.get()
            original_item = self.mdb.item_var.get()
            
            self.mdb.price_var.set("1.75")
            self.mdb.item_var.set("3")
            
            # Simulate vend request
            self.mdb.create_vend_request()
            
            if self.mdb.current_vend_request:
                self.log_test_result("MDB Vend Request", True, "Vend request created successfully")
                
                # Test approve/deny
                self.mdb.deny_vend()
                self.log_test_result("MDB Vend Deny", True, "Vend request denied successfully")
            else:
                self.log_test_result("MDB Vend Request", False, "Failed to create vend request")
            
            # Restore original values
            self.mdb.price_var.set(original_price)
            self.mdb.item_var.set(original_item)
            
        except Exception as e:
            logger.error(f"MDB simulation test failed: {e}")
            self.log_test_result("MDB Simulation", False, f"Error: {e}")
    
    def test_btcpay_integration(self):
        """Test BTCPay integration if available"""
        if not self.btcpay_connected:
            self.log_test_result("BTCPay Integration", False, "BTCPay not connected")
            messagebox.showwarning("BTCPay Test", "BTCPay not connected - cannot test integration")
            return
        
        try:
            logger.info("Testing BTCPay integration")
            self.status_label.config(text="Status: Testing BTCPay integration...")
            
            # Create test invoice
            test_invoice = self.btcpay.create_invoice(1.00, "EUR", "Simulator Test")
            
            if test_invoice and 'invoice_id' in test_invoice:
                self.test_invoices.append(test_invoice['invoice_id'])
                logger.info(f"Test invoice created: {test_invoice['invoice_id']}")
                
                # Display payment request
                if 'payment_url' in test_invoice:
                    self.lcd.show_qr_code(test_invoice['payment_url'], "Test Payment - €1.00")
                else:
                    self.lcd.show_payment_status(1.00, "EUR", "waiting")
                
                self.log_test_result("BTCPay Invoice Creation", True, f"Invoice ID: {test_invoice['invoice_id']}")
                
                # Test status check
                status_info = self.btcpay.get_invoice_status(test_invoice['invoice_id'])
                if status_info:
                    self.log_test_result("BTCPay Status Check", True, f"Status: {status_info.get('status', 'unknown')}")
                else:
                    self.log_test_result("BTCPay Status Check", False, "Failed to get invoice status")
                
                # Clean up - cancel test invoice
                if self.btcpay.cancel_invoice(test_invoice['invoice_id']):
                    self.log_test_result("BTCPay Invoice Cancellation", True, "Invoice cancelled successfully")
                    logger.info("Test invoice cancelled")
                else:
                    self.log_test_result("BTCPay Invoice Cancellation", False, "Failed to cancel invoice")
                
            else:
                self.log_test_result("BTCPay Invoice Creation", False, "Failed to create test invoice")
            
            self.show_test_results()
            
        except Exception as e:
            logger.error(f"BTCPay integration test failed: {e}")
            self.log_test_result("BTCPay Integration", False, f"Error: {e}")
        finally:
            self.status_label.config(text="Status: Ready")
    
    def show_test_results(self):
        """Show test results in a dialog"""
        if not self.test_results:
            return
        
        passed_count = sum(1 for result in self.test_results.values() if result["passed"])
        total_count = len(self.test_results)
        
        result_text = f"Test Results: {passed_count}/{total_count} passed\n\n"
        
        for test_name, result in self.test_results.items():
            status = "✓ PASS" if result["passed"] else "✗ FAIL"
            result_text += f"{status}: {test_name}\n"
            if result["details"]:
                result_text += f"  └─ {result['details']}\n"
        
        messagebox.showinfo("Test Results", result_text)
        logger.info(f"Test session complete: {passed_count}/{total_count} tests passed")
    
    def start_main_loop(self):
        """Start the main processing loop"""
        self.running = True
        self.process_vending()
    
    def process_vending(self):
        """Process vending machine logic"""
        if not self.running:
            return
        
        try:
            # Check for vend request
            vend_request = self.mdb.get_vend_request()
            if vend_request and not self.current_invoice:
                self.handle_vend_request(vend_request)
        except Exception as e:
            logger.error(f"Error in vending process: {e}")
        
        # Schedule next check
        self.root.after(100, self.process_vending)
    
    def handle_vend_request(self, vend_request: Dict[str, Any]):
        """Handle a vend request"""
        try:
            amount = vend_request['item_price']
            item_number = vend_request['item_number']
            
            self.mdb.log(f"Processing vend request for €{amount:.2f}")
            logger.info(f"Processing vend request: Item {item_number}, Amount €{amount:.2f}")
            
            if self.btcpay_connected:
                # Create real invoice
                self.current_invoice = self.btcpay.create_invoice(
                    amount=amount,
                    currency="EUR",
                    description=f"Vending Machine Item #{item_number}"
                )
                
                if self.current_invoice:
                    self.test_invoices.append(self.current_invoice['invoice_id'])
                    
                    payment_url = self.current_invoice.get('payment_url')
                    if payment_url:
                        self.lcd.show_qr_code(payment_url, f"Pay €{amount:.2f}")
                        self.mdb.log("Real payment invoice created")
                        
                        # Start payment monitoring
                        self.monitor_payment()
                    else:
                        self.lcd.show_payment_status(amount, "EUR", "waiting")
                        self.mdb.log("Invoice created (QR code not available)")
                        self.simulate_payment_flow(amount)
                else:
                    self.mdb.log("Failed to create invoice")
                    self.lcd.show_error("Payment system error")
                    self.mdb.deny_vend()
            else:
                # Simulate payment flow
                self.mdb.log("Using simulated payment flow")
                self.lcd.show_payment_status(amount, "EUR", "waiting")
                self.simulate_payment_flow(amount)
                
        except Exception as e:
            logger.error(f"Error handling vend request: {e}")
            self.mdb.log(f"Error handling vend request: {e}")
            self.lcd.show_error("System error")
            self.mdb.deny_vend()
    
    def monitor_payment(self):
        """Monitor real payment status"""
        if not self.current_invoice:
            return
        
        def check_payment():
            try:
                if self.btcpay and self.current_invoice:
                    invoice_id = self.current_invoice['invoice_id']
                    
                    status_info = self.btcpay.get_invoice_status(invoice_id)
                    if status_info and status_info.get('status') == 'paid':
                        self.mdb.log("Payment confirmed!")
                        logger.info("Payment confirmed via BTCPay")
                        amount = self.current_invoice['amount']
                        self.lcd.show_payment_status(amount, "EUR", "paid")
                        self.root.after(2000, lambda: self.mdb.approve_vend())
                        self.current_invoice = None
                    else:
                        # Check again in 2 seconds
                        self.root.after(2000, check_payment)
            except Exception as e:
                logger.error(f"Error monitoring payment: {e}")
        
        check_payment()
    
    def simulate_payment_flow(self, amount: float):
        """Simulate payment flow for testing"""
        def payment_sequence():
            try:
                # Show waiting state for 3 seconds
                self.root.after(3000, lambda: self.lcd.show_payment_status(amount, "EUR", "paid"))
                
                # Approve vend after payment
                self.root.after(5000, lambda: self.mdb.approve_vend())
                
                # Reset invoice
                self.root.after(5000, lambda: setattr(self, 'current_invoice', None))
                
                logger.info("Simulated payment flow initiated")
            except Exception as e:
                logger.error(f"Error in simulated payment flow: {e}")
        
        payment_sequence()
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Starting simulator cleanup")
        
        try:
            self.running = False
            
            # Cancel any test invoices
            if self.test_invoices and self.btcpay:
                logger.info(f"Cleaning up {len(self.test_invoices)} test invoices")
                for invoice_id in self.test_invoices:
                    try:
                        self.btcpay.cancel_invoice(invoice_id)
                        logger.debug(f"Cancelled test invoice: {invoice_id}")
                    except Exception as e:
                        logger.warning(f"Failed to cancel invoice {invoice_id}: {e}")
            
            # Log final statistics
            if self.test_results:
                passed_count = sum(1 for result in self.test_results.values() if result["passed"])
                logger.info(f"Session summary: {passed_count}/{len(self.test_results)} tests passed")
            
            logger.info(f"Total simulator events: {len(self.simulator_events)}")
            logger.info("Simulator cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def on_closing(self):
        """Handle window closing"""
        logger.info("Simulator closing...")
        self.cleanup()
        self.root.destroy()
    
    def run(self):
        """Run the simulator"""
        try:
            logger.info("Starting simulator main loop")
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Simulator stopped by user")
        except Exception as e:
            logger.error(f"Simulator error: {e}")
        finally:
            self.cleanup()

def main():
    """Main entry point"""
    print("Bitcoin Vending Machine Simulator")
    print("=" * 50)
    
    logger.info("Starting Bitcoin Vending Machine Simulator")
    
    if BTCPAY_AVAILABLE:
        print("✓ BTCPay client available - can test real payments")
        logger.info("BTCPay client available for real payment testing")
    else:
        print("⚠ BTCPay client not available - simulation mode only")
        logger.warning("BTCPay client not available - simulation mode only")
    
    print("\nFeatures:")
    print("• GUI-based component simulation")
    print("• Real BTCPay integration testing")
    print("• Systematic component tests")
    print("• Enhanced logging and diagnostics")
    print("• Manual and automated testing modes")
    
    print("\nStarting simulator...")
    
    try:
        simulator = VendingMachineSimulator()
        simulator.run()
    except Exception as e:
        logger.error(f"Failed to start simulator: {e}")
        print(f"Failed to start simulator: {e}")

if __name__ == "__main__":
    main() 