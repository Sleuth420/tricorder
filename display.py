# --- display.py ---
# Handles drawing the user interface onto the Pygame screen.

import pygame
import config
import logging # Add logging import

# Get a logger for this module
logger = logging.getLogger(__name__)

# Global dictionary to hold loaded fonts
fonts = {}


def init_display():
    """
    Initializes Pygame and the display window. Loads fonts.

    Returns:
        tuple: (screen_surface, clock_object, loaded_fonts_dict) or (None, None, None) on failure.
    """
    global fonts
    try:
        pygame.init()
        if config.FULLSCREEN:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            pygame.mouse.set_visible(False)
            logger.info("Display set to fullscreen mode.")
        else:
            screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            logger.info(f"Display set to windowed mode ({config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}).")
        pygame.display.set_caption("tricorder")

        # Load fonts
        try:
            fonts['large'] = pygame.font.Font(config.FONT_PRIMARY_PATH, config.FONT_SIZE_LARGE)
            fonts['medium'] = pygame.font.Font(config.FONT_PRIMARY_PATH, config.FONT_SIZE_MEDIUM)
            fonts['small'] = pygame.font.Font(config.FONT_PRIMARY_PATH, config.FONT_SIZE_SMALL)
            logger.info(f"Custom font '{config.FONT_PRIMARY_PATH}' loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not load custom font ('{config.FONT_PRIMARY_PATH}'): {e}. Using default font.") # Changed from print
            fonts['large'] = pygame.font.SysFont(None, config.FONT_SIZE_LARGE)
            fonts['medium'] = pygame.font.SysFont(None, config.FONT_SIZE_MEDIUM)
            fonts['small'] = pygame.font.SysFont(None, config.FONT_SIZE_SMALL)

        clock = pygame.time.Clock()
        logger.info("Pygame display and clock initialized.") # Changed from print
        return screen, clock, fonts

    except Exception as e:
        logger.error(f"Error initializing display: {e}", exc_info=True) # Changed from print, added traceback
        pygame.quit()
        return None, None, None


