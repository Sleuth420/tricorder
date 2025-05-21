import pygame
import logging

# Import the main config file (used by _load_font if kept, or by main app for font sizes)
import config # app_config will be passed in for colors etc.

logger = logging.getLogger(__name__)

# REMOVE _font_cache and _load_font - fonts will be passed in
# _font_cache = {} 
# def _load_font(size):
#     ...

class VerticalBarGraph:
    """
    Represents a vertical bar graph display element inspired by Star Trek LCARS.
    Displays a single value on a vertical scale with color zones and a pointer.
    """
    def __init__(self, screen, rect, title, units, min_val, max_val, normal_range, fonts, config_module, critical_low=None, critical_high=None, num_ticks=11):
        """
        Initializes the VerticalBarGraph.

        Args:
            screen (pygame.Surface): The surface to draw on.
            rect (pygame.Rect): The bounding rectangle for the graph.
            title (str): The title label (not used anymore, kept for compatibility).
            units (str): The units label (e.g., 'C', 'K3').
            min_val (float): The minimum value of the scale.
            max_val (float): The maximum value of the scale.
            normal_range (tuple): A tuple (min_normal, max_normal) defining the green zone.
            fonts (dict): Dictionary of pre-loaded Pygame fonts.
            config_module (module): The main configuration module (for theme colors, font SIZES if needed).
            critical_low (float, optional): Values below this are critical (red). Defaults to min_val.
            critical_high (float, optional): Values above this are critical (red). Defaults to max_val.
            num_ticks (int): The number of major ticks to display on the scale (including ends).
        """
        self.screen = screen
        self.rect = rect
        self.units = units
        self.min_val = min_val
        self.max_val = max_val
        self.normal_range = normal_range
        self.critical_low = critical_low if critical_low is not None else min_val
        self.critical_high = critical_high if critical_high is not None else max_val
        self.num_ticks = num_ticks
        self.fonts = fonts
        self.config = config_module

        if max_val <= min_val:
            raise ValueError("max_val must be greater than min_val")
        self.value_range = max_val - min_val

        self.font_small = self.fonts.get('small', pygame.font.Font(None, self.config.FONT_SIZE_SMALL))
        self.font_medium = self.fonts.get('medium', pygame.font.Font(None, self.config.FONT_SIZE_MEDIUM))

        self._calculate_layout()

    def _calculate_layout(self):
        """Calculates positions for drawing elements."""
        # Use full rect height for scale since we don't need title space anymore
        self.scale_rect = pygame.Rect(
            self.rect.left,
            self.rect.top,
            self.rect.width,
            self.rect.height
        )
        self.scale_line_x = self.scale_rect.centerx
        self.scale_top_y = self.scale_rect.top + 10  # Padding
        self.scale_bottom_y = self.scale_rect.bottom - 10  # Padding
        self.scale_height = self.scale_bottom_y - self.scale_top_y
        self.tick_length = 10  # Increased for better visibility
        self.label_offset_x = 20  # Increased for better spacing
        self.pointer_width = 25  # Increased for better visibility
        self.pointer_height = 15  # Increased for better visibility
        self.zone_width = 8  # Width of the color zones on each side of the scale line

    def _value_to_y(self, value):
        """Converts a data value to a Y coordinate on the scale."""
        if self.value_range == 0:
            return self.scale_bottom_y
        value = max(self.min_val, min(self.max_val, value))
        proportion = (value - self.min_val) / self.value_range
        y = self.scale_bottom_y - (proportion * self.scale_height)
        return int(y)

    def _get_zone_color(self, value):
        """Determines the color based on the value's zone, using Theme colors."""
        if value is None:
             return self.config.Palette.DARK_GREY # Use Theme
        if value < self.critical_low or value > self.critical_high:
            return self.config.Theme.ALERT # Use Theme
        elif self.normal_range[0] <= value <= self.normal_range[1]:
            return self.config.Theme.FOREGROUND # Use Theme
        else:
            return self.config.Theme.WARNING # Use Theme

    def draw(self, current_value):
        """
        Draws the vertical bar graph with the current value.
        Args:
            current_value (float): The value to display on the graph.
        """
        # Draw the main scale line
        base_scale_color = self.config.Palette.DARK_GREY
        pygame.draw.line(self.screen, base_scale_color,
                         (self.scale_line_x, self.scale_top_y),
                         (self.scale_line_x, self.scale_bottom_y), 3)

        # Draw color zones as thin lines on each side of the scale
        zone_height = self.scale_height
        
        # Draw critical low zone
        if self.critical_low > self.min_val:
            low_zone_height = int((self.critical_low - self.min_val) / self.value_range * zone_height)
            low_zone_y = self.scale_bottom_y - low_zone_height
            pygame.draw.line(self.screen, self.config.Theme.ALERT,
                           (self.scale_line_x - self.zone_width, low_zone_y),
                           (self.scale_line_x + self.zone_width, low_zone_y), 2)
        
        # Draw normal range zone
        normal_low_y = self._value_to_y(self.normal_range[1])
        normal_high_y = self._value_to_y(self.normal_range[0])
        pygame.draw.line(self.screen, self.config.Theme.FOREGROUND,
                        (self.scale_line_x - self.zone_width, normal_low_y),
                        (self.scale_line_x + self.zone_width, normal_low_y), 2)
        pygame.draw.line(self.screen, self.config.Theme.FOREGROUND,
                        (self.scale_line_x - self.zone_width, normal_high_y),
                        (self.scale_line_x + self.zone_width, normal_high_y), 2)
        
        # Draw critical high zone
        if self.critical_high < self.max_val:
            high_zone_height = int((self.max_val - self.critical_high) / self.value_range * zone_height)
            high_zone_y = self.scale_top_y + high_zone_height
            pygame.draw.line(self.screen, self.config.Theme.ALERT,
                           (self.scale_line_x - self.zone_width, high_zone_y),
                           (self.scale_line_x + self.zone_width, high_zone_y), 2)

        # Draw ticks and labels
        for i in range(self.num_ticks):
            proportion = i / (self.num_ticks - 1)
            y = self.scale_bottom_y - int(proportion * self.scale_height)
            tick_value = self.min_val + proportion * self.value_range
            tick_color = self._get_zone_color(tick_value)
            pygame.draw.line(self.screen, tick_color,
                             (self.scale_line_x - self.tick_length // 2, y),
                             (self.scale_line_x + self.tick_length // 2, y), 3)
            
            # Draw value label
            label_text = f"{tick_value:.0f}"
            label_surface = self.font_small.render(label_text, True, self.config.Theme.WHITE)
            label_rect = label_surface.get_rect(centery=y, right=self.scale_line_x - self.label_offset_x)
            self.screen.blit(label_surface, label_rect)
            
            # Draw units only for min and max values
            if i == 0 or i == self.num_ticks - 1:
                units_surface = self.font_small.render(self.units, True, self.config.Theme.WHITE)
                units_rect = units_surface.get_rect(centery=y, left=self.scale_line_x + self.label_offset_x)
                self.screen.blit(units_surface, units_rect)

        # Draw current value pointer
        if current_value is not None:
            pointer_y = self._value_to_y(current_value)
            pointer_color = self._get_zone_color(current_value)
            
            # Draw horizontal line at current value
            pygame.draw.line(self.screen, pointer_color,
                             (self.scale_line_x - self.tick_length // 2, pointer_y),
                             (self.scale_line_x + self.tick_length // 2, pointer_y),
                             3)
            
            # Draw pointer triangle
            pointer_base_x = self.scale_line_x + self.tick_length // 2 + 2
            points = [
                (pointer_base_x, pointer_y),
                (pointer_base_x + self.pointer_width, pointer_y - self.pointer_height // 2),
                (pointer_base_x + self.pointer_width, pointer_y + self.pointer_height // 2)
            ]
            pygame.draw.polygon(self.screen, self.config.Theme.WHITE, points)

        # Debug: Draw bounding box
        # pygame.draw.rect(self.screen, (0, 0, 255), self.rect, 1)
        # pygame.draw.rect(self.screen, (255, 0, 0), self.scale_rect, 1)


