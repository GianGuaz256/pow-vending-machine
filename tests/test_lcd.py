"""
LCD Display Component Test
Comprehensive testing for Waveshare LCD display functionality
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

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LCDTestSuite:
    """Comprehensive LCD Display Test Suite"""
    
    def __init__(self):
        self.display = None
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
    
    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.test_results[test_name] = {"passed": passed, "details": details}
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
        
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {test_name}")
        if details:
            print(f"    └─ {details}")
    
    def test_initialization(self):
        """Test LCD display initialization"""
        print("\n1. Testing LCD Initialization...")
        
        try:
            self.display = LCDDisplay()
            init_success = self.display.initialize()
            
            if init_success:
                self.log_test_result("LCD Initialization", True, 
                                   f"Display initialized: {config.display.width}x{config.display.height}")
                return True
            else:
                self.log_test_result("LCD Initialization", False, "Display failed to initialize")
                return False
        except Exception as e:
            self.log_test_result("LCD Initialization", False, f"Initialization error: {e}")
            return False
    
    def test_basic_display(self):
        """Test basic text display functionality"""
        print("\n2. Testing Basic Display Functions...")
        
        if not self.display or not self.display.is_initialized:
            self.log_test_result("Basic Display", False, "Display not initialized")
            return False
        
        try:
            # Test clear screen
            self.display.clear_screen()
            time.sleep(0.5)
            self.log_test_result("Clear Screen", True, "Screen cleared successfully")
            
            # Test basic message
            self.display.show_message("LCD Test", "Basic text display working")
            time.sleep(1)
            self.log_test_result("Basic Message", True, "Message displayed successfully")
            
            # Test long message
            long_message = "This is a longer message to test text wrapping and multi-line display functionality"
            self.display.show_message("Long Text Test", long_message)
            time.sleep(2)
            self.log_test_result("Long Message", True, "Long message with wrapping displayed")
            
            return True
        except Exception as e:
            self.log_test_result("Basic Display", False, f"Display error: {e}")
            return False
    
    def test_qr_code_generation(self):
        """Test QR code generation and display"""
        print("\n3. Testing QR Code Generation...")
        
        if not self.display or not self.display.is_initialized:
            self.log_test_result("QR Code Generation", False, "Display not initialized")
            return False
        
        qr_test_cases = [
            ("Simple Text", "Hello Bitcoin World!", "Basic text QR code"),
            ("Bitcoin Address", "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh", "Bitcoin address QR code"),
            ("Lightning Invoice", "lnbc1500n1ps8huzfpp5pllm7zpjl3z7nvr8qqtdj2vfvdyfxfmhp6z3xg8k3dkf0", "Lightning payment QR code"),
            ("URL", "https://bitcoin.org", "Website URL QR code"),
            ("Large Data", "This is a much longer string with more complex data to test QR code generation limits and ensure proper scaling", "Large data QR code")
        ]
        
        success_count = 0
        for test_name, test_data, description in qr_test_cases:
            try:
                self.display.show_qr_code(test_data, f"QR: {test_name}")
                time.sleep(1.5)
                self.log_test_result(f"QR Code - {test_name}", True, description)
                success_count += 1
            except Exception as e:
                self.log_test_result(f"QR Code - {test_name}", False, f"QR generation failed: {e}")
        
        overall_success = success_count == len(qr_test_cases)
        self.log_test_result("QR Code Overall", overall_success, 
                           f"Generated {success_count}/{len(qr_test_cases)} QR codes successfully")
        
        return overall_success
    
    def test_payment_status_display(self):
        """Test payment status display functionality"""
        print("\n4. Testing Payment Status Display...")
        
        if not self.display or not self.display.is_initialized:
            self.log_test_result("Payment Status", False, "Display not initialized")
            return False
        
        payment_test_cases = [
            (1.50, "EUR", "waiting", "Waiting for payment"),
            (2.00, "USD", "paid", "Payment received"),
            (0.75, "EUR", "expired", "Payment expired"),
            (5.00, "BTC", "error", "Payment error"),
            (10.99, "EUR", "confirmed", "Payment confirmed")
        ]
        
        success_count = 0
        for amount, currency, status, description in payment_test_cases:
            try:
                self.display.show_payment_status(amount, currency, status)
                time.sleep(1)
                self.log_test_result(f"Payment Status - {status}", True, 
                                   f"{amount} {currency} - {description}")
                success_count += 1
            except Exception as e:
                self.log_test_result(f"Payment Status - {status}", False, 
                                   f"Status display failed: {e}")
        
        overall_success = success_count == len(payment_test_cases)
        return overall_success
    
    def test_error_display(self):
        """Test error message display"""
        print("\n5. Testing Error Display...")
        
        if not self.display or not self.display.is_initialized:
            self.log_test_result("Error Display", False, "Display not initialized")
            return False
        
        error_test_cases = [
            "Connection Error",
            "Payment Failed",
            "System Malfunction",
            "Timeout Occurred",
            "Invalid Selection"
        ]
        
        success_count = 0
        for error_msg in error_test_cases:
            try:
                self.display.show_error(error_msg)
                time.sleep(1)
                self.log_test_result(f"Error - {error_msg}", True, "Error message displayed")
                success_count += 1
            except Exception as e:
                self.log_test_result(f"Error - {error_msg}", False, f"Error display failed: {e}")
        
        return success_count == len(error_test_cases)
    
    def test_system_status_display(self):
        """Test system status display"""
        print("\n6. Testing System Status Display...")
        
        if not self.display or not self.display.is_initialized:
            self.log_test_result("System Status", False, "Display not initialized")
            return False
        
        status_test_cases = [
            (True, True, True, "All systems operational"),
            (True, False, True, "BTCPay server offline"),
            (False, True, True, "MDB controller offline"),
            (True, True, False, "Display issues"),
            (False, False, False, "All systems offline")
        ]
        
        success_count = 0
        for mdb_status, btcpay_status, display_status, description in status_test_cases:
            try:
                self.display.show_system_status(mdb_status, btcpay_status, display_status)
                time.sleep(1)
                self.log_test_result(f"System Status", True, description)
                success_count += 1
            except Exception as e:
                self.log_test_result(f"System Status", False, f"Status display failed: {e}")
        
        return success_count == len(status_test_cases)
    
    def test_dispensing_animation(self):
        """Test dispensing animation display"""
        print("\n7. Testing Dispensing Animation...")
        
        if not self.display or not self.display.is_initialized:
            self.log_test_result("Dispensing Animation", False, "Display not initialized")
            return False
        
        try:
            # Test different item names
            items = ["Coca Cola", "Snickers Bar", "Water Bottle", "Energy Drink"]
            
            for item in items:
                self.display.show_dispensing(item)
                time.sleep(1.5)
            
            self.log_test_result("Dispensing Animation", True, f"Tested {len(items)} dispensing animations")
            return True
        except Exception as e:
            self.log_test_result("Dispensing Animation", False, f"Animation failed: {e}")
            return False
    
    def test_performance(self):
        """Test display performance and responsiveness"""
        print("\n8. Testing Display Performance...")
        
        if not self.display or not self.display.is_initialized:
            self.log_test_result("Performance Test", False, "Display not initialized")
            return False
        
        try:
            # Test rapid screen updates
            start_time = time.time()
            
            for i in range(10):
                self.display.show_message(f"Performance Test {i+1}", f"Update #{i+1}/10")
                time.sleep(0.1)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Performance should be reasonable (less than 5 seconds for 10 updates)
            performance_good = total_time < 5.0
            
            self.log_test_result("Performance Test", performance_good, 
                               f"10 updates in {total_time:.2f}s")
            return performance_good
        except Exception as e:
            self.log_test_result("Performance Test", False, f"Performance test failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up display resources"""
        print("\n9. Cleaning Up...")
        
        try:
            if self.display:
                self.display.clear_screen()
                self.display.show_message("Test Complete", "LCD tests finished successfully")
                time.sleep(2)
                self.display.close()
                self.log_test_result("Cleanup", True, "Display resources cleaned up")
        except Exception as e:
            self.log_test_result("Cleanup", False, f"Cleanup failed: {e}")
    
    def run_all_tests(self):
        """Run all LCD tests"""
        print("=" * 60)
        print("LCD DISPLAY COMPONENT TEST SUITE")
        print("=" * 60)
        print(f"Display Configuration: {config.display.width}x{config.display.height}")
        
        # Run tests in sequence
        if not self.test_initialization():
            print("\n❌ LCD initialization failed - skipping remaining tests")
            return False
        
        self.test_basic_display()
        self.test_qr_code_generation()
        self.test_payment_status_display()
        self.test_error_display()
        self.test_system_status_display()
        self.test_dispensing_animation()
        self.test_performance()
        
        # Always try cleanup
        self.cleanup()
        
        # Print summary
        print("\n" + "=" * 60)
        print("LCD TEST SUMMARY")
        print("=" * 60)
        
        for test_name, result in self.test_results.items():
            status = "PASS" if result["passed"] else "FAIL"
            print(f"{status:4} | {test_name}")
        
        print(f"\nTotal: {self.passed_tests}/{self.total_tests} tests passed")
        
        success_rate = (self.passed_tests / self.total_tests) * 100 if self.total_tests > 0 else 0
        
        if success_rate == 100:
            print("🎉 All LCD tests passed! Display is fully functional.")
        elif success_rate >= 80:
            print("✅ LCD display mostly functional - minor issues detected.")
        elif success_rate >= 50:
            print("⚠️ LCD display partially functional - significant issues detected.")
        else:
            print("❌ LCD display has major issues - check hardware and configuration.")
        
        return success_rate >= 80

def main():
    """Main test function"""
    test_suite = LCDTestSuite()
    success = test_suite.run_all_tests()
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 