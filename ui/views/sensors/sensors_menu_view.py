# --- ui/views/sensors_menu_view.py ---
# Enhanced sensors submenu with tricorder-style animations and theming

import pygame
import logging
import time
import math
from ui.components.menus.menu_base import draw_menu_base_layout
from ui.components.text.text_display import render_footer

logger = logging.getLogger(__name__)

def draw_sensors_menu_view(screen, app_state, sensor_values, sensor_history, fonts, config_module, ui_scaler=None):
    """
    Draw the enhanced sensors submenu view with tricorder-style animations.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        sensor_values (dict): Dictionary of current sensor values
        sensor_history (ReadingHistory): Sensor reading history
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        ui_scaler (UIScaler): UI scaler for scaling the UI
        
    Returns:
        None
    """
    # Use shared menu base layout
    layout = draw_menu_base_layout(screen, app_state, fonts, config_module, ui_scaler)
    main_content_rect = layout['main_content_rect']
    screen_width = layout['screen_width']
    screen_height = layout['screen_height']
    
    # Debug logging for sensors menu view layout
    if ui_scaler and ui_scaler.debug_mode:
        logger.info(f"🎨 SensorsMenuView: screen={screen_width}x{screen_height}, main_content={main_content_rect.width}x{main_content_rect.height}")
    
    # Enhanced main content area for sensors menu with animations
    current_time = time.time()
    _draw_enhanced_sensors_content(screen, main_content_rect, app_state, sensor_values, fonts, config_module, ui_scaler, current_time)