def draw_graph(screen, history, rect, color, min_val=None, max_val=None, mode_name=None):
    """
    Draw a time-series graph of the sensor history on the screen.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        history (list): List of sensor values (or None for missing data)
        rect (pygame.Rect): The rectangle to draw the graph in
        color (tuple): RGB color to use for the graph
        min_val (float, optional): The minimum value for scaling (auto-calculated if None)
        max_val (float, optional): The maximum value for scaling (auto-calculated if None)
        mode_name (str, optional): The name of the sensor mode
    """
    if not history:
        logger.debug(f"No history data to graph for {mode_name if mode_name else 'unknown mode'}")
        return
    
    # Filter out None values to calculate min/max
    valid_values = [v for v in history if v is not None]
    if not valid_values:
        # No valid data points to graph
        logger.debug(f"No valid data points in history for {mode_name if mode_name else 'unknown mode'}")
        return
    
    # Auto-scale if min/max not provided
    if min_val is None:
        min_val = min(valid_values)
        # Add 10% padding at the bottom
        min_val = min_val - (max(valid_values) - min_val) * 0.1
        logger.debug(f"Auto-scaled min value: {min_val:.2f} for {mode_name if mode_name else 'unknown mode'}")
    
    if max_val is None:
        max_val = max(valid_values)
        # Add 10% padding at the top
        max_val = max_val + (max_val - min(valid_values)) * 0.1
        logger.debug(f"Auto-scaled max value: {max_val:.2f} for {mode_name if mode_name else 'unknown mode'}")
    
    # Ensure we have a range (avoid division by zero)
    if min_val == max_val:
        min_val -= 0.5
        max_val += 0.5
        logger.debug(f"Adjusted min/max values to avoid division by zero: {min_val:.2f}/{max_val:.2f}")
    
    logger.debug(f"Drawing graph for {mode_name if mode_name else 'unknown mode'} with {len(valid_values)} data points")
    
    # Draw border
    pygame.draw.rect(screen, config.COLOR_GRAPH_BORDER, rect, 1)
    
    # Draw grid lines (horizontal)
    num_grid_lines = 4  # Number of horizontal grid lines
    for i in range(1, num_grid_lines):
        y_pos = rect.top + int((i / num_grid_lines) * rect.height)
        pygame.draw.line(screen, config.COLOR_GRAPH_GRID, 
                         (rect.left, y_pos), (rect.right, y_pos), 1)
    
    # Draw grid lines (vertical, one line every 15 seconds)
    time_divisions = 4  # Divide into 4 sections (15 seconds each for 60 second graph)
    for i in range(1, time_divisions):
        x_pos = rect.left + int((i / time_divisions) * rect.width)
        pygame.draw.line(screen, config.COLOR_GRAPH_GRID,
                         (x_pos, rect.top), (x_pos, rect.bottom), 1)

    # Draw x and y axes
    pygame.draw.line(screen, (100, 100, 100), (rect.left, rect.bottom - 1), 
                     (rect.right, rect.bottom - 1), 1)  # X-axis
    pygame.draw.line(screen, (100, 100, 100), (rect.left, rect.top), 
                     (rect.left, rect.bottom), 1)  # Y-axis
    
    # Calculate points for the line
    points = []
    width = rect.width - 2  # Adjust for border
    height = rect.height - 2  # Adjust for border
    
    # Calculate points for each data value
    for i, value in enumerate(history):
        if value is None:
            continue
            
        x = rect.left + 1 + (i * width) // (len(history) - 1)
        
        # Scale value to fit in the graph height 
        # Inverted because pygame y increases downward
        scaled_value = 1.0 - (value - min_val) / (max_val - min_val)
        y = rect.top + 1 + int(scaled_value * height)
        
        points.append((x, y))
    
    # Draw line graph if we have enough points
    if len(points) > 1:
        pygame.draw.lines(screen, color, False, points, config.GRAPH_LINE_WIDTH)
    
    # Draw actual points as small circles
    for point in points:
        pygame.draw.circle(screen, color, point, config.GRAPH_POINT_SIZE)
    
    # Draw min and max values
    if fonts.get('small'):
        min_text = fonts['small'].render(f"{min_val:.1f}", True, (180, 180, 180))
        max_text = fonts['small'].render(f"{max_val:.1f}", True, (180, 180, 180))
        
        screen.blit(min_text, (rect.left + 5, rect.bottom - min_text.get_height() - 2))
        screen.blit(max_text, (rect.left + 5, rect.top + 2))


