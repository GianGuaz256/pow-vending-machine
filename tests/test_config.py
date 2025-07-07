"""
Configuration Test
Test if .env file is being loaded correctly
"""
import sys
import os

# Add project root and src to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

def test_env_loading():
    """Test environment variable loading"""
    print("Testing .env file loading...")
    
    # Test if we can load dotenv
    try:
        from dotenv import load_dotenv
        print("✓ python-dotenv module available")
    except ImportError:
        print("✗ python-dotenv not installed!")
        print("Run: pip install python-dotenv")
        return False
    
    # Check for .env file
    env_file = os.path.join(project_root, '.env')
    if os.path.exists(env_file):
        print(f"✓ .env file found: {env_file}")
        
        # Try to read the file
        try:
            with open(env_file, 'r') as f:
                lines = f.readlines()
            print(f"✓ .env file readable ({len(lines)} lines)")
            
            # Show non-empty, non-comment lines
            config_lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
            print(f"✓ Found {len(config_lines)} configuration lines")
            
            # Show variable names (without values for security)
            for line in config_lines[:5]:  # Show first 5 only
                if '=' in line:
                    var_name = line.split('=')[0]
                    print(f"  - {var_name}")
            if len(config_lines) > 5:
                print(f"  ... and {len(config_lines) - 5} more")
                
        except Exception as e:
            print(f"✗ Error reading .env file: {e}")
            return False
    else:
        print(f"✗ .env file not found at: {env_file}")
        print("\nTo create a .env file:")
        print("1. Copy config/env_template.txt to .env in project root")
        print("2. Fill in your BTCPay Server details")
        return False
    
    return True

def test_config_import():
    """Test configuration import and loading"""
    print("\nTesting configuration import...")
    
    try:
        from config import config
        print("✓ Configuration module imported successfully")
        
        # Test configuration status
        config.print_config_status()
        
        # Validate configuration
        is_valid = config.validate()
        if is_valid:
            print("\n✓ Configuration validation passed")
        else:
            print("\n✗ Configuration validation failed")
        
        return is_valid
        
    except Exception as e:
        print(f"✗ Error importing configuration: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_specific_env_vars():
    """Test specific environment variables"""
    print("\nTesting specific environment variables...")
    
    # Important variables to check
    test_vars = [
        'BTCPAY_SERVER_URL',
        'BTCPAY_STORE_ID', 
        'BTCPAY_API_KEY',
        'VENDING_CURRENCY',
        'MDB_SERIAL_PORT'
    ]
    
    # Load environment
    from dotenv import load_dotenv
    load_dotenv()
    
    for var in test_vars:
        value = os.getenv(var)
        if value:
            if 'API_KEY' in var or 'SECRET' in var:
                print(f"✓ {var}: [SET - {len(value)} chars]")
            else:
                print(f"✓ {var}: {value}")
        else:
            print(f"✗ {var}: [NOT SET]")

def main():
    """Main test function"""
    print("="*60)
    print("ENVIRONMENT CONFIGURATION TEST")
    print("="*60)
    
    success = True
    
    # Test 1: Environment file loading
    success &= test_env_loading()
    
    # Test 2: Configuration import
    success &= test_config_import()
    
    # Test 3: Specific environment variables
    test_specific_env_vars()
    
    print("\n" + "="*60)
    if success:
        print("🎉 Configuration test PASSED!")
        print("Your .env file is being loaded correctly.")
    else:
        print("❌ Configuration test FAILED!")
        print("Please check your .env file setup.")
    print("="*60)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 