# --- ui/views/settings/wifi_settings_view.py ---
# Handles rendering of the WiFi settings screen

import pygame
import logging
from ui.components.text_display import render_footer, render_text
import config as app_config # For key names, Theme colors

logger = logging.getLogger(__name__)

def draw_wifi_settings_view(screen, app_state, fonts, config_module):
    """
    Draw the WiFi settings screen content.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state, which provides access to WifiManager
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
    """
    screen.fill(config_module.Theme.BACKGROUND)
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # Header
    header_height = config_module.HEADER_HEIGHT
    header_rect = pygame.Rect(0, 0, screen_width, header_height)
    pygame.draw.rect(screen, config_module.Theme.BACKGROUND, header_rect) # Or another color like Theme.MENU_HEADER_BG

    font_small = fonts['small']
    header_text_str = "Wi-Fi Settings"
    header_text_color = config_module.Theme.ACCENT
    header_text_surface = font_small.render(header_text_str, True, header_text_color)
    screen.blit(header_text_surface, (20, header_rect.centery - header_text_surface.get_height() // 2))

    # Menu items rendering from WifiManager
    content_y_start = header_height + 20
    font_medium = fonts['medium']
    item_height_padding = 15 # Padding around each item's text
    item_text_height = font_medium.get_height()
    effective_item_height = item_text_height + item_height_padding * 2

    # Get menu items and selected index from WifiManager via AppState
    # Ensure wifi_manager is initialized and accessible in app_state
    if not app_state.wifi_manager:
        error_msg = "WifiManager not available in AppState"
        logger.error(error_msg)
        err_surf = font_medium.render(error_msg, True, config_module.Theme.ALERT)
        screen.blit(err_surf, (screen_width // 2 - err_surf.get_width() // 2, screen_height // 2))
        render_footer(screen, "Error - Press Back", fonts, config_module.Theme.FOREGROUND, screen_width, screen_height)
        return

    menu_items_to_render = app_state.wifi_manager.get_current_wifi_display_options()
    current_selection_index = app_state.wifi_manager.get_selected_index()

    y_offset = content_y_start
    item_base_x = 40
    selection_padding_x = 10 # Horizontal padding for selection highlight
    selection_highlight_width = screen_width - (item_base_x - selection_padding_x) * 2

    for i, menu_item_data in enumerate(menu_items_to_render):
        item_name = menu_item_data["name"]
        text_color = config_module.Theme.FOREGROUND

        if i == current_selection_index:
            text_color = config_module.Theme.MENU_SELECTED_TEXT
            bg_color_selected = config_module.Theme.MENU_SELECTED_BG

            selection_bg_rect = pygame.Rect(
                item_base_x - selection_padding_x,
                y_offset - item_height_padding // 2,
                selection_highlight_width,
                effective_item_height
            )
            pygame.draw.rect(screen, bg_color_selected, selection_bg_rect, border_radius=5)

        item_text_surface = font_medium.render(item_name, True, text_color)
        item_text_rect = item_text_surface.get_rect(
            centery=y_offset + item_text_height // 2,
            left=item_base_x
        )
        screen.blit(item_text_surface, item_text_rect)

        y_offset += effective_item_height + 10 # Spacing between items

    # Footer hints
    key_prev_name = pygame.key.name(config_module.KEY_PREV).upper()
    key_next_name = pygame.key.name(config_module.KEY_NEXT).upper()
    key_select_name = pygame.key.name(config_module.KEY_SELECT).upper()
    
    hint = ""

    render_footer(
        screen, hint, fonts,
        config_module.Theme.FOREGROUND,
        screen_width, screen_height
    )

def draw_wifi_networks_view(screen, app_state, fonts, config_module):
    """
    Draw a simple WiFi network list - exactly what was requested.
    """
    screen.fill(config_module.Theme.BACKGROUND)
    
    networks = app_state.wifi_manager.get_available_networks()
    selected_index = app_state.wifi_manager.get_network_selected_index()
    
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Title - bigger font and better positioning
    title_font = fonts['large']
    title_text = title_font.render("WiFi Networks", True, config_module.Theme.FOREGROUND)
    screen.blit(title_text, (20, 15))
    
    # Show error states only - scanning is handled by the reusable loading screen
    if app_state.wifi_manager.last_scan_error:
        error_text = fonts['large'].render(f"Error: {app_state.wifi_manager.last_scan_error}", True, config_module.Theme.ALERT)
        screen.blit(error_text, (20, 70))
        return
    
    if not networks:
        no_networks_text = fonts['large'].render("No networks found", True, config_module.Theme.FOREGROUND)
        screen.blit(no_networks_text, (20, 70))
        return
    
    # Even bigger scrollable list with 6 items and thicker items
    start_y = 70
    item_height = 60  # Even thicker items for better fit
    max_visible = 6  # Show 6 items instead of 4
    list_margin = 15  # Better margins
    
    # Calculate scroll offset
    scroll_offset = max(0, selected_index - max_visible + 1)
    
    # Optimized sidebar space - reduce to use horizontal space better
    sidebar_space = 65  # Smaller sidebar, more space for text
    list_bg_rect = pygame.Rect(list_margin, start_y - 8, screen_width - sidebar_space - list_margin, (max_visible * item_height) + 16)
    pygame.draw.rect(screen, (15, 15, 15), list_bg_rect, border_radius=5)
    
    # Draw networks with bigger fonts and better spacing
    for i in range(max_visible):
        net_index = i + scroll_offset
        if net_index >= len(networks):
            break
        
        network = networks[net_index]
        y_pos = start_y + (i * item_height)
        
        # Bigger highlight selected item
        if net_index == selected_index:
            highlight_rect = pygame.Rect(list_margin + 3, y_pos - 3, screen_width - sidebar_space - list_margin - 6, item_height - 6)
            pygame.draw.rect(screen, config_module.Theme.MENU_SELECTED_BG, highlight_rect, border_radius=4)
            text_color = config_module.Theme.MENU_SELECTED_TEXT
        else:
            text_color = config_module.Theme.FOREGROUND
        
        # Network info - better use of horizontal space in thicker items
        ssid = network['ssid'][:20]  # Longer names since we have more horizontal space
        signal = network['signal_strength']
        saved = "SAVED" if network['is_saved'] else ""
        secure = "SECURE" if network['security'] != 'Open' else "OPEN"
        
        # Main line with network name and signal - bigger font, more space
        main_line = f"{ssid} ({signal}%)"
        main_surface = fonts['medium'].render(main_line, True, text_color)
        screen.blit(main_surface, (list_margin + 10, y_pos + 8))
        
        # Status line with better positioning in thicker items
        if saved or secure != "OPEN":
            status_line = f"{saved} {secure}".strip()
            status_surface = fonts['small'].render(status_line, True, text_color)
            screen.blit(status_surface, (list_margin + 10, y_pos + 35))
        
        # Add signal strength bar on the right side to use the extra horizontal space
        bar_width = 40
        bar_height = 8
        bar_x = screen_width - sidebar_space - bar_width - 25
        bar_y = y_pos + 20
        
        # Background bar
        bar_bg_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (30, 30, 30), bar_bg_rect, border_radius=2)
        
        # Signal strength fill
        fill_width = int((signal / 100.0) * bar_width)
        if fill_width > 0:
            fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
            # Color based on signal strength
            if signal >= 70:
                bar_color = (0, 200, 0)  # Green for strong
            elif signal >= 40:
                bar_color = (255, 165, 0)  # Orange for medium
            else:
                bar_color = (255, 100, 100)  # Red for weak
            pygame.draw.rect(screen, bar_color, fill_rect, border_radius=2)
    
    # Bigger, better scroll indicators in thicker sidebar
    if len(networks) > max_visible:
        # Thicker background for scroll area
        scroll_bg_rect = pygame.Rect(screen_width - sidebar_space + 10, start_y - 8, sidebar_space - 20, (max_visible * item_height) + 16)
        pygame.draw.rect(screen, config_module.Theme.MENU_SELECTED_BG, scroll_bg_rect, border_radius=5)
        
        # Bigger up arrow if we can scroll up
        if scroll_offset > 0:
            up_arrow = fonts['medium'].render("^", True, config_module.Theme.FOREGROUND)
            up_rect = up_arrow.get_rect(center=(screen_width - sidebar_space//2, start_y + 15))
            screen.blit(up_arrow, up_rect)
        
        # Bigger down arrow if we can scroll down
        if scroll_offset + max_visible < len(networks):
            down_arrow = fonts['medium'].render("v", True, config_module.Theme.FOREGROUND)
            down_rect = down_arrow.get_rect(center=(screen_width - sidebar_space//2, start_y + (max_visible * item_height) - 15))
            screen.blit(down_arrow, down_rect)
        
        # Bigger position indicator in center
        scroll_info = f"{selected_index + 1}/{len(networks)}"
        scroll_surface = fonts['medium'].render(scroll_info, True, config_module.Theme.FOREGROUND)
        scroll_rect = scroll_surface.get_rect(center=(screen_width - sidebar_space//2, start_y + (max_visible * item_height) // 2))
        screen.blit(scroll_surface, scroll_rect)
    
    # Bigger footer with better positioning
    footer_y = screen_height - 35
    footer_text = ""
    footer_surface = fonts['medium'].render(footer_text, True, config_module.Theme.FOREGROUND)
    screen.blit(footer_surface, (20, footer_y)) 