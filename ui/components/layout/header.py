# --- ui/components/header.py ---
# Reusable header component to eliminate duplication across views

import pygame
import logging

logger = logging.getLogger(__name__)

class Header:
    """
    Reusable header component that provides consistent header styling
    and positioning across all views.
    
    Eliminates the duplication of header creation code found in:
    - system_info_view.py
    - controls_view.py  
    - sensors_menu_view.py
    - schematics_menu_view.py
    - schematics_3d_viewer.py
    - secret_games_view.py
    - sensor_view.py
    - list_menu_base.py
    """
    
    def __init__(self, ui_scaler, config_module):
        """
        Initialize the Header component.
        
        Args:
            ui_scaler (UIScaler): UI scaling system for consistent dimensions
            config_module (module): Configuration module for colors and constants
        """
        self.ui_scaler = ui_scaler
        self.config = config_module
        
        # Calculate header dimensions using UIScaler
        self.height = self.ui_scaler.header_height()
        self.top_margin = self.ui_scaler.header_top_margin()
        
        logger.debug(f"Header initialized: height={self.height}, top_margin={self.top_margin}")
    
    def draw(self, screen, title, fonts, style="default", status_text=None, center_title=True):
        """
        Draw the header with consistent styling.
        
        Args:
            screen (pygame.Surface): The surface to draw on
            title (str): The header title text
            fonts (dict): Dictionary of loaded fonts
            style (str): Header style - "default", "accent", "frozen", or "large"
            status_text (str, optional): Additional status text (e.g., "[FROZEN]")
            center_title (bool): Whether to center the title (default True)
            
        Returns:
            pygame.Rect: The header rectangle for layout calculations
        """
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        # Create header rectangle
        header_rect = pygame.Rect(0, self.top_margin, screen_width, self.height)
        
        # Debug logging for header layout
        if self.ui_scaler.debug_mode:
            logger.info(f"🎨 Header: screen={screen_width}x{screen_height}, rect={header_rect}, style='{style}', title='{title}'")
        
        # Fill header background (usually same as main background)
        pygame.draw.rect(screen, self.config.Theme.BACKGROUND, header_rect)
        
        # Determine font and color based on style
        if style == "large":
            font = fonts.get('large', fonts.get('medium', fonts['default']))
            text_color = self.config.Palette.VIKING_BLUE
        elif style == "accent":
            font = fonts.get('medium', fonts['default'])
            text_color = self.config.Theme.ACCENT
        elif style == "frozen":
            font = fonts.get('medium', fonts['default'])
            text_color = self.config.Theme.FROZEN_INDICATOR
        else:  # default
            font = fonts.get('medium', fonts['default'])
            text_color = self.config.Theme.ACCENT
        
        # Prepare title text with optional status
        title_text = title
        if status_text:
            title_text += f" {status_text}"
        
        # Render title text
        title_surface = font.render(title_text, True, text_color)
        
        # Position title
        if center_title:
            title_rect = title_surface.get_rect(center=(screen_width // 2, header_rect.centery))
        else:
            # Left-aligned with margin
            margin = self.ui_scaler.margin("medium")
            title_rect = title_surface.get_rect(midleft=(margin, header_rect.centery))
        
        # Draw title
        screen.blit(title_surface, title_rect)
        
        return header_rect
    
    def draw_system_info_header(self, screen, fonts, app_state):
        """
        Draw header specifically for system info view with frozen status.
        
        Args:
            screen (pygame.Surface): The surface to draw on
            fonts (dict): Dictionary of loaded fonts
            app_state (AppState): Application state for frozen status
            
        Returns:
            pygame.Rect: The header rectangle
        """
        title = "System Status"
        status_text = "[FROZEN]" if app_state.is_frozen else None
        style = "frozen" if app_state.is_frozen else "accent"
        
        return self.draw(screen, title, fonts, style=style, status_text=status_text)
    
    def draw_menu_header(self, screen, title, fonts, style="large"):
        """
        Draw header for menu views (sensors, schematics, etc.).
        
        Args:
            screen (pygame.Surface): The surface to draw on
            title (str): Menu title
            fonts (dict): Dictionary of loaded fonts
            style (str): Header style (default "large" for menus)
            
        Returns:
            pygame.Rect: The header rectangle
        """
        return self.draw(screen, title, fonts, style=style, center_title=True)
    
    def draw_settings_header(self, screen, title, fonts):
        """
        Draw header for settings views.
        
        Args:
            screen (pygame.Surface): The surface to draw on
            title (str): Settings page title
            fonts (dict): Dictionary of loaded fonts
            
        Returns:
            pygame.Rect: The header rectangle
        """
        return self.draw(screen, title, fonts, style="default", center_title=True)
    
    def get_content_start_y(self):
        """
        Get the Y coordinate where content should start after the header.
        
        Returns:
            int: Y coordinate for content start
        """
        return self.top_margin + self.height + self.ui_scaler.margin("medium")
    
    def get_header_rect(self, screen_width):
        """
        Get the header rectangle without drawing.
        
        Args:
            screen_width (int): Screen width for rectangle calculation
            
        Returns:
            pygame.Rect: The header rectangle
        """
        return pygame.Rect(0, self.top_margin, screen_width, self.height)
    
    def get_dimensions(self):
        """
        Get header dimensions for layout calculations.
        
        Returns:
            dict: Dictionary with header dimensions
        """
        return {
            "height": self.height,
            "top_margin": self.top_margin,
            "total_height": self.top_margin + self.height
        }

 