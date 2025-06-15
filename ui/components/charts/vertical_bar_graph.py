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
    Features dynamic range scaling with stability for better readability on small displays.
    """
    def __init__(self, screen, rect, title, units, min_val, max_val, normal_range, fonts, config_module, 
                 critical_low=None, critical_high=None, num_ticks=11, 
                 dynamic_range=False, zoom_factor=0.3, min_zoom_range=None, stability_threshold=2.0, ui_scaler=None):
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
            dynamic_range (bool): Enable dynamic scaling around current value.
            zoom_factor (float): Proportion of full range to show (0.3 = 30% of full range).
            min_zoom_range (float): Minimum range to show (prevents over-zooming).
            stability_threshold (float): Minimum change needed to adjust scale range (prevents jumpiness).
            ui_scaler (UIScaler, optional): The UI scaler for scaling calculations.
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
        self.ui_scaler = ui_scaler
        
        # Dynamic range features
        self.dynamic_range = dynamic_range
        self.zoom_factor = zoom_factor
        self.min_zoom_range = min_zoom_range or (max_val - min_val) * 0.2
        self.stability_threshold = stability_threshold
        
        # Stability tracking for range switching
        self.current_display_min = min_val
        self.current_display_max = max_val
        self.switch_counter = 0
        self.pending_range = None

        if max_val <= min_val:
            raise ValueError("max_val must be greater than min_val")
        self.value_range = max_val - min_val

        self.font_small = self.fonts.get('small', pygame.font.Font(None, self.config.FONT_SIZE_SMALL))
        self.font_medium = self.fonts.get('medium', pygame.font.Font(None, self.config.FONT_SIZE_MEDIUM))

        self._calculate_layout()

    def _calculate_layout(self):
        """Calculates positions for drawing elements with improved spacing using UIScaler for responsive design."""
        if self.ui_scaler:
            # Use UIScaler for responsive spacing and dimensions
            padding = self.ui_scaler.margin("medium")
            self.tick_length = self.ui_scaler.scale(20)  # Responsive tick length
            self.label_offset_x = self.ui_scaler.scale(35)  # Responsive label offset
            self.pointer_width = self.ui_scaler.scale(35)  # Responsive pointer width
            self.pointer_height = self.ui_scaler.scale(20)  # Responsive pointer height
            self.zone_width = self.ui_scaler.scale(8)  # Responsive zone width
            
            # Debug logging for vertical bar graph layout
            if self.ui_scaler.debug_mode:
                logger.info(f"🎨 VerticalBarGraph({self.units}): rect={self.rect.width}x{self.rect.height}, tick_len={self.tick_length}px, pointer={self.pointer_width}x{self.pointer_height}px")
        else:
            # Fallback to original hardcoded calculations
            padding = 15
            self.tick_length = 20
            self.label_offset_x = 35
            self.pointer_width = 35
            self.pointer_height = 20
            self.zone_width = 8
        
        # Use full rect height for scale since we don't need title space anymore
        self.scale_rect = pygame.Rect(
            self.rect.left,
            self.rect.top,
            self.rect.width,
            self.rect.height
        )
        self.scale_line_x = self.scale_rect.centerx
        self.scale_top_y = self.scale_rect.top + padding
        self.scale_bottom_y = self.scale_rect.bottom - padding
        self.scale_height = self.scale_bottom_y - self.scale_top_y

    def _calculate_stable_dynamic_range(self, current_value):
        """Calculate range - initialize with correct range, switch when within threshold of edge."""
        if not self.dynamic_range or current_value is None:
            return self.min_val, self.max_val
        
        # Define ranges for temperature
        if self.units == "°C":
            ranges = [
                (-10, 20),
                (0, 30),
                (10, 40),
                (20, 50),
                (30, 60),
                (40, 70)
            ]
            threshold = 3.0
            required_consecutive = 10
        elif self.units == "%":
            ranges = [
                (0, 25),
                (15, 40),
                (30, 55),
                (45, 70),
                (60, 85),
                (75, 100)
            ]
            threshold = 5.0
            required_consecutive = 5
        elif self.units == "mbar":
            ranges = [
                (900, 950),
                (925, 975),
                (950, 1000),
                (975, 1025),
                (1000, 1050),
                (1025, 1075)
            ]
            threshold = 3.0
            required_consecutive = 5
        else:
            ranges = [(0, 75), (25, 100)]
            threshold = 5.0
            required_consecutive = 5

        # Initialize with correct range on first reading only
        if not hasattr(self, 'current_display_min') or not hasattr(self, 'current_display_max'):
            for range_min, range_max in ranges:
                if range_min <= current_value <= range_max:
                    self.current_display_min = range_min
                    self.current_display_max = range_max
                    self.consecutive_readings = 0
                    print(f"[DBG] Initialized range to {range_min}-{range_max} for value {current_value}")
                    break

        # Find the next range (up or down) if needed
        current_idx = None
        for idx, (range_min, range_max) in enumerate(ranges):
            if (range_min, range_max) == (self.current_display_min, self.current_display_max):
                current_idx = idx
                break

        next_range = None
        # Check if we are near the upper edge and can go up
        if current_idx is not None and current_idx + 1 < len(ranges):
            upper_min, upper_max = ranges[current_idx + 1]
            if upper_min <= current_value <= upper_max:
                next_range = (upper_min, upper_max)
                edge = 'upper'
        # Check if we are near the lower edge and can go down
        if next_range is None and current_idx is not None and current_idx - 1 >= 0:
            lower_min, lower_max = ranges[current_idx - 1]
            if lower_min <= current_value <= lower_max:
                next_range = (lower_min, lower_max)
                edge = 'lower'

        # Only increment counter if within threshold of edge
        if self.current_display_min <= current_value <= self.current_display_max:
            near_upper = current_value > self.current_display_max - threshold
            near_lower = current_value < self.current_display_min + threshold
            if near_upper or near_lower:
                self.consecutive_readings = getattr(self, 'consecutive_readings', 0) + 1
                print(f"[DBG] Value {current_value} near {('upper' if near_upper else 'lower')} edge of {self.current_display_min}-{self.current_display_max}. Consecutive: {self.consecutive_readings}")
                if self.consecutive_readings >= required_consecutive and next_range:
                    print(f"[DBG] Switching range from {self.current_display_min}-{self.current_display_max} to {next_range[0]}-{next_range[1]} after {required_consecutive} consecutive readings.")
                    self.current_display_min, self.current_display_max = next_range
                    self.consecutive_readings = 0
            else:
                if getattr(self, 'consecutive_readings', 0) != 0:
                    print(f"[DBG] Value {current_value} not near edge. Resetting consecutive counter.")
                self.consecutive_readings = 0
        else:
            print(f"[DBG] Value {current_value} is outside current range {self.current_display_min}-{self.current_display_max}")
            self.consecutive_readings = 0

        return self.current_display_min, self.current_display_max

    def _value_to_y(self, value, display_min, display_max):
        """Converts a data value to a Y coordinate on the scale using dynamic range."""
        display_range = display_max - display_min
        if display_range == 0:
            return self.scale_bottom_y
        value = max(display_min, min(display_max, value))
        proportion = (value - display_min) / display_range
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

    def draw(self, current_value, formatted_text=None):
        """
        Draws the vertical bar graph with the current value using stable dynamic range.
        Args:
            current_value (float): The value to display on the graph.
            formatted_text (str): Pre-formatted text to display next to arrow.
        """
        # Calculate stable dynamic range if enabled
        if self.dynamic_range:
            display_min, display_max = self._calculate_stable_dynamic_range(current_value)
            display_range = display_max - display_min
        else:
            display_min, display_max = self.min_val, self.max_val
            display_range = self.value_range

        # Draw the main scale line (thicker)
        base_scale_color = self.config.Palette.DARK_GREY
        pygame.draw.line(self.screen, base_scale_color,
                         (self.scale_line_x, self.scale_top_y),
                         (self.scale_line_x, self.scale_bottom_y), 5)  # Increased thickness

        # Draw many small colored ticks along the main bar (LCARS style)
        # Create small ticks between major intervals (8 ticks between each major mark)
        if self.units == "°C":  # Temperature - 1 degree per tick
            small_interval = 1
            major_interval = 10
        elif self.units == "%":  # Humidity - ~3% per tick (8 ticks in 25% span)
            small_interval = 3
            major_interval = 25
        elif self.units == "mbar":  # Pressure - ~2.5 mbar per tick (8 ticks in 20 mbar span)
            small_interval = 2.5
            major_interval = 20
        else:
            small_interval = 3  # Default for CPU/Memory/Disk - ~3% per tick
            major_interval = 25
        
        # Generate small ticks
        current_tick = display_min
        while current_tick <= display_max:
            # Skip major tick positions
            if abs(current_tick % major_interval) > 0.01:  # Use small tolerance for floating point
                proportion = (current_tick - display_min) / (display_max - display_min) if (display_max - display_min) > 0 else 0
                y = self.scale_bottom_y - int(proportion * self.scale_height)
                tick_color = self._get_zone_color(current_tick)
                
                # Draw small colored ticks on the right side of the main bar
                small_tick_length = 6
                pygame.draw.line(self.screen, tick_color,
                               (self.scale_line_x, y),
                               (self.scale_line_x + small_tick_length, y), 2)
            
            current_tick += small_interval

        # Draw exactly 4 major ticks using the predefined ranges
        if self.units == "°C":  # Temperature
            major_ticks = [10, 20, 30, 40]  # Normal range ticks
        elif self.units == "%":  # Humidity
            major_ticks = [30, 45, 60, 75]  # Normal range ticks
        elif self.units == "mbar":  # Pressure
            major_ticks = [950, 975, 1000, 1025]  # Normal range ticks
        else:
            # Default to evenly spaced ticks
            major_ticks = []
            interval = (display_max - display_min) / 3
            for i in range(4):
                tick_value = display_min + (i * interval)
                major_ticks.append(tick_value)
        
        for tick_value in major_ticks:
            proportion = (tick_value - display_min) / display_range if display_range > 0 else 0
            y = self.scale_bottom_y - int(proportion * self.scale_height)
            tick_color = self._get_zone_color(tick_value)
            
            # Draw thicker tick marks for numbered ticks (on the left side)
            pygame.draw.line(self.screen, tick_color,
                             (self.scale_line_x - self.tick_length // 2, y),
                             (self.scale_line_x, y), 4)
            
            # Draw value label
            label_text = f"{tick_value:.0f}"
            label_surface = self.font_small.render(label_text, True, self.config.Theme.WHITE)
            label_rect = label_surface.get_rect(centery=y, right=self.scale_line_x - self.label_offset_x)
            self.screen.blit(label_surface, label_rect)

            # Draw units at top and bottom of graph, on the left side
            units_surface = self.font_small.render(self.units, True, self.config.Theme.WHITE)
            # Top units
            top_units_rect = units_surface.get_rect(centery=self.scale_top_y, right=self.scale_line_x - self.label_offset_x - 30)
            self.screen.blit(units_surface, top_units_rect)
            # Bottom units
            bottom_units_rect = units_surface.get_rect(centery=self.scale_bottom_y, right=self.scale_line_x - self.label_offset_x - 30)
            self.screen.blit(units_surface, bottom_units_rect)

        # Draw current value pointer (enhanced and more prominent)
        if current_value is not None:
            pointer_y = self._value_to_y(current_value, display_min, display_max)
            pointer_color = self._get_zone_color(current_value)
            
            # Draw special tick mark at exact current temperature position
            pygame.draw.line(self.screen, pointer_color,
                           (self.scale_line_x - self.tick_length // 2, pointer_y),
                           (self.scale_line_x + self.tick_length // 2, pointer_y), 3)
            
            # Draw horizontal line at current value (thicker and extends further)
            pygame.draw.line(self.screen, pointer_color,
                             (self.scale_line_x - self.tick_length, pointer_y),
                             (self.scale_line_x + self.tick_length, pointer_y),
                             6)
            
            # Draw much smaller pointer triangle
            pointer_base_x = self.scale_line_x + self.tick_length + 15  # Reduced from 20 to 15
            triangle_size = max(8, self.pointer_height - 8)  # Much smaller (minimum 8px)
            arrow_width = max(15, self.pointer_width - 15)  # Much narrower arrow
            points = [
                (pointer_base_x, pointer_y),
                (pointer_base_x + arrow_width, pointer_y - triangle_size // 2),
                (pointer_base_x + arrow_width, pointer_y + triangle_size // 2)
            ]
            # Fill arrow with temperature zone color
            pygame.draw.polygon(self.screen, pointer_color, points)
            # Add darker border for definition
            border_color = (
                max(0, pointer_color[0] - 40),
                max(0, pointer_color[1] - 40), 
                max(0, pointer_color[2] - 40)
            ) if len(pointer_color) >= 3 else pointer_color
            pygame.draw.polygon(self.screen, border_color, points, 3)
            
            # Draw moving current temperature number next to the arrow
            temp_text = formatted_text if formatted_text else f"{current_value:.1f}"
            temp_surface = self.font_medium.render(temp_text, True, self.config.Theme.WHITE)
            temp_rect = temp_surface.get_rect(midleft=(pointer_base_x + arrow_width + 10, pointer_y))
            self.screen.blit(temp_surface, temp_rect)

        # Debug: Draw bounding box
        # pygame.draw.rect(self.screen, (0, 0, 255), self.rect, 1)
        # pygame.draw.rect(self.screen, (255, 0, 0), self.scale_rect, 1)