def draw_ui(screen, current_mode_name, sensor_value, unit, note, is_frozen, auto_cycle=True, history=None):
    """
    Draws the entire UI onto the provided screen surface.

    Args:
        screen (pygame.Surface): The display surface to draw on.
        current_mode_name (str): The name of the currently active sensor mode.
        sensor_value (str): The formatted string of the sensor reading.
        unit (str): The unit for the sensor reading.
        note (str): Any additional note for the reading (always "" for now).
        is_frozen (bool): True if the display is currently frozen.
        auto_cycle (bool): True if auto-cycling is enabled.
        history (list): List of historical sensor values for graphing.
    """
    if not screen or not fonts:
        logger.error("Screen or fonts not initialized for drawing.") # Changed from print
        return

    # 1. Clear screen / Fill background
    screen.fill(config.COLOR_BACKGROUND)

    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # 2. Draw Mode Name (Top Center) - Add Frozen Indicator if needed
    mode_display_text = current_mode_name
    mode_color = config.COLOR_ACCENT
    if is_frozen:
        mode_display_text += " [FROZEN]"
        mode_color = config.COLOR_FROZEN  # Use a different color for frozen mode title
    elif auto_cycle:
        mode_display_text += " [AUTO]"  # Add auto-cycle indicator

    try:
        mode_text_surface = fonts['medium'].render(mode_display_text, True, mode_color)
        mode_text_rect = mode_text_surface.get_rect(center=(screen_width // 2, config.FONT_SIZE_MEDIUM * 1.5))
        screen.blit(mode_text_surface, mode_text_rect)
    except Exception as e:
        logger.error(f"Error rendering mode text ('{mode_display_text}'): {e}", exc_info=True) # Changed from print

    # 3. Draw current value still (but smaller, above the graph)
    try:
        value_text = f"{sensor_value} {unit}"
        value_color = config.COLOR_FOREGROUND
        value_text_surface = fonts['medium'].render(value_text, True, value_color)  # Use medium instead of large
        # Position above the graph
        value_y_pos = mode_text_rect.bottom + config.FONT_SIZE_MEDIUM
        value_text_rect = value_text_surface.get_rect(center=(screen_width // 2, value_y_pos))
        screen.blit(value_text_surface, value_text_rect)
    except Exception as e:
        logger.error(f"Error rendering sensor value ('{value_text}'): {e}", exc_info=True)
        
    # 4. Draw History Graph
    if history:
        try:
            # Calculate graph dimensions
            graph_margin = 30  # Pixels from edge
            graph_height = screen_height - value_text_rect.bottom - graph_margin*2 - config.FONT_SIZE_SMALL*3
            graph_width = screen_width - graph_margin*2
            
            graph_rect = pygame.Rect(
                graph_margin, 
                value_text_rect.bottom + graph_margin,
                graph_width,
                graph_height
            )
            
            # Get predefined min/max ranges for this sensor type if available
            min_val = None
            max_val = None
            if current_mode_name in config.SENSOR_RANGES:
                min_val, max_val = config.SENSOR_RANGES[current_mode_name]
            
            # Draw the graph with configured scaling
            draw_graph(screen, history, graph_rect, config.COLOR_FOREGROUND, min_val, max_val, current_mode_name)
            
            # Add time scale indicator at the bottom of the graph
            time_text = f"Time ({config.GRAPH_HISTORY_SIZE} seconds →)"
            time_text_surface = fonts['small'].render(time_text, True, (150, 150, 150))
            time_text_rect = time_text_surface.get_rect(
                center=(screen_width // 2, graph_rect.bottom + config.FONT_SIZE_SMALL)
            )
            screen.blit(time_text_surface, time_text_rect)
            
        except Exception as e:
            logger.error(f"Error rendering graph: {e}", exc_info=True)

    # 5. Draw Note (Below Value, if present)
    if note:
        try:
            note_text_surface = fonts['small'].render(note, True, config.COLOR_ACCENT)
            # Position below the graph
            note_y_pos = screen_height - config.FONT_SIZE_SMALL*3
            note_text_rect = note_text_surface.get_rect(center=(screen_width // 2, note_y_pos))
            screen.blit(note_text_surface, note_text_rect)
        except Exception as e:
            logger.error(f"Error rendering note text ('{note}'): {e}", exc_info=True)

    # 6. Draw Button Hints (Bottom Center)
    try:
        # Update hint text slightly to reflect Enter = Freeze/Unfreeze
        hint_text = "< PREV | FREEZE | NEXT >"
        hint_color = config.COLOR_FOREGROUND
        if is_frozen:
            hint_text = "< PREV |UNFREEZE| NEXT >"  # Indicate next action for SELECT
            # hint_color = config.COLOR_FROZEN # Optional: Change hint color when frozen
        elif auto_cycle:
            hint_text = "< PREV | FREEZE | NEXT > (AUTO)"  # Indicate auto-cycling is active

        hint_text_surface = fonts['small'].render(hint_text, True, hint_color)
        hint_text_rect = hint_text_surface.get_rect(center=(screen_width // 2, screen_height - config.FONT_SIZE_SMALL * 1.5))
        screen.blit(hint_text_surface, hint_text_rect)
    except Exception as e:
        logger.error(f"Error rendering hint text ('{hint_text}'): {e}", exc_info=True) # Changed from print

    # Note: pygame.display.flip() is called in the main loop after this function returns
