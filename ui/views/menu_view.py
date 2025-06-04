"""
Menu view that displays the main menu.
"""

import pygame
import logging
import platform
import psutil
from datetime import datetime
from models.menu import get_menu_items
from data import system_info
from ui.components.text_display import render_footer
from models.app_state import STATE_MENU, STATE_DASHBOARD, STATE_SENSOR_VIEW, STATE_SYSTEM_INFO, STATE_SETTINGS
from config import version

logger = logging.getLogger(__name__)

def _get_footer_content(config):
    """
    Generate footer content with stardate and build number.
    
    Args:
        config (module): Configuration module
        
    Returns:
        str: Footer content string
    """
    try:
        # Calculate TNG-era stardate
        # TNG system: First digit 4 (24th century), then year progression
        # For real world: calculate as if we're in 24th century
        now = datetime.now()
        
        # Base stardate calculation - TNG style
        # Years since 2323 (start of TNG era) + fractional day
        years_since_2323 = now.year - 2323
        day_of_year = now.timetuple().tm_yday
        total_days_in_year = 366 if now.year % 4 == 0 else 365
        
        # Calculate fractional year progress
        year_progress = day_of_year / total_days_in_year
        
        # TNG stardate format: 4XXXX.X
        # Where XXXX represents years and progress, X represents fractional day
        stardate_base = 40000 + (years_since_2323 * 1000) + int(year_progress * 1000)
        
        # Fractional day (0.1 = 2.4 hours, so 0.5 = noon)
        fractional_day = (now.hour * 60 + now.minute) / 1440.0
        
        stardate = stardate_base + fractional_day
        
        # Get build number from version module
        build_number = version.get_build_number()
        
        return f"Stardate {stardate:.1f} | {build_number}"
        
    except Exception as e:
        logger.error(f"Error generating footer content: {e}")
        return "Stardate 47457.1 | ALPHA 0.0.1"

