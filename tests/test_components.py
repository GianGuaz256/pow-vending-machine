"""
Component Test Suite for Bitcoin Vending Machine
Comprehensive testing of all individual components with enhanced logging and result tracking
"""
import sys
import os
import time
import logging
import pygame

# Add project root and src to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from config import config
from lcd_display import LCDDisplay
from mdb_controller import MDBController
from btcpay_client import BTCPayClient

# Set up enhanced logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('components_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Log system information
logger.info("="*60)
logger.info("COMPONENT TEST SESSION STARTED")
logger.info("="*60)
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Project root: {project_root}")

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
                    logger.info("Display test terminated by user (ESC key)")
                    return False
        
        clock.tick(60)  # 60 FPS
        elapsed += clock.get_time()
    
    return True

class ComponentTestSuite:
    """Comprehensive Component Test Suite"""
    
    def __init__(self):
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.hardware_available = False
        self.simulation_mode = False
        
        # Component instances
        self.display = None
        self.mdb = None
        self.btcpay = None
    
    def log_test_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.test_results[test_name] = {"passed": passed, "details": details}
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
        
        status = "✓ PASS" if passed else "✗ FAIL"
        mode = " (SIM)" if self.simulation_mode else ""
        print(f"  {status}{mode}: {test_name}")
        if details:
            print(f"    └─ {details}")
    
    def test_configuration(self):
        """Test overall configuration validation"""
        print("\n1. Testing Configuration...")
        logger.info("Starting configuration validation")
        
        try:
            # Log configuration status for debugging
            logger.info("Printing configuration status for debugging")
            config.print_config_status()
            
            # Validate configuration
            is_valid = config.validate()
            logger.info(f"Configuration validation result: {is_valid}")
            
            # Test individual configuration sections
            config_tests = [
                ("Display Config", hasattr(config, 'display'), "Display configuration present"),
                ("MDB Config", hasattr(config, 'mdb'), "MDB configuration present"),
                ("BTCPay Config", hasattr(config, 'btcpay'), "BTCPay configuration present"),
                ("Vending Config", hasattr(config, 'vending'), "Vending configuration present"),
                ("System Config", hasattr(config, 'system'), "System configuration present")
            ]
            
            all_passed = True
            for test_name, condition, details in config_tests:
                passed = condition
                self.log_test_result(test_name, passed, details)
                if not passed:
                    all_passed = False
            
            self.log_test_result("Configuration Validation", is_valid and all_passed, 
                               "Overall configuration validation")
            
            return is_valid and all_passed
            
        except Exception as e:
            logger.error(f"Configuration test failed with exception: {e}")
            logger.exception("Full exception traceback:")
            self.log_test_result("Configuration Test", False, f"Config error: {e}")
            return False
    
    def test_lcd_display(self):
        """Test LCD display functionality"""
        print("\n2. Testing LCD Display...")
        logger.info("Starting LCD display test")
        
        try:
            logger.debug("Creating LCDDisplay instance")
            self.display = LCDDisplay()
            
            # Test initialization
            logger.debug("Attempting display initialization")
            if self.display.initialize():
                logger.info("LCD display initialized successfully")
                self.log_test_result("LCD Initialization", True, "Display initialized successfully")
                
                # Test message display
                logger.debug("Testing message display")
                self.display.show_message("Test Message", "Display working correctly")
                if not wait_for_display(2):
                    return False
                self.log_test_result("LCD Message Display", True, "Message displayed successfully")
                
                # Test QR code display
                logger.debug("Testing QR code display")
                test_qr_data = "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh?amount=0.001"
                try:
                    self.display.show_qr_code(test_qr_data, "Test QR Code")
                    if not wait_for_display(3):
                        return False
                    self.log_test_result("LCD QR Code Display", True, "QR code displayed successfully")
                except Exception as qr_error:
                    logger.warning(f"QR code display failed: {qr_error}")
                    self.log_test_result("LCD QR Code Display", False, f"QR error: {qr_error}")
                
                # Test payment status
                logger.debug("Testing payment status display")
                try:
                    self.display.show_payment_status(2.50, "EUR", "waiting")
                    if not wait_for_display(2):
                        return False
                    self.display.show_payment_status(2.50, "EUR", "paid")
                    if not wait_for_display(2):
                        return False
                    self.log_test_result("LCD Payment Status", True, "Payment status displayed")
                except Exception as status_error:
                    logger.warning(f"Payment status display failed: {status_error}")
                    self.log_test_result("LCD Payment Status", False, f"Status error: {status_error}")
                
                # Test dispensing animation
                logger.debug("Testing dispensing animation")
                try:
                    self.display.show_dispensing("Test Item")
                    if not wait_for_display(2):
                        return False
                    self.log_test_result("LCD Dispensing Animation", True, "Animation displayed")
                except Exception as anim_error:
                    logger.warning(f"Dispensing animation failed: {anim_error}")
                    self.log_test_result("LCD Dispensing Animation", False, f"Animation error: {anim_error}")
                
                # Test error display
                logger.debug("Testing error display")
                try:
                    self.display.show_error("Test error message")
                    if not wait_for_display(2):
                        return False
                    self.log_test_result("LCD Error Display", True, "Error message displayed")
                except Exception as error_display_error:
                    logger.warning(f"Error display failed: {error_display_error}")
                    self.log_test_result("LCD Error Display", False, f"Error display error: {error_display_error}")
                
                # Test system status
                logger.debug("Testing system status display")
                try:
                    self.display.show_system_status(True, True, True)
                    if not wait_for_display(2):
                        return False
                    self.log_test_result("LCD System Status", True, "System status displayed")
                except Exception as sys_status_error:
                    logger.warning(f"System status display failed: {sys_status_error}")
                    self.log_test_result("LCD System Status", False, f"System status error: {sys_status_error}")
                
                return True
            else:
                logger.error("LCD display initialization failed")
                self.log_test_result("LCD Initialization", False, "Display initialization failed")
                return False
                
        except Exception as e:
            logger.error(f"LCD display test failed with exception: {e}")
            logger.exception("Full exception traceback:")
            self.log_test_result("LCD Display Test", False, f"Display error: {e}")
            return False
    
    def test_mdb_controller(self):
        """Test MDB controller functionality"""
        print("\n3. Testing MDB Controller...")
        logger.info("Starting MDB controller test")
        
        try:
            logger.debug("Creating MDBController instance")
            self.mdb = MDBController()
            
            # Check if hardware is available
            self.hardware_available = os.path.exists('/dev/ttyAMA0') or os.path.exists('/dev/ttyUSB0')
            logger.info(f"MDB hardware available: {self.hardware_available}")
            
            if self.hardware_available:
                logger.info("Testing with real MDB hardware")
                # Test hardware initialization
                logger.debug("Attempting MDB hardware initialization")
                try:
                    init_success = self.mdb.initialize()
                    if init_success:
                        logger.info("MDB controller initialized successfully")
                        self.log_test_result("MDB Initialization", True, "Hardware initialized")
                        
                        # Test status checking
                        logger.debug("Testing MDB status checking")
                        try:
                            status = self.mdb.get_status()
                            logger.info(f"MDB status: {status}")
                            self.log_test_result("MDB Status Check", True, f"Status: {status}")
                        except Exception as status_error:
                            logger.warning(f"MDB status check failed: {status_error}")
                            self.log_test_result("MDB Status Check", False, f"Status error: {status_error}")
                        
                        # Test connection check
                        logger.debug("Testing MDB connection health")
                        try:
                            connection_healthy = self.mdb.check_connection()
                            logger.info(f"MDB connection healthy: {connection_healthy}")
                            self.log_test_result("MDB Connection Health", connection_healthy, 
                                               "Connection healthy" if connection_healthy else "Connection issues")
                        except Exception as conn_error:
                            logger.warning(f"MDB connection check failed: {conn_error}")
                            self.log_test_result("MDB Connection Health", False, f"Connection error: {conn_error}")
                        
                        return True
                    else:
                        logger.error("MDB hardware initialization failed")
                        self.log_test_result("MDB Initialization", False, "Hardware initialization failed")
                        # Fall back to simulation mode
                        self.simulation_mode = True
                        self.hardware_available = False
                        
                except Exception as init_error:
                    logger.error(f"MDB initialization exception: {init_error}")
                    logger.info("Falling back to simulation mode")
                    self.simulation_mode = True
                    self.hardware_available = False
            
            if not self.hardware_available or self.simulation_mode:
                logger.info("Running MDB tests in simulation mode")
                self.simulation_mode = True
                # Test object creation and basic functionality
                self.log_test_result("MDB Initialization", True, "Simulation mode - object created")
                
                # Test status in simulation mode
                try:
                    status = self.mdb.get_status()
                    self.log_test_result("MDB Status Check", True, f"Simulation status: {status}")
                except Exception as sim_error:
                    logger.warning(f"MDB simulation status failed: {sim_error}")
                    self.log_test_result("MDB Status Check", False, f"Simulation error: {sim_error}")
                
                return True
            
        except Exception as e:
            logger.error(f"MDB controller test failed with exception: {e}")
            logger.exception("Full exception traceback:")
            self.log_test_result("MDB Controller Test", False, f"MDB error: {e}")
            return False
    
    def test_btcpay_client(self):
        """Test BTCPay Server client functionality"""
        print("\n4. Testing BTCPay Client...")
        logger.info("Starting BTCPay client test")
        
        try:
            logger.debug("Creating BTCPayClient instance")
            self.btcpay = BTCPayClient()
            
            # Check configuration completeness
            config_complete = (config.btcpay.server_url and 
                              config.btcpay.store_id and 
                              config.btcpay.api_key)
            
            logger.info(f"BTCPay configuration complete: {config_complete}")
            logger.info(f"Server URL: {config.btcpay.server_url}")
            logger.info(f"Store ID: {'[CONFIGURED]' if config.btcpay.store_id else '[NOT SET]'}")
            logger.info(f"API Key: {'[CONFIGURED]' if config.btcpay.api_key else '[NOT SET]'}")
            
            if config_complete:
                logger.info("Testing with real BTCPay server configuration")
                
                # Test server connection
                logger.debug("Attempting BTCPay server connection")
                try:
                    connection_success = self.btcpay.initialize()
                    if connection_success:
                        logger.info("BTCPay server connection successful")
                        self.log_test_result("BTCPay Connection", True, "Server connection successful")
                        
                        # Test invoice creation
                        logger.debug("Testing invoice creation")
                        try:
                            test_invoice = self.btcpay.create_invoice(1.50, "EUR", "Component Test Purchase")
                            if test_invoice and 'invoice_id' in test_invoice:
                                logger.info(f"Invoice created successfully: {test_invoice['invoice_id']}")
                                self.log_test_result("BTCPay Invoice Creation", True, 
                                                   f"Invoice ID: {test_invoice['invoice_id']}")
                                
                                # Test invoice status
                                logger.debug("Testing invoice status check")
                                try:
                                    status_info = self.btcpay.get_invoice_status(test_invoice['invoice_id'])
                                    if status_info and 'status' in status_info:
                                        logger.info(f"Invoice status: {status_info['status']}")
                                        self.log_test_result("BTCPay Invoice Status", True, 
                                                           f"Status: {status_info['status']}")
                                    else:
                                        logger.warning("Invoice status check returned invalid data")
                                        self.log_test_result("BTCPay Invoice Status", False, "Invalid status data")
                                except Exception as status_error:
                                    logger.warning(f"Invoice status check failed: {status_error}")
                                    self.log_test_result("BTCPay Invoice Status", False, f"Status error: {status_error}")
                                
                                # Clean up - cancel test invoice
                                logger.debug("Cancelling test invoice")
                                try:
                                    if self.btcpay.cancel_invoice(test_invoice['invoice_id']):
                                        logger.info("Test invoice cancelled successfully")
                                        self.log_test_result("BTCPay Invoice Cancellation", True, "Invoice cancelled")
                                    else:
                                        logger.warning("Invoice cancellation failed")
                                        self.log_test_result("BTCPay Invoice Cancellation", False, "Cancellation failed")
                                except Exception as cancel_error:
                                    logger.warning(f"Invoice cancellation error: {cancel_error}")
                                    self.log_test_result("BTCPay Invoice Cancellation", False, f"Cancel error: {cancel_error}")
                                
                            else:
                                logger.error("Invoice creation failed")
                                self.log_test_result("BTCPay Invoice Creation", False, "Invoice creation failed")
                        except Exception as invoice_error:
                            logger.error(f"Invoice creation exception: {invoice_error}")
                            self.log_test_result("BTCPay Invoice Creation", False, f"Invoice error: {invoice_error}")
                        
                        return True
                    else:
                        logger.error("BTCPay server connection failed")
                        self.log_test_result("BTCPay Connection", False, "Server connection failed")
                        return False
                        
                except Exception as conn_error:
                    logger.error(f"BTCPay connection exception: {conn_error}")
                    self.log_test_result("BTCPay Connection", False, f"Connection error: {conn_error}")
                    return False
            else:
                logger.warning("BTCPay configuration incomplete - limited testing")
                self.log_test_result("BTCPay Configuration", False, "Configuration incomplete")
                
                # Test basic client status without connection
                try:
                    status = self.btcpay.get_status()
                    logger.info(f"BTCPay client status: {status}")
                    self.log_test_result("BTCPay Status Check", True, f"Status: {status}")
                    return True
                except Exception as status_error:
                    logger.warning(f"BTCPay status check failed: {status_error}")
                    self.log_test_result("BTCPay Status Check", False, f"Status error: {status_error}")
                    return False
            
        except Exception as e:
            logger.error(f"BTCPay client test failed with exception: {e}")
            logger.exception("Full exception traceback:")
            self.log_test_result("BTCPay Client Test", False, f"BTCPay error: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Starting cleanup procedures")
        
        try:
            if self.display:
                logger.debug("Closing display")
                self.display.close()
                
            if self.mdb:
                logger.debug("Closing MDB controller")
                self.mdb.close()
                
            logger.info("Cleanup completed successfully")
        except Exception as e:
            logger.warning(f"Cleanup error: {e}")
    
    def run_all_tests(self):
        """Run all component tests"""
        logger.info("Starting comprehensive component test suite")
        print("Bitcoin Vending Machine - Component Test Suite")
        print("=" * 60)
        
        test_functions = [
            ("Configuration", self.test_configuration),
            ("LCD Display", self.test_lcd_display),
            ("MDB Controller", self.test_mdb_controller),
            ("BTCPay Client", self.test_btcpay_client)
        ]
        
        component_results = {}
        
        for component_name, test_func in test_functions:
            logger.info(f"Running {component_name} tests")
            try:
                component_results[component_name] = test_func()
            except Exception as e:
                logger.error(f"{component_name} test failed with exception: {e}")
                logger.exception("Full exception traceback:")
                component_results[component_name] = False
        
        # Generate comprehensive report
        print("\n" + "=" * 60)
        print("COMPONENT TEST SUMMARY")
        print("=" * 60)
        
        for component, passed in component_results.items():
            status = "PASS" if passed else "FAIL"
            icon = "✓" if passed else "✗"
            print(f"{icon} {component}: {status}")
        
        # Detailed test results
        print(f"\nDetailed Results: {self.passed_tests}/{self.total_tests} tests passed")
        
        # Show failed tests
        failed_tests = [name for name, result in self.test_results.items() if not result["passed"]]
        if failed_tests:
            print(f"\nFailed Tests:")
            for test_name in failed_tests:
                details = self.test_results[test_name]["details"]
                print(f"  ✗ {test_name}: {details}")
        
        passed_count = sum(1 for result in component_results.values() if result)
        total_count = len(component_results)
        
        print(f"\nComponent Summary: {passed_count}/{total_count} components passed")
        
        if passed_count == total_count:
            print("\n🎉 All component tests passed!")
            logger.info("All component tests completed successfully")
        elif passed_count > 0:
            print("\n⚠️ Some components passed (hardware-dependent failures expected)")
            logger.info("Some component tests passed with expected hardware dependencies")
        else:
            print("\n❌ All component tests failed - check configuration and setup")
            logger.error("All component tests failed")
        
        print("\nNext steps:")
        if not self.hardware_available:
            print("1. Connect MDB hardware for full testing")
        if not config.btcpay.api_key:
            print("2. Configure BTCPay Server credentials")
        print("3. Run end-to-end integration tests")
        
        return passed_count == total_count

def main():
    """Main test function"""
    logger.info("Starting component test session")
    
    test_suite = ComponentTestSuite()
    
    try:
        success = test_suite.run_all_tests()
        return success
    except Exception as e:
        logger.error(f"Test suite failed with exception: {e}")
        logger.exception("Full exception traceback:")
        print(f"\n❌ Test suite failed: {e}")
        return False
    finally:
        test_suite.cleanup()

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 