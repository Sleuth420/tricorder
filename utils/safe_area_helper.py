# --- utils/safe_area_helper.py ---
# Helper functions for safe area visualization and testing

import pygame
import logging

logger = logging.getLogger(__name__)

def draw_safe_area_overlay(screen, ui_scaler, config_module, alpha=100):
    """
    Draw a visual overlay showing the safe area boundaries.
    Useful for testing and adjusting safe area settings.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        ui_scaler (UIScaler): UI scaler instance with safe area settings
        config_module (module): Configuration module for colors
        alpha (int): Transparency level (0-255)
    """
    if not ui_scaler.safe_area_enabled:
        return
    
    # Create overlay surface
    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(alpha)
    
    # Fill with background color
    overlay.fill(config_module.Theme.BACKGROUND)
    
    # Draw safe area rectangle
    safe_rect = ui_scaler.get_safe_area_rect()
    pygame.draw.rect(overlay, config_module.Theme.ACCENT, safe_rect, 2)
    
    # Draw corner indicators
    corner_size = 10
    corners = [
        (safe_rect.left, safe_rect.top),  # Top-left
        (safe_rect.right - corner_size, safe_rect.top),  # Top-right
        (safe_rect.left, safe_rect.bottom - corner_size),  # Bottom-left
        (safe_rect.right - corner_size, safe_rect.bottom - corner_size)  # Bottom-right
    ]
    
    for corner_x, corner_y in corners:
        pygame.draw.rect(overlay, config_module.Theme.ALERT, 
                        (corner_x, corner_y, corner_size, corner_size))
    
    # Blit overlay to screen
    screen.blit(overlay, (0, 0))

def draw_safe_area_info(screen, ui_scaler, fonts, config_module, x=10, y=10):
    """
    Draw text information about safe area settings.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        ui_scaler (UIScaler): UI scaler instance with safe area settings
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module for colors
        x (int): X position for text
        y (int): Y position for text
    """
    if not ui_scaler.safe_area_enabled:
        return
    
    font = fonts.get('small', fonts.get('medium'))
    safe_rect = ui_scaler.get_safe_area_rect()
    margins = ui_scaler.get_safe_area_margins()
    
    lines = [
        f"Safe Area: {safe_rect.width}x{safe_rect.height}",
        f"Margins: T:{margins['top']} B:{margins['bottom']} L:{margins['left']} R:{margins['right']}",
        f"Position: ({safe_rect.left}, {safe_rect.top})"
    ]
    
    for i, line in enumerate(lines):
        text_surface = font.render(line, True, config_module.Theme.TEXT_ACCENT)
        screen.blit(text_surface, (x, y + i * 20))

def test_safe_area_settings(ui_scaler, test_points=None):
    """
    Test safe area settings with sample points.
    
    Args:
        ui_scaler (UIScaler): UI scaler instance with safe area settings
        test_points (list): List of (x, y) tuples to test
        
    Returns:
        dict: Test results
    """
    if not ui_scaler.safe_area_enabled:
        return {"safe_area_enabled": False}
    
    if test_points is None:
        # Default test points
        test_points = [
            (0, 0),  # Top-left corner
            (ui_scaler.screen_width - 1, 0),  # Top-right corner
            (0, ui_scaler.screen_height - 1),  # Bottom-left corner
            (ui_scaler.screen_width - 1, ui_scaler.screen_height - 1),  # Bottom-right corner
            (ui_scaler.screen_width // 2, ui_scaler.screen_height // 2),  # Center
        ]
    
    results = {
        "safe_area_enabled": True,
        "safe_area_rect": ui_scaler.get_safe_area_rect(),
        "test_points": {}
    }
    
    for point in test_points:
        x, y = point
        in_safe_area = ui_scaler.is_point_in_safe_area(x, y)
        results["test_points"][f"({x}, {y})"] = in_safe_area
    
    return results

def adjust_safe_area_for_cover(cover_type="curved_corners", screen_width=320, screen_height=240):
    """
    Get recommended safe area settings for different cover types.
    
    Args:
        cover_type (str): Type of cover ("curved_corners", "bezel", "none")
        screen_width (int): Screen width
        screen_height (int): Screen height
        
    Returns:
        dict: Recommended safe area settings
    """
    recommendations = {
        "curved_corners": {
            "SAFE_AREA_ENABLED": True,
            "SAFE_AREA_TOP": max(8, screen_height // 30),
            "SAFE_AREA_BOTTOM": max(8, screen_height // 30),
            "SAFE_AREA_LEFT": max(8, screen_width // 40),
            "SAFE_AREA_RIGHT": max(8, screen_width // 40),
            "SAFE_AREA_CORNER_RADIUS": max(12, min(screen_width, screen_height) // 20)
        },
        "bezel": {
            "SAFE_AREA_ENABLED": True,
            "SAFE_AREA_TOP": max(4, screen_height // 60),
            "SAFE_AREA_BOTTOM": max(4, screen_height // 60),
            "SAFE_AREA_LEFT": max(4, screen_width // 80),
            "SAFE_AREA_RIGHT": max(4, screen_width // 80),
            "SAFE_AREA_CORNER_RADIUS": 0
        },
        "none": {
            "SAFE_AREA_ENABLED": False,
            "SAFE_AREA_TOP": 0,
            "SAFE_AREA_BOTTOM": 0,
            "SAFE_AREA_LEFT": 0,
            "SAFE_AREA_RIGHT": 0,
            "SAFE_AREA_CORNER_RADIUS": 0
        }
    }
    
    return recommendations.get(cover_type, recommendations["none"])
