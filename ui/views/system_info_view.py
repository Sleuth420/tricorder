# --- ui/views/system_info_view.py ---
# Handles rendering of the system information screen

import pygame
import logging
from ui.components.ui_elements import draw_panel
from ui.components.text_display import render_footer
import config as app_config # For theme colors and constants

logger = logging.getLogger(__name__)

def draw_system_info_view(screen, app_state, sensor_values, fonts, config_module, target_rect=None, draw_footer=True):
    """
    Draw the system information screen.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state (for frozen status)
        sensor_values (dict): Dictionary containing formatted system values (new structure)
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config.py)
        target_rect (pygame.Rect, optional): The rectangle to draw within. Defaults to the full screen.
        draw_footer (bool): Whether to draw the footer. Defaults to True.
    """
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    if target_rect:
        rect = target_rect
        pygame.draw.rect(screen, config_module.Theme.BACKGROUND, rect)
    else:
        rect = pygame.Rect(0, 0, screen_width, screen_height)
        screen.fill(config_module.Theme.BACKGROUND)

    header_height = 20 
    header_rect = pygame.Rect(rect.left, rect.top, rect.width, header_height)
    pygame.draw.rect(screen, config_module.Theme.BACKGROUND, header_rect)

    font = fonts['medium']
    header_text_str = "System Information"
    if app_state.is_frozen:
        header_text_str += " [FROZEN]"
    header_text_color = config_module.Theme.ACCENT if not app_state.is_frozen else config_module.Theme.FROZEN_INDICATOR
    header_text = font.render(header_text_str, True, header_text_color)
    screen.blit(header_text, (rect.left + 20, header_rect.centery - header_text.get_height() // 2))

    logo_surface = None
    logo_rect = None
    logo_padding = 5
    try:
        logo_surface = pygame.image.load(config_module.SPLASH_LOGO_PATH).convert_alpha()
        max_logo_height = 30
        if logo_surface.get_height() > max_logo_height:
            scale = max_logo_height / logo_surface.get_height()
            new_width = int(logo_surface.get_width() * scale)
            logo_surface = pygame.transform.smoothscale(logo_surface, (new_width, max_logo_height))
        logo_rect = logo_surface.get_rect(centerx=rect.centerx, top=header_rect.bottom + logo_padding)
        screen.blit(logo_surface, logo_rect)
        logo_bottom = logo_rect.bottom + logo_padding
    except pygame.error as e:
        logger.warning(f"Could not load or display logo '{config_module.SPLASH_LOGO_PATH}': {e}")
        logo_bottom = header_rect.bottom

    content_y = logo_bottom + 5
    footer_height_calc = config_module.FONT_SIZE_SMALL * 2 if draw_footer else 0
    available_content_height = rect.height - content_y - footer_height_calc
    content_rect = pygame.Rect(rect.left + 10, content_y, rect.width - 20, available_content_height)

    if available_content_height <= 0:
        logger.warning("Not enough vertical space for system_info_view content.")
        if draw_footer:
            key_prev_name = pygame.key.name(config_module.KEY_PREV).upper()
            key_next_name = pygame.key.name(config_module.KEY_NEXT).upper()
            key_select_name = pygame.key.name(config_module.KEY_SELECT).upper()
            action_text = "Freeze" if not app_state.is_frozen else "Unfreeze"
            hint = f"< Hold {key_prev_name}=Menu | {key_select_name}={action_text} | {key_next_name}= - >"
            render_footer(screen, hint, fonts, config_module.Theme.FOREGROUND, rect.width, rect.bottom)
        return

    # Define panel color schemes using Theme
    wifi_panel_theme = {
        'background': config_module.Theme.CONTENT_WIFI_INFO_BG,
        'border': config_module.Theme.ACCENT,
        'title': config_module.Theme.CONTENT_PANEL_HEADER_BG, 
        'title_text': config_module.Theme.CONTENT_PANEL_TITLE_TEXT
    }
    cell_panel_theme = {
        'background': config_module.Theme.CONTENT_CELLULAR_INFO_BG,
        'border': config_module.Theme.ACCENT,
        'title': config_module.Theme.CONTENT_PANEL_HEADER_BG,
        'title_text': config_module.Theme.CONTENT_PANEL_TITLE_TEXT
    }

    network_proportion = 0.6
    network_height = max(40, int(available_content_height * network_proportion))
    network_rect = pygame.Rect(content_rect.left, content_rect.top, content_rect.width, network_height)
    panel_spacing = 5
    panel_height = (network_rect.height - panel_spacing) // 2
    panel_width = network_rect.width

    # WiFi panel
    wifi_rect = pygame.Rect(network_rect.left, network_rect.top, panel_width, panel_height)
    wifi_content_area = draw_panel(screen, wifi_rect, "WiFi", fonts, wifi_panel_theme)
    wifi_status_data = sensor_values.get(app_config.INFO_WIFI_STATUS, {})
    wifi_ssid_data = sensor_values.get(app_config.INFO_WIFI_SSID, {})
    wifi_status = wifi_status_data.get("text", "N/A")
    network_name = wifi_ssid_data.get("text", "N/A")
    wifi_status_color = config_module.Theme.CONTENT_WIFI_ONLINE_STATUS if wifi_status.lower() == "online" else config_module.Theme.ALERT
    status_surface = fonts['small'].render(wifi_status, True, wifi_status_color)
    status_pos = (wifi_content_area.left + 5, wifi_content_area.centery - status_surface.get_height() - 2)
    screen.blit(status_surface, status_pos)
    network_surface = fonts['small'].render(network_name, True, config_module.Theme.FOREGROUND)
    network_pos = (wifi_content_area.left + 5, wifi_content_area.centery + 2)
    screen.blit(network_surface, network_pos)

    # Cellular panel
    cell_rect = pygame.Rect(network_rect.left, network_rect.top + panel_height + panel_spacing, panel_width, panel_height)
    cell_content_area = draw_panel(screen, cell_rect, "Cellular", fonts, cell_panel_theme)
    cell_status_data = sensor_values.get(app_config.INFO_CELL_STATUS, {})
    cell_provider_data = sensor_values.get(app_config.INFO_CELL_PROVIDER, {})
    cell_status = cell_status_data.get("text", "N/A")
    provider = cell_provider_data.get("text", "N/A")
    cell_provider_color = config_module.Theme.FOREGROUND if provider != "N/A" else config_module.Theme.ALERT
    cell_status_color = config_module.Theme.WHITE if cell_status.lower() == "online" else config_module.Theme.ALERT # Assuming white for online status text
    provider_surface = fonts['small'].render(provider, True, cell_provider_color)
    provider_pos = (cell_content_area.left + 5, cell_content_area.centery - provider_surface.get_height() - 2)
    screen.blit(provider_surface, provider_pos)
    status_surface_cell = fonts['small'].render(cell_status, True, cell_status_color)
    status_pos_cell = (cell_content_area.left + 5, cell_content_area.centery + 2)
    screen.blit(status_surface_cell, status_pos_cell)

    # System Information list (below network info)
    sys_info_top = network_rect.bottom + 10
    font_to_use = fonts['small']
    line_padding = 4
    
    sys_info_items_config = [
        (app_config.SENSOR_CLOCK, "Time: "),
        (app_config.SENSOR_CPU_USAGE, "CPU: "),
        (app_config.SENSOR_MEMORY_USAGE, "Memory: "),
        (app_config.SENSOR_DISK_USAGE, "Disk: ")
    ]
    num_sys_items = len(sys_info_items_config)
    required_sys_info_height = num_sys_items * (font_to_use.get_height() + line_padding)
    original_available_sys_info_height = available_content_height - network_height - 10
    sys_info_height = min(required_sys_info_height, original_available_sys_info_height)
    sys_rect = pygame.Rect(content_rect.left, sys_info_top, content_rect.width, sys_info_height)

    if sys_info_height > font_to_use.get_height():
        pygame.draw.rect(screen, config_module.Theme.BACKGROUND, sys_rect) # Clear this specific area
        line_height = font_to_use.get_height() + line_padding
        current_y = sys_rect.top + line_padding // 2
        items_drawn_count = 0
        for sensor_key, label_prefix in sys_info_items_config:
            if items_drawn_count * line_height >= sys_rect.height: # Stop if no more vertical space in allocated rect
                break
            sensor_data = sensor_values.get(sensor_key, {})
            value_text = sensor_data.get("text", "N/A")
            unit_text = sensor_data.get("unit", "")
            note_text = sensor_data.get("note", "")
            
            full_text = f"{label_prefix}{value_text}{unit_text}"
            if note_text and sensor_key != app_config.SENSOR_CLOCK: # Clock note is handled differently by data_updater for full date
                full_text += f" ({note_text})"
            elif sensor_key == app_config.SENSOR_CLOCK and note_text:
                 # For clock, the note is the full date, display it on a new line or side by side if space allows
                 # For simplicity now, let's display clock note on new line if present
                 time_surface = font_to_use.render(f"{label_prefix}{value_text}", True, config_module.Theme.FOREGROUND)
                 screen.blit(time_surface, (sys_rect.left + 10, current_y))
                 current_y += line_height
                 items_drawn_count += 1
                 if items_drawn_count * line_height < sys_rect.height and note_text: # Check space for note
                     date_surface = font_to_use.render(note_text, True, config_module.Theme.ACCENT) # Different color for date?
                     screen.blit(date_surface, (sys_rect.left + 20, current_y)) # Indent date slightly
                     current_y += line_height
                     items_drawn_count += 1
                 continue # Skip to next item

            text_surface = font_to_use.render(full_text, True, config_module.Theme.FOREGROUND)
            screen.blit(text_surface, (sys_rect.left + 10, current_y))
            current_y += line_height
            items_drawn_count += 1
    else:
        logger.warning("Skipping System Info list drawing due to insufficient calculated height.")

    if draw_footer:
        key_prev_name = pygame.key.name(config_module.KEY_PREV).upper()
        key_next_name = pygame.key.name(config_module.KEY_NEXT).upper()
        key_select_name = pygame.key.name(config_module.KEY_SELECT).upper()
        action_text = "Freeze" if not app_state.is_frozen else "Unfreeze"
        hint = f"< Hold {key_prev_name}=Menu | {key_select_name}={action_text} | {key_next_name}= - >"
        render_footer(screen, hint, fonts, config_module.Theme.FOREGROUND, rect.width, rect.bottom) 