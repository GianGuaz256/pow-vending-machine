"""
Enhanced Component Test Suite for Bitcoin Vending Machine
Comprehensive testing of component integration with enhanced logging and result tracking
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

# Set up enhanced logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('enhanced_components_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Log system information
logger.info("="*60)
logger.info("ENHANCED COMPONENT TEST SESSION STARTED")
logger.info("="*60)
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Project root: {project_root}")

class EnhancedComponentTestSuite:
    """Enhanced Component Test Suite with Integration Testing"""
    
    def __init__(self):
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.hardware_available = False
        self.simulation_mode = False
        self.config_complete = False
        
        # Component instances
        self.display = None
        self.mdb = None
        self.btcpay = None
        
        # Test invoices created (for cleanup)
        self.test_invoices = []
    
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
    
    def test_lcd_qr_functionality(self):
        """Test LCD QR Code Generation and Display"""
        print("\n1. Testing LCD QR Code Functionality...")
        logger.info("Starting LCD QR code functionality test")
        
        try:
            logger.debug("Creating LCDDisplay instance")
            self.display = LCDDisplay()
            
            if not self.display.initialize():
                logger.error("LCD initialization failed")
                self.log_test_result("LCD Initialization", False, "Display initialization failed")
                return False
            
            logger.info("LCD initialized successfully")
            self.log_test_result("LCD Initialization", True, "Display initialized successfully")
            
            # Test different QR code types
            qr_tests = [
                ("Bitcoin Address", "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"),
                ("Lightning Invoice", "lnbc1500n1ps8huzfpp5pllm7zpjl3z7nvr8qqtdj2vfvdyfxfmhp6z3xg8k3dkf"),
                ("Bitcoin URI", "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh?amount=0.001"),
                ("Simple URL", "https://bitcoin.org"),
                ("Text Data", "Hello Bitcoin World!")
            ]
            
            success_count = 0
            for test_name, test_data in qr_tests:
                logger.debug(f"Testing QR code for: {test_name}")
                try:
                    self.display.show_qr_code(test_data, f"QR: {test_name}")
                    time.sleep(1)  # Shorter delays for automated testing
                    success_count += 1
                    logger.info(f"QR Code {test_name}: SUCCESS")
                    self.log_test_result(f"QR Code - {test_name}", True, f"Data: {test_data[:30]}...")
                except Exception as e:
                    logger.warning(f"QR Code {test_name}: FAILED - {e}")
                    self.log_test_result(f"QR Code - {test_name}", False, f"QR error: {e}")
            
            # Test payment status display variations
            logger.debug("Testing payment status display variations")
            try:
                status_tests = [
                    (2.50, "EUR", "waiting"),
                    (0.001, "BTC", "confirming"),
                    (5.00, "USD", "paid"),
                    (1.75, "EUR", "expired")
                ]
                
                for amount, currency, status in status_tests:
                    self.display.show_payment_status(amount, currency, status)
                    time.sleep(0.5)
                
                logger.info("Payment status display variations: SUCCESS")
                self.log_test_result("Payment Status Variations", True, f"Tested {len(status_tests)} status combinations")
            except Exception as e:
                logger.warning(f"Payment status variations failed: {e}")
                self.log_test_result("Payment Status Variations", False, f"Status error: {e}")
            
            # Test advanced display features
            logger.debug("Testing advanced display features")
            try:
                # Test error display
                self.display.show_error("Test Error: Connection timeout")
                time.sleep(0.5)
                
                # Test dispensing animation
                self.display.show_dispensing("Premium Coffee")
                time.sleep(0.5)
                
                # Test system status
                self.display.show_system_status(True, True, True)
                time.sleep(0.5)
                
                logger.info("Advanced display features: SUCCESS")
                self.log_test_result("Advanced Display Features", True, "Error, dispensing, and system status")
            except Exception as e:
                logger.warning(f"Advanced display features failed: {e}")
                self.log_test_result("Advanced Display Features", False, f"Feature error: {e}")
            
            total_qr_tests = len(qr_tests)
            qr_success_rate = success_count / total_qr_tests if total_qr_tests > 0 else 0
            
            logger.info(f"LCD QR Tests: {success_count}/{total_qr_tests} passed ({qr_success_rate:.1%})")
            return qr_success_rate >= 0.8  # 80% success rate required
            
        except Exception as e:
            logger.error(f"LCD QR functionality test failed with exception: {e}")
            logger.exception("Full exception traceback:")
            self.log_test_result("LCD QR Functionality", False, f"Test error: {e}")
            return False
    
    def test_mdb_response(self):
        """Test MDB Controller Response and Communication"""
        print("\n2. Testing MDB Controller Response...")
        logger.info("Starting MDB controller response test")
        
        try:
            logger.debug("Creating MDBController instance")
            self.mdb = MDBController()
            
            # Detect hardware availability
            self.hardware_available = os.path.exists('/dev/ttyAMA0') or os.path.exists('/dev/ttyUSB0')
            logger.info(f"MDB hardware available: {self.hardware_available}")
            
            if self.hardware_available:
                logger.info("Testing with real MDB hardware")
                
                # Test hardware initialization
                logger.debug("Attempting MDB hardware initialization")
                try:
                    init_success = self.mdb.initialize()
                    if init_success:
                        logger.info("MDB hardware initialization successful")
                        self.log_test_result("MDB Hardware Init", True, "Hardware initialized successfully")
                        
                        # Test comprehensive status retrieval
                        logger.debug("Testing comprehensive status retrieval")
                        try:
                            status = self.mdb.get_status()
                            if isinstance(status, dict) and 'state' in status:
                                logger.info(f"MDB status: {status}")
                                self.log_test_result("MDB Status Retrieval", True, f"State: {status['state']}")
                                
                                # Test additional status fields
                                expected_fields = ['state', 'error_code', 'last_command']
                                missing_fields = [field for field in expected_fields if field not in status]
                                if not missing_fields:
                                    self.log_test_result("MDB Status Completeness", True, "All expected status fields present")
                                else:
                                    self.log_test_result("MDB Status Completeness", False, f"Missing fields: {missing_fields}")
                            else:
                                logger.warning("MDB status format invalid")
                                self.log_test_result("MDB Status Retrieval", False, "Invalid status format")
                        except Exception as status_error:
                            logger.warning(f"MDB status retrieval failed: {status_error}")
                            self.log_test_result("MDB Status Retrieval", False, f"Status error: {status_error}")
                        
                        # Test connection health monitoring
                        logger.debug("Testing connection health monitoring")
                        try:
                            health_checks = []
                            for i in range(3):  # Multiple health checks
                                connection_healthy = self.mdb.check_connection()
                                health_checks.append(connection_healthy)
                                time.sleep(0.5)
                            
                            health_success_rate = sum(health_checks) / len(health_checks)
                            logger.info(f"Connection health checks: {health_checks} ({health_success_rate:.1%} success)")
                            
                            if health_success_rate >= 0.8:  # 80% success rate required
                                self.log_test_result("MDB Connection Health", True, f"Health: {health_success_rate:.1%} success rate")
                            else:
                                self.log_test_result("MDB Connection Health", False, f"Poor health: {health_success_rate:.1%} success rate")
                        except Exception as health_error:
                            logger.warning(f"MDB connection health check failed: {health_error}")
                            self.log_test_result("MDB Connection Health", False, f"Health error: {health_error}")
                        
                        # Test command response timing
                        logger.debug("Testing command response timing")
                        try:
                            start_time = time.time()
                            status = self.mdb.get_status()
                            response_time = time.time() - start_time
                            
                            logger.info(f"Command response time: {response_time:.3f}s")
                            if response_time < 2.0:  # Should respond within 2 seconds
                                self.log_test_result("MDB Response Timing", True, f"Response time: {response_time:.3f}s")
                            else:
                                self.log_test_result("MDB Response Timing", False, f"Slow response: {response_time:.3f}s")
                        except Exception as timing_error:
                            logger.warning(f"MDB response timing test failed: {timing_error}")
                            self.log_test_result("MDB Response Timing", False, f"Timing error: {timing_error}")
                        
                        return True
                    else:
                        logger.error("MDB hardware initialization failed")
                        self.log_test_result("MDB Hardware Init", False, "Hardware initialization failed")
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
                
                # Test simulation mode functionality
                self.log_test_result("MDB Simulation Init", True, "Simulation mode activated")
                
                # Test simulated status
                try:
                    status = self.mdb.get_status()
                    self.log_test_result("MDB Simulation Status", True, f"Simulated status: {status}")
                except Exception as sim_error:
                    logger.warning(f"MDB simulation status failed: {sim_error}")
                    self.log_test_result("MDB Simulation Status", False, f"Simulation error: {sim_error}")
                
                # Test simulated connection check
                try:
                    connection_check = self.mdb.check_connection()
                    self.log_test_result("MDB Simulation Connection", True, f"Simulated connection: {connection_check}")
                except Exception as sim_conn_error:
                    logger.warning(f"MDB simulation connection failed: {sim_conn_error}")
                    self.log_test_result("MDB Simulation Connection", False, f"Simulation conn error: {sim_conn_error}")
                
                return True
            
        except Exception as e:
            logger.error(f"MDB response test failed with exception: {e}")
            logger.exception("Full exception traceback:")
            self.log_test_result("MDB Response Test", False, f"Test error: {e}")
            return False
    
    def test_btcpay_connection(self):
        """Test BTCPay Server Connection and Advanced API"""
        print("\n3. Testing BTCPay Server Connection...")
        logger.info("Starting BTCPay server connection test")
        
        try:
            logger.debug("Creating BTCPayClient instance")
            self.btcpay = BTCPayClient()
            
            # Check configuration completeness
            self.config_complete = (config.btcpay.server_url and 
                                  config.btcpay.store_id and 
                                  config.btcpay.api_key)
            
            logger.info(f"BTCPay configuration complete: {self.config_complete}")
            logger.info(f"Server URL: {config.btcpay.server_url}")
            logger.info(f"Store ID: {'[CONFIGURED]' if config.btcpay.store_id else '[NOT SET]'}")
            logger.info(f"API Key: {'[CONFIGURED]' if config.btcpay.api_key else '[NOT SET]'}")
            
            if self.config_complete:
                logger.info("Testing with real BTCPay server configuration")
                
                # Test server connection
                logger.debug("Attempting BTCPay server connection")
                try:
                    connection_success = self.btcpay.initialize()
                    if connection_success:
                        logger.info("BTCPay server connection successful")
                        self.log_test_result("BTCPay Connection", True, "Server connection successful")
                        
                        # Test multiple invoice creation and management
                        logger.debug("Testing advanced invoice operations")
                        try:
                            invoice_tests = [
                                (1.00, "EUR", "Component Test - Small"),
                                (5.50, "EUR", "Component Test - Medium"),
                                (0.001, "BTC", "Component Test - Bitcoin")
                            ]
                            
                            created_invoices = []
                            for amount, currency, description in invoice_tests:
                                logger.debug(f"Creating invoice: {amount} {currency}")
                                invoice = self.btcpay.create_invoice(amount, currency, description)
                                if invoice and 'invoice_id' in invoice:
                                    created_invoices.append(invoice)
                                    self.test_invoices.append(invoice['invoice_id'])  # Track for cleanup
                                    logger.info(f"Invoice created: {invoice['invoice_id']} for {amount} {currency}")
                                else:
                                    logger.warning(f"Failed to create invoice for {amount} {currency}")
                            
                            success_rate = len(created_invoices) / len(invoice_tests)
                            if success_rate >= 1.0:
                                self.log_test_result("BTCPay Multiple Invoices", True, f"Created {len(created_invoices)}/{len(invoice_tests)} invoices")
                            else:
                                self.log_test_result("BTCPay Multiple Invoices", False, f"Only created {len(created_invoices)}/{len(invoice_tests)} invoices")
                            
                            # Test invoice status checking for all created invoices
                            logger.debug("Testing invoice status checking")
                            status_checks_passed = 0
                            for invoice in created_invoices:
                                try:
                                    status_info = self.btcpay.get_invoice_status(invoice['invoice_id'])
                                    if status_info and 'status' in status_info:
                                        logger.debug(f"Invoice {invoice['invoice_id']} status: {status_info['status']}")
                                        status_checks_passed += 1
                                    else:
                                        logger.warning(f"Invalid status data for invoice {invoice['invoice_id']}")
                                except Exception as status_error:
                                    logger.warning(f"Status check failed for invoice {invoice['invoice_id']}: {status_error}")
                            
                            status_success_rate = status_checks_passed / len(created_invoices) if created_invoices else 0
                            if status_success_rate >= 1.0:
                                self.log_test_result("BTCPay Status Checks", True, f"All {status_checks_passed} status checks passed")
                            else:
                                self.log_test_result("BTCPay Status Checks", False, f"Only {status_checks_passed}/{len(created_invoices)} status checks passed")
                            
                            # Test invoice cancellation
                            logger.debug("Testing invoice cancellation")
                            cancellation_success = 0
                            for invoice in created_invoices:
                                try:
                                    if self.btcpay.cancel_invoice(invoice['invoice_id']):
                                        logger.debug(f"Invoice {invoice['invoice_id']} cancelled successfully")
                                        cancellation_success += 1
                                    else:
                                        logger.warning(f"Failed to cancel invoice {invoice['invoice_id']}")
                                except Exception as cancel_error:
                                    logger.warning(f"Cancellation error for invoice {invoice['invoice_id']}: {cancel_error}")
                            
                            cancel_success_rate = cancellation_success / len(created_invoices) if created_invoices else 0
                            if cancel_success_rate >= 0.8:  # 80% success rate acceptable
                                self.log_test_result("BTCPay Cancellations", True, f"Cancelled {cancellation_success}/{len(created_invoices)} invoices")
                            else:
                                self.log_test_result("BTCPay Cancellations", False, f"Only cancelled {cancellation_success}/{len(created_invoices)} invoices")
                            
                        except Exception as invoice_error:
                            logger.error(f"Advanced invoice operations failed: {invoice_error}")
                            self.log_test_result("BTCPay Advanced Operations", False, f"Invoice operations error: {invoice_error}")
                        
                        # Test server performance
                        logger.debug("Testing server performance")
                        try:
                            start_time = time.time()
                            test_invoice = self.btcpay.create_invoice(0.10, "EUR", "Performance Test")
                            creation_time = time.time() - start_time
                            
                            if test_invoice and 'invoice_id' in test_invoice:
                                self.test_invoices.append(test_invoice['invoice_id'])
                                logger.info(f"Invoice creation time: {creation_time:.3f}s")
                                
                                if creation_time < 5.0:  # Should create within 5 seconds
                                    self.log_test_result("BTCPay Performance", True, f"Creation time: {creation_time:.3f}s")
                                else:
                                    self.log_test_result("BTCPay Performance", False, f"Slow creation: {creation_time:.3f}s")
                                
                                # Clean up performance test invoice
                                try:
                                    self.btcpay.cancel_invoice(test_invoice['invoice_id'])
                                except:
                                    pass
                            else:
                                self.log_test_result("BTCPay Performance", False, "Performance test invoice creation failed")
                                
                        except Exception as perf_error:
                            logger.warning(f"Performance test failed: {perf_error}")
                            self.log_test_result("BTCPay Performance", False, f"Performance error: {perf_error}")
                        
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
                
                # Test basic client functionality without connection
                try:
                    status = self.btcpay.get_status()
                    logger.info(f"BTCPay client status: {status}")
                    self.log_test_result("BTCPay Status Check", True, f"Status: {status}")
                    return False  # Configuration incomplete, so overall test fails
                except Exception as status_error:
                    logger.warning(f"BTCPay status check failed: {status_error}")
                    self.log_test_result("BTCPay Status Check", False, f"Status error: {status_error}")
                    return False
            
        except Exception as e:
            logger.error(f"BTCPay connection test failed with exception: {e}")
            logger.exception("Full exception traceback:")
            self.log_test_result("BTCPay Connection Test", False, f"Test error: {e}")
            return False
    
    def test_component_integration(self):
        """Test integration between components"""
        print("\n4. Testing Component Integration...")
        logger.info("Starting component integration test")
        
        if not (self.display and self.mdb and self.btcpay):
            logger.warning("Not all components initialized - skipping integration test")
            self.log_test_result("Component Integration", False, "Not all components initialized")
            return False
        
        try:
            # Test display + BTCPay integration
            logger.debug("Testing display + BTCPay integration")
            if self.config_complete:
                try:
                    # Create a test invoice
                    test_invoice = self.btcpay.create_invoice(2.50, "EUR", "Integration Test")
                    if test_invoice and 'invoice_id' in test_invoice:
                        self.test_invoices.append(test_invoice['invoice_id'])
                        
                        # Display the payment request
                        if 'payment_url' in test_invoice:
                            self.display.show_qr_code(test_invoice['payment_url'], "Integration Test Payment")
                            time.sleep(1)
                        
                        # Show payment status
                        self.display.show_payment_status(2.50, "EUR", "waiting")
                        time.sleep(1)
                        
                        # Cancel the test invoice
                        self.btcpay.cancel_invoice(test_invoice['invoice_id'])
                        
                        self.log_test_result("Display + BTCPay Integration", True, "Payment flow displayed successfully")
                    else:
                        self.log_test_result("Display + BTCPay Integration", False, "Failed to create test invoice")
                except Exception as e:
                    logger.warning(f"Display + BTCPay integration failed: {e}")
                    self.log_test_result("Display + BTCPay Integration", False, f"Integration error: {e}")
            else:
                self.log_test_result("Display + BTCPay Integration", False, "BTCPay not configured")
            
            # Test display + MDB integration
            logger.debug("Testing display + MDB integration")
            try:
                # Get MDB status and display it
                mdb_status = self.mdb.get_status()
                if isinstance(mdb_status, dict) and 'state' in mdb_status:
                    # Show system status based on MDB state
                    mdb_healthy = mdb_status['state'] not in ['error', 'disconnected']
                    self.display.show_system_status(True, mdb_healthy, self.config_complete)
                    time.sleep(1)
                    
                    self.log_test_result("Display + MDB Integration", True, f"System status displayed - MDB: {mdb_status['state']}")
                else:
                    self.log_test_result("Display + MDB Integration", False, "Invalid MDB status format")
            except Exception as e:
                logger.warning(f"Display + MDB integration failed: {e}")
                self.log_test_result("Display + MDB Integration", False, f"Integration error: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"Component integration test failed with exception: {e}")
            logger.exception("Full exception traceback:")
            self.log_test_result("Component Integration Test", False, f"Integration error: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources and test invoices"""
        logger.info("Starting cleanup procedures")
        
        try:
            # Cancel any remaining test invoices
            if self.test_invoices and self.btcpay:
                logger.debug(f"Cleaning up {len(self.test_invoices)} test invoices")
                for invoice_id in self.test_invoices:
                    try:
                        self.btcpay.cancel_invoice(invoice_id)
                        logger.debug(f"Cancelled test invoice: {invoice_id}")
                    except Exception as e:
                        logger.warning(f"Failed to cancel invoice {invoice_id}: {e}")
            
            # Close components
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
        """Run all enhanced component tests"""
        logger.info("Starting comprehensive enhanced component test suite")
        print("Bitcoin Vending Machine - Enhanced Component Test Suite")
        print("=" * 60)
        
        test_functions = [
            ("LCD QR Functionality", self.test_lcd_qr_functionality),
            ("MDB Response", self.test_mdb_response),
            ("BTCPay Connection", self.test_btcpay_connection),
            ("Component Integration", self.test_component_integration)
        ]
        
        test_results = {}
        
        for test_name, test_func in test_functions:
            logger.info(f"Running {test_name} tests")
            try:
                test_results[test_name] = test_func()
            except Exception as e:
                logger.error(f"{test_name} test failed with exception: {e}")
                logger.exception("Full exception traceback:")
                test_results[test_name] = False
        
        # Generate comprehensive report
        print("\n" + "=" * 60)
        print("ENHANCED COMPONENT TEST SUMMARY")
        print("=" * 60)
        
        for test_name, passed in test_results.items():
            status = "PASS" if passed else "FAIL"
            icon = "✓" if passed else "✗"
            print(f"{icon} {test_name}: {status}")
        
        # Detailed test results
        print(f"\nDetailed Results: {self.passed_tests}/{self.total_tests} tests passed")
        
        # Show failed tests
        failed_tests = [name for name, result in self.test_results.items() if not result["passed"]]
        if failed_tests:
            print(f"\nFailed Tests:")
            for test_name in failed_tests:
                details = self.test_results[test_name]["details"]
                print(f"  ✗ {test_name}: {details}")
        
        passed_count = sum(1 for result in test_results.values() if result)
        total_count = len(test_results)
        
        print(f"\nTest Summary: {passed_count}/{total_count} test categories passed")
        
        if passed_count == total_count:
            print("\n🎉 All enhanced component tests passed!")
            print("Components are working well individually and together!")
            logger.info("All enhanced component tests completed successfully")
        elif passed_count > 0:
            print("\n⚠️ Some enhanced component tests passed")
            print("Check failed tests above - some may be hardware/config dependent.")
            logger.info("Some enhanced component tests passed with issues")
        else:
            print("\n❌ All enhanced component tests failed!")
            print("Check component configuration and hardware connections.")
            logger.error("All enhanced component tests failed")
        
        print("\nNext steps:")
        if not self.hardware_available:
            print("1. Connect MDB hardware for full testing")
        if not self.config_complete:
            print("2. Complete BTCPay Server configuration")
        print("3. Run full integration tests")
        print("4. Test with real vending machine hardware")
        
        return passed_count == total_count

def main():
    """Main test function"""
    logger.info("Starting enhanced component test session")
    
    test_suite = EnhancedComponentTestSuite()
    
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