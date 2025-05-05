# --- ui/sensor_view.py ---
# Handles rendering of individual sensor views OR the auto-cycling dashboard view

import pygame
import logging
from ui.components.text_display import render_title, render_value, render_note, render_footer
from ui.components.vertical_bar_graph import VerticalBarGraph
from ui.components.graph import draw_graph # Re-import the old graph component
# Import app state constants
from models.app_state import STATE_SENSOR_VIEW, STATE_DASHBOARD

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

        # --- Special Handling for ORIENTATION --- 
        if current_sensor == "ORIENTATION":
            # Use the old horizontal line graph for orientation
            history_data = sensor_history.get_history(current_sensor)
            
            # Calculate graph dimensions (similar to old logic, adjust as needed)
            graph_margin = 15 
            graph_height = screen_height - value_rect.bottom - graph_margin*2 - config.FONT_SIZE_SMALL*2 
            graph_width = screen_width - graph_margin*2
            graph_rect = pygame.Rect(
                graph_margin, 
                value_rect.bottom + graph_margin,
                graph_width,
                graph_height
            )

            # Get min/max ranges (likely auto-scale based on config)
            min_val, max_val = config.SENSOR_RANGES.get(current_sensor, (None, None))

            try:
                # Draw the old time-series graph
                draw_graph(
                    screen, 
                    history_data, 
                    graph_rect, 
                    config.COLOR_FOREGROUND, # Use foreground color
                    min_val, 
                    max_val, 
                    current_sensor,
                    config # Pass config for internal colors/settings
                )
                
                # Add time scale indicator (optional, from old logic)
                time_font = fonts.get('small', fonts['medium']) # Handle missing font entry
                time_text = f"Time ({config.GRAPH_HISTORY_SIZE} seconds →)"
                time_surf = time_font.render(time_text, True, (150, 150, 150))
                time_rect = time_surf.get_rect(
                    center=(screen_width // 2, graph_rect.bottom + config.FONT_SIZE_SMALL)
                )
                screen.blit(time_surf, time_rect)
            except Exception as e:
                 logger.error(f"Error drawing original graph for {current_sensor}: {e}")

        # --- Handling for Vertical Bar Graph Sensors ---
        elif current_sensor in config.VERTICAL_GRAPH_CONFIG:
            graph_config = config.VERTICAL_GRAPH_CONFIG[current_sensor]

            # --- Define Rect for the Vertical Graph ---
            # Let's place it below the value, centered horizontally
            graph_width = 60 # Make it relatively narrow
            graph_height = screen_height - value_rect.bottom - config.FONT_SIZE_SMALL*4 # Use available vertical space, leave room for footer/title
            graph_margin_top = 15
            graph_x = (screen_width - graph_width) // 2
            graph_y = value_rect.bottom + graph_margin_top

            graph_rect = pygame.Rect(
                graph_x,
                graph_y,
                graph_width,
                graph_height
            )

            # --- Instantiate and Draw VerticalBarGraph ---
            try:
                vertical_graph = VerticalBarGraph(
                    screen=screen,
                    rect=graph_rect,
                    title=current_sensor, # Use sensor name as title
                    units=graph_config.get("units", unit), # Use config unit, fallback to sensor_values unit
                    min_val=graph_config["min_val"],
                    max_val=graph_config["max_val"],
                    normal_range=graph_config["normal_range"],
                    critical_low=graph_config.get("critical_low"), # Optional
                    critical_high=graph_config.get("critical_high"), # Optional
                    num_ticks=graph_config.get("num_ticks", 11) # Optional
                )

                # --- Get the *current* value (handle parsing for ACCELERATION) ---
                current_value_num = None
                value_to_convert = value # Default to the original value string

                # Special parsing for ACCELERATION
                if current_sensor == "ACCELERATION" and isinstance(value, str):
                    try:
                        # Attempt to extract the Y value (adjust regex if format differs)
                        import re # Quick import for regex
                        match = re.search(r'Y:([\s]*[\-]?\d+\.?\d*)', value)
                        if match:
                            value_to_convert = match.group(1).strip() # Get the number part for Y
                            logger.debug(f"Extracted Y-value for ACCELERATION: {value_to_convert}")
                        else:
                            logger.warning(f"Could not parse Y-value from ACCELERATION string: {value}")
                            value_to_convert = "N/A" # Treat as N/A if parsing fails
                    except Exception as parse_err:
                         logger.error(f"Error parsing ACCELERATION string '{value}': {parse_err}")
                         value_to_convert = "N/A"


                # Now attempt conversion on potentially modified value
                if value_to_convert != "N/A":
                    try:
                        current_value_num = float(value_to_convert)
                    except (ValueError, TypeError):
                        logger.warning(f"Could not convert sensor value '{value_to_convert}' to float for {current_sensor}")
                        current_value_num = None 

                vertical_graph.draw(current_value_num)

            except KeyError as e:
                 logger.error(f"Missing key in VERTICAL_GRAPH_CONFIG for {current_sensor}: {e}")
                 # Optionally draw an error message on screen
            except Exception as e:
                 logger.error(f"Error creating/drawing VerticalBarGraph for {current_sensor}: {e}")
                 # Optionally draw an error message on screen

        # --- Fallback for other sensors without specific graph handling ---
        else:
            # Fallback or message if no vertical graph config defined *and* not Orientation
            logger.warning(f"No graph configuration defined for sensor: {current_sensor}")
            # Optionally draw a message like "Graph N/A"
            fallback_font = fonts.get('medium', pygame.font.Font(None, config.FONT_SIZE_MEDIUM)) # Safer font access
            fallback_text = "Graph N/A"
            fallback_surf = fallback_font.render(fallback_text, True, config.COLOR_ACCENT)
            fallback_rect = fallback_surf.get_rect(center=(screen_width // 2, value_rect.bottom + 80)) 
            screen.blit(fallback_surf, fallback_rect)

    # Draw the note if present
    if note:
        # Adjust note position if needed, as graph area changed
        note_y_pos = screen_height - config.FONT_SIZE_SMALL*3 - 10 # Move slightly up maybe?
        render_note(
            screen,
            note,
            fonts,
            config.COLOR_ACCENT,
            (screen_width // 2, note_y_pos)
        )
    
    # Draw navigation help at the bottom
    key_prev_name = pygame.key.name(config.KEY_PREV).upper()
    key_next_name = pygame.key.name(config.KEY_NEXT).upper()
    key_select_name = pygame.key.name(config.KEY_SELECT).upper()

    hint_text = ""
    action_text = "Freeze" if not app_state.is_frozen else "Unfreeze"

    # Back is now long press A, D does nothing here
    hint_text = f"< Hold {key_prev_name}=Menu | {key_select_name}={action_text} | {key_next_name}= - >"

    render_footer(
        screen,
        hint_text,
        fonts,
        config.COLOR_FOREGROUND,
        screen_width,
        screen_height
    ) 