"""
Simple LCD Test - Just QR Code and Success Message
Minimal test for display functionality on regular monitor
"""
import sys
import os
import pygame
import qrcode
from PIL import Image

# Add project root and src to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

def create_simple_display():
    """Create a simple pygame display"""
    pygame.init()
    
    # Use a reasonable size for regular monitor
    width, height = 800, 600
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Bitcoin Vending Machine Test")
    
    return screen, width, height

def show_text_message(screen, width, height, title, message):
    """Show a simple text message"""
    # Clear screen with black background
    screen.fill((0, 0, 0))
    
    # Create fonts
    try:
        title_font = pygame.font.Font(None, 48)
        message_font = pygame.font.Font(None, 32)
    except:
        title_font = pygame.font.Font(None, 36)
        message_font = pygame.font.Font(None, 24)
    
    # Render title
    title_surface = title_font.render(title, True, (255, 255, 255))
    title_rect = title_surface.get_rect(center=(width // 2, height // 4))
    screen.blit(title_surface, title_rect)
    
    # Render message
    message_surface = message_font.render(message, True, (200, 200, 200))
    message_rect = message_surface.get_rect(center=(width // 2, height // 2))
    screen.blit(message_surface, message_rect)
    
    pygame.display.flip()

def show_qr_with_message(screen, width, height, qr_data, title):
    """Show QR code with a title message"""
    # Clear screen
    screen.fill((0, 0, 0))
    
    try:
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=6,
            border=4,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        
        # Create QR image
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Resize QR code to fit nicely
        qr_size = min(width - 100, height - 150)
        qr_img = qr_img.resize((qr_size, qr_size), Image.Resampling.LANCZOS)
        
        # Convert PIL image to pygame surface properly
        # Convert to RGB if not already
        if qr_img.mode != 'RGB':
            qr_img = qr_img.convert('RGB')
        
        qr_size_tuple = qr_img.size
        qr_data_bytes = qr_img.tobytes()
        qr_surface = pygame.image.fromstring(qr_data_bytes, qr_size_tuple, 'RGB')
        
        # Show title
        try:
            title_font = pygame.font.Font(None, 36)
        except:
            title_font = pygame.font.Font(None, 24)
            
        title_surface = title_font.render(title, True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(width // 2, 50))
        screen.blit(title_surface, title_rect)
        
        # Show QR code
        qr_rect = qr_surface.get_rect(center=(width // 2, height // 2 + 20))
        screen.blit(qr_surface, qr_rect)
        
        pygame.display.flip()
        return True
        
    except Exception as e:
        print(f"QR generation failed: {e}")
        show_text_message(screen, width, height, "QR Error", f"Failed: {str(e)}")
        return False

def wait_for_events(duration):
    """Wait while processing events"""
    clock = pygame.time.Clock()
    elapsed = 0
    
    while elapsed < duration * 1000:  # Convert to milliseconds
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        
        clock.tick(60)  # 60 FPS
        elapsed += clock.get_time()
    
    return True

def main():
    """Simple test main function"""
    print("Starting simple LCD test...")
    
    try:
        # Create display
        screen, width, height = create_simple_display()
        
        # Test 1: Welcome message
        print("Test 1: Welcome message")
        show_text_message(screen, width, height, "Bitcoin Vending Machine", "Display Test Starting...")
        if not wait_for_events(2):
            return
        
        # Test 2: QR Code
        print("Test 2: QR Code display")
        test_data = "bitcoin:bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh?amount=0.001"
        qr_success = show_qr_with_message(screen, width, height, test_data, "Scan to Pay - Test QR")
        
        if qr_success:
            print("✓ QR code displayed successfully!")
        else:
            print("✗ QR code failed")
            
        if not wait_for_events(5):
            return
        
        # Test 3: Success message
        print("Test 3: Success message")
        show_text_message(screen, width, height, "Payment Received!", "Transaction Successful")
        if not wait_for_events(3):
            return
        
        # Test 4: Final message
        show_text_message(screen, width, height, "Test Complete", "Closing automatically in 3 seconds...")
        if not wait_for_events(3):
            return
        
        print("✓ All tests completed successfully!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
    finally:
        pygame.quit()

if __name__ == "__main__":
    main() 