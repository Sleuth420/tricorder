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

    # Draw header (Make it shorter)
    header_height = 20 # Reduced from 30
    header_rect = pygame.Rect(rect.left, rect.top, rect.width, header_height)
    pygame.draw.rect(screen, config.COLOR_BACKGROUND, header_rect)

    # Draw "System Information" in the header
    font = fonts['medium']
    header_text_str = "System Information"
    if app_state.is_frozen:
        header_text_str += " [FROZEN]"
    header_text = font.render(header_text_str, True, config.COLOR_ACCENT if not app_state.is_frozen else config.COLOR_FROZEN)
    screen.blit(header_text, (rect.left + 20, header_rect.centery - header_text.get_height() // 2))

    # --- Logo Display ---
    logo_surface = None
    logo_rect = None
    logo_padding = 5
    try:
        # Attempt to load the logo
        logo_surface = pygame.image.load("images/logo.png").convert_alpha()
        # Optional: Scale logo if it's too big
        max_logo_height = 30 # Restored from 25
        if logo_surface.get_height() > max_logo_height:
            scale = max_logo_height / logo_surface.get_height()
            new_width = int(logo_surface.get_width() * scale)
            logo_surface = pygame.transform.smoothscale(logo_surface, (new_width, max_logo_height))

        logo_rect = logo_surface.get_rect(
            centerx=rect.centerx,
            top=header_rect.bottom + logo_padding
        )
        screen.blit(logo_surface, logo_rect)
        logo_bottom = logo_rect.bottom + logo_padding
    except pygame.error as e:
        logger.warning(f"Could not load or display logo.png: {e}")
        logo_bottom = header_rect.bottom # Start content right below header if logo fails

    # Calculate content area STARTING below the logo (or header if logo failed)
    content_y = logo_bottom + 5 # Add padding below logo
    footer_height = config.FONT_SIZE_SMALL * 2 # Restored from 15
    available_content_height = rect.height - content_y - footer_height
    content_rect = pygame.Rect(rect.left + 10, content_y, rect.width - 20, available_content_height)

    # Check if there's enough space to draw content
    if available_content_height <= 0:
        logger.warning("Not enough vertical space for content after header and logo.")
        # Render footer and return if no space
        if draw_footer:
            key_prev_name = pygame.key.name(config.KEY_PREV).upper()
            key_next_name = pygame.key.name(config.KEY_NEXT).upper()
            key_select_name = pygame.key.name(config.KEY_SELECT).upper()
            action_text = "Freeze" if not app_state.is_frozen else "Unfreeze"
            hint = f"< Hold {key_prev_name}=Menu | {key_select_name}={action_text} | {key_next_name}= - >"
            render_footer(screen, hint, fonts, config.COLOR_FOREGROUND, rect.width, rect.bottom)
        return # Stop drawing if no space

    # Network information section
    # Adjust proportion based on available height
    network_proportion = 0.6 # Increased significantly from 0.4
    network_height = max(40, int(available_content_height * network_proportion)) # Ensure minimum height
    network_rect = pygame.Rect(
        content_rect.left,
        content_rect.top,
        content_rect.width,
        network_height
    )

    # Stack WiFi and Cellular panels vertically
    panel_spacing = 5 # Reduce spacing slightly
    panel_height = (network_rect.height - panel_spacing) // 2
    panel_width = network_rect.width # Use full width

    # WiFi panel (top)
    wifi_rect = pygame.Rect(
        network_rect.left,
        network_rect.top,
        panel_width,
        panel_height
    )
    wifi_panel_colors = {
        'background': config.COLOR_WIFI,
        'border': config.COLOR_ACCENT,
        'title': config.COLOR_MENU_HEADER,
        'title_text': (255, 255, 255)
    }
    wifi_content = draw_panel(screen, wifi_rect, "WiFi", fonts, wifi_panel_colors)

    # Get WiFi content from sensor_values, with fallbacks
    wifi_status = sensor_values.get("WIFI_STATUS", ("N/A", "", ""))[0]
    network_name = sensor_values.get("WIFI_SSID", ("N/A", "", ""))[0]
    # Determine color based on status
    wifi_status_color = config.COLOR_WIFI_ONLINE if wifi_status.lower() == "online" else config.COLOR_ALERT

    status_surface = fonts['small'].render(wifi_status, True, wifi_status_color)
    # Position relative to wifi_content Rect
    status_pos = (wifi_content.left + 5, wifi_content.centery - status_surface.get_height() - 2)
    screen.blit(status_surface, status_pos)

    network_surface = fonts['small'].render(network_name, True, config.COLOR_FOREGROUND)
    # Position below status
    network_pos = (wifi_content.left + 5, wifi_content.centery + 2)
    screen.blit(network_surface, network_pos)

    # Cellular panel (bottom)
    cell_rect = pygame.Rect(
        network_rect.left,
        network_rect.top + panel_height + panel_spacing, # Position below WiFi panel
        panel_width,
        panel_height
    )
    cell_panel_colors = {
        'background': config.COLOR_CELLULAR,
        'border': config.COLOR_ACCENT,
        'title': config.COLOR_MENU_HEADER,
        'title_text': (255, 255, 255)
    }
    cell_content = draw_panel(screen, cell_rect, "Cellular", fonts, cell_panel_colors)

    # Get Cellular content from sensor_values, with fallbacks
    cell_status = sensor_values.get("CELL_STATUS", ("N/A", "", ""))[0]
    provider = sensor_values.get("CELL_PROVIDER", ("N/A", "", ""))[0]
    # Determine color based on status
    cell_provider_color = config.COLOR_FOREGROUND if provider != "N/A" else config.COLOR_ALERT
    cell_status_color = (255, 255, 255) if cell_status.lower() == "online" else config.COLOR_ALERT

    # Align text similarly to WiFi panel for consistency
    provider_surface = fonts['small'].render(provider, True, cell_provider_color)
    provider_pos = (cell_content.left + 5, cell_content.centery - provider_surface.get_height() - 2)
    screen.blit(provider_surface, provider_pos)

    status_surface = fonts['small'].render(cell_status, True, cell_status_color)
    status_pos = (cell_content.left + 5, cell_content.centery + 2)
    screen.blit(status_surface, status_pos)

    # System Information panel (below network info)
    sys_info_top = network_rect.bottom + 10 # Restored padding from 5
    # Calculate height based on content needed, not remaining space
    font_to_use = fonts['small']
    num_sys_items = 4 # Time, CPU, Mem, Disk
    line_padding = 4  # Fixed vertical padding between lines
    required_sys_info_height = num_sys_items * (font_to_use.get_height() + line_padding)
    # Ensure it doesn't exceed the originally available space
    original_available_sys_info_height = available_content_height - network_height - 10
    sys_info_height = min(required_sys_info_height, original_available_sys_info_height)

    sys_rect = pygame.Rect(
        content_rect.left,
        sys_info_top,
        content_rect.width,
        sys_info_height # Use the calculated height
    )

    # Check if sys_info_height is valid before drawing
    if sys_info_height > font_to_use.get_height(): # Check if at least one line can fit
        # Draw dark background for system info area
        pygame.draw.rect(screen, config.COLOR_BACKGROUND, sys_rect)

        # Determine font size based on available space - Always use small font now
        # font_to_use = fonts['small'] # Already defined above
        # Adjust line height based on available system info panel height (simplified)
        # Calculate line height based on fixed padding
        line_height = font_to_use.get_height() + line_padding
        y_offset = sys_rect.top + line_padding // 2 # Start with half padding

        # Get system information from sensor_values dictionary

        current_y = y_offset
        items_drawn = 0
        # Time
        if "CLOCK" in sensor_values:
            value, _, note = sensor_values["CLOCK"]
            time_text = f"Time: {value}"
            if note:
                time_text += f" ({note})"
            time_surface = font_to_use.render(time_text, True, config.COLOR_FOREGROUND)
            screen.blit(time_surface, (sys_rect.left + 10, current_y))
            current_y += line_height
            items_drawn += 1

        # CPU Usage
        if "CPU_USAGE" in sensor_values and items_drawn < num_sys_items:
            value, unit, note = sensor_values["CPU_USAGE"]
            cpu_text = f"CPU: {value}{unit}"
            if note:
                cpu_text += f" ({note})"
            cpu_surface = font_to_use.render(cpu_text, True, config.COLOR_FOREGROUND)
            screen.blit(cpu_surface, (sys_rect.left + 10, current_y))
            current_y += line_height
            items_drawn += 1

        # Memory Usage
        if "MEMORY_USAGE" in sensor_values and items_drawn < num_sys_items:
            value, unit, note = sensor_values["MEMORY_USAGE"]
            memory_text = f"Memory: {value}{unit}"
            if note:
                 memory_text += f" ({note})"
            memory_surface = font_to_use.render(memory_text, True, config.COLOR_FOREGROUND)
            screen.blit(memory_surface, (sys_rect.left + 10, current_y))
            current_y += line_height
            items_drawn += 1

        # Disk Usage
        if "DISK_USAGE" in sensor_values and items_drawn < num_sys_items:
            value, unit, note = sensor_values["DISK_USAGE"]
            disk_text = f"Disk: {value}{unit}"
            if note:
                 disk_text += f" ({note})"
            disk_surface = font_to_use.render(disk_text, True, config.COLOR_FOREGROUND)
            screen.blit(disk_surface, (sys_rect.left + 10, current_y))
            # items_drawn += 1 # No need to increment after last item
    else:
        logger.warning("Skipping System Info panel drawing due to insufficient calculated height.")

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