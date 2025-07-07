"""
BTCPay Server Client for Lightning Network Payments
Handles invoice creation, payment monitoring, and webhook processing
"""
import requests
import json
import time
import threading
from typing import Optional, Dict, Any, Callable
from enum import Enum
import logging
from config import config

logger = logging.getLogger(__name__)

class InvoiceStatus(Enum):
    """Invoice status constants - Updated to match BTCPay Server v1 API"""
    NEW = "New"
    PROCESSING = "Processing"
    SETTLED = "Settled"  # Changed from PAID/CONFIRMED/COMPLETE
    EXPIRED = "Expired"
    INVALID = "Invalid"

class BTCPayClient:
    """Client for BTCPay Server API"""
    
    def __init__(self):
        self.server_url = config.btcpay.server_url.rstrip('/')
        self.store_id = config.btcpay.store_id
        self.api_key = config.btcpay.api_key
        self.headers = {
            'Authorization': f'token {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.is_connected = False
        self._payment_callbacks = {}
        
    def initialize(self) -> bool:
        """Initialize BTCPay Server connection using a simple test"""
        try:
            # Instead of accessing store settings (which requires btcpay.store.canviewstoresettings),
            # we'll test by attempting to create a minimal test invoice and then cancel it
            logger.info("Testing BTCPay Server connection...")
            
            # Try to create a small test invoice
            test_invoice_data = {
                "amount": "0.01",
                "currency": "EUR",
                "metadata": {
                    "orderId": f"connection_test_{int(time.time())}",
                    "itemDesc": "Connection Test"
                }
            }
            
            response = self._make_request('POST', f'/api/v1/stores/{self.store_id}/invoices', test_invoice_data)
            
            if response and 'id' in response:
                test_invoice_id = response['id']
                logger.info(f"Connection test successful - created test invoice: {test_invoice_id}")
                
                # Try to cancel the test invoice to clean up
                try:
                    self._make_request('DELETE', f'/api/v1/stores/{self.store_id}/invoices/{test_invoice_id}')
                    logger.debug("Test invoice cancelled successfully")
                except:
                    logger.debug("Test invoice cleanup failed (not critical)")
                
                self.is_connected = True
                logger.info("BTCPay Server connection established")
                return True
            else:
                logger.error("Failed to connect to BTCPay Server - cannot create invoices")
                return False
                
        except Exception as e:
            logger.error(f"Failed to initialize BTCPay client: {e}")
            return False
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request to BTCPay Server"""
        try:
            url = f"{self.server_url}{endpoint}"
            
            if method == 'GET':
                response = requests.get(url, headers=self.headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=self.headers, json=data, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, headers=self.headers, json=data, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=self.headers, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            if response.content:
                return response.json()
            else:
                return {}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"BTCPay API request failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error making BTCPay request: {e}")
            return None
    
    def create_invoice(self, amount: float, currency: str = "EUR", 
                      description: str = "Vending Machine Purchase") -> Optional[Dict[str, Any]]:
        """Create a new invoice"""
        try:
            invoice_data = {
                "amount": str(amount),
                "currency": currency,
                "metadata": {
                    "orderId": f"vending_{int(time.time())}",
                    "itemDesc": description
                },
                "checkout": {
                    "speedPolicy": "MediumSpeed",
                    "paymentMethods": ["BTC-LightningNetwork"],
                    "defaultPaymentMethod": "BTC-LightningNetwork",
                    "expirationMinutes": config.btcpay.payment_timeout // 60,
                    "monitoringMinutes": config.btcpay.payment_timeout // 60 + 5
                }
            }
            
            response = self._make_request('POST', f'/api/v1/stores/{self.store_id}/invoices', invoice_data)
            
            if response:
                invoice_id = response.get('id')
                logger.info(f"Created invoice {invoice_id} for {amount} {currency}")
                
                # Start monitoring this invoice
                self._start_invoice_monitoring(invoice_id)
                
                return {
                    'invoice_id': invoice_id,
                    'amount': amount,
                    'currency': currency,
                    'payment_url': response.get('checkoutLink'),
                    'lightning_invoice': self._get_lightning_invoice(invoice_id),
                    'status': InvoiceStatus.NEW.value,
                    'created_time': time.time()
                }
            else:
                logger.error("Failed to create invoice")
                return None
                
        except Exception as e:
            logger.error(f"Error creating invoice: {e}")
            return None
    
    def _get_lightning_invoice(self, invoice_id: str) -> Optional[str]:
        """Get Lightning Network invoice string"""
        try:
            response = self._make_request('GET', f'/api/v1/stores/{self.store_id}/invoices/{invoice_id}/payment-methods')
            
            if response:
                for payment_method in response:
                    if payment_method.get('paymentMethod') == 'BTC-LightningNetwork':
                        return payment_method.get('destination')
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting Lightning invoice: {e}")
            return None
    
    def get_invoice_status(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """Get current invoice status"""
        try:
            response = self._make_request('GET', f'/api/v1/stores/{self.store_id}/invoices/{invoice_id}')
            
            if response:
                return {
                    'invoice_id': invoice_id,
                    'status': response.get('status'),
                    'amount': float(response.get('amount', 0)),
                    'currency': response.get('currency'),
                    'paid_amount': float(response.get('paidAmount', 0)),
                    'created_time': response.get('createdTime'),
                    'expiration_time': response.get('expirationTime')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting invoice status: {e}")
            return None
    
    def _start_invoice_monitoring(self, invoice_id: str):
        """Start monitoring invoice for status changes"""
        def monitor():
            start_time = time.time()
            last_status = None
            
            while time.time() - start_time < config.btcpay.payment_timeout:
                try:
                    status_info = self.get_invoice_status(invoice_id)
                    
                    if status_info:
                        current_status = status_info['status']
                        
                        # Check if status changed
                        if current_status != last_status:
                            logger.info(f"Invoice {invoice_id} status changed to: {current_status}")
                            
                            # Call registered callback if exists
                            if invoice_id in self._payment_callbacks:
                                try:
                                    self._payment_callbacks[invoice_id](status_info)
                                except Exception as e:
                                    logger.error(f"Error in payment callback: {e}")
                            
                            last_status = current_status
                            
                            # Stop monitoring if payment is settled, expired, or invalid
                            if current_status in [InvoiceStatus.SETTLED.value,
                                                InvoiceStatus.EXPIRED.value, 
                                                InvoiceStatus.INVALID.value]:
                                break
                    
                    time.sleep(2)  # Check every 2 seconds
                    
                except Exception as e:
                    logger.error(f"Error monitoring invoice {invoice_id}: {e}")
                    time.sleep(5)
            
            # Clean up callback
            if invoice_id in self._payment_callbacks:
                del self._payment_callbacks[invoice_id]
        
        # Start monitoring in separate thread
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def register_payment_callback(self, invoice_id: str, callback: Callable[[Dict], None]):
        """Register callback for payment status updates"""
        self._payment_callbacks[invoice_id] = callback
    
    def is_invoice_paid(self, invoice_id: str) -> bool:
        """Check if invoice is paid"""
        try:
            status_info = self.get_invoice_status(invoice_id)
            if status_info:
                status = status_info['status']
                # Only SETTLED status means the invoice is actually paid
                return status == InvoiceStatus.SETTLED.value
            return False
            
        except Exception as e:
            logger.error(f"Error checking invoice payment status: {e}")
            return False
    
    def wait_for_payment(self, invoice_id: str, timeout: float = None) -> bool:
        """Wait for invoice payment with timeout"""
        if timeout is None:
            timeout = config.btcpay.payment_timeout
            
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.is_invoice_paid(invoice_id):
                logger.info(f"Invoice {invoice_id} payment confirmed")
                return True
                
            time.sleep(2)
        
        logger.warning(f"Invoice {invoice_id} payment timeout")
        return False
    
    def cancel_invoice(self, invoice_id: str) -> bool:
        """Cancel an invoice"""
        try:
            response = self._make_request('DELETE', f'/api/v1/stores/{self.store_id}/invoices/{invoice_id}')
            if response is not None:
                logger.info(f"Invoice {invoice_id} cancelled")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling invoice: {e}")
            return False
    
    def check_connection(self) -> bool:
        """Check BTCPay Server connection"""
        try:
            # Use the same method as initialize() - create a small test invoice
            test_invoice_data = {
                "amount": "0.01",
                "currency": "EUR",
                "metadata": {
                    "orderId": f"connection_check_{int(time.time())}",
                    "itemDesc": "Connection Check"
                }
            }
            
            response = self._make_request('POST', f'/api/v1/stores/{self.store_id}/invoices', test_invoice_data)
            
            if response and 'id' in response:
                # Try to cancel the test invoice to clean up
                try:
                    self._make_request('DELETE', f'/api/v1/stores/{self.store_id}/invoices/{response["id"]}')
                except:
                    pass  # Ignore cleanup failures
                
                self.is_connected = True
                return True
            else:
                self.is_connected = False
                return False
            
        except Exception as e:
            logger.error(f"BTCPay connection check failed: {e}")
            self.is_connected = False
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get client status"""
        return {
            'connected': self.is_connected,
            'server_url': self.server_url,
            'store_id': self.store_id
        } 