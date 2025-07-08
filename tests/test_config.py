"""
Configuration Test Suite for Bitcoin Vending Machine
Comprehensive testing of configuration loading and validation with enhanced logging
"""
import sys
import os
import logging

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
        logging.FileHandler('config_test.log')
    ]
)
logger = logging.getLogger(__name__)

# Log system information
logger.info("="*60)
logger.info("CONFIGURATION TEST SESSION STARTED")
logger.info("="*60)
logger.info(f"Python version: {sys.version}")
logger.info(f"Working directory: {os.getcwd()}")
logger.info(f"Project root: {project_root}")

class ConfigurationTestSuite:
    """Comprehensive Configuration Test Suite"""
    
    def __init__(self):
        self.test_results = {}
        self.total_tests = 0
        self.passed_tests = 0
        self.env_file_exists = False
        self.config_loaded = False
    
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
    
    def test_dotenv_availability(self):
        """Test if python-dotenv is available"""
        print("\n1. Testing dotenv Module Availability...")
        logger.info("Testing python-dotenv module availability")
        
        try:
            from dotenv import load_dotenv
            logger.info("python-dotenv module successfully imported")
            self.log_test_result("Dotenv Module Import", True, "python-dotenv module available")
            return True
        except ImportError as e:
            logger.error(f"python-dotenv not installed: {e}")
            self.log_test_result("Dotenv Module Import", False, "python-dotenv not installed - run: pip install python-dotenv")
            return False
    
    def test_env_file_existence(self):
        """Test .env file existence and readability"""
        print("\n2. Testing .env File...")
        logger.info("Testing .env file existence and readability")
        
        env_file = os.path.join(project_root, '.env')
        logger.debug(f"Looking for .env file at: {env_file}")
        
        if os.path.exists(env_file):
            logger.info(f".env file found at: {env_file}")
            self.env_file_exists = True
            self.log_test_result("Env File Existence", True, f"Found at: {env_file}")
            
            # Test file readability
            try:
                with open(env_file, 'r') as f:
                    lines = f.readlines()
                
                logger.info(f".env file readable with {len(lines)} lines")
                self.log_test_result("Env File Readability", True, f"File readable ({len(lines)} lines)")
                
                # Analyze file content
                config_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
                comment_lines = [line.strip() for line in lines if line.strip().startswith('#')]
                empty_lines = len(lines) - len(config_lines) - len(comment_lines)
                
                logger.info(f"File analysis: {len(config_lines)} config lines, {len(comment_lines)} comments, {empty_lines} empty lines")
                self.log_test_result("Env File Analysis", True, 
                                   f"{len(config_lines)} config vars, {len(comment_lines)} comments")
                
                # Show variable names (without values for security)
                logger.debug("Configuration variables found:")
                displayed_vars = []
                for line in config_lines[:10]:  # Show first 10 only
                    if '=' in line:
                        var_name = line.split('=')[0]
                        logger.debug(f"  - {var_name}")
                        displayed_vars.append(var_name)
                
                if len(config_lines) > 10:
                    logger.debug(f"  ... and {len(config_lines) - 10} more variables")
                
                self.log_test_result("Env Variables Found", len(config_lines) > 0, 
                                   f"Found {len(config_lines)} variables: {', '.join(displayed_vars[:5])}{'...' if len(displayed_vars) > 5 else ''}")
                
                return True
                
            except Exception as e:
                logger.error(f"Error reading .env file: {e}")
                self.log_test_result("Env File Readability", False, f"Read error: {e}")
                return False
        else:
            logger.error(f".env file not found at: {env_file}")
            self.log_test_result("Env File Existence", False, f"Not found at: {env_file}")
            
            # Provide helpful guidance
            template_file = os.path.join(project_root, 'config', 'env_template.txt')
            if os.path.exists(template_file):
                logger.info(f"Template found at: {template_file}")
                self.log_test_result("Env Template Available", True, "Template file available for copying")
            else:
                logger.warning("No template file found")
                self.log_test_result("Env Template Available", False, "No template file found")
            
            return False
    
    def test_env_loading(self):
        """Test environment variable loading"""
        print("\n3. Testing Environment Loading...")
        logger.info("Testing environment variable loading")
        
        if not self.env_file_exists:
            logger.warning("Skipping env loading test - no .env file")
            self.log_test_result("Env Loading", False, "No .env file to load")
            return False
        
        try:
            from dotenv import load_dotenv
            
            # Load environment variables
            logger.debug("Loading environment variables from .env file")
            env_loaded = load_dotenv()
            logger.info(f"Environment loading result: {env_loaded}")
            
            if env_loaded:
                self.log_test_result("Env Loading", True, "Environment variables loaded successfully")
                return True
            else:
                self.log_test_result("Env Loading", False, "Environment loading failed")
                return False
                
        except Exception as e:
            logger.error(f"Environment loading failed: {e}")
            self.log_test_result("Env Loading", False, f"Loading error: {e}")
            return False
    
    def test_specific_env_vars(self):
        """Test specific required environment variables"""
        print("\n4. Testing Specific Environment Variables...")
        logger.info("Testing specific environment variables")
        
        # Load environment if not already loaded
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except:
            pass
        
        # Important variables to check
        required_vars = [
            ('BTCPAY_SERVER_URL', 'BTCPay Server URL', lambda x: x and x.startswith(('http://', 'https://'))),
            ('BTCPAY_STORE_ID', 'BTCPay Store ID', lambda x: x and len(x) > 10),
            ('BTCPAY_API_KEY', 'BTCPay API Key', lambda x: x and len(x) > 20),
            ('VENDING_CURRENCY', 'Vending Currency', lambda x: x and x.upper() in ['EUR', 'USD', 'BTC']),
            ('MDB_SERIAL_PORT', 'MDB Serial Port', lambda x: x and x.startswith('/dev/'))
        ]
        
        optional_vars = [
            ('BTCPAY_WEBHOOK_SECRET', 'BTCPay Webhook Secret', lambda x: True),  # Optional
            ('VENDING_DEBUG', 'Debug Mode', lambda x: x.lower() in ['true', 'false', '1', '0'] if x else True),
            ('LCD_WIDTH', 'LCD Width', lambda x: x.isdigit() if x else True),
            ('LCD_HEIGHT', 'LCD Height', lambda x: x.isdigit() if x else True)
        ]
        
        all_vars = required_vars + optional_vars
        
        all_passed = True
        required_failed = False
        
        for var_name, description, validator in all_vars:
            logger.debug(f"Checking environment variable: {var_name}")
            value = os.getenv(var_name)
            
            is_required = var_name in [v[0] for v in required_vars]
            
            if value:
                # Validate the value
                try:
                    is_valid = validator(value)
                    
                    # Mask sensitive values
                    if 'API_KEY' in var_name or 'SECRET' in var_name:
                        display_value = f"[SET - {len(value)} chars]"
                        logger.info(f"{var_name}: {display_value}")
                    else:
                        display_value = value
                        logger.info(f"{var_name}: {display_value}")
                    
                    if is_valid:
                        self.log_test_result(f"Env Var - {description}", True, f"Valid: {display_value}")
                    else:
                        logger.warning(f"{var_name} has invalid value format")
                        self.log_test_result(f"Env Var - {description}", False, f"Invalid format: {display_value}")
                        if is_required:
                            required_failed = True
                        all_passed = False
                        
                except Exception as e:
                    logger.error(f"Error validating {var_name}: {e}")
                    self.log_test_result(f"Env Var - {description}", False, f"Validation error: {e}")
                    if is_required:
                        required_failed = True
                    all_passed = False
            else:
                # Variable not set
                if is_required:
                    logger.error(f"Required variable {var_name} not set")
                    self.log_test_result(f"Env Var - {description}", False, "Required variable not set")
                    required_failed = True
                    all_passed = False
                else:
                    logger.debug(f"Optional variable {var_name} not set")
                    self.log_test_result(f"Env Var - {description}", True, "Optional variable (not set)")
        
        # Overall assessment
        if not required_failed:
            self.log_test_result("Required Variables Complete", True, "All required variables are set and valid")
        else:
            self.log_test_result("Required Variables Complete", False, "Some required variables missing or invalid")
        
        return not required_failed
    
    def test_config_import(self):
        """Test configuration module import and loading"""
        print("\n5. Testing Configuration Import...")
        logger.info("Testing configuration module import")
        
        try:
            logger.debug("Importing config module")
            from config import config
            logger.info("Configuration module imported successfully")
            self.config_loaded = True
            self.log_test_result("Config Module Import", True, "Configuration module imported")
            
            # Test configuration status
            logger.debug("Getting configuration status")
            try:
                config.print_config_status()
                self.log_test_result("Config Status Print", True, "Status printed successfully")
            except Exception as status_error:
                logger.warning(f"Config status print failed: {status_error}")
                self.log_test_result("Config Status Print", False, f"Status error: {status_error}")
            
            # Test configuration validation
            logger.debug("Validating configuration")
            try:
                is_valid = config.validate()
                logger.info(f"Configuration validation result: {is_valid}")
                
                if is_valid:
                    self.log_test_result("Config Validation", True, "Configuration validation passed")
                else:
                    self.log_test_result("Config Validation", False, "Configuration validation failed")
                
                return is_valid
                
            except Exception as validation_error:
                logger.error(f"Configuration validation error: {validation_error}")
                self.log_test_result("Config Validation", False, f"Validation error: {validation_error}")
                return False
        
        except Exception as e:
            logger.error(f"Configuration import failed: {e}")
            logger.exception("Full exception traceback:")
            self.log_test_result("Config Module Import", False, f"Import error: {e}")
            return False
    
    def test_config_sections(self):
        """Test individual configuration sections"""
        print("\n6. Testing Configuration Sections...")
        logger.info("Testing individual configuration sections")
        
        if not self.config_loaded:
            logger.warning("Skipping config sections test - config not loaded")
            self.log_test_result("Config Sections", False, "Configuration not loaded")
            return False
        
        try:
            from config import config
            
            # Test individual sections
            sections = [
                ('display', 'Display Configuration'),
                ('mdb', 'MDB Configuration'),
                ('btcpay', 'BTCPay Configuration'),
                ('vending', 'Vending Configuration'),
                ('system', 'System Configuration')
            ]
            
            all_sections_present = True
            
            for section_name, description in sections:
                logger.debug(f"Testing {section_name} configuration section")
                
                if hasattr(config, section_name):
                    section = getattr(config, section_name)
                    logger.info(f"{description}: Present")
                    
                    # Try to access some properties
                    try:
                        # Get all attributes of the section
                        attrs = [attr for attr in dir(section) if not attr.startswith('_')]
                        logger.debug(f"{section_name} attributes: {attrs}")
                        self.log_test_result(f"Config Section - {description}", True, 
                                           f"Present with {len(attrs)} attributes")
                    except Exception as attr_error:
                        logger.warning(f"Error accessing {section_name} attributes: {attr_error}")
                        self.log_test_result(f"Config Section - {description}", False, f"Attribute error: {attr_error}")
                        all_sections_present = False
                else:
                    logger.error(f"{description}: Missing")
                    self.log_test_result(f"Config Section - {description}", False, "Section missing")
                    all_sections_present = False
            
            return all_sections_present
            
        except Exception as e:
            logger.error(f"Config sections test failed: {e}")
            logger.exception("Full exception traceback:")
            self.log_test_result("Config Sections", False, f"Sections test error: {e}")
            return False
    
    def cleanup(self):
        """Clean up resources"""
        logger.info("Starting cleanup procedures")
        # No specific cleanup needed for config tests
        logger.info("Cleanup completed successfully")
    
    def run_all_tests(self):
        """Run all configuration tests"""
        logger.info("Starting comprehensive configuration test suite")
        print("Bitcoin Vending Machine - Configuration Test Suite")
        print("=" * 60)
        
        test_functions = [
            ("Dotenv Availability", self.test_dotenv_availability),
            ("Env File", self.test_env_file_existence),
            ("Env Loading", self.test_env_loading),
            ("Environment Variables", self.test_specific_env_vars),
            ("Config Import", self.test_config_import),
            ("Config Sections", self.test_config_sections)
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
        print("CONFIGURATION TEST SUMMARY")
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
            print("\n🎉 All configuration tests passed!")
            print("Your .env file is being loaded correctly and configuration is valid.")
            logger.info("All configuration tests completed successfully")
        elif passed_count > 0:
            print("\n⚠️ Some configuration tests passed")
            print("Check failed tests above and fix configuration issues.")
            logger.info("Some configuration tests passed with issues to resolve")
        else:
            print("\n❌ All configuration tests failed!")
            print("Please check your .env file setup and configuration.")
            logger.error("All configuration tests failed")
        
        print("\nNext steps:")
        if not self.env_file_exists:
            print("1. Copy config/env_template.txt to .env in project root")
            print("2. Fill in your BTCPay Server details in .env")
        if not self.config_loaded:
            print("3. Check configuration module imports")
        print("4. Run component tests: python tests/test_components.py")
        
        return passed_count == total_count

def main():
    """Main test function"""
    logger.info("Starting configuration test session")
    
    test_suite = ConfigurationTestSuite()
    
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