def draw_menu_view(screen, app_state, sensor_values, sensor_history, fonts, config):
    """
    Draw the menu view.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        sensor_values (dict): Dictionary of current sensor values
        sensor_history (ReadingHistory): Sensor reading history
        fonts (dict): Dictionary of loaded fonts
        config (module): Configuration module
        
    Returns:
        bool: True if rendering was successful
    """
    # Get menu items
    menu_items = get_menu_items()
    selected_index = app_state.menu_index
    
    # Clear the screen
    screen.fill(config.COLOR_BACKGROUND)
    
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Create sidebar dimensions - make it about 1/4 of the screen width
    sidebar_width = min(screen_width // 4, 150)
    
    # Draw the sidebar
    _draw_sidebar(screen, sidebar_width, screen_height, menu_items, selected_index, fonts, config)
    
    # Draw the main content area
    main_content_rect = pygame.Rect(sidebar_width, 0, screen_width - sidebar_width, screen_height)
    _draw_main_content(screen, main_content_rect, fonts, config, sensor_values)
    
    # Draw footer with stardate and build
    footer_content = _get_footer_content(config)
    render_footer(
        screen,
        footer_content,
        fonts,
        config.COLOR_FOREGROUND,
        screen_width,
        screen_height
    )
    
    # Process input events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False  # Signal to quit
            
        if event.type == pygame.KEYDOWN:
            key = event.key
            key_name = pygame.key.name(key).lower()
            
            if key == pygame.K_a or key == pygame.K_LEFT or key_name == 'a':
                # Previous item
                app_state.menu_index = (app_state.menu_index - 1) % len(menu_items)
                logger.debug(f"Menu navigation: PREV -> {menu_items[app_state.menu_index].name}")
                return True
                
            elif key == pygame.K_d or key == pygame.K_RIGHT or key_name == 'd':
                # Next item
                app_state.menu_index = (app_state.menu_index + 1) % len(menu_items)
                logger.debug(f"Menu navigation: NEXT -> {menu_items[app_state.menu_index].name}")
                return True
                
            elif key == pygame.K_RETURN or key == pygame.K_SPACE:
                # Select item
                selected_item = menu_items[app_state.menu_index]
                logger.debug(f"Selected menu item: {selected_item.name}")
                
                # Set appropriate state based on selection
                if selected_item.view_id == "sensor_view":
                    app_state.current_sensor = selected_item.sensor
                    app_state.set_state(STATE_SENSOR_VIEW)
                elif selected_item.view_id == "system_info_view":
                    app_state.set_state(STATE_SYSTEM_INFO)
                elif selected_item.view_id == "all_sensors_view":
                    app_state.set_state(STATE_DASHBOARD)
                elif selected_item.view_id == "settings_view":
                    app_state.set_state(STATE_SETTINGS)
                return True
    
    return True

def _draw_sidebar(screen, sidebar_width, screen_height, menu_items, selected_index, fonts, config):
    """
    Draw the sidebar with menu items.
    
    Args:
        screen (pygame.Surface): The screen to render on
        sidebar_width (int): Width of the sidebar
        screen_height (int): Height of the screen
        menu_items (list): List of menu items
        selected_index (int): Index of the selected menu item
        fonts (dict): Dictionary of loaded fonts
        config (module): Configuration module
    """
    # Calculate item height
    item_height = screen_height // len(menu_items)
    
    for i, item in enumerate(menu_items):
        item_rect = pygame.Rect(
            0,
            i * item_height,
            sidebar_width,
            item_height
        )
        
        # Get color for this item
        if hasattr(config, item.color_key):
            color = getattr(config, item.color_key)
        else:
            color = config.COLOR_FOREGROUND
            
        # Draw background
        pygame.draw.rect(screen, color, item_rect)
        
        # Draw text
        font = fonts['small']
        text_surface = font.render(item.name, True, (255, 255, 255))
        text_pos = (item_rect.left + 10, item_rect.centery - text_surface.get_height() // 2)
        screen.blit(text_surface, text_pos)
        
        # Draw selection indicator
        if i == selected_index:
            border_width = 3
            selection_rect = pygame.Rect(
                item_rect.left, 
                item_rect.top, 
                item_rect.width - border_width, 
                item_rect.height - border_width
            )
            pygame.draw.rect(screen, (255, 255, 255), selection_rect, border_width)

def _draw_main_content(screen, content_rect, fonts, config, sensor_values):
    """
    Draw the main content area with system information.
    
    Args:
        screen (pygame.Surface): The screen to render on
        content_rect (pygame.Rect): Rectangle for the main content
        fonts (dict): Dictionary of loaded fonts
        config (module): Configuration module
        sensor_values (dict): Dictionary of current sensor values
    """
    # Draw a header
    header_height = 30
    header_rect = pygame.Rect(content_rect.left, content_rect.top, content_rect.width, header_height)
    pygame.draw.rect(screen, config.COLOR_BACKGROUND, header_rect)
    
    # Draw system information title in the header
    font = fonts['small']
    header_text = font.render("System Information", True, config.COLOR_FOREGROUND)
    screen.blit(header_text, (content_rect.left + 20, header_rect.centery - header_text.get_height() // 2))
    
    # Get system information
    system_info_data = _get_system_info(config, sensor_values)
    
    # Draw system information
    font = fonts['small']
    y_offset = content_rect.top + header_height + 20
    line_height = font.get_height() + 5
    
    for label, value in system_info_data:
        text = f"{label}: {value}"
        text_surface = font.render(text, True, config.COLOR_FOREGROUND)
        screen.blit(text_surface, (content_rect.left + 20, y_offset))
        y_offset += line_height

def _get_system_info(config, sensor_values):
    """
    Get system information.
    
    Args:
        config (module): Configuration module
        sensor_values (dict): Dictionary of current sensor values
        
    Returns:
        list: List of (label, value) tuples with system information
    """
    info = []
    
    # OS Information
    info.append(("System", platform.system()))
    info.append(("Python Version", platform.python_version()))
    
    # Network Information
    wifi_status, wifi_info = system_info.get_wifi_status()
    cellular_status, cellular_info = system_info.get_cellular_status()
    
    info.append(("WiFi", f"{wifi_status} {wifi_info}"))
    info.append(("Cellular", f"{cellular_status} {cellular_info}"))
    
    # CPU Information
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        info.append(("CPU Usage", f"{cpu_percent}%"))
    except Exception as e:
        logger.error(f"Error getting CPU usage: {e}")
        info.append(("CPU Usage", "N/A"))
    
    # Memory Information
    try:
        memory = psutil.virtual_memory()
        memory_used_gb = memory.used / (1024 ** 3)
        memory_total_gb = memory.total / (1024 ** 3)
        info.append(("Memory Usage", f"{memory_used_gb:.1f}GB / {memory_total_gb:.1f}GB"))
    except Exception as e:
        logger.error(f"Error getting memory usage: {e}")
        info.append(("Memory Usage", "N/A"))
    
    # Disk Information
    try:
        disk = psutil.disk_usage('/')
        disk_used_gb = disk.used / (1024 ** 3)
        disk_total_gb = disk.total / (1024 ** 3)
        info.append(("Disk Usage", f"{disk_used_gb:.1f}GB / {disk_total_gb:.1f}GB"))
    except Exception as e:
        logger.error(f"Error getting disk usage: {e}")
        info.append(("Disk Usage", "N/A"))
    
    # Current Time
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    current_date = now.strftime("%Y-%m-%d")
    info.append(("Time", current_time))
    info.append(("Date", current_date))
    
    # Get sensor information if available
    try:
        for sensor_name in config.SENSOR_MODES:
            if sensor_name == "CLOCK":
                continue
                
            if sensor_name in sensor_values:
                value = sensor_values[sensor_name]
                if value and len(value) >= 2:
                    display_val, unit, _ = value
                    info.append((sensor_name, f"{display_val} {unit}"))
    except Exception as e:
        logger.error(f"Error getting sensor information: {e}")
        for sensor_name in config.SENSOR_MODES:
            if sensor_name == "CLOCK":
                continue
            info.append((sensor_name, "N/A"))
        
    return info

# For compatibility with the display_manager
class MenuView:
    def __init__(self, app_state, screen, fonts, config):
        self.app_state = app_state
        self.screen = screen
        self.fonts = fonts
        self.config = config
        
    def render(self):
        return draw_menu_view(self.screen, self.app_state, {}, None, self.fonts, self.config) 