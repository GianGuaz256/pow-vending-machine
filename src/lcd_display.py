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
        self.width = config.display.width
        self.height = config.display.height
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
            
            # Load fonts
            try:
                self.font_small = pygame.font.Font(None, 24)
                self.font_medium = pygame.font.Font(None, 36)
                self.font_large = pygame.font.Font(None, 48)
            except:
                # Fallback to default font
                self.font_small = pygame.font.Font(None, 24)
                self.font_medium = pygame.font.Font(None, 32)
                self.font_large = pygame.font.Font(None, 40)
            
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
            
        with self._lock:
            self.clear_screen()
            
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
            qr_mode = qr_img.mode
            qr_size = qr_img.size
            qr_data = qr_img.tobytes()
            qr_surface = pygame.image.fromstring(qr_data, qr_size, qr_mode)
            
            with self._lock:
                self.clear_screen()
                
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
    
    def show_payment_status(self, amount: float, currency: str, status: str):
        """Display payment status"""
        if not self.is_initialized:
            return
            
        status_colors = {
            "waiting": (255, 255, 0),    # Yellow
            "paid": (0, 255, 0),         # Green
            "expired": (255, 0, 0),      # Red
            "error": (255, 0, 0)         # Red
        }
        
        color = status_colors.get(status.lower(), (255, 255, 255))
        
        with self._lock:
            self.clear_screen()
            
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
            
        with self._lock:
            self.clear_screen()
            
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
        self.show_message("ERROR", error_message, 
                         title_color=(255, 0, 0), 
                         message_color=(255, 200, 200))
    
    def show_system_status(self, mdb_status: bool, btcpay_status: bool, display_status: bool):
        """Show system component status"""
        if not self.is_initialized:
            return
            
        with self._lock:
            self.clear_screen()
            
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