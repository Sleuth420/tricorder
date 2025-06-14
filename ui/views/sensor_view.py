# --- ui/sensor_view.py ---
# Handles rendering of individual sensor views OR the auto-cycling dashboard view

import pygame
import logging
from ui.components.text_display import render_title, render_value, render_note, render_footer
from ui.components.vertical_bar_graph import VerticalBarGraph
from ui.components.graph import draw_graph # Re-import the old graph component
# Import app state constants
from models.app_state import STATE_SENSOR_VIEW, STATE_DASHBOARD # These are fine as they are AppState internal states
# Import config for sensor mode constants and display properties
import config as app_config # Use an alias
# import re # No longer needed

logger = logging.getLogger(__name__)

def draw_sensor_view(screen, app_state, sensor_values, sensor_history, fonts, config_module):
    """
    Draw the individual sensor view screen.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        sensor_values (dict): Dictionary of current sensor data (new structure with dict per sensor)
        sensor_history (ReadingHistory): The history of sensor readings
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
    """
    screen.fill(config_module.Theme.BACKGROUND)
    
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    current_sensor_key = app_state.current_sensor
    if not current_sensor_key:
        logger.error("No sensor selected for sensor view, defaulting.")
        current_sensor_key = config_module.SENSOR_MODES[0] if config_module.SENSOR_MODES else "UNKNOWN_SENSOR_KEY"
        
    # Get display properties for the current sensor
    display_props = config_module.SENSOR_DISPLAY_PROPERTIES.get(current_sensor_key, {})
    display_name = display_props.get("display_name", current_sensor_key)

                    # Get the values for the current sensor using the new structure
    current_sensor_data = sensor_values.get(current_sensor_key, {})
    text_val = current_sensor_data.get("text", "N/A")
    unit = current_sensor_data.get("unit", "")
    note = current_sensor_data.get("note", "")
    numeric_val = current_sensor_data.get("value")
    
    # Prepare text for vertical bar graph arrow display
    arrow_text = text_val  # Default to main text (inertia no longer uses vertical bar graph)
    
    # Draw sensor name in top left
    title_font = fonts['medium']
    title_surface = title_font.render(display_name, True, config_module.Theme.ACCENT)
    title_rect = title_surface.get_rect(topleft=(10, 10))
    screen.blit(title_surface, title_rect)
    
    # Draw current value to the right of the title
    value_font = fonts['large']
    value_text = f"{text_val} {unit}".strip()
    value_surface = value_font.render(value_text, True, config_module.Theme.FOREGROUND)
    value_rect = value_surface.get_rect(midleft=(title_rect.right + 20, title_rect.centery))
    screen.blit(value_surface, value_rect)
    
    # Draw frozen indicator if needed
    if app_state.is_frozen:
        frozen_font = fonts['small']
        frozen_surface = frozen_font.render("[FROZEN]", True, config_module.Theme.FROZEN_INDICATOR)
        frozen_rect = frozen_surface.get_rect(midleft=(value_rect.right + 20, value_rect.centery))
        screen.blit(frozen_surface, frozen_rect)
    
    graph_type = display_props.get("graph_type", "NONE")

    if graph_type == "LINE":
        history_data = sensor_history.get_history(current_sensor_key)
        graph_margin = 15 
        graph_height = screen_height - title_rect.bottom - graph_margin*2 - config_module.FONT_SIZE_SMALL*2 
        graph_width = screen_width - graph_margin*2
        graph_rect = pygame.Rect(
            graph_margin, 
            title_rect.bottom + graph_margin,
            graph_width,
            graph_height
        )
        range_override = display_props.get("range_override", (None, None))
        min_val_cfg, max_val_cfg = range_override if range_override is not None else (None, None)

        try:
            draw_graph(
                screen, history_data, graph_rect, 
                config_module.Theme.FOREGROUND, 
                min_val_cfg, max_val_cfg, 
                current_sensor_key,
                config_module
            )
            time_font = fonts.get('small', fonts['medium'])
            time_text = f"Time ({config_module.GRAPH_HISTORY_SIZE} seconds →)"
            time_surf = time_font.render(time_text, True, config_module.Theme.GRAPH_GRID)
            time_rect = time_surf.get_rect(center=(screen_width // 2, graph_rect.bottom + config_module.FONT_SIZE_SMALL))
            screen.blit(time_surf, time_rect)
        except Exception as e:
             logger.error(f"Error drawing line graph for {current_sensor_key}: {e}", exc_info=True)

    elif graph_type == "VERTICAL_BAR":
        vbar_config = display_props.get("vertical_graph_config")
        if vbar_config:
            # Calculate graph dimensions to maximize available space - make it wider
            graph_width = 120  # Increased from 80 for better visibility and spacing
            graph_height = screen_height - title_rect.bottom - config_module.FONT_SIZE_SMALL*3  # More vertical space
            graph_margin_top = 20
            graph_x = (screen_width - graph_width) // 2
            graph_y = title_rect.bottom + graph_margin_top
            graph_rect = pygame.Rect(graph_x, graph_y, graph_width, graph_height)
            
            try:
                vertical_graph = VerticalBarGraph(
                    screen=screen, rect=graph_rect,
                    title="",  # Remove title since we show it at top
                    units=display_props.get("units", unit),
                    min_val=vbar_config["min_val"],
                    max_val=vbar_config["max_val"],
                    normal_range=vbar_config["normal_range"],
                    fonts=fonts,
                    config_module=config_module,
                    critical_low=vbar_config.get("critical_low"),
                    critical_high=vbar_config.get("critical_high"),
                    num_ticks=vbar_config.get("num_ticks", 11),
                    dynamic_range=vbar_config.get("dynamic_range", False),
                    zoom_factor=vbar_config.get("zoom_factor", 0.3),
                    min_zoom_range=vbar_config.get("min_zoom_range"),
                    stability_threshold=vbar_config.get("stability_threshold", 2.0)
                )
                vertical_graph.draw(numeric_val, arrow_text)
            except KeyError as e:
                 logger.error(f"Missing key in VERTICAL_GRAPH_CONFIG for {current_sensor_key}: {e}", exc_info=True)
            except Exception as e:
                 logger.error(f"Error creating/drawing VerticalBarGraph for {current_sensor_key}: {e}", exc_info=True)
        else:
            logger.warning(f"Graph type for {current_sensor_key} is VERTICAL_BAR but no vertical_graph_config found.")
            fallback_font = fonts.get('medium', pygame.font.Font(None, config_module.FONT_SIZE_MEDIUM))
            fallback_text = "Graph N/A"
            fallback_surf = fallback_font.render(fallback_text, True, config_module.Theme.ACCENT)
            fallback_rect = fallback_surf.get_rect(center=(screen_width // 2, title_rect.bottom + 80))
            screen.blit(fallback_surf, fallback_rect)

    elif graph_type == "NONE" or current_sensor_key == config_module.SENSOR_CLOCK:
        logger.debug(f"No graph to display for sensor: {current_sensor_key}")
        fallback_font = fonts.get('medium', pygame.font.Font(None, config_module.FONT_SIZE_MEDIUM))
        fallback_text = "Graph N/A" if graph_type == "NONE" else ""
        if fallback_text:
            fallback_surf = fallback_font.render(fallback_text, True, config_module.Theme.ACCENT)
            fallback_rect = fallback_surf.get_rect(center=(screen_width // 2, title_rect.bottom + 80))
            screen.blit(fallback_surf, fallback_rect)
    else:
        logger.warning(f"Unknown graph_type '{graph_type}' or no graph configured for sensor: {current_sensor_key}")
        fallback_font = fonts.get('medium', pygame.font.Font(None, config_module.FONT_SIZE_MEDIUM))
        fallback_text = "Graph N/A"
        fallback_surf = fallback_font.render(fallback_text, True, config_module.Theme.ACCENT)
        fallback_rect = fallback_surf.get_rect(center=(screen_width // 2, title_rect.bottom + 80))
        screen.blit(fallback_surf, fallback_rect)

    if note:
        # Position note in top area to avoid overlapping with vertical bar graph scale
        note_x_pos = screen_width - 10  # Right side of screen  
        note_y_pos = title_rect.bottom + 5  # Just below the title area
        # Use render_text with right alignment to prevent text from going off screen
        from ui.components.text_display import render_text
        render_text(
            screen, note, 
            fonts['small'] if 'small' in fonts else fonts['medium'],
            config_module.Theme.ACCENT,
            (note_x_pos, note_y_pos),
            align="right"
        )
    
    key_prev_name = pygame.key.name(config_module.KEY_PREV).upper()
    key_next_name = pygame.key.name(config_module.KEY_NEXT).upper()
    key_select_name = pygame.key.name(config_module.KEY_SELECT).upper()
    action_text = "Freeze" if not app_state.is_frozen else "Unfreeze"
    hint_text = ""

    render_footer(
        screen, hint_text, fonts,
        config_module.Theme.FOREGROUND,
        screen_width, screen_height
    ) 