# --- ui/views/system_info_view.py ---
# Handles rendering of the redesigned system information screen

import pygame
import logging
from ui.components.horizontal_status_bar import HorizontalStatusBar
from ui.components.text_display import render_footer
import config as app_config # For theme colors and constants

logger = logging.getLogger(__name__)

def draw_system_info_view(screen, app_state, sensor_values, fonts, config_module, target_rect=None, draw_footer=False):
    """
    Draw the redesigned system information screen with horizontal status bars.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state (for frozen status)
        sensor_values (dict): Dictionary containing formatted system values
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
        target_rect (pygame.Rect, optional): The rectangle to draw within. Defaults to the full screen.
        draw_footer (bool): Whether to draw the footer. Defaults to False (disabled).
    """
    screen.fill(config_module.Theme.BACKGROUND)
    
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Header - use proportional spacing like list_menu_base.py
    header_top_margin = screen_height // 20
    header_height = config_module.HEADER_HEIGHT
    header_rect = pygame.Rect(0, header_top_margin, screen_width, header_height)
    pygame.draw.rect(screen, config_module.Theme.BACKGROUND, header_rect)

    font_medium = fonts['medium']
    font_small = fonts['small']
    
    header_text_str = "System Status"
    if app_state.is_frozen:
        header_text_str += " [FROZEN]"
    header_text_color = config_module.Theme.ACCENT if not app_state.is_frozen else config_module.Theme.FROZEN_INDICATOR
    header_text = font_medium.render(header_text_str, True, header_text_color)
    screen.blit(header_text, (header_rect.centerx - header_text.get_width() // 2, header_rect.centery - header_text.get_height() // 2))

    # Use proportional margins based on screen size
    content_margin = max(8, screen_width // 30)  # 3-4% of screen width
    content_y = header_rect.bottom + content_margin
    
    # Section 1: Time and Date - fixed height like other views
    time_section_height = 40
    time_rect = pygame.Rect(content_margin, content_y, screen_width - (content_margin * 2), time_section_height)
    
    # Get time data
    clock_data = sensor_values.get(app_config.SENSOR_CLOCK, {})
    time_text = clock_data.get("text", "N/A")
    date_text = clock_data.get("note", "")
    
    # Draw time (larger)
    time_surface = font_medium.render(time_text, True, config_module.Theme.FOREGROUND)
    time_pos = (time_rect.left, time_rect.top)
    screen.blit(time_surface, time_pos)
    
    # Draw date (smaller, below time)
    if date_text:
        date_surface = font_small.render(date_text, True, config_module.Theme.ACCENT)
        date_pos = (time_rect.left, time_rect.top + time_surface.get_height() + 5)
        screen.blit(date_surface, date_pos)

    # Section 2: Network Status - fixed height like other views
    network_section_y = time_rect.bottom + content_margin
    network_section_height = 50
    network_rect = pygame.Rect(content_margin, network_section_y, screen_width - (content_margin * 2), network_section_height)
    
    # WiFi Status
    wifi_status_data = sensor_values.get(app_config.INFO_WIFI_STATUS, {})
    wifi_ssid_data = sensor_values.get(app_config.INFO_WIFI_SSID, {})
    wifi_status = wifi_status_data.get("text", "N/A")
    wifi_ssid = wifi_ssid_data.get("text", "N/A")
    
    wifi_color = config_module.Palette.GREEN if wifi_status.lower() in ["connected", "online"] else config_module.Palette.RED_ALERT
    wifi_text = f"WiFi: {wifi_status}"
    if wifi_status.lower() in ["connected", "online"] and wifi_ssid != "N/A" and wifi_ssid != "Connected":
        wifi_text += f" - {wifi_ssid}"
    
    wifi_surface = font_small.render(wifi_text, True, wifi_color)
    wifi_pos = (network_rect.left, network_rect.top)
    screen.blit(wifi_surface, wifi_pos)
    
    # Bluetooth Status
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
    
    bluetooth_surface = font_small.render(bluetooth_text, True, bluetooth_color)
    bluetooth_pos = (network_rect.left, network_rect.top + wifi_surface.get_height() + 10)
    screen.blit(bluetooth_surface, bluetooth_pos)

    # Section 3: System Status Bars - fixed position and spacing
    status_bars_y = network_rect.bottom + content_margin
    available_status_height = screen_height - status_bars_y - content_margin  # Reserve bottom margin
    status_bars_rect = pygame.Rect(content_margin, status_bars_y, screen_width - (content_margin * 2), available_status_height)
    
    # Define status bar configurations
    status_bar_configs = []
    
    # CPU Status Bar
    cpu_data = sensor_values.get(app_config.SENSOR_CPU_USAGE, {})
    cpu_value = cpu_data.get("value")
    if cpu_value is not None:
        status_bar_configs.append({
            "label": "CPU",
            "value": cpu_value,
            "units": "%",
            "green_range": (0, 60),
            "yellow_range": (60, 85)
        })
    
    # Memory Status Bar
    memory_data = sensor_values.get(app_config.SENSOR_MEMORY_USAGE, {})
    memory_value = memory_data.get("value")
    if memory_value is not None:
        status_bar_configs.append({
            "label": "Memory",
            "value": memory_value,
            "units": "%",
            "green_range": (0, 60),
            "yellow_range": (60, 85)
        })
    
    # Voltage Status Bar (always show)
    voltage_data = sensor_values.get(app_config.SENSOR_VOLTAGE, {})
    voltage_value = voltage_data.get("value")
    status_bar_configs.append({
        "label": "Voltage",
        "value": voltage_value,
        "units": "V",
        "green_range": (4.8, 5.2),  # Normal USB voltage range
        "yellow_range": (4.5, 4.8)  # Warning range
    })
    
    # Battery Status Bar (always show)
    battery_data = sensor_values.get(app_config.SENSOR_BATTERY, {})
    battery_value = battery_data.get("value")
    status_bar_configs.append({
        "label": "Battery",
        "value": battery_value,
        "units": "%",
        "green_range": (30, 100),
        "yellow_range": (15, 30)
    })
    
    # Draw status bars with simple fixed spacing like other views
    if status_bar_configs:
        # Use simple fixed dimensions like other views
        bar_height = 25  # Fixed height like other views
        bar_spacing = 30  # Fixed spacing like other views
        
        current_y = status_bars_rect.top
        
        for config_dict in status_bar_configs:
            bar_rect = pygame.Rect(status_bars_rect.left, current_y, status_bars_rect.width, bar_height)
            
            try:
                status_bar = HorizontalStatusBar(
                    screen=screen,
                    rect=bar_rect,
                    label=config_dict["label"],
                    units=config_dict["units"],
                    min_val=0,
                    max_val=100 if config_dict["units"] == "%" else 6.0,  # 6V max for voltage
                    green_range=config_dict["green_range"],
                    yellow_range=config_dict["yellow_range"],
                    fonts=fonts,
                    config_module=config_module
                )
                status_bar.draw(config_dict["value"])
            except Exception as e:
                logger.error(f"Error drawing status bar for {config_dict['label']}: {e}", exc_info=True)
            
            current_y += bar_height + bar_spacing
    else:
        # No status bars available, show message
        fallback_text = "No system status data available"
        fallback_surface = font_small.render(fallback_text, True, config_module.Theme.ALERT)
        fallback_pos = (status_bars_rect.left, status_bars_rect.top + (status_bars_rect.height // 4))
        screen.blit(fallback_surface, fallback_pos)

    # Footer is completely removed - no drawing at all 