def _draw_enhanced_sensors_content(screen, main_content_rect, app_state, sensor_values, fonts, config_module, ui_scaler, current_time):
    """
    Draw enhanced main content area with tricorder-style animations and theming.
    """
    # Use UIScaler for responsive spacing if available
    if ui_scaler:
        title_spacing = ui_scaler.margin("large")
        content_spacing = ui_scaler.margin("large")
        section_spacing = ui_scaler.margin("medium")
    else:
        # Fallback to proportional values
        title_spacing = max(25, main_content_rect.height // 15)
        content_spacing = max(25, main_content_rect.height // 15)
        section_spacing = max(20, main_content_rect.height // 18)
    
    # Animated title with glow effect
    title_font = fonts['large']
    title_text = "Environmental Sensors"
    _draw_glowing_title(screen, title_text, title_font, config_module.Theme.ACCENT, 
                       (main_content_rect.centerx, main_content_rect.top + title_spacing), current_time)
    
    # Calculate content areas
    title_height = title_font.get_height()
    content_start_y = main_content_rect.top + title_spacing + title_height + content_spacing
    
    # Get currently selected sensor info
    menu_items = app_state.get_current_menu_items()
    selected_index = app_state.get_current_menu_index()

    if menu_items and 0 <= selected_index < len(menu_items):
        selected_item = menu_items[selected_index]
        sensor_data_dict = selected_item.data
        sensor_key = None
        if sensor_data_dict and isinstance(sensor_data_dict, dict):
            sensor_key = sensor_data_dict.get("sensor_type")
        
        # Display enhanced sensor preview with animations
        if sensor_key and sensor_key in sensor_values:
            _draw_enhanced_sensor_preview(screen, main_content_rect, content_start_y, sensor_key, 
                                        sensor_values[sensor_key], fonts, config_module, ui_scaler, current_time)
    
    # Enhanced sensor status with animations
    _draw_enhanced_sensor_status(screen, main_content_rect, sensor_values, fonts, config_module, ui_scaler, current_time)
    
    # Add tricorder-style ambient animations
    _draw_sensor_ambient_effects(screen, main_content_rect, current_time, config_module, ui_scaler)

def _draw_glowing_title(screen, text, font, color, center_pos, current_time):
    """Draw title with animated glow effect."""
    # Main title
    title_surface = font.render(text, True, color)
    title_rect = title_surface.get_rect(center=center_pos)
    
    # Animated glow effect
    glow_intensity = 0.4 + 0.2 * (0.5 + 0.5 * math.sin(current_time * 1.5))
    glow_color = tuple(min(255, int(c * glow_intensity * 0.4)) for c in color)
    
    # Draw glow layers
    for offset in [(-2, -2), (-2, 2), (2, -2), (2, 2), (-1, 0), (1, 0), (0, -1), (0, 1)]:
        glow_surface = font.render(text, True, glow_color)
        glow_pos = (title_rect.x + offset[0], title_rect.y + offset[1])
        screen.blit(glow_surface, glow_pos)
    
    # Draw main title on top
    screen.blit(title_surface, title_rect)

def _draw_enhanced_sensor_preview(screen, main_content_rect, content_y, sensor_key, sensor_data, fonts, config_module, ui_scaler, current_time):
    """
    Draw enhanced sensor preview with animations and tricorder styling.
    """
    # Get display properties
    display_props = config_module.SENSOR_DISPLAY_PROPERTIES.get(sensor_key, {})
    display_name = display_props.get("display_name", sensor_key)
    
    # Use responsive spacing
    if ui_scaler:
        name_spacing = ui_scaler.margin("medium")
        value_spacing = ui_scaler.margin("small")
        note_spacing = ui_scaler.margin("small")
    else:
        name_spacing = 25
        value_spacing = 15
        note_spacing = 10
    
    # Animated sensor name with subtle pulse
    name_font = fonts['medium']
    pulse_alpha = 0.8 + 0.2 * (0.5 + 0.5 * math.sin(current_time * 2.0))
    name_color = tuple(min(255, int(c * pulse_alpha)) for c in config_module.Theme.FOREGROUND)
    name_surface = name_font.render(display_name, True, name_color)
    name_rect = name_surface.get_rect(centerx=main_content_rect.centerx, y=content_y)
    screen.blit(name_surface, name_rect)
    
    # Large animated value display (temperature shown in Kelvin to match sensor view)
    value_font = fonts['large']
    text_val = sensor_data.get("text", "N/A")
    unit = sensor_data.get("unit", "")
    numeric_val = sensor_data.get("value")
    if sensor_key == config_module.SENSOR_TEMPERATURE and numeric_val is not None:
        k_val = numeric_val + 273.15
        value_text = f"{k_val:.1f} K"
    else:
        value_text = f"{text_val} {unit}".strip()
    
    # Color-code based on sensor type and add breathing effect
    if "temp" in sensor_key.lower():
        base_color = config_module.Palette.ENGINEERING_GOLD
    elif "humid" in sensor_key.lower():
        base_color = config_module.Palette.VIKING_BLUE
    elif "press" in sensor_key.lower():
        base_color = config_module.Palette.COPPER_ROSE
    else:
        base_color = config_module.Theme.ACCENT
    
    # Breathing effect for the value
    breathing_scale = 1.0 + 0.05 * (0.5 + 0.5 * math.sin(current_time * 1.2))
    value_color = tuple(min(255, int(c * breathing_scale)) for c in base_color)
    value_surface = value_font.render(value_text, True, value_color)
    value_rect = value_surface.get_rect(centerx=main_content_rect.centerx, y=name_rect.bottom + name_spacing)
    screen.blit(value_surface, value_rect)
    
    # Animated data bars around the value
    _draw_sensor_data_visualization(screen, value_rect, sensor_data, current_time, config_module)
    
    # Note with fade-in effect
    note = sensor_data.get("note", "")
    if note:
        note_font = fonts['small']
        note_alpha = 0.7 + 0.3 * (0.5 + 0.5 * math.sin(current_time * 0.8 + 1.0))
        note_color = tuple(min(255, int(c * note_alpha)) for c in config_module.Theme.FOREGROUND)
        note_surface = note_font.render(note, True, note_color)
        note_rect = note_surface.get_rect(centerx=main_content_rect.centerx, y=value_rect.bottom + value_spacing)
        screen.blit(note_surface, note_rect)

def _draw_sensor_data_visualization(screen, value_rect, sensor_data, current_time, config_module):
    """Draw animated data visualization around the sensor value."""
    # Get numeric value for visualization
    try:
        text_val = sensor_data.get("text", "0")
        # Extract numeric part
        numeric_val = float(''.join(c for c in text_val if c.isdigit() or c == '.' or c == '-'))
    except:
        numeric_val = 0
    
    # Normalize value for visualization (0-100 range)
    normalized_val = min(100, max(0, abs(numeric_val)))
    
    # Draw animated data bars on sides of value
    bar_count = 5
    bar_width = 3
    bar_spacing = 12
    bar_height_base = 8
    
    for i in range(bar_count):
        # Left side bars
        bar_height = bar_height_base + int(4 * math.sin(current_time * 2.0 + i * 0.5))
        bar_alpha = 0.3 + 0.4 * (normalized_val / 100.0) * (0.5 + 0.5 * math.sin(current_time * 1.5 + i * 0.3))
        
        if bar_alpha > 0.1:
            bar_color = tuple(min(255, int(c * bar_alpha)) for c in config_module.Theme.ACCENT)
            left_x = value_rect.left - (bar_spacing * (i + 1)) - bar_width
            bar_y = value_rect.centery - bar_height // 2
            pygame.draw.rect(screen, bar_color, (left_x, bar_y, bar_width, bar_height))
            
            # Right side bars (mirrored)
            right_x = value_rect.right + (bar_spacing * (i + 1))
            pygame.draw.rect(screen, bar_color, (right_x, bar_y, bar_width, bar_height))

def _draw_animated_instructions(screen, main_content_rect, content_y, fonts, config_module, ui_scaler, current_time):
    """Draw animated instructions when no sensor is selected."""
    if ui_scaler:
        instruction_spacing = ui_scaler.margin("large")
        hint_spacing = ui_scaler.margin("medium")
    else:
        instruction_spacing = 40
        hint_spacing = 25
    
    # Main instruction with fade animation
    instruction_font = fonts['medium']
    fade_alpha = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(current_time * 1.0))
    instruction_color = tuple(min(255, int(c * fade_alpha)) for c in config_module.Theme.FOREGROUND)
    instruction_text = "Select a sensor to view details"
    instruction_surface = instruction_font.render(instruction_text, True, instruction_color)
    instruction_rect = instruction_surface.get_rect(centerx=main_content_rect.centerx, y=content_y + instruction_spacing)
    screen.blit(instruction_surface, instruction_rect)
    
    # Animated navigation hint
    hint_font = fonts['small']
    hint_alpha = 0.5 + 0.3 * (0.5 + 0.5 * math.sin(current_time * 1.5 + 0.5))
    hint_color = tuple(min(255, int(c * hint_alpha)) for c in config_module.Theme.ACCENT)
    labels = config_module.get_control_labels()
    hint_text = f"Use {labels['prev']}/{labels['next']} to browse sensors"
    hint_surface = hint_font.render(hint_text, True, hint_color)
    hint_rect = hint_surface.get_rect(centerx=main_content_rect.centerx, y=instruction_rect.bottom + hint_spacing)
    screen.blit(hint_surface, hint_rect)
    
    # Add scanning lines animation
    _draw_scanning_lines_effect(screen, main_content_rect, current_time, config_module)

def _draw_enhanced_sensor_status(screen, main_content_rect, sensor_values, fonts, config_module, ui_scaler, current_time):
    """Draw enhanced sensor status with animations at the bottom."""
    if ui_scaler:
        bottom_margin = ui_scaler.margin("large")
        status_spacing = ui_scaler.margin("small")
    else:
        bottom_margin = 50
        status_spacing = 8
    
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
    
    # Animated status text
    status_text = f"Status: {working_sensors}/{total_sensors} sensors online"
    
    # Color and animation based on status
    if error_sensors == 0:
        status_color = config_module.Palette.GREEN
        pulse_alpha = 0.8 + 0.2 * (0.5 + 0.5 * math.sin(current_time * 1.0))
    else:
        status_color = config_module.Palette.ENGINEERING_GOLD
        pulse_alpha = 0.7 + 0.3 * (0.5 + 0.5 * math.sin(current_time * 2.0))
    
    animated_color = tuple(min(255, int(c * pulse_alpha)) for c in status_color)
    status_surface = summary_font.render(status_text, True, animated_color)
    
    # Position at bottom with animated indicator
    status_rect = status_surface.get_rect(centerx=main_content_rect.centerx, 
                                        y=main_content_rect.bottom - bottom_margin)
    
    # Draw status indicator dot
    indicator_radius = 4
    indicator_x = status_rect.left - 15
    indicator_y = status_rect.centery
    indicator_pulse = 0.5 + 0.5 * (0.5 + 0.5 * math.sin(current_time * 3.0))
    indicator_color = tuple(min(255, int(c * indicator_pulse)) for c in status_color)
    pygame.draw.circle(screen, indicator_color, (indicator_x, indicator_y), indicator_radius)
    
    screen.blit(status_surface, status_rect)
    
    # Error details with pulsing effect
    if error_sensors > 0:
        error_alpha = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(current_time * 1.8))
        error_color = tuple(min(255, int(c * error_alpha)) for c in config_module.Palette.RED_ALERT)
        error_text = f"({error_sensors} sensors offline)"
        error_surface = summary_font.render(error_text, True, error_color)
        error_rect = error_surface.get_rect(centerx=main_content_rect.centerx, 
                                          y=status_rect.bottom + status_spacing)
        screen.blit(error_surface, error_rect)

def _draw_sensor_ambient_effects(screen, main_content_rect, current_time, config_module, ui_scaler):
    """Draw ambient tricorder-style effects in the background."""
    # Only draw if we have enough space
    if main_content_rect.width < 200 or main_content_rect.height < 150:
        return
    
    # Corner data streams (similar to main menu but sensor-themed)
    _draw_sensor_data_streams(screen, main_content_rect, current_time, config_module)
    
    # Subtle grid pattern
    _draw_sensor_grid_pattern(screen, main_content_rect, current_time, config_module)

def _draw_scanning_lines_effect(screen, main_content_rect, current_time, config_module):
    """Draw scanning lines effect for when no sensor is selected."""
    scan_speed = 1.5
    line_height = 2
    line_spacing = 30
    
    # Calculate number of lines that fit
    num_lines = max(1, main_content_rect.height // line_spacing)
    
    for i in range(num_lines):
        line_offset = i * 0.4
        line_progress = (current_time * scan_speed + line_offset) % 3.0
        
        if line_progress < 1.5:  # Line visible for half the cycle
            line_y = main_content_rect.top + (i * line_spacing) + 50  # Offset from top
            
            # Calculate line width and alpha
            max_width = main_content_rect.width * 0.4
            if line_progress < 0.75:
                line_width = int(max_width * (line_progress / 0.75))
                alpha = line_progress / 0.75
            else:
                line_width = int(max_width * ((1.5 - line_progress) / 0.75))
                alpha = (1.5 - line_progress) / 0.75
            
            if line_width > 4 and alpha > 0.1:
                line_x = main_content_rect.centerx - line_width // 2
                line_color = (0, int(80 * alpha), int(25 * alpha))
                pygame.draw.rect(screen, line_color, (line_x, line_y, line_width, line_height))

def _draw_sensor_data_streams(screen, main_content_rect, current_time, config_module):
    """Draw flowing data streams in corners."""
    corner_margin = 10
    stream_length = 6
    dot_size = 2
    
    # Top-right corner stream
    start_x = main_content_rect.right - corner_margin - 30
    start_y = main_content_rect.top + corner_margin + 40  # Below title area
    
    for i in range(stream_length):
        flow_offset = (current_time * 2.5 + i * 0.4) % 4.0
        
        if flow_offset < 2.0:
            dot_x = start_x + int(flow_offset * 6)
            dot_y = start_y + (i * 5)
            
            alpha_factor = 1.0 - (flow_offset / 2.0) if flow_offset > 1.0 else flow_offset
            dot_color = (0, int(60 * alpha_factor), int(20 * alpha_factor))
            
            if dot_color[1] > 10:
                pygame.draw.circle(screen, dot_color, (dot_x, dot_y), dot_size)

def _draw_sensor_grid_pattern(screen, main_content_rect, current_time, config_module):
    """Draw subtle grid pattern for ambient effect."""
    grid_spacing = 40
    dot_size = 1
    
    # Only draw a few grid points to keep it subtle
    cols = min(6, main_content_rect.width // grid_spacing)
    rows = min(4, main_content_rect.height // grid_spacing)
    
    for row in range(rows):
        for col in range(cols):
            # Stagger animation
            offset = (row * cols + col) * 0.3
            alpha_cycle = (current_time * 0.8 + offset) % 4.0
            
            if alpha_cycle < 2.0:
                alpha = 0.3 * (1.0 - abs(alpha_cycle - 1.0))
                
                if alpha > 0.05:
                    dot_x = main_content_rect.left + col * grid_spacing + 20
                    dot_y = main_content_rect.top + row * grid_spacing + 60
                    
                    dot_color = (0, int(40 * alpha), int(15 * alpha))
                    pygame.draw.circle(screen, dot_color, (dot_x, dot_y), dot_size)