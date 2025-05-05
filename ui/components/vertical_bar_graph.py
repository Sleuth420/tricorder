import pygame
import logging

# Import the main config file
import config

logger = logging.getLogger(__name__)

_font_cache = {} # Simple cache for fonts loaded here

def _load_font(size):
    """Loads font using config settings, caching results."""
    cache_key = (config.FONT_PRIMARY_PATH, size)
    if cache_key in _font_cache:
        return _font_cache[cache_key]
    
    try:
        font = pygame.font.Font(config.FONT_PRIMARY_PATH, size)
        _font_cache[cache_key] = font
        logger.debug(f"Loaded font: {config.FONT_PRIMARY_PATH if config.FONT_PRIMARY_PATH else 'Default'} size {size}")
        return font
    except pygame.error as e:
        logger.error(f"Could not load font: {config.FONT_PRIMARY_PATH} ({e}). Falling back to default font.")
        try:
            font = pygame.font.Font(None, size) # Use default font
            _font_cache[(None, size)] = font # Cache default font
            return font
        except pygame.error as e_default:
             logger.critical(f"Could not load default font! Error: {e_default}")
             raise SystemExit(f"Fatal Error: Cannot load required fonts.")

class VerticalBarGraph:
    """
    Represents a vertical bar graph display element inspired by Star Trek LCARS.
    Displays a single value on a vertical scale with color zones and a pointer.
    """
    def __init__(self, screen, rect, title, units, min_val, max_val, normal_range, critical_low=None, critical_high=None, num_ticks=11):
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

        if max_val <= min_val:
            raise ValueError("max_val must be greater than min_val")
        self.value_range = max_val - min_val

        # Load fonts using config sizes and the helper function
        self.font_small = _load_font(config.FONT_SIZE_SMALL) # Use config size
        self.font_medium = _load_font(config.FONT_SIZE_MEDIUM) # Use config size

        # Pre-calculate positions and sizes
        self._calculate_layout()

    def _calculate_layout(self):
        """Calculates positions for drawing elements."""
        # Scale area (leave space for title and units)
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
        self.label_offset_x = 15 # Horizontal distance from scale line to labels

        # Pointer dimensions
        self.pointer_width = 15
        self.pointer_height = 10

    def _value_to_y(self, value):
        """Converts a data value to a Y coordinate on the scale."""
        if self.value_range == 0:
            return self.scale_bottom_y # Avoid division by zero, place at bottom

        # Clamp value within min/max
        value = max(self.min_val, min(self.max_val, value))

        # Calculate proportion (0.0 at min_val, 1.0 at max_val)
        proportion = (value - self.min_val) / self.value_range

        # Y is inverted: 0.0 at bottom, 1.0 at top
        y = self.scale_bottom_y - (proportion * self.scale_height)
        return int(y)

    def _get_zone_color(self, value):
        """Determines the color based on the value's zone."""
        if value is None: # Handle case where current value is None
             return config.COLOR_DARK_GREY # Correct, exists
        if value < self.critical_low or value > self.critical_high:
            return config.COLOR_ALERT # Use ALERT instead of CRITICAL
        elif self.normal_range[0] <= value <= self.normal_range[1]:
            return config.COLOR_FOREGROUND # Use FOREGROUND instead of NORMAL
        else:
            return config.COLOR_WARNING # Correct, exists (aliases ACCENT)

    def draw(self, current_value):
        """
        Draws the vertical bar graph with the current value.

        Args:
            current_value (float): The value to display on the graph.
        """
        # 1. Draw Scale Line (base color, maybe grey?)
        base_scale_color = config.COLOR_DARK_GREY # Correct, exists
        pygame.draw.line(self.screen, base_scale_color,
                         (self.scale_line_x, self.scale_top_y),
                         (self.scale_line_x, self.scale_bottom_y), 2)

        # 2. Draw Ticks and Labels
        for i in range(self.num_ticks):
            proportion = i / (self.num_ticks - 1)
            y = self.scale_bottom_y - int(proportion * self.scale_height)
            tick_value = self.min_val + proportion * self.value_range

            # Determine color based on tick value zone
            tick_color = self._get_zone_color(tick_value)

            # Draw tick mark - make it thicker and colored by zone
            pygame.draw.line(self.screen, tick_color,
                             (self.scale_line_x - self.tick_length // 2, y),
                             (self.scale_line_x + self.tick_length // 2, y), 3) # Thicker tick

            # Draw label (alternate sides or pick one side)
            # Example: Labels on the left
            label_text = f"{tick_value:.0f}" # Format as integer for now
            label_surface = self.font_small.render(label_text, True, config.COLOR_WHITE) # Correct, exists now
            label_rect = label_surface.get_rect(centery=y, right=self.scale_line_x - self.label_offset_x)
            self.screen.blit(label_surface, label_rect)

            # Display units next to specific ticks (e.g., first and last)
            if i == 0 or i == self.num_ticks - 1 : # Show units near top/bottom
                units_surface = self.font_small.render(self.units, True, config.COLOR_WHITE) # Correct, exists now
                # Position units on the right side
                units_rect = units_surface.get_rect(centery=y, left=self.scale_line_x + self.label_offset_x)
                self.screen.blit(units_surface, units_rect)


        # 3. Draw Title
        title_surface = self.font_medium.render(self.title.upper(), True, config.COLOR_ACCENT) # Correct, exists
        title_rect = title_surface.get_rect(centerx=self.rect.centerx, bottom=self.rect.bottom - 5) # Position below scale
        self.screen.blit(title_surface, title_rect)


        # 4. Draw Pointer
        pointer_y = self._value_to_y(current_value if current_value is not None else self.min_val) # Place pointer at min if None
        pointer_color = self._get_zone_color(current_value) # Get color even if None (will be grey)


        # Draw pointer shape (adjust position to align with scale line)
        pointer_base_x = self.scale_line_x + self.tick_length // 2 + 2
        points = [
            (pointer_base_x, pointer_y), # Tip point
            (pointer_base_x + self.pointer_width, pointer_y - self.pointer_height // 2), # Top back
            (pointer_base_x + self.pointer_width, pointer_y + self.pointer_height // 2)  # Bottom back
        ]
        pygame.draw.polygon(self.screen, config.COLOR_WHITE, points) # Correct, exists now

        # Draw a horizontal line across the scale at the current value's Y position
        # Use the zone color for this line
        if current_value is not None:
             pygame.draw.line(self.screen, pointer_color,
                              (self.scale_line_x - self.tick_length // 2, pointer_y), # Start left of scale
                              (self.scale_line_x + self.tick_length // 2, pointer_y), # End right of scale
                              3) # Thickness
        else:
             # Optionally indicate missing value on the scale itself
             pass # For now, the grey pointer indicates missing data

        # Debug: Draw bounding box
        # pygame.draw.rect(self.screen, (0, 0, 255), self.rect, 1)
        # pygame.draw.rect(self.screen, (255, 0, 0), self.scale_rect, 1)


