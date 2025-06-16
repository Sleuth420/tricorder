# --- ui/sensor_view.py ---
# Handles rendering of individual sensor views OR the auto-cycling dashboard view

import pygame
import logging
import time
import math
from ui.components.text.text_display import render_title, render_value, render_note, render_footer, render_text
from ui.components.charts.vertical_bar_graph import VerticalBarGraph
from ui.components.charts.graph import draw_graph # Re-import the old graph component
# Import app state constants
from models.app_state import STATE_SENSOR_VIEW, STATE_DASHBOARD # These are fine as they are AppState internal states
# Import config for sensor mode constants and display properties
import config as app_config # Use an alias
# import re # No longer needed

logger = logging.getLogger(__name__)

def draw_sensor_view(screen, app_state, sensor_values, sensor_history, fonts, config_module, ui_scaler=None):
    """
    Draw the individual sensor view screen.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        sensor_values (dict): Dictionary of current sensor data (new structure with dict per sensor)
        sensor_history (ReadingHistory): The history of sensor readings
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
        ui_scaler (UIScaler): The UI scaler for scaling the graph
    """
    screen.fill(config_module.Theme.BACKGROUND)
    
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    current_time = time.time()
    
    # Use UIScaler for responsive spacing if available
    if ui_scaler:
        title_margin = ui_scaler.margin("small")
        value_spacing = ui_scaler.margin("medium")
        graph_margin = ui_scaler.margin("medium")
        
        # Debug logging for sensor view layout
        if ui_scaler.debug_mode:
            logger.info(f"🎨 SensorView: screen={screen_width}x{screen_height}, margins={title_margin}px/{graph_margin}px")
    else:
        # Fallback to original hardcoded values
        title_margin = 10
        value_spacing = 15
        graph_margin = 15
    
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
    
    # Draw sensor name in top left with subtle glow effect
    title_font = fonts['medium']
    title_surface = title_font.render(display_name, True, config_module.Theme.ACCENT)
    title_rect = title_surface.get_rect(topleft=(title_margin, title_margin))
    _draw_subtle_title_glow(screen, display_name, title_font, config_module.Theme.ACCENT, title_rect.center, current_time)
    screen.blit(title_surface, title_rect)
    
    # Draw frozen indicator if needed (moved to top right) - solid color for small screen visibility
    if app_state.is_frozen:
        frozen_font = fonts['medium']
        frozen_surface = frozen_font.render("[FROZEN]", True, config_module.Theme.FROZEN_INDICATOR)
        frozen_rect = frozen_surface.get_rect(topright=(screen_width - title_margin, title_margin))
        screen.blit(frozen_surface, frozen_rect)
    
    # Draw current value below the title - remove breathing effect for small screen
    value_font = fonts['large']
    value_text = f"{text_val} {unit}".strip()
    value_surface = value_font.render(value_text, True, config_module.Theme.FOREGROUND)
    value_rect = value_surface.get_rect(midleft=(title_margin, title_rect.bottom + value_spacing))
    screen.blit(value_surface, value_rect)
    
    # Draw note in middle right if present
    if note:
        note_x_pos = screen_width - title_margin  # Right side of screen  
        note_y_pos = screen_height // 2  # Middle of screen
        render_text(
            screen, note, 
            fonts['small'] if 'small' in fonts else fonts['medium'],
            config_module.Theme.ACCENT,
            (note_x_pos, note_y_pos),
            align="right"
        )
    
    graph_type = display_props.get("graph_type", "NONE")
    graph_rect = None  # Track graph position for ambient effects

    if graph_type == "LINE":
        history_data = sensor_history.get_history(current_sensor_key)
        # Leave more space for time label and footer
        graph_height = screen_height - value_rect.bottom - graph_margin*3 - config_module.FONT_SIZE_SMALL*3 - 40
        graph_width = screen_width - graph_margin*2
        graph_rect = pygame.Rect(
            graph_margin, 
            value_rect.bottom + graph_margin,
            graph_width,
            max(100, graph_height)  # Ensure minimum height
        )
        range_override = display_props.get("range_override", (None, None))
        min_val_cfg, max_val_cfg = range_override if range_override is not None else (None, None)

        try:
            draw_graph(
                screen, history_data, graph_rect, 
                config_module.Theme.FOREGROUND, 
                min_val_cfg, max_val_cfg, 
                current_sensor_key,
                config_module,
                ui_scaler
            )
            # Draw time axis label with better positioning
            time_font = fonts.get('small', fonts['medium'])
            time_text = f"Time ({config_module.GRAPH_HISTORY_SIZE}s →)"
            time_surf = time_font.render(time_text, True, config_module.Theme.GRAPH_GRID)
            time_rect = time_surf.get_rect(center=(graph_rect.centerx, graph_rect.bottom + config_module.FONT_SIZE_SMALL + 5))
            screen.blit(time_surf, time_rect)
        except Exception as e:
             logger.error(f"Error drawing line graph for {current_sensor_key}: {e}", exc_info=True)

    elif graph_type == "VERTICAL_BAR":
        vbar_config = display_props.get("vertical_graph_config")
        if vbar_config:
            # Calculate graph dimensions to maximize available space using UIScaler
            if ui_scaler:
                graph_width = ui_scaler.scale(120)  # Responsive graph width
                graph_margin_top = ui_scaler.margin("medium")  # Responsive top margin
                graph_margin_bottom = ui_scaler.margin("medium")  # Responsive bottom margin
            else:
                # Fallback to original hardcoded values
                graph_width = 120
                graph_margin_top = 20
                graph_margin_bottom = 20
                
            # Maximize vertical space by using margins from top and bottom
            graph_height = screen_height - graph_margin_top - graph_margin_bottom  # Use all available space between margins
            graph_x = (screen_width - graph_width) // 2
            graph_y = graph_margin_top  # Start from top margin
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
                    stability_threshold=vbar_config.get("stability_threshold", 2.0),
                    ui_scaler=ui_scaler
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

    # Draw ambient tricorder effects in available spaces
    _draw_sensor_ambient_effects(screen, screen_width, screen_height, graph_rect, current_sensor_data, current_time, config_module, ui_scaler, app_state.is_frozen)

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

