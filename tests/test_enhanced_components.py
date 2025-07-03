"""
Enhanced Component Testing for Bitcoin Vending Machine
Specific tests for LCD QR display, MDB response, and BTCPay server connection
"""
import sys
import os
import time
import logging

# Add project root and src to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from config import config
from lcd_display import LCDDisplay
from mdb_controller import MDBController
from btcpay_client import BTCPayClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_lcd_qr_functionality():
    """Test LCD QR Code Generation and Display"""
    print("\n=== LCD QR CODE FUNCTIONALITY TEST ===")
    
    try:
        display = LCDDisplay()
        if not display.initialize():
            print("✗ LCD initialization failed")
            return False
        
        print("✓ LCD initialized successfully")
        
        # Test different QR code types
        qr_tests = [
            ("Bitcoin Address", "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"),
            ("Lightning Invoice", "lnbc1500n1ps8huzfpp5pllm7zpjl3z7nvr8qqtdj2vfvdyfxfmhp6z3xg8k3dkf"),
            ("Simple URL", "https://bitcoin.org"),
            ("Text Data", "Hello Bitcoin World!")
        ]
        
        success_count = 0
        for test_name, test_data in qr_tests:
            try:
                print(f"Testing QR: {test_name}")
                display.show_qr_code(test_data, f"QR: {test_name}")
                time.sleep(2)
                success_count += 1
                print(f"✓ QR Code {test_name}: SUCCESS")
            except Exception as e:
                print(f"✗ QR Code {test_name}: FAILED - {e}")
        
        # Test payment status display
        try:
            display.show_payment_status(2.50, "EUR", "waiting")
            time.sleep(1)
            display.show_payment_status(2.50, "EUR", "paid")
            time.sleep(1)
            print("✓ Payment status display: SUCCESS")
            success_count += 1
        except Exception as e:
            print(f"✗ Payment status display: FAILED - {e}")
        
        display.close()
        
        total_tests = len(qr_tests) + 1
        print(f"LCD QR Tests: {success_count}/{total_tests} passed")
        return success_count == total_tests
        
    except Exception as e:
        print(f"✗ LCD QR test failed: {e}")
        return False

def test_mdb_response():
    """Test MDB Controller Response and Communication"""
    print("\n=== MDB CONTROLLER RESPONSE TEST ===")
    
    try:
        mdb = MDBController()
        
        # Check if hardware is available
        hardware_available = os.path.exists('/dev/ttyAMA0') or os.path.exists('/dev/ttyUSB0')
        
        if hardware_available:
            print("Hardware detected - testing real MDB communication")
            init_success = mdb.initialize()
            if not init_success:
                print("✗ MDB hardware initialization failed")
                return False
            print("✓ MDB hardware initialized")
        else:
            print("⚠ No MDB hardware detected - testing in simulation mode")
        
        # Test status retrieval
        try:
            status = mdb.get_status()
            if isinstance(status, dict) and 'state' in status:
                print(f"✓ MDB status retrieved: {status['state']}")
                status_test_passed = True
            else:
                print("✗ MDB status format invalid")
                status_test_passed = False
        except Exception as e:
            print(f"✗ MDB status retrieval failed: {e}")
            status_test_passed = False
        
        # Test connection health
        try:
            connection_healthy = mdb.check_connection()
            if hardware_available:
                print(f"✓ MDB connection health: {'HEALTHY' if connection_healthy else 'ISSUES'}")
            else:
                print("⚠ MDB connection test skipped (no hardware)")
            connection_test_passed = True
        except Exception as e:
            print(f"✗ MDB connection test failed: {e}")
            connection_test_passed = False
        
        mdb.close()
        
        # Return true if either we're in simulation mode or hardware tests passed
        if hardware_available:
            return status_test_passed and connection_test_passed
        else:
            return status_test_passed  # In simulation, just check status works
        
    except Exception as e:
        print(f"✗ MDB response test failed: {e}")
        return False

def test_btcpay_connection():
    """Test BTCPay Server Connection and API"""
    print("\n=== BTCPAY SERVER CONNECTION TEST ===")
    
    try:
        btcpay = BTCPayClient()
        
        # Check configuration
        config_complete = (config.btcpay.server_url and 
                          config.btcpay.store_id and 
                          config.btcpay.api_key)
        
        print(f"Server URL: {config.btcpay.server_url}")
        print(f"Store ID: {'[CONFIGURED]' if config.btcpay.store_id else '[NOT SET]'}")
        print(f"API Key: {'[CONFIGURED]' if config.btcpay.api_key else '[NOT SET]'}")
        
        if not config_complete:
            print("⚠ BTCPay configuration incomplete - limited testing")
            return False
        
        # Test server connection
        try:
            connection_success = btcpay.initialize()
            if connection_success:
                print("✓ BTCPay server connection: SUCCESS")
            else:
                print("✗ BTCPay server connection: FAILED")
                return False
        except Exception as e:
            print(f"✗ BTCPay server connection error: {e}")
            return False
        
        # Test invoice creation
        try:
            test_invoice = btcpay.create_invoice(1.00, "EUR", "Component Test")
            if test_invoice and 'invoice_id' in test_invoice:
                print(f"✓ Invoice creation: SUCCESS (ID: {test_invoice['invoice_id']})")
                
                # Test invoice status check
                try:
                    status_info = btcpay.get_invoice_status(test_invoice['invoice_id'])
                    if status_info and 'status' in status_info:
                        print(f"✓ Invoice status check: SUCCESS (Status: {status_info['status']})")
                        invoice_tests_passed = True
                    else:
                        print("✗ Invoice status check: FAILED")
                        invoice_tests_passed = False
                except Exception as e:
                    print(f"✗ Invoice status check error: {e}")
                    invoice_tests_passed = False
                
                # Clean up - cancel test invoice
                try:
                    btcpay.cancel_invoice(test_invoice['invoice_id'])
                    print("✓ Test invoice cancelled")
                except:
                    pass  # Not critical if cleanup fails
                
            else:
                print("✗ Invoice creation: FAILED")
                invoice_tests_passed = False
        except Exception as e:
            print(f"✗ Invoice creation error: {e}")
            invoice_tests_passed = False
        
        return connection_success and invoice_tests_passed
        
    except Exception as e:
        print(f"✗ BTCPay connection test failed: {e}")
        return False

def main():
    """Run enhanced component tests"""
    print("Bitcoin Vending Machine - Enhanced Component Tests")
    print("=" * 60)
    print("Focus: LCD QR Display, MDB Response, BTCPay Connection")
    print("=" * 60)
    
    results = {}
    
    # Run specific component tests
    results['LCD_QR'] = test_lcd_qr_functionality()
    results['MDB_Response'] = test_mdb_response()
    results['BTCPay_Connection'] = test_btcpay_connection()
    
    # Summary
    print("\n" + "=" * 60)
    print("ENHANCED TEST SUMMARY")
    print("=" * 60)
    
    for component, passed in results.items():
        status = "PASS" if passed else "FAIL"
        icon = "✓" if passed else "✗"
        print(f"{icon} {component.replace('_', ' ')}: {status}")
    
    passed_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    print(f"\nOverall: {passed_count}/{total_count} components passed")
    
    if passed_count == total_count:
        print("🎉 All enhanced tests passed!")
    elif passed_count >= 2:
        print("✅ Core functionality working")
    elif passed_count >= 1:
        print("⚠️ Partial functionality - check configuration")
    else:
        print("❌ Major issues detected - check system setup")
    
    return passed_count >= 2  # Consider success if at least 2/3 pass

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 