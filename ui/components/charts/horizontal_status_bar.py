# --- ui/components/horizontal_status_bar.py ---
# Enhanced horizontal battery-style status bar component for system metrics

import pygame
import logging
import time

logger = logging.getLogger(__name__)

class HorizontalStatusBar:
    """
    An enhanced horizontal battery-style status bar for displaying system metrics.
    Shows a value with red/yellow/green color zones with subtle animations and improved styling.
    """
    
    def __init__(self, screen, rect, label, units, min_val, max_val, 
                 green_range, yellow_range, fonts, config_module, ui_scaler=None):
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
            ui_scaler (UIScaler): UI scaler for scaling calculations
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
        self.ui_scaler = ui_scaler
        self._layout_logged = False  # Flag to prevent repeated layout logging
        
        # Calculate layout
        self._calculate_layout()
        
    def _calculate_layout(self):
        """Calculate positions for drawing elements using UIScaler for responsive design."""
        if self.ui_scaler:
            # Use UIScaler for responsive spacing and dimensions
            margin = self.ui_scaler.margin("small")
            self.label_width = max(60, self.ui_scaler.scale(70))  # Increased for better readability
            self.value_width = max(50, self.ui_scaler.scale(60))  # Increased for better readability
            self.bar_height = max(14, self.ui_scaler.scale(16))   # Increased height for better visibility
            
            # Debug logging for horizontal status bar layout
            if self.ui_scaler.debug_mode and not self._layout_logged:
                logger.info(f"🎨 HorizontalStatusBar({self.label}): rect={self.rect.width}x{self.rect.height}, bar_h={self.bar_height}px, label_w={self.label_width}px, value_w={self.value_width}px")
                self._layout_logged = True
        else:
            # Fallback to improved proportional calculations
            margin = max(6, self.rect.width // 35)  # Slightly larger margin
            self.label_width = max(60, self.rect.width // 4)   # 25% of width for label (increased)
            self.value_width = max(50, self.rect.width // 5)   # 20% of width for value (increased)
            self.bar_height = max(14, self.rect.height // 2)   # Increased height
        
        # Bar dimensions - improved spacing and positioning
        self.bar_x = self.rect.left + self.label_width + margin
        self.bar_y = self.rect.centery - (self.bar_height // 2)  # Center vertically
        self.bar_width = self.rect.width - self.label_width - self.value_width - (margin * 3)
        
        # Ensure minimum bar width
        self.bar_width = max(50, self.bar_width)
        
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
    
    def _get_enhanced_color_for_value(self, value, current_time):
        """Get enhanced color with subtle animation for critical values."""
        base_color = self._get_color_for_value(value)
        
        # Add pulsing effect for critical values (red)
        if value is not None and base_color == self.config.Palette.RED_ALERT:
            pulse = (current_time * 2.0) % 2.0
            pulse_factor = 0.8 + 0.2 * (0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate(pulse * 180).x)
            return tuple(int(c * pulse_factor) for c in base_color)
        
        return base_color
            
    def draw(self, current_value, formatted_text=None):
        """
        Draw the enhanced horizontal status bar with improved styling and animations.
        
        Args:
            current_value (float): The current value to display
            formatted_text (str): Pre-formatted text to display (optional)
        """
        current_time = time.time()
        
        # Draw label with improved styling
        font_small = self.fonts.get('small', pygame.font.Font(None, self.config.FONT_SIZE_SMALL))
        label_surface = font_small.render(self.label, True, self.config.Theme.FOREGROUND)
        
        # Center label vertically and position it properly
        label_rect = label_surface.get_rect(midleft=(self.rect.left + 6, self.rect.centery))
        # Ensure label doesn't extend past reserved width
        if label_rect.right > self.rect.left + self.label_width - 6:
            label_rect.right = self.rect.left + self.label_width - 6
        self.screen.blit(label_surface, label_rect)
        
        # Draw enhanced bar with improved styling
        bar_rect = pygame.Rect(self.bar_x, self.bar_y, self.bar_width, self.bar_height)
        
        # Outer border (green theme color)
        pygame.draw.rect(self.screen, self.config.Theme.FOREGROUND, bar_rect, 2)
        
        # Inner background (dark grey for better contrast)
        inner_rect = pygame.Rect(self.bar_x + 2, self.bar_y + 2, self.bar_width - 4, self.bar_height - 4)
        pygame.draw.rect(self.screen, (25, 25, 25), inner_rect)
        
        # Draw filled portion with enhanced styling
        if current_value is not None:
            # Calculate fill percentage
            value_range = self.max_val - self.min_val
            if value_range > 0:
                fill_percentage = max(0, min(1, (current_value - self.min_val) / value_range))
                fill_width = int((self.bar_width - 4) * fill_percentage)
                
                if fill_width > 0:
                    # Get enhanced color with animations
                    fill_color = self._get_enhanced_color_for_value(current_value, current_time)
                    
                    # Draw filled portion
                    fill_rect = pygame.Rect(self.bar_x + 2, self.bar_y + 2, fill_width, self.bar_height - 4)
                    pygame.draw.rect(self.screen, fill_color, fill_rect)
                    
                    # Add subtle gradient effect for better visual appeal
                    if fill_width > 6:
                        # Top highlight
                        highlight_color = tuple(min(255, int(c * 1.2)) for c in fill_color)
                        highlight_rect = pygame.Rect(self.bar_x + 2, self.bar_y + 2, fill_width, 2)
                        pygame.draw.rect(self.screen, highlight_color, highlight_rect)
                        
                        # Add scanning effect for active bars
                        if fill_percentage > 0.1:  # Only show scanning if there's meaningful progress
                            scan_progress = (current_time * 1.5) % 2.0
                            if scan_progress < 1.0:  # Scanning beam visible for half the cycle
                                scan_width = max(2, fill_width // 8)
                                scan_x = self.bar_x + 2 + int((fill_width - scan_width) * scan_progress)
                                scan_rect = pygame.Rect(scan_x, self.bar_y + 2, scan_width, self.bar_height - 4)
                                scan_color = tuple(min(255, int(c * 1.4)) for c in fill_color)
                                pygame.draw.rect(self.screen, scan_color, scan_rect)
        
        # Draw value text with improved formatting and positioning
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
            value_text = "N/A"
        
        # Color-code the value text based on status
        if current_value is not None:
            value_color = self._get_enhanced_color_for_value(current_value, current_time)
        else:
            value_color = self.config.Theme.ALERT
            
        value_surface = font_small.render(value_text, True, value_color)
        value_rect = value_surface.get_rect(midleft=(self.value_x, self.value_y))
        self.screen.blit(value_surface, value_rect) 