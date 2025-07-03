"""
Individual Component Testing for Bitcoin Vending Machine
Test each component (LCD, MDB, BTCPay) independently
"""
import sys
import os
import time
import logging

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.config import config
from src.lcd_display import LCDDisplay
from src.mdb_controller import MDBController
from src.btcpay_client import BTCPayClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_lcd_display():
    """Test LCD display functionality"""
    print("\n=== Testing LCD Display ===")
    
    try:
        display = LCDDisplay()
        
        # Test initialization
        if display.initialize():
            print("✓ Display initialized successfully")
            
            # Test message display
            display.show_message("Test Message", "Display working correctly")
            time.sleep(2)
            
            # Test QR code display
            test_qr_data = "lnbc1500n1ps8huzfpp5pllm7zpjl3z7nvr8qqtdj2vfvdyfxfmhp6z3xg8k3dkf"
            display.show_qr_code(test_qr_data, "Test QR Code")
            time.sleep(3)
            
            # Test payment status
            display.show_payment_status(2.50, "EUR", "waiting")
            time.sleep(2)
            
            # Test dispensing animation
            display.show_dispensing("Test Item")
            time.sleep(2)
            
            # Test error display
            display.show_error("Test error message")
            time.sleep(2)
            
            # Test system status
            display.show_system_status(True, True, True)
            time.sleep(2)
            
            display.close()
            print("✓ All display tests passed")
            return True
        else:
            print("✗ Display initialization failed")
            return False
            
    except Exception as e:
        print(f"✗ Display test failed: {e}")
        return False

def test_mdb_controller():
    """Test MDB controller functionality"""
    print("\n=== Testing MDB Controller ===")
    
    try:
        mdb = MDBController()
        
        # Test initialization
        if mdb.initialize():
            print("✓ MDB controller initialized successfully")
            
            # Test status checking
            status = mdb.get_status()
            print(f"✓ MDB status: {status}")
            
            # Test connection check
            if mdb.check_connection():
                print("✓ MDB connection healthy")
            else:
                print("⚠ MDB connection check failed (expected if no hardware)")
            
            mdb.close()
            print("✓ MDB controller tests completed")
            return True
        else:
            print("⚠ MDB initialization failed (expected without hardware)")
            return False
            
    except Exception as e:
        print(f"⚠ MDB test failed (expected without hardware): {e}")
        return False

def test_btcpay_client():
    """Test BTCPay Server client functionality"""
    print("\n=== Testing BTCPay Client ===")
    
    try:
        btcpay = BTCPayClient()
        
        # Test configuration
        status = btcpay.get_status()
        print(f"BTCPay configuration: {status}")
        
        # Test connection (will fail without proper config)
        if btcpay.initialize():
            print("✓ BTCPay client initialized successfully")
            
            # Test invoice creation
            invoice = btcpay.create_invoice(1.50, "EUR", "Test Purchase")
            if invoice:
                print(f"✓ Invoice created: {invoice['invoice_id']}")
                
                # Test invoice status
                status_info = btcpay.get_invoice_status(invoice['invoice_id'])
                if status_info:
                    print(f"✓ Invoice status: {status_info['status']}")
                
                # Test invoice cancellation
                if btcpay.cancel_invoice(invoice['invoice_id']):
                    print("✓ Invoice cancelled successfully")
                
            return True
        else:
            print("⚠ BTCPay initialization failed (check configuration)")
            return False
            
    except Exception as e:
        print(f"⚠ BTCPay test failed: {e}")
        return False

def test_configuration():
    """Test configuration validation"""
    print("\n=== Testing Configuration ===")
    
    try:
        print(f"Display config: {config.display}")
        print(f"MDB config: {config.mdb}")
        print(f"BTCPay config: {config.btcpay}")
        print(f"Vending config: {config.vending}")
        print(f"System config: {config.system}")
        
        # Test validation
        if config.validate():
            print("✓ Configuration validation passed")
            return True
        else:
            print("⚠ Configuration validation failed")
            return False
            
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def main():
    """Run all component tests"""
    print("Bitcoin Vending Machine - Component Tests")
    print("=" * 50)
    
    results = {}
    
    # Test configuration first
    results['config'] = test_configuration()
    
    # Test individual components
    results['display'] = test_lcd_display()
    results['mdb'] = test_mdb_controller()
    results['btcpay'] = test_btcpay_client()
    
    # Summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY:")
    for component, passed in results.items():
        status = "PASS" if passed else "FAIL/SKIP"
        print(f"{component.upper()}: {status}")
    
    passed_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    print(f"\nPassed: {passed_count}/{total_count}")
    
    if passed_count == total_count:
        print("🎉 All tests passed!")
    elif passed_count > 0:
        print("⚠️ Some tests passed (hardware-dependent failures expected)")
    else:
        print("❌ All tests failed - check configuration")

if __name__ == "__main__":
    main() 