def _draw_subtle_title_glow(screen, text, font, color, center_pos, current_time):
    """Draw title with subtle animated glow effect behind the main text."""
    # Remove glow effect - not visible on small screen, just draw normal text
    pass  # No glow effect needed

def _draw_sensor_ambient_effects(screen, screen_width, screen_height, graph_rect, sensor_data, current_time, config_module, ui_scaler, is_frozen=False):
    """Draw ambient tricorder effects in available spaces around the graph."""
    # Only draw effects if we have enough space
    if screen_width < 200 or screen_height < 150:
        return
    
    # Freeze animations when frozen
    animation_time = 0 if is_frozen else current_time
    
    # Calculate safe Y position to avoid overlapping with title and value text
    # Title + value + some padding = roughly 80-100px from top
    safe_top_y = 100  # Safe distance from top to avoid text overlap
    
    # Define available areas based on graph position
    if graph_rect:
        # Areas around the graph - ensure left area starts below title/value text
        left_area_top = max(graph_rect.top, safe_top_y)
        left_area = pygame.Rect(5, left_area_top, max(0, graph_rect.left - 15), max(0, graph_rect.bottom - left_area_top - 20))
        # Right area - start below frozen indicator to avoid overlap
        right_area_top = max(graph_rect.top, 50)  # Frozen indicator is smaller, 50px is enough
        right_area = pygame.Rect(graph_rect.right + 10, right_area_top, max(0, screen_width - graph_rect.right - 20), max(0, graph_rect.bottom - right_area_top - 10))
        bottom_area = pygame.Rect(10, graph_rect.bottom + 10, screen_width - 20, max(0, screen_height - graph_rect.bottom - 60))
    else:
        # Full bottom area if no graph - ensure left area starts below title/value text
        left_area_top = max(screen_height // 2, safe_top_y)
        left_area = pygame.Rect(5, left_area_top, screen_width // 3, max(0, screen_height - left_area_top - 50))
        # Right area - start below frozen indicator
        right_area = pygame.Rect(screen_width * 2 // 3, max(screen_height // 2, 50), screen_width // 3 - 10, screen_height // 2 - 50)
        bottom_area = pygame.Rect(10, screen_height * 3 // 4, screen_width - 20, screen_height // 4 - 50)
    
    # Draw effects in each area
    if left_area.width > 50 and left_area.height > 50:
        _draw_sensor_data_stream(screen, left_area, animation_time, config_module, "left")
    
    if right_area.width > 50 and right_area.height > 50:
        _draw_sensor_data_stream(screen, right_area, animation_time, config_module, "right")
    
    if bottom_area.width > 100 and bottom_area.height > 30:
        _draw_sensor_status_indicators(screen, bottom_area, animation_time, config_module)

def _draw_sensor_data_stream(screen, area, current_time, config_module, side):
    """Draw flickering data stream effect with fixed position dots."""
    if current_time == 0:  # Frozen
        return
        
    dot_spacing = 20  # Spacing between fixed dot positions
    
    # Calculate number of dots that fit
    num_dots = max(1, area.height // dot_spacing)
    
    for i in range(num_dots):
        # Fixed Y position for each dot
        dot_y = area.top + (i * dot_spacing) + 7
        
        # Fixed X position based on side
        if side == "left":
            dot_x = area.left + area.width // 3  # Fixed position in left third
        else:
            dot_x = area.right - area.width // 3  # Fixed position in right third
        
        # Staggered flickering animation - each dot has different timing
        flicker_offset = i * 0.7  # Stagger the timing for each dot
        flicker_progress = (current_time * 1.5 + flicker_offset) % 3.0
        
        # Calculate alpha for flickering effect
        if flicker_progress < 1.0:
            # Fade in
            alpha = flicker_progress
        elif flicker_progress < 2.0:
            # Stay bright
            alpha = 1.0
        else:
            # Fade out
            alpha = 3.0 - flicker_progress
        
        # Only draw if visible
        if alpha > 0.1:
            # Use viking blue color for better visibility
            viking_blue = config_module.Palette.VIKING_BLUE
            dot_color = tuple(min(255, int(c * alpha)) for c in viking_blue)
            dot_size = 4  # Fixed size, larger and more visible
            pygame.draw.circle(screen, dot_color, (dot_x, dot_y), dot_size)

def _draw_sensor_readout_display(screen, area, sensor_data, current_time, config_module):
    """Draw animated sensor readout information without text messages."""
    if not sensor_data or current_time == 0:  # Skip if frozen
        return
    
    # Remove all text messages to avoid conflict with frozen indicator
    # Instead, draw animated circuit-like patterns
    
    # Draw animated circuit lines
    line_count = min(4, area.height // 20)
    line_width = min(area.width - 10, 50)
    
    for i in range(line_count):
        line_y = area.top + 20 + (i * 20)
        line_x = area.centerx - line_width // 2
        
        # Animated line segments
        segment_progress = (current_time * 2.0 + i * 0.6) % 4.0
        if segment_progress < 2.0:
            segment_length = int(line_width * (segment_progress / 2.0) * 0.9)
            segment_alpha = 0.4 + 0.4 * (segment_progress / 2.0)
            
            if segment_length > 3:
                segment_color = tuple(min(255, int(c * segment_alpha)) for c in config_module.Theme.ACCENT)
                # Draw horizontal line segments
                pygame.draw.line(screen, segment_color, (line_x, line_y), (line_x + segment_length, line_y), 2)
                # Draw small connection dots
                pygame.draw.circle(screen, segment_color, (line_x + segment_length, line_y), 2)

def _draw_sensor_status_indicators(screen, area, current_time, config_module):
    """Draw status indicator dots across the bottom - larger and more prominent."""
    if current_time == 0:  # Frozen
        return
        
    indicator_count = min(6, area.width // 30)  # Fewer but larger indicators
    indicator_spacing = area.width // max(1, indicator_count)
    
    for i in range(indicator_count):
        indicator_x = area.left + (i * indicator_spacing) + indicator_spacing // 2
        indicator_y = area.centery
        
        # Staggered pulsing
        pulse_offset = i * 0.5
        pulse_alpha = 0.4 + 0.5 * (0.5 + 0.5 * math.sin(current_time * 1.8 + pulse_offset))
        
        # Alternate colors
        if i % 3 == 0:
            base_color = config_module.Palette.GREEN
        elif i % 3 == 1:
            base_color = config_module.Palette.ENGINEERING_GOLD
        else:
            base_color = config_module.Theme.ACCENT
        
        indicator_color = tuple(min(255, int(c * pulse_alpha)) for c in base_color)
        # Much larger dots for small screen visibility - increased from 3 to 8
        pygame.draw.circle(screen, indicator_color, (indicator_x, indicator_y), 8) 