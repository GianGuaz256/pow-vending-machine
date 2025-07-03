"""
Bitcoin Vending Machine Simulator for Mac Testing
Simulates hardware components using tkinter GUI
"""
import tkinter as tk
from tkinter import ttk, messagebox
import qrcode
from PIL import Image, ImageTk
import threading
import time
import sys
import os
from typing import Optional, Dict, Any

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from src.btcpay_client import BTCPayClient, InvoiceStatus
    from src.config import config
    BTCPAY_AVAILABLE = True
except ImportError:
    BTCPAY_AVAILABLE = False
    print("Warning: BTCPay client not available, using simulation mode")

class SimulatedLCDDisplay:
    """Simulated LCD display using tkinter"""
    
    def __init__(self, master):
        self.master = master
        self.width = 320
        self.height = 480
        
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
    
    def show_message(self, title: str, message: str = ""):
        """Display a message"""
        text = f"{title}\n\n{message}" if message else title
        self.display_label.config(text=text, image='')
    
    def show_qr_code(self, data: str, title: str = "Scan to Pay"):
        """Display QR code"""
        try:
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=8, border=4)
            qr.add_data(data)
            qr.make(fit=True)
            
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img = qr_img.resize((200, 200), Image.Resampling.LANCZOS)
            
            # Convert to tkinter format
            self.qr_photo = ImageTk.PhotoImage(qr_img)
            
            self.display_label.config(text=title, image=self.qr_photo, compound=tk.BOTTOM)
        except Exception as e:
            self.show_message("QR Error", str(e))
    
    def show_payment_status(self, amount: float, currency: str, status: str):
        """Display payment status"""
        colors = {
            "waiting": "yellow",
            "paid": "green", 
            "expired": "red",
            "error": "red"
        }
        color = colors.get(status.lower(), "white")
        
        text = f"{amount:.2f} {currency}\n\n{status.upper()}"
        self.display_label.config(text=text, fg=color, image='')
    
    def show_dispensing(self, item_name: str = "Item"):
        """Show dispensing animation"""
        self.display_label.config(
            text=f"Dispensing...\n\nEnjoy your {item_name}!", 
            fg="green",
            image=''
        )
    
    def show_error(self, error_message: str):
        """Display error message"""
        self.display_label.config(
            text=f"ERROR\n\n{error_message}", 
            fg="red",
            image=''
        )
    
    def clear_screen(self):
        """Clear the display"""
        self.display_label.config(text="", image='')

class SimulatedMDBController:
    """Simulated MDB controller with GUI controls"""
    
    def __init__(self, master, lcd_display):
        self.master = master
        self.lcd_display = lcd_display
        self.is_connected = True
        self.current_vend_request = None
        
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
    
    def log(self, message: str):
        """Log message to status display"""
        self.status_text.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {message}\n")
        self.status_text.see(tk.END)
    
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
            
            # Disable button to prevent multiple requests
            self.vend_button.config(state='disabled', text='Vend Request Active')
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid price and item number")
    
    def get_vend_request(self) -> Optional[Dict[str, Any]]:
        """Get pending vend request"""
        return self.current_vend_request.copy() if self.current_vend_request else None
    
    def approve_vend(self):
        """Approve vend request"""
        if self.current_vend_request:
            self.log("Vend APPROVED - Dispensing item")
            self.lcd_display.show_dispensing(f"Item #{self.current_vend_request['item_number']}")
            
            # Simulate dispensing delay
            threading.Timer(3.0, self.complete_vend).start()
            return True
        return False
    
    def deny_vend(self):
        """Deny vend request"""
        if self.current_vend_request:
            self.log("Vend DENIED")
            self.reset_vend()
            return True
        return False
    
    def complete_vend(self):
        """Complete vending process"""
        self.log("Item dispensed successfully")
        self.reset_vend()
        self.lcd_display.show_message("Complete", "Thank you!")
        threading.Timer(2.0, lambda: self.lcd_display.show_message("Ready", "Bitcoin Vending Machine")).start()
    
    def reset_vend(self):
        """Reset vend request"""
        self.current_vend_request = None
        self.vend_button.config(state='normal', text='Create Vend Request')

