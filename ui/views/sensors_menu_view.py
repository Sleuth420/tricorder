# --- ui/views/sensors_menu_view.py ---
# Handles rendering of the sensors submenu using shared menu base component

import pygame
import logging
from ui.components.menu_base import draw_menu_base_layout
from ui.components.text_display import render_footer

logger = logging.getLogger(__name__)

def draw_sensors_menu_view(screen, app_state, sensor_values, sensor_history, fonts, config_module):
    """
    Draw the sensors submenu view with enhanced main content area.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        sensor_values (dict): Dictionary of current sensor values
        sensor_history (ReadingHistory): Sensor reading history
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        
    Returns:
        None
    """
    # Use shared menu base layout
    layout = draw_menu_base_layout(screen, app_state, fonts, config_module)
    main_content_rect = layout['main_content_rect']
    screen_width = layout['screen_width']
    screen_height = layout['screen_height']
    
    # Enhanced main content area for sensors menu
    _draw_sensors_main_content(screen, main_content_rect, app_state, sensor_values, fonts, config_module)
    
    # Draw footer
    _draw_sensors_footer(screen, main_content_rect, fonts, config_module, screen_height)

def _draw_sensors_main_content(screen, main_content_rect, app_state, sensor_values, fonts, config_module):
    """
    Draw enhanced main content area for sensors menu.
    """
    # Title
    title_font = fonts['large']
    title_text = "Environmental Sensors"
    title_surface = title_font.render(title_text, True, config_module.Theme.ACCENT)
    title_rect = title_surface.get_rect(centerx=main_content_rect.centerx, y=main_content_rect.top + 20)
    screen.blit(title_surface, title_rect)
    
    # Get currently selected sensor info
    menu_items = app_state.get_current_menu_items()
    selected_index = app_state.get_current_menu_index()

    if menu_items and 0 <= selected_index < len(menu_items):
        selected_item = menu_items[selected_index]
        # Extract sensor_key from the data dictionary
        sensor_data_dict = selected_item.data  # This is {"sensor_type": "TEMPERATURE"}
        sensor_key = None
        if sensor_data_dict and isinstance(sensor_data_dict, dict):
            sensor_key = sensor_data_dict.get("sensor_type")
        
        # Display preview of selected sensor
        if sensor_key and sensor_key in sensor_values:
            _draw_sensor_preview(screen, main_content_rect, title_rect, sensor_key, sensor_values[sensor_key], fonts, config_module)
        else:
            # Fallback: general instructions
            _draw_general_instructions(screen, main_content_rect, title_rect, fonts, config_module)
    else:
        # Fallback: general instructions
        _draw_general_instructions(screen, main_content_rect, title_rect, fonts, config_module)
    
    # Show sensor status summary at bottom of content area
    _draw_sensor_status_summary(screen, main_content_rect, sensor_values, fonts, config_module)

def _draw_sensor_preview(screen, main_content_rect, title_rect, sensor_key, sensor_data, fonts, config_module):
    """
    Draw a preview of the currently selected sensor.
    """
    # Get display properties for the sensor
    display_props = config_module.SENSOR_DISPLAY_PROPERTIES.get(sensor_key, {})
    display_name = display_props.get("display_name", sensor_key)
    
    # Sensor name
    name_font = fonts['medium']
    name_text = f"Selected: {display_name}"
    name_surface = name_font.render(name_text, True, config_module.Theme.FOREGROUND)
    name_rect = name_surface.get_rect(centerx=main_content_rect.centerx, y=title_rect.bottom + 30)
    screen.blit(name_surface, name_rect)
    
    # Current value (large display)
    value_font = fonts['large']
    text_val = sensor_data.get("text", "N/A")
    unit = sensor_data.get("unit", "")
    value_text = f"{text_val} {unit}".strip()
    value_surface = value_font.render(value_text, True, config_module.Theme.ACCENT)
    value_rect = value_surface.get_rect(centerx=main_content_rect.centerx, y=name_rect.bottom + 20)
    screen.blit(value_surface, value_rect)
    
    # Note/additional info if available
    note = sensor_data.get("note", "")
    if note:
        note_font = fonts['small']
        note_surface = note_font.render(note, True, config_module.Theme.FOREGROUND)
        note_rect = note_surface.get_rect(centerx=main_content_rect.centerx, y=value_rect.bottom + 10)
        screen.blit(note_surface, note_rect)
    
    # Graph type indicator
    graph_type = display_props.get("graph_type", "NONE")
    if graph_type != "NONE":
        graph_font = fonts['small']
        graph_text = f"Graph: {graph_type.replace('_', ' ').title()}"
        graph_surface = graph_font.render(graph_text, True, config_module.Palette.LIGHT_GREY)
        graph_rect = graph_surface.get_rect(centerx=main_content_rect.centerx, 
                                          y=(note_rect.bottom + 15) if note else (value_rect.bottom + 25))
        screen.blit(graph_surface, graph_rect)

