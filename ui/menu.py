# --- ui/menu.py ---
# Handles rendering of the menu system with sidebar and main content area

import pygame
import logging
from ui.components.ui_elements import draw_panel
from ui.components.text_display import render_footer
from data.system_info import get_cpu_usage, get_memory_usage, get_disk_usage, get_current_time

logger = logging.getLogger(__name__)

# Define menu categories with config color references
MENU_CATEGORIES = [
    {"name": "System Info", "color_key": "COLOR_SIDEBAR_SYSTEM"},
    {"name": "Temperature", "color_key": "COLOR_SIDEBAR_TEMP"},
    {"name": "Humidity", "color_key": "COLOR_SIDEBAR_HUMID"},
    {"name": "Pressure", "color_key": "COLOR_SIDEBAR_PRESS"},
    {"name": "Orientation", "color_key": "COLOR_SIDEBAR_ORIENT"},
    {"name": "Acceleration", "color_key": "COLOR_SIDEBAR_ACCEL"},
    {"name": "All Sensors", "color_key": "COLOR_SIDEBAR_ALL"},
    {"name": "Settings", "color_key": "COLOR_SIDEBAR_SETTINGS"}
]

def draw_menu_screen(screen, app_state, fonts, config):
    """
    Draw the menu screen with sidebar and main content area.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config (module): Configuration module
        
    Returns:
        None
    """
    # Clear screen with background color
    screen.fill(config.COLOR_BACKGROUND)
    
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Only show sidebar when in MENU state
    if app_state.current_state == "MENU":
        # Create sidebar dimensions - make it about 1/4 of the screen width
        sidebar_width = min(screen_width // 4, 150)
        
        # Get currently selected menu item
        selected_index = app_state.get_current_menu_index()
        
        # Draw the sidebar 
        sidebar_rect = pygame.Rect(0, 0, sidebar_width, screen_height)
        _draw_sidebar(screen, sidebar_rect, selected_index, fonts, config)
        
        # Draw the main content area with System Info
        main_content_rect = pygame.Rect(sidebar_width, 0, screen_width - sidebar_width, screen_height)
        
        # Draw system info
        _draw_system_info(screen, main_content_rect, fonts, config)
        
        # Draw footer
        render_footer(
            screen,
            "< PREV = A | SELECT = Enter | NEXT = D >",
            fonts,
            config.COLOR_FOREGROUND,
            screen_width,
            screen_height
        )
    elif app_state.current_state == "SYSTEM":
        # System Info view shows system information
        _draw_system_info(screen, pygame.Rect(0, 0, screen_width, screen_height), fonts, config)
        
        # Draw footer
        render_footer(
            screen,
            "< MENU | REFRESH | MENU >",
            fonts,
            config.COLOR_FOREGROUND,
            screen_width,
            screen_height
        )
    elif app_state.current_state == "SETTINGS":
        # Settings view shows settings options
        _draw_settings(screen, pygame.Rect(0, 0, screen_width, screen_height), fonts, config)
        
        # Draw footer
        render_footer(
            screen,
            "< MENU | APPLY | MENU >",
            fonts,
            config.COLOR_FOREGROUND,
            screen_width,
            screen_height
        )
    else:
        # When in other states, we shouldn't be calling draw_menu_screen
        # This is handled by display_manager.py now
        logger.error(f"draw_menu_screen called with invalid state: {app_state.current_state}")
        error_text = fonts['medium'].render("Error: Invalid state for menu", True, config.COLOR_ALERT)
        screen.blit(error_text, (screen_width//2 - error_text.get_width()//2, screen_height//2))

def _draw_sidebar(screen, rect, selected_index, fonts, config):
    """
    Draw the sidebar with menu categories.
    """
    # Calculate item height
    item_height = rect.height // len(MENU_CATEGORIES)
    
    # Draw each menu category
    for i, category in enumerate(MENU_CATEGORIES):
        item_rect = pygame.Rect(
            rect.left,
            rect.top + (i * item_height),
            rect.width,
            item_height
        )
        
        # Draw the background
        color = getattr(config, category["color_key"])
        pygame.draw.rect(screen, color, item_rect)
        
        # Draw the category name
        font = fonts['small']
        text_surface = font.render(category["name"], True, (255, 255, 255))
        text_pos = (item_rect.left + 10, item_rect.centery - text_surface.get_height() // 2)
        screen.blit(text_surface, text_pos)
        
        # Draw selection indicator if this item is selected
        if i == selected_index:
            # Draw a white border or indicator
            border_width = 3
            selection_rect = pygame.Rect(
                item_rect.left, 
                item_rect.top, 
                item_rect.width - border_width, 
                item_rect.height - border_width
            )
            pygame.draw.rect(screen, (255, 255, 255), selection_rect, border_width)

def _draw_system_info(screen, rect, fonts, config):
    """
    Draw the system information content.
    """
    # Draw header
    header_height = 30
    header_rect = pygame.Rect(rect.left, rect.top, rect.width, header_height)
    pygame.draw.rect(screen, config.COLOR_BACKGROUND, header_rect)
    
    # Draw "System Info" in the header
    font = fonts['small']
    header_text = font.render("System Information", True, config.COLOR_FOREGROUND)
    screen.blit(header_text, (rect.left + 20, header_rect.centery - header_text.get_height() // 2))
    
    # Calculate content area
    content_y = rect.top + header_height + 5
    content_height = rect.height - header_height - 10
    
    # Determine if we're in a small space
    small_space = rect.height < 400
    
    # Network information section (top)
    network_height = content_height // 3 if small_space else content_height // 2
    network_rect = pygame.Rect(
        rect.left + 10, 
        content_y, 
        rect.width - 20, 
        network_height
    )
    
    # Draw Network section with panels for WiFi and Cellular
    panel_spacing = 10
    cell_width = (network_rect.width - panel_spacing) // 2
    
    # WiFi panel (left)
    wifi_rect = pygame.Rect(
        network_rect.left,
        network_rect.top,
        cell_width,
        network_rect.height
    )
    wifi_panel_colors = {
        'background': config.COLOR_WIFI,
        'border': config.COLOR_ACCENT,
        'title': config.COLOR_MENU_HEADER,
        'title_text': (255, 255, 255)
    }
    wifi_content = draw_panel(screen, wifi_rect, "WiFi", fonts, wifi_panel_colors)
    
    # Add WiFi content
    wifi_status = "Online"
    network_name = "2.4GHz-Home_Network"
    
    status_surface = fonts['small'].render(wifi_status, True, config.COLOR_WIFI_ONLINE)
    status_pos = (wifi_content.left + 10, wifi_content.top + 10)
    screen.blit(status_surface, status_pos)
    
    network_surface = fonts['small'].render(network_name, True, config.COLOR_FOREGROUND)
    network_pos = (wifi_content.left + 10, wifi_content.top + 35)
    screen.blit(network_surface, network_pos)
    
    # Cellular panel (right)
    cell_rect = pygame.Rect(
        network_rect.left + cell_width + panel_spacing,
        network_rect.top,
        cell_width,
        network_rect.height
    )
    cell_panel_colors = {
        'background': config.COLOR_CELLULAR,
        'border': config.COLOR_ACCENT,
        'title': config.COLOR_MENU_HEADER,
        'title_text': (255, 255, 255)
    }
    cell_content = draw_panel(screen, cell_rect, "Cellular", fonts, cell_panel_colors)
    
    # Add Cellular content
    cell_status = "5G"
    provider = "Verizon"
    
    status_surface = fonts['small'].render(cell_status, True, (255, 255, 255))
    status_pos = (cell_content.right - status_surface.get_width() - 10, cell_content.top + 10)
    screen.blit(status_surface, status_pos)
    
    provider_surface = fonts['small'].render(provider, True, config.COLOR_NETWORK)
    provider_pos = (cell_content.left + 10, cell_content.top + 10)
    screen.blit(provider_surface, provider_pos)
    
    # System Information panel (below network info)
    sys_rect = pygame.Rect(
        rect.left + 10,
        network_rect.bottom + 10,
        rect.width - 20,
        content_height - network_height - 20
    )
    
    # Draw dark background for system info area
    pygame.draw.rect(screen, config.COLOR_BACKGROUND, sys_rect)
    
    # Determine font size based on available space
    if small_space:
        font_to_use = fonts['small']
        line_height = font_to_use.get_height() + 5
    else:
        font_to_use = fonts['medium']
        line_height = font_to_use.get_height() + 10
    
    # Get system information
    cpu_usage, cpu_info = get_cpu_usage()
    memory_percent, memory_used, memory_total = get_memory_usage()
    disk_percent, disk_used, disk_total = get_disk_usage()
    current_time = get_current_time()
    
    # Draw the system information
    y_offset = sys_rect.top + 10
    
    # Time
    if current_time:
        time_text = f"Time: {current_time.strftime('%H:%M:%S')}"
        time_surface = font_to_use.render(time_text, True, config.COLOR_FOREGROUND)
        screen.blit(time_surface, (sys_rect.left + 10, y_offset))
        y_offset += line_height
    
    # CPU Usage
    if cpu_usage is not None:
        cpu_text = f"CPU: {cpu_usage:.1f}%"
        if cpu_info and cpu_info[0] == "temperature" and rect.height >= 200:
            cpu_text += f" (Temp: {cpu_info[1]:.1f}°C)"
        
        cpu_surface = font_to_use.render(cpu_text, True, config.COLOR_FOREGROUND)
        screen.blit(cpu_surface, (sys_rect.left + 10, y_offset))
        y_offset += line_height
    
    # Memory Usage
    if memory_percent is not None:
        memory_text = f"Memory: {memory_percent:.1f}%"
        if rect.height >= 200:
            memory_text += f" ({memory_used:.0f}MB/{memory_total:.0f}MB)"
        
        memory_surface = font_to_use.render(memory_text, True, config.COLOR_FOREGROUND)
        screen.blit(memory_surface, (sys_rect.left + 10, y_offset))
        y_offset += line_height
    
    # Disk Usage
    if disk_percent is not None:
        disk_text = f"Disk: {disk_percent:.1f}%"
        if rect.height >= 200:
            disk_text += f" ({disk_used:.1f}GB/{disk_total:.1f}GB)"
        
        disk_surface = font_to_use.render(disk_text, True, config.COLOR_FOREGROUND)
        screen.blit(disk_surface, (sys_rect.left + 10, y_offset)) 

def _draw_settings(screen, rect, fonts, config):
    """
    Draw the settings screen content.
    """
    # Draw header
    header_height = 30
    header_rect = pygame.Rect(rect.left, rect.top, rect.width, header_height)
    pygame.draw.rect(screen, config.COLOR_BACKGROUND, header_rect)
    
    # Draw header text
    font = fonts['small']
    header_text = font.render("Settings", True, config.COLOR_FOREGROUND)
    screen.blit(header_text, (rect.left + 20, header_rect.centery - header_text.get_height() // 2))
    
    # Calculate content area
    content_y = rect.top + header_height + 20
    content_height = rect.height - header_height - 40
    
    # Settings panel
    settings_rect = pygame.Rect(
        rect.left + 20, 
        content_y, 
        rect.width - 40, 
        content_height
    )
    
    # Draw settings background
    pygame.draw.rect(screen, config.COLOR_BACKGROUND, settings_rect)
    pygame.draw.rect(screen, config.COLOR_ACCENT, settings_rect, 1)  # Border
    
    # Determine font size based on available space
    font_to_use = fonts['medium']
    line_height = font_to_use.get_height() + 20
    
    # Draw settings options
    y_offset = settings_rect.top + 20
    
    # Fullscreen setting
    fullscreen_text = f"Fullscreen: {'On' if config.FULLSCREEN else 'Off'}"
    fullscreen_surface = font_to_use.render(fullscreen_text, True, config.COLOR_FOREGROUND)
    screen.blit(fullscreen_surface, (settings_rect.left + 20, y_offset))
    y_offset += line_height
    
    # Auto-cycle interval setting
    cycle_text = f"Auto-cycle Interval: {config.AUTO_CYCLE_INTERVAL} seconds"
    cycle_surface = font_to_use.render(cycle_text, True, config.COLOR_FOREGROUND)
    screen.blit(cycle_surface, (settings_rect.left + 20, y_offset))
    y_offset += line_height
    
    # FPS setting
    fps_text = f"Framerate: {config.FPS} FPS"
    fps_surface = font_to_use.render(fps_text, True, config.COLOR_FOREGROUND)
    screen.blit(fps_surface, (settings_rect.left + 20, y_offset))
    y_offset += line_height
    
    # Graph history setting
    history_text = f"Graph History: {config.GRAPH_HISTORY_SIZE} seconds"
    history_surface = font_to_use.render(history_text, True, config.COLOR_FOREGROUND)
    screen.blit(history_surface, (settings_rect.left + 20, y_offset)) 