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
            title (str): The title label displayed below the graph.
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
        self.title = title
        self.units = units
        self.min_val = min_val
        self.max_val = max_val
        self.normal_range = normal_range
        self.critical_low = critical_low if critical_low is not None else min_val
        self.critical_high = critical_high if critical_high is not None else max_val
        self.num_ticks = num_ticks
        self.fonts = fonts # Store the passed fonts dictionary
        self.config = config_module # Store the passed config module for theme access

        if max_val <= min_val:
            raise ValueError("max_val must be greater than min_val")
        self.value_range = max_val - min_val

        # Use fonts from the passed dictionary
        # Fallback to default font if specific size not found (or handle in main font loading)
        self.font_small = self.fonts.get('small', pygame.font.Font(None, self.config.FONT_SIZE_SMALL))
        self.font_medium = self.fonts.get('medium', pygame.font.Font(None, self.config.FONT_SIZE_MEDIUM))

        # Pre-calculate positions and sizes
        self._calculate_layout()

    def _calculate_layout(self):
        """Calculates positions for drawing elements."""
        title_height = self.font_medium.get_height() + 5
        self.scale_rect = pygame.Rect(
            self.rect.left,
            self.rect.top,
            self.rect.width,
            self.rect.height - title_height
        )
        self.scale_line_x = self.scale_rect.centerx
        self.scale_top_y = self.scale_rect.top + 10 # Padding
        self.scale_bottom_y = self.scale_rect.bottom - 10 # Padding
        self.scale_height = self.scale_bottom_y - self.scale_top_y
        self.title_pos = (self.rect.centerx, self.scale_rect.bottom + 5)
        self.tick_length = 8
        self.label_offset_x = 15
        self.pointer_width = 15
        self.pointer_height = 10

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
        base_scale_color = self.config.Palette.DARK_GREY # Use Theme
        pygame.draw.line(self.screen, base_scale_color,
                         (self.scale_line_x, self.scale_top_y),
                         (self.scale_line_x, self.scale_bottom_y), 2)

        for i in range(self.num_ticks):
            proportion = i / (self.num_ticks - 1)
            y = self.scale_bottom_y - int(proportion * self.scale_height)
            tick_value = self.min_val + proportion * self.value_range
            tick_color = self._get_zone_color(tick_value)
            pygame.draw.line(self.screen, tick_color,
                             (self.scale_line_x - self.tick_length // 2, y),
                             (self.scale_line_x + self.tick_length // 2, y), 3)
            label_text = f"{tick_value:.0f}"
            label_surface = self.font_small.render(label_text, True, self.config.Theme.WHITE) # Use Theme
            label_rect = label_surface.get_rect(centery=y, right=self.scale_line_x - self.label_offset_x)
            self.screen.blit(label_surface, label_rect)
            if i == 0 or i == self.num_ticks - 1:
                units_surface = self.font_small.render(self.units, True, self.config.Theme.WHITE) # Use Theme
                units_rect = units_surface.get_rect(centery=y, left=self.scale_line_x + self.label_offset_x)
                self.screen.blit(units_surface, units_rect)

        title_surface = self.font_medium.render(self.title.upper(), True, self.config.Theme.ACCENT) # Use Theme
        title_rect = title_surface.get_rect(centerx=self.rect.centerx, bottom=self.rect.bottom - 5)
        self.screen.blit(title_surface, title_rect)

        pointer_y = self._value_to_y(current_value if current_value is not None else self.min_val)
        pointer_color = self._get_zone_color(current_value)
        pointer_base_x = self.scale_line_x + self.tick_length // 2 + 2
        points = [
            (pointer_base_x, pointer_y),
            (pointer_base_x + self.pointer_width, pointer_y - self.pointer_height // 2),
            (pointer_base_x + self.pointer_width, pointer_y + self.pointer_height // 2)
        ]
        pygame.draw.polygon(self.screen, self.config.Theme.WHITE, points) # Use Theme

        if current_value is not None:
             pygame.draw.line(self.screen, pointer_color,
                              (self.scale_line_x - self.tick_length // 2, pointer_y),
                              (self.scale_line_x + self.tick_length // 2, pointer_y),
                              3)
        else:
             pass

        # Debug: Draw bounding box
        # pygame.draw.rect(self.screen, (0, 0, 255), self.rect, 1)
        # pygame.draw.rect(self.screen, (255, 0, 0), self.scale_rect, 1)