def _draw_general_instructions(screen, main_content_rect, title_rect, fonts, config_module):
    """
    Draw general instructions when no specific sensor is selected.
    """
    instruction_font = fonts['medium']
    instruction_text = "Select a sensor to view details"
    instruction_surface = instruction_font.render(instruction_text, True, config_module.Theme.FOREGROUND)
    instruction_rect = instruction_surface.get_rect(centerx=main_content_rect.centerx, y=title_rect.bottom + 40)
    screen.blit(instruction_surface, instruction_rect)
    
    # Navigation hint
    hint_font = fonts['small']
    hint_text = "Use UP/DOWN or A/D to browse sensors"
    hint_surface = hint_font.render(hint_text, True, config_module.Theme.FOREGROUND)
    hint_rect = hint_surface.get_rect(centerx=main_content_rect.centerx, y=instruction_rect.bottom + 20)
    screen.blit(hint_surface, hint_rect)

def _draw_sensor_status_summary(screen, main_content_rect, sensor_values, fonts, config_module):
    """
    Draw a summary of sensor statuses at the bottom of the main content area.
    """
    summary_font = fonts['small']
    
    # Count working vs error sensors
    total_sensors = len(config_module.SENSOR_MODES)
    working_sensors = 0
    error_sensors = 0
    
    for sensor_key in config_module.SENSOR_MODES:
        if sensor_key in sensor_values:
            sensor_data = sensor_values[sensor_key]
            text_val = sensor_data.get("text", "N/A")
            if text_val != "N/A" and text_val != "Error":
                working_sensors += 1
            else:
                error_sensors += 1
        else:
            error_sensors += 1
    
    # Status summary text
    status_text = f"Status: {working_sensors}/{total_sensors} sensors online"
    status_color = config_module.Theme.CONTENT_WIFI_ONLINE_STATUS if error_sensors == 0 else config_module.Theme.WARNING
    status_surface = summary_font.render(status_text, True, status_color)
    
    # Position at bottom of main content area
    status_rect = status_surface.get_rect(centerx=main_content_rect.centerx, 
                                        y=main_content_rect.bottom - 60)
    screen.blit(status_surface, status_rect)
    
    # Error details if any
    if error_sensors > 0:
        error_text = f"({error_sensors} sensors offline)"
        error_surface = summary_font.render(error_text, True, config_module.Theme.ALERT)
        error_rect = error_surface.get_rect(centerx=main_content_rect.centerx, 
                                          y=status_rect.bottom + 5)
        screen.blit(error_surface, error_rect)

def _draw_sensors_footer(screen, main_content_rect, fonts, config_module, screen_height):
    """
    Draw footer for sensors menu.
    """
    # Navigation hints
    key_prev_name = pygame.key.name(config_module.KEY_PREV).upper()
    key_select_name = pygame.key.name(config_module.KEY_SELECT).upper()
    key_next_name = pygame.key.name(config_module.KEY_NEXT).upper()
    
    hint_text = f"{key_prev_name}/{key_next_name}: Navigate | {key_select_name}: Select | Long {key_prev_name}: Back"

    # Create footer rendering centered on main content area
    footer_font = fonts.get('small', fonts.get('medium'))
    footer_surface = footer_font.render(hint_text, True, config_module.Theme.FOREGROUND)
    footer_y = screen_height - footer_surface.get_height() - 5
    footer_x = main_content_rect.centerx - footer_surface.get_width() // 2
    screen.blit(footer_surface, (footer_x, footer_y))