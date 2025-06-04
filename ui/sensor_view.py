# --- ui/sensor_view.py ---
# Handles rendering of individual sensor views

import pygame
import logging
from ui.components.text_display import render_title, render_value, render_note, render_footer
from ui.components.graph import draw_graph

logger = logging.getLogger(__name__)

def draw_sensor_view(screen, app_state, sensor_values, sensor_history, fonts, config):
    """
    Draw the individual sensor view screen.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        sensor_values (dict): Dictionary of current sensor values, units and notes
        sensor_history (ReadingHistory): The history of sensor readings
        fonts (dict): Dictionary of loaded fonts
        config (module): Configuration module
        
    Returns:
        None
    """
    # Clear screen with background color
    screen.fill(config.COLOR_BACKGROUND)
    
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Get the current sensor being displayed
    current_sensor = app_state.current_sensor
    if not current_sensor:
        logger.error("No sensor selected for sensor view")
        current_sensor = config.SENSOR_MODES[0] if config.SENSOR_MODES else "UNKNOWN"
        
    # Get the values for the current sensor
    value, unit, note = "N/A", "", ""
    if current_sensor in sensor_values:
        value, unit, note = sensor_values[current_sensor]
    
    # Draw the title
    title_rect = render_title(
        screen, 
        current_sensor, 
        fonts, 
        config.COLOR_ACCENT, 
        config.FONT_SIZE_MEDIUM * 1.5,  # Y position
        screen_width,
        app_state.is_frozen,
        config.COLOR_FROZEN
    )
    
    # Draw the value
    value_y_pos = title_rect.bottom + config.FONT_SIZE_MEDIUM
    value_rect = render_value(
        screen,
        value,
        unit,
        fonts,
        config.COLOR_FOREGROUND,
        (screen_width // 2, value_y_pos)
    )
    
    # Draw the graph for graphable sensors (skip CLOCK)
    if current_sensor != "CLOCK":
        # Get history for the current sensor
        history_data = sensor_history.get_history(current_sensor)
        
        # Calculate graph dimensions
        graph_margin = 30  # Pixels from edge
        graph_height = screen_height - value_rect.bottom - graph_margin*2 - config.FONT_SIZE_SMALL*3
        graph_width = screen_width - graph_margin*2
        
        graph_rect = pygame.Rect(
            graph_margin, 
            value_rect.bottom + graph_margin,
            graph_width,
            graph_height
        )
        
        # Get predefined min/max ranges for this sensor type if available
        min_val = None
        max_val = None
        if current_sensor in config.SENSOR_RANGES:
            min_val, max_val = config.SENSOR_RANGES[current_sensor]
        
        # Draw the graph
        draw_graph(
            screen, 
            history_data, 
            graph_rect, 
            config.COLOR_FOREGROUND, 
            min_val, 
            max_val, 
            current_sensor,
            config
        )
        
        # Add time scale indicator at the bottom of the graph
        time_font = fonts['small'] if 'small' in fonts else fonts['medium']
        time_text = f"Time ({config.GRAPH_HISTORY_SIZE} seconds →)"
        time_surf = time_font.render(time_text, True, (150, 150, 150))
        time_rect = time_surf.get_rect(
            center=(screen_width // 2, graph_rect.bottom + config.FONT_SIZE_SMALL)
        )
        screen.blit(time_surf, time_rect)
    
    # Draw the note if present
    if note:
        note_y_pos = screen_height - config.FONT_SIZE_SMALL*3
        render_note(
            screen,
            note,
            fonts,
            config.COLOR_ACCENT,
            (screen_width // 2, note_y_pos)
        )
    
    # Draw navigation help at the bottom
    hint_text = "< PREV | FREEZE | NEXT >"
    if app_state.is_frozen:
        hint_text = "< PREV | UNFREEZE | NEXT >"
        
    render_footer(
        screen,
        "",
        fonts,
        config.COLOR_FOREGROUND,
        screen_width,
        screen_height
    ) 