# --- ui/components/horizontal_status_bar.py ---
# Horizontal battery-style status bar component for system metrics

import pygame
import logging

logger = logging.getLogger(__name__)

class HorizontalStatusBar:
    """
    A horizontal battery-style status bar for displaying system metrics.
    Shows a value with red/yellow/green color zones similar to a battery indicator.
    """
    
    def __init__(self, screen, rect, label, units, min_val, max_val, 
                 green_range, yellow_range, fonts, config_module):
        """
        Initialize the horizontal status bar.
        
        Args:
            screen (pygame.Surface): The surface to draw on
            rect (pygame.Rect): The bounding rectangle for the status bar
            label (str): The label text (e.g., "CPU", "Memory")
            units (str): The units (e.g., "%", "V")
            min_val (float): Minimum value of the range
            max_val (float): Maximum value of the range
            green_range (tuple): (min, max) for green zone (good)
            yellow_range (tuple): (min, max) for yellow zone (warning)
            fonts (dict): Dictionary of pre-loaded fonts
            config_module (module): Configuration module for colors
        """
        self.screen = screen
        self.rect = rect
        self.label = label
        self.units = units
        self.min_val = min_val
        self.max_val = max_val
        self.green_range = green_range
        self.yellow_range = yellow_range
        self.fonts = fonts
        self.config = config_module
        
        # Calculate layout
        self._calculate_layout()
        
    def _calculate_layout(self):
        """Calculate positions for drawing elements using proportional spacing like other views."""
        # Use proportional spacing based on rect width like other views
        margin = max(5, self.rect.width // 40)  # Proportional margin
        
        # Reserve proportional space for label and value
        self.label_width = max(50, self.rect.width // 5)  # 20% of width for label
        self.value_width = max(40, self.rect.width // 6)  # ~17% of width for value
        
        # Bar dimensions - proportional spacing and size
        self.bar_x = self.rect.left + self.label_width + margin
        self.bar_y = self.rect.centery - 6  # Center vertically, bar height = 12
        self.bar_width = self.rect.width - self.label_width - self.value_width - (margin * 3)  # Use remaining space
        self.bar_height = 12
        
        # Value text position
        self.value_x = self.bar_x + self.bar_width + margin
        self.value_y = self.rect.centery
        
    def _get_color_for_value(self, value):
        """Get the appropriate color for the given value."""
        if value is None:
            return self.config.Palette.DARK_GREY
            
        # Check green range first (good values)
        if self.green_range[0] <= value <= self.green_range[1]:
            return self.config.Palette.GREEN
        # Check yellow range (warning values)
        elif self.yellow_range[0] <= value <= self.yellow_range[1]:
            return self.config.Palette.ENGINEERING_GOLD
        # Everything else is red (critical)
        else:
            return self.config.Palette.RED_ALERT
            
    def draw(self, current_value, formatted_text=None):
        """
        Draw the horizontal status bar.
        
        Args:
            current_value (float): The current value to display
            formatted_text (str): Pre-formatted text to display (optional)
        """
        # Draw label - constrain to label_width area
        font_small = self.fonts.get('small', pygame.font.Font(None, self.config.FONT_SIZE_SMALL))
        label_surface = font_small.render(self.label, True, self.config.Theme.FOREGROUND)
        # Clip label to fit in reserved space
        label_rect = label_surface.get_rect(midleft=(self.rect.left + 5, self.rect.centery))
        # Ensure label doesn't extend past reserved width
        if label_rect.right > self.rect.left + self.label_width:
            label_rect.right = self.rect.left + self.label_width
        self.screen.blit(label_surface, label_rect)
        
        # Draw bar background (dark grey border)
        bar_rect = pygame.Rect(self.bar_x, self.bar_y, self.bar_width, self.bar_height)
        pygame.draw.rect(self.screen, self.config.Palette.DARK_GREY, bar_rect)
        
        # Draw bar background (black interior)
        inner_rect = pygame.Rect(self.bar_x + 1, self.bar_y + 1, self.bar_width - 2, self.bar_height - 2)
        pygame.draw.rect(self.screen, self.config.Theme.BACKGROUND, inner_rect)
        
        # Draw filled portion if we have a value
        if current_value is not None:
            # Calculate fill percentage
            value_range = self.max_val - self.min_val
            if value_range > 0:
                fill_percentage = max(0, min(1, (current_value - self.min_val) / value_range))
                fill_width = int((self.bar_width - 2) * fill_percentage)
                
                if fill_width > 0:
                    # Get color for current value
                    fill_color = self._get_color_for_value(current_value)
                    
                    # Draw filled portion
                    fill_rect = pygame.Rect(self.bar_x + 1, self.bar_y + 1, fill_width, self.bar_height - 2)
                    pygame.draw.rect(self.screen, fill_color, fill_rect)
        
        # Draw value text
        if formatted_text:
            value_text = formatted_text
        elif current_value is not None:
            if self.units == "%":
                value_text = f"{current_value:.0f}%"
            elif self.units == "V":
                value_text = f"{current_value:.1f}V"
            else:
                value_text = f"{current_value:.1f}{self.units}"
        else:
            value_text = "Not Available"
            
        value_surface = font_small.render(value_text, True, self.config.Theme.FOREGROUND)
        value_rect = value_surface.get_rect(midleft=(self.value_x, self.value_y))
        self.screen.blit(value_surface, value_rect) 