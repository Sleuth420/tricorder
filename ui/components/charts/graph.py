# --- ui/components/graph.py ---
# Reusable graphing component

import pygame
import logging

# No direct config import needed here if config_module is always passed
# import config # This would be the global config

logger = logging.getLogger(__name__)

def draw_graph(screen, history, rect, color, min_val=None, max_val=None, sensor_name="Data", config_module=None, ui_scaler=None):
    """
    Draws a time-series line graph for the given history.

    Args:
        screen (pygame.Surface): The surface to draw on.
        history (list): List of numerical data points (or None for no data).
        rect (pygame.Rect): The rectangle where the graph should be drawn.
        color (tuple): The color of the graph line and points.
        min_val (float, optional): Minimum value for the Y-axis. Auto-scales if None.
        max_val (float, optional): Maximum value for the Y-axis. Auto-scales if None.
        sensor_name (str): Name of the sensor/data, used for logging.
        config_module (module): The main configuration module. This is now MANDATORY.
        ui_scaler (UIScaler, optional): The UI scaler for scaling values.
    """
    if not config_module:
        logger.error(f"Graph for '{sensor_name}' cannot be drawn: config_module is mandatory but was not provided.")
        # Optionally, draw an error message on the graph rect
        font = pygame.font.Font(None, 20)
        err_surf = font.render("Graph Config Error", True, (255,0,0))
        screen.blit(err_surf, err_surf.get_rect(center=rect.center))
        return

    # Use theme colors from the passed config_module
    color_grid = config_module.Theme.GRAPH_GRID
    color_border = config_module.Theme.GRAPH_BORDER
    color_axis = config_module.Theme.GRAPH_AXIS # New theme color for axes
    
    # Use UIScaler for responsive dimensions if available
    if ui_scaler:
        point_size = ui_scaler.scale(config_module.GRAPH_POINT_SIZE)
        line_width = max(1, ui_scaler.scale(config_module.GRAPH_LINE_WIDTH))
        
        # Debug logging for graph layout
        if ui_scaler.debug_mode:
            logger.info(f"🎨 Graph({sensor_name}): rect={rect.width}x{rect.height}, point_size={point_size}px, line_width={line_width}px")
    else:
        # Fallback to original values
        point_size = config_module.GRAPH_POINT_SIZE
        line_width = config_module.GRAPH_LINE_WIDTH

    # Filter out None values for min/max calculation and actual plotting
    valid_history = [v for v in history if v is not None]

    if not valid_history:
        # logger.debug(f"No valid data to plot for {sensor_name}.")
        # Draw empty graph area (border and grid)
        pygame.draw.rect(screen, config_module.Theme.BACKGROUND, rect) # Clear area
        pygame.draw.rect(screen, color_border, rect, 1)
        # Draw grid lines even if no data
        num_grid_lines = 4 # Horizontal grid lines
        spacing_y = rect.height / (num_grid_lines + 1)
        for i in range(1, num_grid_lines + 1):
            y = rect.top + i * spacing_y
            pygame.draw.line(screen, color_grid, (rect.left, y), (rect.right, y), 1)
        # No data points to draw, so return early
        return

    # Auto-scaling if min_val or max_val is not provided
    auto_min_val = min(valid_history) if min_val is None else min_val
    auto_max_val = max(valid_history) if max_val is None else max_val

    # Handle case where all values are the same or min/max are equal
    if auto_min_val == auto_max_val:
        auto_min_val -= 0.5  # Add some padding
        auto_max_val += 0.5

    # Apply padding if auto-scaling was used for either min or max
    if min_val is None or max_val is None:
        padding = (auto_max_val - auto_min_val) * 0.1 # 10% padding
        padding = max(padding, 0.1) # Ensure at least a small padding if range is tiny
        if min_val is None:
            auto_min_val -= padding
        if max_val is None:
            auto_max_val += padding
            
    # Final min/max for y-axis
    y_min = auto_min_val
    y_max = auto_max_val
    y_range = y_max - y_min
    if y_range == 0: y_range = 1 # Avoid division by zero

    # X-axis parameters
    num_points = len(history) # Use full history length for x-axis scaling
    x_spacing = rect.width / max(1, num_points -1) if num_points > 1 else rect.width

    # --- Drawing --- 
    pygame.draw.rect(screen, config_module.Theme.BACKGROUND, rect) # Clear graph area with background
    pygame.draw.rect(screen, color_border, rect, 1) # Draw border

    # Draw grid lines (horizontal and vertical)
    num_grid_lines_h = 4
    spacing_y = rect.height / (num_grid_lines_h + 1)
    for i in range(1, num_grid_lines_h + 1):
        y = rect.top + i * spacing_y
        pygame.draw.line(screen, color_grid, (rect.left, y), (rect.right, y), 1)
    
    # Vertical grid lines (time divisions)
    time_divisions = 4 # Number of vertical divisions
    if num_points > 1 and time_divisions > 0:
        spacing_x_grid = rect.width / time_divisions
        for i in range(1, time_divisions):
            x = rect.left + i * spacing_x_grid
            pygame.draw.line(screen, color_grid, (x, rect.top), (x, rect.bottom), 1)

    # Draw Y-axis (simple line on the left)
    pygame.draw.line(screen, color_axis, (rect.left, rect.top), (rect.left, rect.bottom), 1)
    # Draw X-axis (simple line on the bottom)
    pygame.draw.line(screen, color_axis, (rect.left, rect.bottom), (rect.right, rect.bottom), 1)

    # Plot points and lines
    points_to_draw = []
    for i, value in enumerate(history):
        if value is None: continue # Skip None values in history for plotting
        
        x = rect.left + i * x_spacing
        # Clamp value to y_min/y_max before scaling to prevent drawing outside bounds
        clamped_value = max(y_min, min(y_max, value))
        y = rect.bottom - ((clamped_value - y_min) / y_range * rect.height)
        
        # Ensure points are within the drawable rect to avoid overdraw
        x = max(rect.left, min(rect.right, x))
        y = max(rect.top, min(rect.bottom, y))
        points_to_draw.append((x, y))

    if len(points_to_draw) >= 2:
        pygame.draw.lines(screen, color, False, points_to_draw, line_width)
    
    for point_x, point_y in points_to_draw:
        pygame.draw.circle(screen, color, (int(point_x), int(point_y)), point_size)

    # logger.debug(f"Drew graph for {sensor_name} with {len(valid_history)} points. Range: {y_min:.2f}-{y_max:.2f}")

    return y_min, y_max  # Return the min/max values used for the graph 