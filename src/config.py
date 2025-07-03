"""
Configuration settings for the Bitcoin Lightning Vending Machine
"""
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DisplayConfig:
    """LCD Display configuration"""
    width: int = 320
    height: int = 480
    spi_bus: int = 0
    spi_device: int = 0
    dc_pin: int = 24
    rst_pin: int = 25
    bl_pin: int = 18
    orientation: int = 90  # Rotation in degrees

@dataclass
class MDBConfig:
    """MDB board configuration"""
    serial_port: str = "/dev/ttyAMA0"
    baud_rate: int = 9600
    timeout: float = 1.0
    retry_attempts: int = 3
    
@dataclass
class BTCPayConfig:
    """BTCPay Server configuration"""
    server_url: str = os.getenv("BTCPAY_SERVER_URL", "https://your-btcpay-server.com")
    store_id: str = os.getenv("BTCPAY_STORE_ID", "")
    api_key: str = os.getenv("BTCPAY_API_KEY", "")
    webhook_secret: str = os.getenv("BTCPAY_WEBHOOK_SECRET", "")
    payment_timeout: int = 300  # 5 minutes
    
@dataclass
class VendingConfig:
    """Vending machine configuration"""
    max_price: float = 100.0  # Maximum item price in EUR/USD
    min_price: float = 0.50   # Minimum item price
    currency: str = "EUR"
    payment_confirmation_time: int = 30  # seconds to wait for payment confirmation
    
@dataclass
class SystemConfig:
    """System-wide configuration"""
    log_level: str = "INFO"
    log_file: str = "/var/log/vending_machine.log"
    pid_file: str = "/var/run/vending_machine.pid"
    status_check_interval: int = 10  # seconds
    
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

# Global configuration instance
config = Config() 