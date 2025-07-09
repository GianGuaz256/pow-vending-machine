"""
LCD Display Controller for Waveshare 3.5 inch Touch Screen
Handles display initialization, text rendering, and QR code display
"""
import pygame
import time
import threading
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple, List
import qrcode
import logging
from config import config

logger = logging.getLogger(__name__)

class LCDDisplay:
    """Controller for Waveshare 3.5 inch LCD display"""
    
    def __init__(self):
        # Use larger display size for better visibility
        self.width = max(config.display.width, 640)
        self.height = max(config.display.height, 480)
        self.screen = None
        self.font_small = None
        self.font_medium = None
        self.font_large = None
        self.is_initialized = False
        self._lock = threading.Lock()
        
    def initialize(self) -> bool:
        """Initialize the LCD display"""
        try:
            # Initialize pygame
            pygame.init()
            
            # Set up display
            self.screen = pygame.display.set_mode((self.width, self.height))
            pygame.display.set_caption("Bitcoin Vending Machine")
            
            # Load fonts (increased sizes for better visibility)
            try:
                self.font_small = pygame.font.Font(None, 32)
                self.font_medium = pygame.font.Font(None, 48)
                self.font_large = pygame.font.Font(None, 64)
            except:
                # Fallback to default font
                self.font_small = pygame.font.Font(None, 28)
                self.font_medium = pygame.font.Font(None, 42)
                self.font_large = pygame.font.Font(None, 56)
            
            self.is_initialized = True
            self.clear_screen()
            self.show_message("Display Initialized", "System Ready")
            logger.info("LCD display initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize LCD display: {e}")
            return False
    
    def clear_screen(self, color: Tuple[int, int, int] = (0, 0, 0)):
        """Clear the screen with specified color"""
        if not self.is_initialized:
            return
            
        with self._lock:
            self.screen.fill(color)
            pygame.display.flip()
    
    def show_message(self, title: str, message: str = "", 
                    title_color: Tuple[int, int, int] = (255, 255, 255),
                    message_color: Tuple[int, int, int] = (200, 200, 200)):
        """Display a message with title"""
        if not self.is_initialized:
            return
        
        # Debug output so user can see what's displayed
        print(f"🖥️  DISPLAY: {title}")
        if message:
            print(f"     {message}")
            
        with self._lock:
            # Clear screen without flipping
            self.screen.fill((0, 0, 0))
            
            # Render title
            title_surface = self.font_large.render(title, True, title_color)
            title_rect = title_surface.get_rect(center=(self.width // 2, self.height // 4))
            self.screen.blit(title_surface, title_rect)
            
            # Render message if provided
            if message:
                # Split long messages into multiple lines
                words = message.split(' ')
                lines = []
                current_line = ""
                
                for word in words:
                    test_line = current_line + word + " "
                    test_surface = self.font_medium.render(test_line, True, message_color)
                    if test_surface.get_width() > self.width - 40:
                        if current_line:
                            lines.append(current_line.strip())
                        current_line = word + " "
                    else:
                        current_line = test_line
                
                if current_line:
                    lines.append(current_line.strip())
                
                # Render each line
                for i, line in enumerate(lines):
                    line_surface = self.font_medium.render(line, True, message_color)
                    line_rect = line_surface.get_rect(center=(self.width // 2, 
                                                            self.height // 2 + i * 40))
                    self.screen.blit(line_surface, line_rect)
            
            pygame.display.flip()
    
    def show_qr_code(self, data: str, title: str = "Scan to Pay"):
        """Display a QR code with title"""
        if not self.is_initialized:
            return
        
        # Debug output so user can see what's displayed
        print(f"🖥️  DISPLAY QR: {title}")
        print(f"     QR Data: {data[:80]}{'...' if len(data) > 80 else ''}")
            
        try:
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=4,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create QR code image
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Resize to fit display
            qr_size = min(self.width - 40, self.height - 100)
            qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
            
            # Convert PIL image to pygame surface
            # Ensure image is in RGB mode for pygame compatibility
            if qr_img.mode != 'RGB':
                qr_img = qr_img.convert('RGB')
            qr_size = qr_img.size
            qr_data = qr_img.tobytes()
            qr_surface = pygame.image.fromstring(qr_data, qr_size, 'RGB')
            
            with self._lock:
                # Clear screen without flipping
                self.screen.fill((0, 0, 0))
                
                # Show title
                title_surface = self.font_medium.render(title, True, (255, 255, 255))
                title_rect = title_surface.get_rect(center=(self.width // 2, 30))
                self.screen.blit(title_surface, title_rect)
                
                # Show QR code
                qr_rect = qr_surface.get_rect(center=(self.width // 2, self.height // 2 + 20))
                self.screen.blit(qr_surface, qr_rect)
                
                pygame.display.flip()
                
        except Exception as e:
            logger.error(f"Failed to display QR code: {e}")
            self.show_message("Error", "Failed to generate QR code")
    
    def show_qr_with_status(self, qr_data: str, amount: float, currency: str, status: str, title: str = "Scan to Pay"):
        """Display QR code with payment status underneath"""
        if not self.is_initialized:
            return
        
        # Debug output so user can see what's displayed
        print(f"🖥️  DISPLAY QR + STATUS: {title}")
        print(f"     QR Data: {qr_data[:80]}{'...' if len(qr_data) > 80 else ''}")
        print(f"     Payment: {amount:.2f} {currency} - {status.upper()}")
            
        try:
            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=3,  # Smaller QR code to leave room for status
                border=4,
            )
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            # Create QR code image
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Resize to fit display (smaller to leave room for status)
            qr_size = min(self.width - 60, (self.height - 120) // 2)
            qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
            
            # Convert PIL image to pygame surface
            if qr_img.mode != 'RGB':
                qr_img = qr_img.convert('RGB')
            qr_img_size = qr_img.size
            qr_data_bytes = qr_img.tobytes()
            qr_surface = pygame.image.fromstring(qr_data_bytes, qr_img_size, 'RGB')
            
            # Status colors
            status_colors = {
                "waiting": (255, 255, 0),    # Yellow
                "paid": (0, 255, 0),         # Green
                "expired": (255, 0, 0),      # Red
                "error": (255, 0, 0)         # Red
            }
            status_color = status_colors.get(status.lower(), (255, 255, 255))
            
            with self._lock:
                # Clear screen without flipping
                self.screen.fill((0, 0, 0))
                
                # Show title
                title_surface = self.font_medium.render(title, True, (255, 255, 255))
                title_rect = title_surface.get_rect(center=(self.width // 2, 30))
                self.screen.blit(title_surface, title_rect)
                
                # Show QR code (positioned higher)
                qr_y_pos = 80 + (self.height - 200) // 4
                qr_rect = qr_surface.get_rect(center=(self.width // 2, qr_y_pos))
                self.screen.blit(qr_surface, qr_rect)
                
                # Show amount
                amount_text = f"{amount:.2f} {currency}"
                amount_surface = self.font_large.render(amount_text, True, (255, 255, 255))
                amount_rect = amount_surface.get_rect(center=(self.width // 2, qr_y_pos + qr_size//2 + 40))
                self.screen.blit(amount_surface, amount_rect)
                
                # Show status
                status_surface = self.font_medium.render(status.upper(), True, status_color)
                status_rect = status_surface.get_rect(center=(self.width // 2, qr_y_pos + qr_size//2 + 90))
                self.screen.blit(status_surface, status_rect)
                
                pygame.display.flip()
                
        except Exception as e:
            logger.error(f"Failed to display QR code with status: {e}")
            self.show_message("Error", "Failed to generate QR code")
    
    def show_payment_status(self, amount: float, currency: str, status: str):
        """Display payment status"""
        if not self.is_initialized:
            return
        
        # Debug output so user can see what's displayed
        print(f"🖥️  DISPLAY PAYMENT: {amount:.2f} {currency} - {status.upper()}")
            
        status_colors = {
            "waiting": (255, 255, 0),    # Yellow
            "paid": (0, 255, 0),         # Green
            "expired": (255, 0, 0),      # Red
            "error": (255, 0, 0)         # Red
        }
        
        color = status_colors.get(status.lower(), (255, 255, 255))
        
        with self._lock:
            # Clear screen without flipping
            self.screen.fill((0, 0, 0))
            
            # Amount
            amount_text = f"{amount:.2f} {currency}"
            amount_surface = self.font_large.render(amount_text, True, (255, 255, 255))
            amount_rect = amount_surface.get_rect(center=(self.width // 2, self.height // 3))
            self.screen.blit(amount_surface, amount_rect)
            
            # Status
            status_surface = self.font_medium.render(status.upper(), True, color)
            status_rect = status_surface.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(status_surface, status_rect)
            
            pygame.display.flip()
    
    def show_dispensing(self, item_name: str = "Item"):
        """Show item dispensing animation"""
        if not self.is_initialized:
            return
        
        # Debug output so user can see what's displayed
        print(f"🖥️  DISPLAY DISPENSING: {item_name}")
            
        with self._lock:
            # Clear screen without flipping
            self.screen.fill((0, 0, 0))
            
            # Show dispensing message
            title = "Dispensing..."
            item_text = f"Enjoy your {item_name}!"
            
            title_surface = self.font_large.render(title, True, (0, 255, 0))
            title_rect = title_surface.get_rect(center=(self.width // 2, self.height // 3))
            self.screen.blit(title_surface, title_rect)
            
            item_surface = self.font_medium.render(item_text, True, (255, 255, 255))
            item_rect = item_surface.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(item_surface, item_rect)
            
            pygame.display.flip()
    
    def show_error(self, error_message: str):
        """Display error message"""
        # Debug output so user can see what's displayed
        print(f"🖥️  DISPLAY ERROR: {error_message}")
        
        self.show_message("ERROR", error_message, 
                         title_color=(255, 0, 0), 
                         message_color=(255, 200, 200))
    
    def show_system_status(self, mdb_status: bool, btcpay_status: bool, display_status: bool):
        """Show system component status"""
        if not self.is_initialized:
            return
            
        with self._lock:
            # Clear screen without flipping
            self.screen.fill((0, 0, 0))
            
            # Title
            title_surface = self.font_large.render("System Status", True, (255, 255, 255))
            title_rect = title_surface.get_rect(center=(self.width // 2, 50))
            self.screen.blit(title_surface, title_rect)
            
            # Status items
            statuses = [
                ("MDB Board", mdb_status),
                ("BTCPay Server", btcpay_status),
                ("Display", display_status)
            ]
            
            for i, (component, status) in enumerate(statuses):
                y_pos = 120 + i * 60
                
                # Component name
                comp_surface = self.font_medium.render(component, True, (255, 255, 255))
                comp_rect = comp_surface.get_rect(left=20, centery=y_pos)
                self.screen.blit(comp_surface, comp_rect)
                
                # Status
                status_text = "OK" if status else "ERROR"
                status_color = (0, 255, 0) if status else (255, 0, 0)
                status_surface = self.font_medium.render(status_text, True, status_color)
                status_rect = status_surface.get_rect(right=self.width - 20, centery=y_pos)
                self.screen.blit(status_surface, status_rect)
            
            pygame.display.flip()
    
    def close(self):
        """Close the display"""
        if self.is_initialized:
            pygame.quit()
            self.is_initialized = False
            logger.info("LCD display closed") 