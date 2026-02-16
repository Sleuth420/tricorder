# --- ui/views/system_info_view.py ---
# Handles rendering of the redesigned system information screen (LCARS / Tricorder theme)

import pygame
import logging
import time
from ui.components.charts.horizontal_status_bar import HorizontalStatusBar
import config as app_config  # For theme colors and constants

logger = logging.getLogger(__name__)

# Module-level flag to prevent repeated layout logging
_system_info_logged = False

def draw_system_info_view(screen, app_state, sensor_values, fonts, config_module, target_rect=None, draw_footer=False, ui_scaler=None):
    """
    Draw the redesigned system information screen with rotating status bar and tricorder animations.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state (for frozen status)
        sensor_values (dict): Dictionary containing formatted system values
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
        target_rect (pygame.Rect, optional): The rectangle to draw within. Defaults to the full screen.
        draw_footer (bool): Whether to draw the footer. Defaults to False (disabled).
        ui_scaler (UIScaler, optional): UI scaling system for responsive design
    """
    screen.fill(config_module.Theme.BACKGROUND)
    if ui_scaler:
        screen_width = ui_scaler.screen_width
        screen_height = ui_scaler.screen_height
    else:
        screen_width = screen.get_width()
        screen_height = screen.get_height()
    current_time = time.time()
    
    # Layout: use UI scaler for all spacing so it scales with screen
    if ui_scaler:
        header_height = ui_scaler.header_height()
        header_top_margin = ui_scaler.header_top_margin()
        content_margin = ui_scaler.content_margin()
        section_spacing = ui_scaler.margin("small")
        line_spacing = ui_scaler.margin("small")
        text_spacing = ui_scaler.margin("small")
    else:
        header_height = config_module.HEADER_HEIGHT
        header_top_margin = screen_height // 20
        content_margin = max(8, screen_width // 30)
        section_spacing = max(4, screen_height // 60)
        line_spacing = max(4, screen_height // 60)
        text_spacing = max(4, screen_height // 60)
    
    # Debug logging for system info view layout
    global _system_info_logged
    if ui_scaler and ui_scaler.debug_mode and not _system_info_logged:
        logger.info(f"🎨 SystemInfoView: screen={screen_width}x{screen_height}, spacing: section={section_spacing}px, line={line_spacing}px, text={text_spacing}px")
        _system_info_logged = True

    # Draw header within safe area so it is not cut off by curved bezel
    safe_rect = ui_scaler.get_safe_area_rect() if (ui_scaler and ui_scaler.safe_area_enabled) else pygame.Rect(0, 0, screen_width, screen_height)
    header_rect = pygame.Rect(safe_rect.left, safe_rect.top + header_top_margin, safe_rect.width, header_height)

    _draw_animated_header(screen, header_rect, app_state, fonts, config_module, current_time)

    font_medium = fonts["medium"]
    font_small = fonts["small"]

    # Use standardized spacing throughout
    content_y = header_rect.bottom + section_spacing

    # Section 1: Time and Date with standardized spacing
    time_rect = pygame.Rect(content_margin, content_y, screen_width - (content_margin * 2), font_medium.get_height())
    
    # Get time data
    clock_data = sensor_values.get(app_config.SENSOR_CLOCK, {})
    time_text = clock_data.get("text", "N/A")
    date_text = clock_data.get("note", "")
    
    # Draw time with subtle glow effect
    _draw_glowing_text(screen, time_text, font_medium, config_module.Theme.FOREGROUND, 
                      (time_rect.left, time_rect.top), current_time)
    
    # Draw date with standardized spacing
    date_y = time_rect.bottom + text_spacing
    if date_text:
        date_surface = font_small.render(date_text, True, config_module.Theme.ACCENT)
        screen.blit(date_surface, (time_rect.left, date_y))

    # Section 2: Network Status (reserve space for date line only if date is shown)
    network_section_y = date_y + (font_small.get_height() if date_text else 0) + section_spacing
    network_rect = pygame.Rect(content_margin, network_section_y, screen_width - (content_margin * 2),
                               font_small.get_height() * 2 + line_spacing)
    
    _draw_network_status_with_indicators(screen, network_rect, sensor_values, fonts, config_module, current_time, line_spacing, ui_scaler)

    # Section 3: Rotating Status Bar
    status_bar_y = network_rect.bottom + section_spacing
    status_bar_height = ui_scaler.scale(22) if ui_scaler else 22
    status_bar_rect = pygame.Rect(content_margin, status_bar_y, screen_width - (content_margin * 2), status_bar_height)
    
    _draw_rotating_status_bar(screen, status_bar_rect, sensor_values, fonts, config_module, current_time, ui_scaler)
    
    # Section 4: Dots + readout under status bar (stay within safe area when enabled)
    animation_area_y = status_bar_rect.bottom + section_spacing
    content_bottom = safe_rect.bottom - content_margin
    animation_area_height = content_bottom - animation_area_y
    content_width = safe_rect.right - 2 * content_margin
    animation_rect = pygame.Rect(content_margin, animation_area_y, max(0, content_width), max(0, animation_area_height))

    min_bottom_height = ui_scaler.scale(22) if ui_scaler else 22
    if animation_area_height >= min_bottom_height and animation_rect.width > 0:
        _draw_tricorder_data_analysis(screen, animation_rect, sensor_values, fonts, config_module, current_time, ui_scaler)

def _draw_animated_header(screen, header_rect, app_state, fonts, config_module, current_time):
    """Draw header with subtle animation effects."""
    pygame.draw.rect(screen, config_module.Theme.BACKGROUND, header_rect)

    font_medium = fonts['medium']
    header_text_str = "System Status"
    if app_state.is_frozen:
        header_text_str += " [FROZEN]"
    
    header_text_color = config_module.Theme.ACCENT if not app_state.is_frozen else config_module.Theme.FROZEN_INDICATOR
    
    # Add subtle pulsing effect to frozen indicator
    if app_state.is_frozen:
        pulse = (current_time * 2.0) % 2.0
        pulse_alpha = 0.7 + 0.3 * (0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate(pulse * 180).x)
        header_text_color = tuple(int(c * pulse_alpha) for c in header_text_color)
    
    header_text = font_medium.render(header_text_str, True, header_text_color)
    text_pos = (header_rect.centerx - header_text.get_width() // 2, header_rect.centery - header_text.get_height() // 2)
    screen.blit(header_text, text_pos)

def _draw_glowing_text(screen, text, font, color, pos, current_time):
    """Draw text with subtle glow effect."""
    # Main text
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, pos)
    
    # Subtle glow effect (very dim)
    glow_intensity = 0.3 + 0.1 * (0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate(current_time * 60).x)
    glow_color = tuple(int(c * glow_intensity * 0.3) for c in color)
    
    # Draw glow slightly offset
    for offset in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        glow_surface = font.render(text, True, glow_color)
        glow_pos = (pos[0] + offset[0], pos[1] + offset[1])
        screen.blit(glow_surface, glow_pos)
    
    # Draw main text on top
    screen.blit(text_surface, pos)

def _draw_network_status_with_indicators(screen, network_rect, sensor_values, fonts, config_module, current_time, line_spacing, ui_scaler=None):
    """Draw network status with animated status indicators; uses ui_scaler for sizes when provided."""
    font_small = fonts['small']
    indicator_size = ui_scaler.scale(4) if ui_scaler else 4
    indicator_margin = ui_scaler.scale(12) if ui_scaler else 12
    
    # WiFi Status with indicator
    wifi_status_data = sensor_values.get(app_config.INFO_WIFI_STATUS, {})
    wifi_ssid_data = sensor_values.get(app_config.INFO_WIFI_SSID, {})
    wifi_status = wifi_status_data.get("text", "N/A")
    wifi_ssid = wifi_ssid_data.get("text", "N/A")
    
    wifi_color = config_module.Palette.GREEN if wifi_status.lower() in ["connected", "online"] else config_module.Palette.RED_ALERT
    wifi_text = f"WiFi: {wifi_status}"
    if wifi_status.lower() in ["connected", "online"] and wifi_ssid != "N/A" and wifi_ssid != "Connected":
        wifi_text += f" - {wifi_ssid}"
    
    # Draw WiFi status with standardized positioning
    wifi_surface = font_small.render(wifi_text, True, wifi_color)
    wifi_pos = (network_rect.left + indicator_margin, network_rect.top)
    screen.blit(wifi_surface, wifi_pos)
    
    # WiFi status indicator (pulsing dot)
    if wifi_status.lower() in ["connected", "online"]:
        pulse = (current_time * 1.5) % 2.0
        pulse_alpha = 0.5 + 0.5 * (0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate(pulse * 180).x)
        indicator_color = tuple(int(c * pulse_alpha) for c in config_module.Palette.GREEN)
    else:
        indicator_color = config_module.Palette.RED_ALERT
    
    wifi_indicator_pos = (network_rect.left + indicator_size + 2, network_rect.top + font_small.get_height() // 2)
    pygame.draw.circle(screen, indicator_color, wifi_indicator_pos, indicator_size)
    
    # Bluetooth Status with indicator and standardized spacing
    bluetooth_status_data = sensor_values.get(app_config.INFO_BLUETOOTH_STATUS, {})
    bluetooth_device_data = sensor_values.get(app_config.INFO_BLUETOOTH_DEVICE, {})
    bluetooth_status = bluetooth_status_data.get("text", "N/A")
    bluetooth_device = bluetooth_device_data.get("text", "")
    
    if bluetooth_status.lower() == "connected":
        bluetooth_color = config_module.Palette.GREEN
    elif bluetooth_status.lower() in ["on", "available"]:
        bluetooth_color = config_module.Palette.ENGINEERING_GOLD
    else:
        bluetooth_color = config_module.Palette.RED_ALERT
    
    bluetooth_text = f"Bluetooth: {bluetooth_status}"
    if bluetooth_device and bluetooth_device not in ["N/A", "Not Available", "Windows", "Unsupported"]:
        bluetooth_text += f" - {bluetooth_device}"
    
    # Draw Bluetooth status with standardized spacing
    bluetooth_y = network_rect.top + font_small.get_height() + line_spacing
    bluetooth_surface = font_small.render(bluetooth_text, True, bluetooth_color)
    bluetooth_pos = (network_rect.left + indicator_margin, bluetooth_y)
    screen.blit(bluetooth_surface, bluetooth_pos)
    
    # Bluetooth status indicator
    bluetooth_indicator_pos = (network_rect.left + indicator_size + 2, bluetooth_y + font_small.get_height() // 2)
    pygame.draw.circle(screen, bluetooth_color, bluetooth_indicator_pos, indicator_size)

def _draw_rotating_status_bar(screen, status_bar_rect, sensor_values, fonts, config_module, current_time, ui_scaler):
    """Draw a single status bar that rotates through CPU, RAM, and Disk (LCARS-style)."""
    rotation_interval = 4.0
    rotation_index = int(current_time / rotation_interval) % 3

    # CPU, RAM, Disk only (battery and voltage removed)
    status_bar_configs = [
        {
            "sensor_key": app_config.SENSOR_CPU_USAGE,
            "label": "CPU",
            "units": "%",
            "green_range": (0, 60),
            "yellow_range": (60, 85),
            "max_val": 100,
        },
        {
            "sensor_key": app_config.SENSOR_MEMORY_USAGE,
            "label": "RAM",
            "units": "%",
            "green_range": (0, 60),
            "yellow_range": (60, 85),
            "max_val": 100,
        },
        {
            "sensor_key": app_config.SENSOR_DISK_USAGE,
            "label": "DISK",
            "units": "%",
            "green_range": (0, 60),
            "yellow_range": (60, 85),
            "max_val": 100,
        },
    ]
    
    current_config = status_bar_configs[rotation_index]
    
    # Get sensor data
    sensor_data = sensor_values.get(current_config["sensor_key"], {})
    sensor_value = sensor_data.get("value")
    
    # Draw transition effect
    transition_progress = (current_time % rotation_interval) / rotation_interval
    if transition_progress > 0.9:  # Last 10% of cycle - fade out
        fade_alpha = (1.0 - transition_progress) / 0.1
    elif transition_progress < 0.1:  # First 10% of cycle - fade in
        fade_alpha = transition_progress / 0.1
    else:
        fade_alpha = 1.0
    
    # Draw the status bar with fade effect
    try:
        status_bar = HorizontalStatusBar(
            screen=screen,
            rect=status_bar_rect,
            label=current_config["label"],
            units=current_config["units"],
            min_val=0,
            max_val=current_config["max_val"],
            green_range=current_config["green_range"],
            yellow_range=current_config["yellow_range"],
            fonts=fonts,
            config_module=config_module,
            ui_scaler=ui_scaler
        )
        
        # Apply fade effect by temporarily modifying the screen
        if fade_alpha < 1.0:
            # Create a temporary surface for fading
            temp_surface = pygame.Surface(status_bar_rect.size, pygame.SRCALPHA)
            temp_surface.fill((0, 0, 0, 0))
            
            # Draw status bar to temp surface
            temp_bar = HorizontalStatusBar(
                screen=temp_surface,
                rect=pygame.Rect(0, 0, status_bar_rect.width, status_bar_rect.height),
                label=current_config["label"],
                units=current_config["units"],
                min_val=0,
                max_val=current_config["max_val"],
                green_range=current_config["green_range"],
                yellow_range=current_config["yellow_range"],
                fonts=fonts,
                config_module=config_module,
                ui_scaler=ui_scaler
            )
            temp_bar.draw(sensor_value)
            
            # Apply alpha and blit to main screen
            temp_surface.set_alpha(int(255 * fade_alpha))
            screen.blit(temp_surface, status_bar_rect.topleft)
        else:
            status_bar.draw(sensor_value)
            
    except Exception as e:
        logger.error(f"Error drawing rotating status bar: {e}", exc_info=True)
        fallback_text = f"{current_config['label']}: {sensor_value if sensor_value is not None else 'N/A'}"
        fallback_surface = fonts["small"].render(fallback_text, True, config_module.Theme.FOREGROUND)
        screen.blit(fallback_surface, status_bar_rect.topleft)

def _draw_tricorder_data_analysis(screen, animation_rect, sensor_values, fonts, config_module, current_time, ui_scaler):
    """Dots then readout strip; readout is always drawn and kept visible."""
    if animation_rect.height <= 0 or animation_rect.width <= 0:
        return

    line_h = fonts["small"].get_height()
    readout_pad = ui_scaler.margin("small") * 2 if ui_scaler else 4
    readout_strip_height = min(animation_rect.height, line_h + readout_pad)
    readout_strip_height = max(readout_strip_height, line_h + 2)
    grid_height = max(0, animation_rect.height - readout_strip_height)
    grid_rect = pygame.Rect(
        animation_rect.left,
        animation_rect.top,
        animation_rect.width,
        grid_height,
    )
    readout_rect = pygame.Rect(
        animation_rect.left,
        animation_rect.bottom - readout_strip_height,
        animation_rect.width,
        readout_strip_height,
    )

    min_grid_height = ui_scaler.scale(12) if ui_scaler else 12
    if grid_rect.height > min_grid_height:
        _draw_data_stream_grid(screen, grid_rect, current_time, config_module, ui_scaler)
    _draw_system_readout_text(screen, readout_rect, sensor_values, fonts, config_module, current_time, ui_scaler)

def _draw_data_stream_grid(screen, rect, current_time, config_module, ui_scaler=None):
    """Grid of flowing dots; grid_spacing and dot_size from ui_scaler when provided."""
    grid_spacing = ui_scaler.scale(16) if ui_scaler else 16
    dot_size = max(1, ui_scaler.scale(3) if ui_scaler else 3)

    cols = rect.width // grid_spacing if grid_spacing else 1
    rows = max(1, rect.height // grid_spacing) if grid_spacing else 1

    for row in range(rows):
        for col in range(cols):
            offset = (row * cols + col) * 0.3
            flow_progress = (current_time * 1.8 + offset) % 4.0

            if flow_progress < 2.5:
                dot_x = rect.left + col * grid_spacing + grid_spacing // 2
                dot_y = rect.top + row * grid_spacing + grid_spacing // 2
                
                # Improved fade in/out with flickering effect like sensor view
                if flow_progress < 0.8:
                    # Fade in
                    alpha = flow_progress / 0.8
                elif flow_progress < 1.8:
                    # Stay bright with slight flicker
                    base_alpha = 1.0
                    flicker = 0.1 * (0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate(current_time * 300 + offset * 100).x)
                    alpha = base_alpha - flicker
                else:
                    # Fade out
                    alpha = (2.5 - flow_progress) / 0.7
                
                # Use viking blue color like sensor view for consistency
                viking_blue = config_module.Palette.VIKING_BLUE
                dot_color = tuple(min(255, int(c * alpha)) for c in viking_blue)
                
                # Only draw if visible enough
                if alpha > 0.15:
                    pygame.draw.circle(screen, dot_color, (dot_x, dot_y), dot_size)

def _draw_system_readout_text(screen, readout_rect, sensor_values, fonts, config_module, current_time, ui_scaler=None):
    """Draw readout strip: opaque dark background, rotating status text (always visible)."""
    if readout_rect.height <= 0 or readout_rect.width <= 0:
        return
    font_small = fonts["small"]
    if readout_rect.height < font_small.get_height():
        return

    # Opaque dark strip so readout is always visible
    strip_bg = config_module.Palette.DARK_GREY
    s = pygame.Surface((readout_rect.width, readout_rect.height))
    s.fill(strip_bg)
    screen.blit(s, readout_rect.topleft)

    readout_interval = 4.0
    readout_index = int(current_time / readout_interval) % 4
    readout_texts = [
        "SYSTEM ANALYSIS: NOMINAL",
        "DATA PROCESSING: ACTIVE",
        "SENSOR ARRAY: ONLINE",
        "TRICORDER READY",
    ]
    readout_text = readout_texts[readout_index]

    transition_progress = (current_time % readout_interval) / readout_interval
    if transition_progress > 0.9:
        alpha = (1.0 - transition_progress) / 0.1
    elif transition_progress < 0.1:
        alpha = transition_progress / 0.1
    else:
        alpha = 1.0 - 0.08 * (0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate(current_time * 120).x)

    if alpha > 0.1:
        text_color = tuple(int(c * alpha) for c in config_module.Theme.FOREGROUND)
        text_surface = font_small.render(readout_text, True, text_color)
        text_x = readout_rect.centerx - text_surface.get_width() // 2
        text_y = readout_rect.centery - text_surface.get_height() // 2
        screen.blit(text_surface, (text_x, text_y)) 