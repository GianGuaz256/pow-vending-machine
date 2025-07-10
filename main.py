#!/usr/bin/env python3
"""
Bitcoin Lightning Vending Machine - Main Entry Point
Simple launcher for the vending machine application
"""
import sys
import os
import argparse

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Bitcoin Vending Machine')
    parser.add_argument('--sim', '--simulator', action='store_true', 
                       help='Run in simulator mode with interactive terminal interface')
    parser.add_argument('--test', action='store_true',
                       help='Run the full test simulator')
    
    args = parser.parse_args()
    
    try:
        if args.test:
            # Run the full test simulator
            from tests.simulator import main as simulator_main
            simulator_main()
        elif args.sim:
            # Run with simulation capabilities
            from src.vending_machine_sim import main as sim_main
            sim_main()
        else:
            # Run normal hardware mode
            from src.vending_machine import main as vending_main
            print("Starting Bitcoin Vending Machine...")
            print("Note: This mode requires physical hardware (MDB controller)")
            print("For testing without hardware, use: python main.py --sim")
            print("For full test suite, use: python main.py --test")
            print()
            vending_main()
    except ImportError as e:
        print(f"Error importing vending machine: {e}")
        print("Make sure you're running from the project root directory")
        if "vending_machine_sim" in str(e):
            print("Simulation mode not available. Creating simulation module...")
            create_sim_module()
            print("Please run the command again.")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting vending machine: {e}")
        sys.exit(1)

def create_sim_module():
    """Create a simplified simulation module"""
    sim_content = '''"""
Simplified Vending Machine Simulator
Provides interactive testing capabilities for the main vending machine
"""
import threading
import time
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src'))

from vending_machine import VendingMachine, VendingMachineState
import logging

logger = logging.getLogger(__name__)

class InteractiveVendingMachine(VendingMachine):
    """Extended vending machine with interactive capabilities"""
    
    def __init__(self):
        super().__init__()
        self.simulation_mode = True
        self.products = {
            "1": {"name": "Coca Cola", "price": 1.50},
            "2": {"name": "Sprite", "price": 1.50}, 
            "3": {"name": "Water", "price": 1.00},
            "4": {"name": "Coffee", "price": 2.00},
            "5": {"name": "Snacks", "price": 1.75},
        }
    
    def run(self):
        """Override run method to include interactive simulation"""
        if not self.initialize():
            logger.error("Failed to initialize, exiting")
            return
        
        self.running = True
        logger.info("Starting interactive vending machine")
        
        # Start the main state machine in a separate thread
        state_thread = threading.Thread(target=self._run_state_machine, daemon=True)
        state_thread.start()
        
        # Run interactive menu in main thread
        self._run_interactive_menu()
    
    def _run_state_machine(self):
        """Run the main state machine"""
        try:
            while self.running:
                self._process_state()
                time.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in state machine: {e}")
            self.running = False
    
    def _run_interactive_menu(self):
        """Run interactive menu for simulation"""
        try:
            while self.running:
                self._show_menu()
                choice = self._get_user_input()
                
                if choice == "0":
                    print("\\nExiting...")
                    self.running = False
                    break
                elif choice in self.products:
                    self._simulate_vend_request(choice)
                elif choice == "9":
                    self._show_status()
                else:
                    print("❌ Invalid selection. Please try again.")
                    
        except KeyboardInterrupt:
            print("\\n\\nShutting down...")
            self.running = False
    
    def _show_menu(self):
        """Display interactive menu"""
        print("\\n" + "="*50)
        print("🪙 BITCOIN VENDING MACHINE - SIMULATION MODE")
        print("="*50)
        print("Available Products:")
        print("-"*30)
        
        for num, product in self.products.items():
            print(f"  {num}. {product['name']:<15} €{product['price']:.2f}")
        
        print("-"*30)
        print("  9. Show Status")
        print("  0. Exit")
        print("="*50)
        print(f"Current State: {self.state.value}")
        print("💡 Check your display for visual output")
    
    def _get_user_input(self):
        """Get user input"""
        try:
            return input("\\nSelect product (0-9): ").strip()
        except (EOFError, KeyboardInterrupt):
            return "0"
    
    def _simulate_vend_request(self, product_id):
        """Simulate a vend request"""
        if self.state != VendingMachineState.READY:
            print(f"❌ Cannot process request. Current state: {self.state.value}")
            return
        
        product = self.products[product_id]
        print(f"\\n🔄 Processing {product['name']} (€{product['price']:.2f})")
        
        # Create simulated vend request
        vend_request = {
            'item_number': product_id,
            'item_price': product['price']
        }
        
        # Simulate MDB vend request
        self.current_vend_request = vend_request
        self._set_state(VendingMachineState.VEND_REQUEST)
        
        print("💳 Payment QR code should appear on display")
        print("⏳ Waiting for payment...")
    
    def _show_status(self):
        """Show system status"""
        print("\\n" + "="*40)
        print("📊 SYSTEM STATUS")
        print("="*40)
        print(f"State: {self.state.value}")
        print(f"Display: {'✓' if self.component_status['display'] else '❌'}")
        print(f"MDB: {'✓' if self.component_status['mdb'] else '❌'}")
        print(f"BTCPay: {'✓' if self.component_status['btcpay'] else '❌'}")
        
        if self.current_invoice:
            print(f"\\nActive Invoice: {self.current_invoice.get('invoice_id', 'N/A')}")
            print(f"Amount: €{self.current_invoice.get('amount', 0):.2f}")
        
        if self.current_vend_request:
            item_num = self.current_vend_request.get('item_number', 'N/A')
            print(f"\\nPending Vend: Item #{item_num}")
        
        print("="*40)

def main():
    """Main entry point for simulation mode"""
    try:
        print("🚀 Starting Bitcoin Vending Machine Simulator...")
        print("This mode provides interactive testing without requiring physical hardware.\\n")
        
        machine = InteractiveVendingMachine()
        machine.run()
        
    except KeyboardInterrupt:
        print("\\n\\nSimulator stopped by user")
    except Exception as e:
        logger.error(f"Simulator error: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
'''
    
    # Create the simulation module
    sim_file = os.path.join(os.path.dirname(__file__), 'src', 'vending_machine_sim.py')
    with open(sim_file, 'w') as f:
        f.write(sim_content)
    
    print(f"Created simulation module: {sim_file}")

if __name__ == "__main__":
    main() 