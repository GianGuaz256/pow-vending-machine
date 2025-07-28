"""
Configuration settings for the Bitcoin Lightning Vending Machine
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class DisplayConfig:
    """LCD Display configuration"""
    width: int = int(os.getenv("DISPLAY_WIDTH", "320"))
    height: int = int(os.getenv("DISPLAY_HEIGHT", "480"))
    spi_bus: int = 0
    spi_device: int = 0
    dc_pin: int = 24
    rst_pin: int = 25
    bl_pin: int = 18
    orientation: int = int(os.getenv("DISPLAY_ROTATION", "90"))  # Rotation in degrees

@dataclass
class MDBConfig:
    """MDB board configuration"""
    serial_port: str = os.getenv("MDB_SERIAL_PORT", "/dev/ttyACM0")  # USB interface
    baud_rate: int = int(os.getenv("MDB_BAUD_RATE", "115200"))  # USB interface baud rate
    timeout: float = 50.0  # High timeout as specified in the guide
    retry_attempts: int = 3
    
@dataclass
class BTCPayConfig:
    """BTCPay Server configuration"""
    server_url: str = os.getenv("BTCPAY_SERVER_URL", "https://your-btcpay-server.com")
    store_id: str = os.getenv("BTCPAY_STORE_ID", "")
    api_key: str = os.getenv("BTCPAY_API_KEY", "")
    webhook_secret: str = os.getenv("BTCPAY_WEBHOOK_SECRET", "")
    payment_timeout: int = int(os.getenv("PAYMENT_TIMEOUT", "300"))  # 5 minutes
    
@dataclass
class VendingConfig:
    """Vending machine configuration"""
    max_price: float = float(os.getenv("VENDING_MAX_PRICE", "100.0"))  # Maximum item price in EUR/USD
    min_price: float = float(os.getenv("VENDING_MIN_PRICE", "0.50"))   # Minimum item price
    currency: str = os.getenv("VENDING_CURRENCY", "EUR")
    payment_confirmation_time: int = 30  # seconds to wait for payment confirmation
    
@dataclass
class SystemConfig:
    """System-wide configuration"""
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "/var/log/vending_machine.log")
    pid_file: str = "/var/run/vending_machine.pid"
    status_check_interval: int = int(os.getenv("STATUS_CHECK_INTERVAL", "10"))  # seconds
    
class Config:
    """Main configuration class"""
    def __init__(self):
        self.display = DisplayConfig()
        self.mdb = MDBConfig()
        self.btcpay = BTCPayConfig()
        self.vending = VendingConfig()
        self.system = SystemConfig()
        
    def validate(self) -> bool:
        """Validate configuration"""
        if not self.btcpay.server_url or not self.btcpay.store_id or not self.btcpay.api_key:
            print("ERROR: BTCPay Server configuration is incomplete")
            return False
            
        if self.vending.max_price <= self.vending.min_price:
            print("ERROR: Invalid price configuration")
            return False
            
        return True
    
    def print_config_status(self):
        """Print configuration status for debugging"""
        print("="*50)
        print("CONFIGURATION STATUS")
        print("="*50)
        
        # Check if .env file exists
        env_file = os.path.join(os.getcwd(), '.env')
        if os.path.exists(env_file):
            print(f"✓ .env file found: {env_file}")
        else:
            print("✗ .env file not found in current directory")
            print(f"  Looking for: {env_file}")
        
        print(f"\nBTCPay Configuration:")
        print(f"  Server URL: {self.btcpay.server_url}")
        print(f"  Server URL Status: {'[SET]' if self.btcpay.server_url != 'https://your-btcpay-server.com' else '[NOT SET]'}")
        print(f"  Store ID: {'[SET - ' + str(len(self.btcpay.store_id)) + ' chars]' if self.btcpay.store_id else '[NOT SET]'}")
        print(f"  API Key: {'[SET - ' + str(len(self.btcpay.api_key)) + ' chars]' if self.btcpay.api_key else '[NOT SET]'}")
        print(f"  Webhook Secret: {'[SET - ' + str(len(self.btcpay.webhook_secret)) + ' chars]' if self.btcpay.webhook_secret else '[NOT SET]'}")
        
        print(f"\nMDB Configuration:")
        print(f"  Serial Port: {self.mdb.serial_port}")
        print(f"  Baud Rate: {self.mdb.baud_rate}")
        
        print(f"\nVending Configuration:")
        print(f"  Currency: {self.vending.currency}")
        print(f"  Price Range: {self.vending.min_price} - {self.vending.max_price}")
        
        print(f"\nDisplay Configuration:")
        print(f"  Size: {self.display.width}x{self.display.height}")
        print(f"  Rotation: {self.display.orientation}°")
        
        # Debug validation
        print(f"\nValidation Debug:")
        print(f"  server_url valid: {bool(self.btcpay.server_url)}")
        print(f"  store_id valid: {bool(self.btcpay.store_id)}")
        print(f"  api_key valid: {bool(self.btcpay.api_key)}")
        print(f"  validation result: {self.validate()}")
        
        print("="*50)

# Global configuration instance
config = Config() 