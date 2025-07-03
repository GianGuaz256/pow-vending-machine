"""
Mac Testing Script for Bitcoin Vending Machine
Tests individual components on macOS before deployment to Raspberry Pi
"""
import sys
import os
import time

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    
    try:
        from src.config import config
        print("✓ Config module imported")
    except ImportError as e:
        print(f"✗ Config import failed: {e}")
        return False
    
    try:
        # These will fail on Mac due to hardware dependencies
        from src.lcd_display import LCDDisplay
        print("✓ LCD Display module imported (will use pygame)")
    except ImportError as e:
        print(f"⚠ LCD Display import failed: {e}")
    
    try:
        from src.mdb_controller import MDBController
        print("⚠ MDB Controller imported (will fail without hardware)")
    except ImportError as e:
        print(f"⚠ MDB Controller import failed: {e}")
    
    try:
        from src.btcpay_client import BTCPayClient
        print("✓ BTCPay Client module imported")
    except ImportError as e:
        print(f"✗ BTCPay Client import failed: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from src.config import config
        
        print(f"Display config: {config.display.width}x{config.display.height}")
        print(f"MDB port: {config.mdb.serial_port}")
        print(f"BTCPay URL: {config.btcpay.server_url}")
        print(f"Currency: {config.vending.currency}")
        
        return True
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_btcpay_client():
    """Test BTCPay client (without real connection)"""
    print("\nTesting BTCPay client...")
    
    try:
        from src.btcpay_client import BTCPayClient
        
        client = BTCPayClient()
        status = client.get_status()
        print(f"BTCPay status: {status}")
        
        # Test connection (will likely fail without proper config)
        if client.check_connection():
            print("✓ BTCPay connection successful")
        else:
            print("⚠ BTCPay connection failed (expected without configuration)")
        
        return True
    except Exception as e:
        print(f"⚠ BTCPay test failed: {e}")
        return False

def test_display_simulation():
    """Test display using pygame (Mac compatible)"""
    print("\nTesting display simulation...")
    
    try:
        from src.lcd_display import LCDDisplay
        
        display = LCDDisplay()
        
        if display.initialize():
            print("✓ Display initialized with pygame")
            
            # Test different display modes
            display.show_message("Mac Test", "Testing on macOS")
            time.sleep(1)
            
            # Test QR code
            test_qr = "lnbc2500n1pvjluezpp5qqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqqqsyqcyq5rqwzqfqypqd"
            display.show_qr_code(test_qr, "Test QR Code")
            time.sleep(2)
            
            # Test payment status
            display.show_payment_status(2.50, "EUR", "waiting")
            time.sleep(1)
            
            display.close()
            print("✓ Display tests completed")
            return True
        else:
            print("✗ Display initialization failed")
            return False
            
    except Exception as e:
        print(f"⚠ Display test failed: {e}")
        return False

def test_package_structure():
    """Test if the package structure is correct"""
    print("\nTesting package structure...")
    
    try:
        # Test if src package can be imported
        import src
        print("✓ src package structure is correct")
        
        # Test main classes
        from src import VendingMachine, config, LCDDisplay, BTCPayClient
        print("✓ Main classes can be imported from package")
        
        return True
    except ImportError as e:
        print(f"✗ Package structure test failed: {e}")
        return False

def main():
    """Run all Mac-specific tests"""
    print("Bitcoin Vending Machine - Mac Testing")
    print("=" * 50)
    print("Testing compatibility before Raspberry Pi deployment\n")
    
    tests = [
        ("Package Structure", test_package_structure),
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("BTCPay Client", test_btcpay_client),
        ("Display Simulation", test_display_simulation),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("MAC TESTING SUMMARY:")
    print("=" * 50)
    
    for test_name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        icon = "✓" if passed else "✗"
        print(f"{icon} {test_name}: {status}")
    
    passed_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    print(f"\nPassed: {passed_count}/{total_count}")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! Ready for Raspberry Pi deployment.")
    elif passed_count >= total_count * 0.7:
        print("\n⚠️ Most tests passed. Some failures are expected on Mac.")
        print("   Hardware-dependent components will work on Raspberry Pi.")
    else:
        print("\n❌ Many tests failed. Check configuration and dependencies.")
    
    print("\nNext steps:")
    print("1. Fix any configuration issues")
    print("2. Test simulator: python tests/simulator.py")
    print("3. Deploy to Raspberry Pi for full hardware testing")

if __name__ == "__main__":
    main() 