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
    
    if ui_scaler:
        screen_width = ui_scaler.screen_width
        screen_height = ui_scaler.screen_height
        safe_rect = ui_scaler.get_safe_area_rect() if ui_scaler.safe_area_enabled else pygame.Rect(0, 0, screen_width, screen_height)
    else:
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        safe_rect = pygame.Rect(0, 0, screen_width, screen_height)
    current_time = time.time()
    
    # Use UIScaler for responsive spacing if available; keep content inside safe area for curved bezel
    if ui_scaler:
        title_margin = max(ui_scaler.margin("small"), ui_scaler.get_safe_area_margins()["left"] if ui_scaler.safe_area_enabled else 0)
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
    # UI-only: show temperature as K (convert at draw time; data stays in Celsius)
    if current_sensor_key == config_module.SENSOR_TEMPERATURE and numeric_val is not None:
        k_val = numeric_val + 273.15
        value_text_display = f"{k_val:.1f} K"
        arrow_text = f"{k_val:.1f}"
    else:
        value_text_display = f"{text_val} {unit}".strip()
    
    # Draw sensor name in top left within safe area
    title_font = fonts['medium']
    title_surface = title_font.render(display_name, True, config_module.Theme.ACCENT)
    title_rect = title_surface.get_rect(topleft=(safe_rect.left + title_margin, safe_rect.top + title_margin))
    _draw_subtle_title_glow(screen, display_name, title_font, config_module.Theme.ACCENT, title_rect.center, current_time)
    screen.blit(title_surface, title_rect)
    
    # Draw frozen indicator if needed (moved to top right) within safe area
    if app_state.is_frozen:
        frozen_font = fonts['medium']
        frozen_surface = frozen_font.render("[FROZEN]", True, config_module.Theme.FROZEN_INDICATOR)
        frozen_rect = frozen_surface.get_rect(topright=(safe_rect.right - title_margin, safe_rect.top + title_margin))
        screen.blit(frozen_surface, frozen_rect)
    
    # Draw current value below the title (temperature: omit so only small ticks show), within safe area
    value_font = fonts['large']
    value_surface = value_font.render(value_text_display, True, config_module.Theme.FOREGROUND)
    value_rect = value_surface.get_rect(midleft=(safe_rect.left + title_margin, title_rect.bottom + value_spacing))
    if current_sensor_key != config_module.SENSOR_TEMPERATURE:
        screen.blit(value_surface, value_rect)
    else:
        value_rect = pygame.Rect(title_rect.x, title_rect.y, title_rect.width, title_rect.height + value_spacing)
    
    # Draw note in middle right if present, within safe area
    if note:
        note_x_pos = safe_rect.right - title_margin
        note_y_pos = safe_rect.centery
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
        # Reserve space: time axis label + orange/yellow scanning strip below graph
        time_label_height = (config_module.FONT_SIZE_SMALL or 14) + (ui_scaler.scale(8) if ui_scaler else 8)
        scan_strip_height = ui_scaler.scale(24) if ui_scaler else 24
        min_graph_h = ui_scaler.scale(100) if ui_scaler else 100
        graph_height = safe_rect.bottom - value_rect.bottom - graph_margin * 2 - time_label_height - scan_strip_height
        graph_width = safe_rect.width - graph_margin * 2
        graph_rect = pygame.Rect(
            safe_rect.left + graph_margin,
            value_rect.bottom + graph_margin,
            graph_width,
            max(min_graph_h, graph_height)
        )
        scan_strip_rect = pygame.Rect(graph_rect.left, graph_rect.bottom, graph_rect.width, scan_strip_height)
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
            # Orange/yellow scanning lines animation below the graph (tricorder-style)
            if not app_state.is_frozen and scan_strip_rect.height >= 12:
                _draw_line_graph_scanning_effect(screen, scan_strip_rect, current_time, config_module, ui_scaler)
            # Draw time axis label below the scanning strip
            time_font = fonts.get('small', fonts['medium'])
            time_text = f"Time ({config_module.GRAPH_HISTORY_SIZE}s →)"
            time_surf = time_font.render(time_text, True, config_module.Theme.GRAPH_GRID)
            time_label_offset = scan_strip_height + (config_module.FONT_SIZE_SMALL or 14) + (ui_scaler.scale(5) if ui_scaler else 5)
            time_rect = time_surf.get_rect(center=(graph_rect.centerx, graph_rect.bottom + time_label_offset))
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
                
            # No footer when graph is shown; use full safe area height
            graph_height = safe_rect.height - graph_margin_top - graph_margin_bottom
            graph_height = max(80, graph_height)
            graph_x = safe_rect.centerx - (graph_width // 2)
            graph_y = safe_rect.top + graph_margin_top
            graph_rect = pygame.Rect(graph_x, graph_y, graph_width, graph_height)
            
            # UI-only: temperature graph shows K scale 0–1701 (convert at draw time; data unchanged)
            if current_sensor_key == config_module.SENSOR_TEMPERATURE:
                vbar_units = "K"
                vbar_min = 0
                vbar_max = 1701
                vbar_normal = (291, 301)
                vbar_critical_low = 283
                vbar_critical_high = 308
                graph_val = (numeric_val + 273.15) if numeric_val is not None else None
                graph_arrow_text = arrow_text  # already set to Kelvin string above
            else:
                vbar_units = display_props.get("units", unit)
                vbar_min = vbar_config["min_val"]
                vbar_max = vbar_config["max_val"]
                vbar_normal = vbar_config["normal_range"]
                vbar_critical_low = vbar_config.get("critical_low")
                vbar_critical_high = vbar_config.get("critical_high")
                graph_val = numeric_val
                graph_arrow_text = arrow_text
            
            try:
                # Temperature uses full 0–1701 K scale; no dynamic zoom
                use_dynamic_range = vbar_config.get("dynamic_range", False) if current_sensor_key != config_module.SENSOR_TEMPERATURE else False
                vertical_graph = VerticalBarGraph(
                    screen=screen, rect=graph_rect,
                    title="",
                    units=vbar_units,
                    min_val=vbar_min,
                    max_val=vbar_max,
                    normal_range=vbar_normal,
                    fonts=fonts,
                    config_module=config_module,
                    critical_low=vbar_critical_low,
                    critical_high=vbar_critical_high,
                    num_ticks=vbar_config.get("num_ticks", 11),
                    dynamic_range=use_dynamic_range,
                    zoom_factor=vbar_config.get("zoom_factor", 0.3),
                    min_zoom_range=vbar_config.get("min_zoom_range"),
                    stability_threshold=vbar_config.get("stability_threshold", 2.0),
                    ui_scaler=ui_scaler
                )
                show_pointer_label = current_sensor_key != config_module.SENSOR_TEMPERATURE
                vertical_graph.draw(graph_val, graph_arrow_text, show_pointer_label=show_pointer_label)
            except KeyError as e:
                 logger.error(f"Missing key in VERTICAL_GRAPH_CONFIG for {current_sensor_key}: {e}", exc_info=True)
            except Exception as e:
                 logger.error(f"Error creating/drawing VerticalBarGraph for {current_sensor_key}: {e}", exc_info=True)
        else:
            logger.warning(f"Graph type for {current_sensor_key} is VERTICAL_BAR but no vertical_graph_config found.")
            fallback_font = fonts.get('medium', pygame.font.Font(None, config_module.FONT_SIZE_MEDIUM))
            fallback_text = "Graph N/A"
            fallback_surf = fallback_font.render(fallback_text, True, config_module.Theme.ACCENT)
            fallback_offset = ui_scaler.scale(80) if ui_scaler else 80
            fallback_rect = fallback_surf.get_rect(center=(safe_rect.centerx, title_rect.bottom + fallback_offset))
            screen.blit(fallback_surf, fallback_rect)

    elif graph_type == "NONE" or current_sensor_key == config_module.SENSOR_CLOCK:
        logger.debug(f"No graph to display for sensor: {current_sensor_key}")
        fallback_font = fonts.get('medium', pygame.font.Font(None, config_module.FONT_SIZE_MEDIUM))
        fallback_text = "Graph N/A" if graph_type == "NONE" else ""
        if fallback_text:
            fallback_surf = fallback_font.render(fallback_text, True, config_module.Theme.ACCENT)
            fallback_offset = ui_scaler.scale(80) if ui_scaler else 80
            fallback_rect = fallback_surf.get_rect(center=(safe_rect.centerx, title_rect.bottom + fallback_offset))
            screen.blit(fallback_surf, fallback_rect)
    else:
        logger.warning(f"Unknown graph_type '{graph_type}' or no graph configured for sensor: {current_sensor_key}")
        fallback_font = fonts.get('medium', pygame.font.Font(None, config_module.FONT_SIZE_MEDIUM))
        fallback_text = "Graph N/A"
        fallback_surf = fallback_font.render(fallback_text, True, config_module.Theme.ACCENT)
        fallback_offset = ui_scaler.scale(80) if ui_scaler else 80
        fallback_rect = fallback_surf.get_rect(center=(safe_rect.centerx, title_rect.bottom + fallback_offset))
        screen.blit(fallback_surf, fallback_rect)

    # Draw ambient tricorder effects in available spaces
    _draw_sensor_ambient_effects(screen, screen_width, screen_height, graph_rect, current_sensor_data, current_time, config_module, ui_scaler, app_state.is_frozen)

    # No footer when a graph is shown (LINE or VERTICAL_BAR) to avoid overlap; short hint when no graph
    if graph_type not in ("LINE", "VERTICAL_BAR"):
        labels = config_module.get_control_labels()
        hint_text = f"< {labels['back']}=Back >"
        render_footer(
            screen, hint_text, fonts,
            config_module.Theme.FOREGROUND,
            screen_width, screen_height,
            ui_scaler=ui_scaler,
            content_center_x=safe_rect.centerx
        )

def _draw_subtle_title_glow(screen, text, font, color, center_pos, current_time):
    """Draw title with subtle animated glow effect behind the main text."""
    # Remove glow effect - not visible on small screen, just draw normal text
    pass  # No glow effect needed

def _draw_line_graph_scanning_effect(screen, strip_rect, current_time, config_module, ui_scaler=None):
    """Draw orange/yellow tricorder-style scanning lines (growing/shrinking bars) below the line graph."""
    scan_speed = 2.2
    scan_height = max(2, ui_scaler.scale(2) if ui_scaler else 2)
    scan_spacing = max(10, (ui_scaler.scale(12) if ui_scaler else 12))
    if strip_rect.height < scan_spacing:
        return
    num_lines = max(1, strip_rect.height // scan_spacing)
    max_width = strip_rect.width * 0.75
    # Orange and yellow (theme accent / engineering gold)
    primary = getattr(config_module.Palette, "ORANGE", (255, 165, 0))
    secondary = getattr(config_module.Palette, "ENGINEERING_GOLD", (255, 200, 0))
    for i in range(num_lines):
        line_offset = i * 0.25
        line_progress = (current_time * scan_speed + line_offset) % 4.0
        if line_progress >= 2.0:
            continue
        line_y = strip_rect.top + (i * scan_spacing) + 2
        if line_progress < 1.0:
            line_width = int(max_width * line_progress)
        else:
            line_width = int(max_width * (2.0 - line_progress))
        if line_width < 6:
            continue
        line_x = strip_rect.centerx - line_width // 2
        line_rect = pygame.Rect(line_x, line_y, line_width, scan_height)
        scan_color = secondary if i % 2 else primary
        pygame.draw.rect(screen, scan_color, line_rect)
        highlight = (min(255, scan_color[0] + 30), min(255, scan_color[1] + 25), min(255, scan_color[2] + 10))
        pygame.draw.line(screen, highlight, (line_rect.left, line_rect.top), (line_rect.right, line_rect.top), 1)

def _draw_sensor_ambient_effects(screen, screen_width, screen_height, graph_rect, sensor_data, current_time, config_module, ui_scaler, is_frozen=False):
    """Draw ambient tricorder effects in available spaces around the graph. Uses ui_scaler for insets when available."""
    if screen_width < 200 or screen_height < 150:
        return
    animation_time = 0 if is_frozen else current_time
    if ui_scaler:
        safe_top_y = ui_scaler.scale(100)
        inset_sm = ui_scaler.margin("small")
        inset_md = ui_scaler.margin("medium")
        inset_bottom = ui_scaler.scale(40)
        frozen_top = ui_scaler.scale(50)
    else:
        safe_top_y = 100
        inset_sm = 10
        inset_md = 15
        inset_bottom = 40
        frozen_top = 50
    if graph_rect:
        left_area_top = max(graph_rect.top, safe_top_y)
        left_area = pygame.Rect(inset_sm, left_area_top, max(0, graph_rect.left - inset_md), max(0, graph_rect.bottom - left_area_top - inset_md))
        right_area_top = max(graph_rect.top, frozen_top)
        right_area = pygame.Rect(graph_rect.right + inset_sm, right_area_top, max(0, screen_width - graph_rect.right - inset_md * 2), max(0, graph_rect.bottom - right_area_top - inset_sm))
        bottom_area = pygame.Rect(inset_sm, graph_rect.bottom + inset_sm, screen_width - inset_sm * 2, max(0, screen_height - graph_rect.bottom - inset_bottom))
    else:
        left_area_top = max(screen_height // 2, safe_top_y)
        left_area = pygame.Rect(inset_sm, left_area_top, screen_width // 3, max(0, screen_height - left_area_top - inset_bottom))
        right_area = pygame.Rect(screen_width * 2 // 3, max(screen_height // 2, frozen_top), screen_width // 3 - inset_sm, screen_height // 2 - inset_bottom)
        bottom_area = pygame.Rect(inset_sm, screen_height * 3 // 4, screen_width - inset_sm * 2, screen_height // 4 - inset_bottom)
    
    min_effect_size = ui_scaler.scale(50) if ui_scaler else 50
    min_bottom_w = ui_scaler.scale(100) if ui_scaler else 100
    min_bottom_h = ui_scaler.scale(30) if ui_scaler else 30
    if left_area.width > min_effect_size and left_area.height > min_effect_size:
        _draw_sensor_data_stream(screen, left_area, animation_time, config_module, "left", ui_scaler)
    if right_area.width > min_effect_size and right_area.height > min_effect_size:
        _draw_sensor_data_stream(screen, right_area, animation_time, config_module, "right", ui_scaler)
    if bottom_area.width > min_bottom_w and bottom_area.height > min_bottom_h:
        _draw_sensor_status_indicators(screen, bottom_area, animation_time, config_module, ui_scaler)

def _draw_sensor_data_stream(screen, area, current_time, config_module, side, ui_scaler=None):
    """Draw flickering data stream effect with fixed position dots. Uses ui_scaler for spacing/size when available."""
    if current_time == 0:  # Frozen
        return
    dot_spacing = ui_scaler.scale(14) if ui_scaler else 14
    dot_offset = ui_scaler.scale(5) if ui_scaler else 5
    num_dots = max(1, area.height // dot_spacing)
    for i in range(num_dots):
        dot_y = area.top + (i * dot_spacing) + dot_offset
        if side == "left":
            dot_x = area.left + area.width // 3
        else:
            dot_x = area.right - area.width // 3
        flicker_offset = i * 0.7
        flicker_progress = (current_time * 1.5 + flicker_offset) % 3.0
        if flicker_progress < 1.0:
            alpha = flicker_progress
        elif flicker_progress < 2.0:
            alpha = 1.0
        else:
            alpha = 3.0 - flicker_progress
        if alpha > 0.1:
            viking_blue = config_module.Palette.VIKING_BLUE
            dot_color = tuple(min(255, int(c * alpha)) for c in viking_blue)
            dot_size = max(1, ui_scaler.scale(2) if ui_scaler else 2)
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

def _draw_sensor_status_indicators(screen, area, current_time, config_module, ui_scaler=None):
    """Draw status indicator dots across the bottom. Uses ui_scaler for spacing/size when available."""
    if current_time == 0:  # Frozen
        return
    min_width_per_indicator = ui_scaler.scale(24) if ui_scaler else 24
    indicator_radius = max(1, ui_scaler.scale(5) if ui_scaler else 5)
    indicator_count = min(6, area.width // max(1, min_width_per_indicator))
    indicator_spacing = area.width // max(1, indicator_count)
    for i in range(indicator_count):
        indicator_x = area.left + (i * indicator_spacing) + indicator_spacing // 2
        indicator_y = area.centery
        pulse_offset = i * 0.5
        pulse_alpha = 0.4 + 0.5 * (0.5 + 0.5 * math.sin(current_time * 1.8 + pulse_offset))
        if i % 3 == 0:
            base_color = config_module.Palette.GREEN
        elif i % 3 == 1:
            base_color = config_module.Palette.ENGINEERING_GOLD
        else:
            base_color = config_module.Theme.ACCENT
        indicator_color = tuple(min(255, int(c * pulse_alpha)) for c in base_color)
        pygame.draw.circle(screen, indicator_color, (indicator_x, indicator_y), max(1, indicator_radius)) 