class VendingMachineSimulator:
    """Main simulator application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Bitcoin Vending Machine Simulator")
        self.root.geometry("800x600")
        
        # Create main components
        self.lcd = SimulatedLCDDisplay(self.root)
        self.mdb = SimulatedMDBController(self.root, self.lcd)
        
        # BTCPay client (real or simulated)
        if BTCPAY_AVAILABLE:
            self.btcpay = BTCPayClient()
            self.btcpay_connected = self.btcpay.initialize()
        else:
            self.btcpay = None
            self.btcpay_connected = False
        
        self.current_invoice = None
        self.running = False
        
        # Create control buttons
        self.create_control_buttons()
        
        # Initial display
        self.lcd.show_message("Ready", "Bitcoin Vending Machine")
        
        # Start main loop
        self.start_main_loop()
    
    def create_control_buttons(self):
        """Create control buttons"""
        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.BOTTOM, pady=10)
        
        # Test buttons
        tk.Button(button_frame, text="Test QR Code", 
                 command=self.test_qr_code).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Test Payment Status", 
                 command=self.test_payment_status).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Test Error", 
                 command=self.test_error).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Reset Display", 
                 command=self.reset_display).pack(side=tk.LEFT, padx=5)
    
    def test_qr_code(self):
        """Test QR code display"""
        test_data = "lnbc2500n1pvjluezpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqd"
        self.lcd.show_qr_code(test_data, "Test Lightning Invoice")
    
    def test_payment_status(self):
        """Test payment status display"""
        self.lcd.show_payment_status(2.50, "EUR", "waiting")
    
    def test_error(self):
        """Test error display"""
        self.lcd.show_error("Test error message")
    
    def reset_display(self):
        """Reset display to ready state"""
        self.lcd.show_message("Ready", "Bitcoin Vending Machine")
    
    def start_main_loop(self):
        """Start the main processing loop"""
        self.running = True
        self.process_vending()
    
    def process_vending(self):
        """Process vending machine logic"""
        if not self.running:
            return
        
        # Check for vend request
        vend_request = self.mdb.get_vend_request()
        if vend_request and not self.current_invoice:
            self.handle_vend_request(vend_request)
        
        # Schedule next check
        self.root.after(100, self.process_vending)
    
    def handle_vend_request(self, vend_request: Dict[str, Any]):
        """Handle a vend request"""
        try:
            amount = vend_request['item_price']
            item_number = vend_request['item_number']
            
            self.mdb.log(f"Processing vend request for €{amount:.2f}")
            
            if self.btcpay_connected:
                # Create real invoice
                self.current_invoice = self.btcpay.create_invoice(
                    amount=amount,
                    currency="EUR",
                    description=f"Vending Machine Item #{item_number}"
                )
                
                if self.current_invoice:
                    lightning_invoice = self.current_invoice.get('lightning_invoice')
                    if lightning_invoice:
                        self.lcd.show_qr_code(lightning_invoice, f"Pay €{amount:.2f}")
                        self.mdb.log("Real Lightning invoice created")
                        
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
            self.mdb.log(f"Error handling vend request: {e}")
            self.lcd.show_error("System error")
            self.mdb.deny_vend()
    
    def monitor_payment(self):
        """Monitor real payment status"""
        if not self.current_invoice:
            return
        
        def check_payment():
            if self.btcpay and self.current_invoice:
                invoice_id = self.current_invoice['invoice_id']
                
                if self.btcpay.is_invoice_paid(invoice_id):
                    self.mdb.log("Payment confirmed!")
                    amount = self.current_invoice['amount']
                    self.lcd.show_payment_status(amount, "EUR", "paid")
                    self.root.after(2000, lambda: self.mdb.approve_vend())
                    self.current_invoice = None
                else:
                    # Check again in 2 seconds
                    self.root.after(2000, check_payment)
        
        check_payment()
    
    def simulate_payment_flow(self, amount: float):
        """Simulate payment flow for testing"""
        def payment_sequence():
            # Show waiting state for 3 seconds
            self.root.after(3000, lambda: self.lcd.show_payment_status(amount, "EUR", "paid"))
            
            # Approve vend after payment
            self.root.after(5000, lambda: self.mdb.approve_vend())
            
            # Reset invoice
            self.root.after(5000, lambda: setattr(self, 'current_invoice', None))
        
        payment_sequence()
    
    def run(self):
        """Run the simulator"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            print("Simulator stopped by user")
        finally:
            self.running = False

def main():
    """Main entry point"""
    print("Bitcoin Vending Machine Simulator")
    print("=" * 40)
    
    if BTCPAY_AVAILABLE:
        print("✓ BTCPay client available - can test real payments")
    else:
        print("⚠ BTCPay client not available - simulation mode only")
    
    print("\nStarting simulator...")
    
    simulator = VendingMachineSimulator()
    simulator.run()

if __name__ == "__main__":
    main() 