# --- ui/views/system_info_view.py ---
# Handles rendering of the system information screen

import pygame
import logging
from ui.components.ui_elements import draw_panel
from ui.components.text_display import render_footer

logger = logging.getLogger(__name__)

def draw_system_info_view(screen, app_state, sensor_values, fonts, config, target_rect=None, draw_footer=True):
    """
    Draw the system information screen.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state (for frozen status)
        sensor_values (dict): Dictionary containing formatted system values
                              Expected keys: CPU_USAGE, MEMORY_USAGE, DISK_USAGE, CLOCK
        fonts (dict): Dictionary of loaded fonts
        config (module): Configuration module
        target_rect (pygame.Rect, optional): The rectangle to draw within. Defaults to the full screen.
        draw_footer (bool): Whether to draw the footer. Defaults to True.
    """
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # Determine the drawing area
    if target_rect:
        rect = target_rect
        # Clear only the target area if provided
        pygame.draw.rect(screen, config.COLOR_BACKGROUND, rect)
    else:
        rect = pygame.Rect(0, 0, screen_width, screen_height) # Use full screen
        # Clear the whole screen if no target_rect
        screen.fill(config.COLOR_BACKGROUND)

    # Draw header
    header_height = 30
    header_rect = pygame.Rect(rect.left, rect.top, rect.width, header_height)
    pygame.draw.rect(screen, config.COLOR_BACKGROUND, header_rect)

    # Draw "System Information" in the header
    font = fonts['small']
    header_text_str = "System Information"
    if app_state.is_frozen:
        header_text_str += " [FROZEN]"
    header_text = font.render(header_text_str, True, config.COLOR_ACCENT if not app_state.is_frozen else config.COLOR_FROZEN)
    screen.blit(header_text, (rect.left + 20, header_rect.centery - header_text.get_height() // 2))

    # Calculate content area
    content_y = rect.top + header_height + 5
    content_height = rect.height - header_height - config.FONT_SIZE_SMALL * 3 # Reserve space for footer
    content_rect = pygame.Rect(rect.left + 10, content_y, rect.width - 20, content_height)

    # Network information section (top) - Keep placeholder layout
    network_height = content_height // 3 # Always use the smaller proportion
    network_rect = pygame.Rect(
        content_rect.left,
        content_rect.top,
        content_rect.width,
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

    # Add WiFi content (placeholders for now, could be passed in sensor_values later)
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

    # Add Cellular content (placeholders)
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
        content_rect.left,
        network_rect.bottom + 10,
        content_rect.width,
        content_rect.height - network_height - 10 # Adjusted height
    )

    # Draw dark background for system info area
    pygame.draw.rect(screen, config.COLOR_BACKGROUND, sys_rect)

    # Determine font size based on available space - Always use small font now
    font_to_use = fonts['small']
    line_height = font_to_use.get_height() + 5 # Use consistent small line height

    # Get system information from sensor_values dictionary
    y_offset = sys_rect.top + 10

    # Time
    if "CLOCK" in sensor_values:
        value, _, note = sensor_values["CLOCK"]
        time_text = f"Time: {value}"
        if note:
            time_text += f" ({note})"
        time_surface = font_to_use.render(time_text, True, config.COLOR_FOREGROUND)
        screen.blit(time_surface, (sys_rect.left + 10, y_offset))
        y_offset += line_height

    # CPU Usage
    if "CPU_USAGE" in sensor_values:
        value, unit, note = sensor_values["CPU_USAGE"]
        cpu_text = f"CPU: {value}{unit}"
        if note:
            cpu_text += f" ({note})"
        cpu_surface = font_to_use.render(cpu_text, True, config.COLOR_FOREGROUND)
        screen.blit(cpu_surface, (sys_rect.left + 10, y_offset))
        y_offset += line_height

    # Memory Usage
    if "MEMORY_USAGE" in sensor_values:
        value, unit, note = sensor_values["MEMORY_USAGE"]
        memory_text = f"Memory: {value}{unit}"
        if note:
             memory_text += f" ({note})"
        memory_surface = font_to_use.render(memory_text, True, config.COLOR_FOREGROUND)
        screen.blit(memory_surface, (sys_rect.left + 10, y_offset))
        y_offset += line_height

    # Disk Usage
    if "DISK_USAGE" in sensor_values:
        value, unit, note = sensor_values["DISK_USAGE"]
        disk_text = f"Disk: {value}{unit}"
        if note:
             disk_text += f" ({note})"
        disk_surface = font_to_use.render(disk_text, True, config.COLOR_FOREGROUND)
        screen.blit(disk_surface, (sys_rect.left + 10, y_offset))

    # Draw footer only if requested
    if draw_footer:
        key_prev_name = pygame.key.name(config.KEY_PREV).upper()
        key_next_name = pygame.key.name(config.KEY_NEXT).upper()
        key_select_name = pygame.key.name(config.KEY_SELECT).upper()

        action_text = "Freeze" if not app_state.is_frozen else "Unfreeze"
        # Back is long press A, D does nothing
        hint = f"< Hold {key_prev_name}=Menu | {key_select_name}={action_text} | {key_next_name}= - >"

        render_footer(
            screen,
            hint,
            fonts,
            config.COLOR_FOREGROUND,
            rect.width, # Use rect's width/height for positioning
            rect.bottom # Position relative to rect bottom
        ) 