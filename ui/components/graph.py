# --- ui/components/graph.py ---
# Reusable graphing component

import pygame
import logging

logger = logging.getLogger(__name__)

def draw_graph(screen, history, rect, color, min_val=None, max_val=None, mode_name=None, config=None):
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
        config (module, optional): Configuration module with color definitions
    """
    if not history:
        logger.debug(f"No history data to graph for {mode_name if mode_name else 'unknown mode'}")
        return
    
    # Use provided config or default colors
    if config:
        color_grid = config.COLOR_GRAPH_GRID
        color_border = config.COLOR_GRAPH_BORDER
        point_size = config.GRAPH_POINT_SIZE
        line_width = config.GRAPH_LINE_WIDTH
    else:
        color_grid = (30, 30, 30)    # Dark gray for grid lines
        color_border = (50, 50, 50)  # Medium gray for border
        point_size = 3
        line_width = 2
    
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
    pygame.draw.rect(screen, color_border, rect, 1)
    
    # Draw grid lines (horizontal)
    num_grid_lines = 4  # Number of horizontal grid lines
    for i in range(1, num_grid_lines):
        y_pos = rect.top + int((i / num_grid_lines) * rect.height)
        pygame.draw.line(screen, color_grid, 
                         (rect.left, y_pos), (rect.right, y_pos), 1)
    
    # Draw grid lines (vertical, one line every 15 seconds)
    time_divisions = 4  # Divide into 4 sections (15 seconds each for 60 second graph)
    for i in range(1, time_divisions):
        x_pos = rect.left + int((i / time_divisions) * rect.width)
        pygame.draw.line(screen, color_grid,
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
        pygame.draw.lines(screen, color, False, points, line_width)
    
    # Draw actual points as small circles
    for point in points:
        pygame.draw.circle(screen, color, point, point_size)
    
    return min_val, max_val  # Return the min/max values used for the graph 