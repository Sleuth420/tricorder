# --- ui/views/settings/wifi_settings_view.py ---
# Handles rendering of the WiFi settings screen

import pygame
import logging
from ui.components.menus.list_menu_base import draw_simple_list_menu
from ui.components.text.text_display import render_footer, render_text
import config as app_config # For key names, Theme colors

logger = logging.getLogger(__name__)

def draw_wifi_settings_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the WiFi settings screen content using the shared list menu component.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state, which provides access to WifiManager
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
        ui_scaler (UIScaler, optional): UI scaling system for responsive design
    """
    # Check if WifiManager is available
    if not app_state.wifi_manager:
        screen.fill(config_module.Theme.BACKGROUND)
        if ui_scaler:
            screen_width = ui_scaler.screen_width
            screen_height = ui_scaler.screen_height
        else:
            screen_width = screen.get_width()
            screen_height = screen.get_height()
        error_msg = "WifiManager not available in AppState"
        logger.error(error_msg)
        font_medium = fonts['medium']
        err_surf = font_medium.render(error_msg, True, config_module.Theme.ALERT)
        screen.blit(err_surf, (screen_width // 2 - err_surf.get_width() // 2, screen_height // 2))
        labels = config_module.get_control_labels()
        render_footer(screen, f"Error - Press {labels['back']}", fonts, config_module.Theme.FOREGROUND, screen_width, screen_height, ui_scaler=ui_scaler)
        return

    # Get menu items and selected index from WifiManager
    menu_items_data = app_state.wifi_manager.get_current_wifi_display_options()
    current_selection_index = app_state.wifi_manager.get_selected_index()
    
    # Extract just the names for the list menu component
    menu_items = [item_data["name"] for item_data in menu_items_data]
    
    # Use the shared list menu component
    draw_simple_list_menu(
        screen=screen,
        title="Wi-Fi Settings",
        menu_items=menu_items,
        selected_index=current_selection_index,
        fonts=fonts,
        config_module=config_module,
        footer_hint=None,  # No footer for this view
        ui_scaler=ui_scaler
    )

def draw_wifi_networks_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw a WiFi network list with responsive design.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
        ui_scaler (UIScaler, optional): UI scaling system for responsive design
    """
    screen.fill(config_module.Theme.BACKGROUND)
    
    networks = app_state.wifi_manager.get_available_networks()
    selected_index = app_state.wifi_manager.get_network_selected_index()
    
    if ui_scaler:
        screen_width = ui_scaler.screen_width
        screen_height = ui_scaler.screen_height
    else:
        screen_width = screen.get_width()
        screen_height = screen.get_height()
    if ui_scaler:
        title_margin = ui_scaler.margin("medium")
        content_start_y = ui_scaler.header_height() + ui_scaler.margin("large")
        item_height = ui_scaler.scale(60)
        list_margin = ui_scaler.margin("medium")
        sidebar_space = ui_scaler.scale(65)
        max_visible = 6  # Keep this fixed for good UX
        
        # Debug logging for wifi networks layout
        if ui_scaler.debug_mode:
            logger.info(f"🎨 WiFiNetworks: screen={screen_width}x{screen_height}, item_height={item_height}px, margin={list_margin}px")
    else:
        # Fallback to original calculations
        title_margin = 20
        content_start_y = 70
        item_height = 60
        list_margin = 15
        sidebar_space = 65
        max_visible = 6
    
    title_font = fonts['large']
    title_text = title_font.render("WiFi Networks", True, config_module.Theme.FOREGROUND)
    title_top = ui_scaler.margin("small") if ui_scaler else 15
    screen.blit(title_text, (title_margin, title_top))
    
    # Show error states only - scanning is handled by the reusable loading screen
    if app_state.wifi_manager.last_scan_error:
        error_text = fonts['large'].render(f"Error: {app_state.wifi_manager.last_scan_error}", True, config_module.Theme.ALERT)
        screen.blit(error_text, (title_margin, content_start_y))
        return
    
    if not networks:
        no_networks_text = fonts['large'].render("No networks found", True, config_module.Theme.FOREGROUND)
        screen.blit(no_networks_text, (title_margin, content_start_y))
        return
    
    # Calculate scroll offset
    scroll_offset = max(0, selected_index - max_visible + 1)
    
    # Responsive list background
    list_bg_rect = pygame.Rect(list_margin, content_start_y - 8, screen_width - sidebar_space - list_margin, (max_visible * item_height) + 16)
    pygame.draw.rect(screen, (15, 15, 15), list_bg_rect, border_radius=5)
    
    # Draw networks with responsive spacing
    for i in range(max_visible):
        net_index = i + scroll_offset
        if net_index >= len(networks):
            break
        
        network = networks[net_index]
        y_pos = content_start_y + (i * item_height)
        
        # Highlight selected item
        if net_index == selected_index:
            highlight_rect = pygame.Rect(list_margin + 3, y_pos - 3, screen_width - sidebar_space - list_margin - 6, item_height - 6)
            pygame.draw.rect(screen, config_module.Theme.MENU_SELECTED_BG, highlight_rect, border_radius=4)
            text_color = config_module.Theme.MENU_SELECTED_TEXT
        else:
            text_color = config_module.Theme.FOREGROUND
        
        # Network info - responsive text positioning
        ssid = network['ssid'][:20]  # Longer names since we have more horizontal space
        signal = network['signal_strength']
        saved = "SAVED" if network['is_saved'] else ""
        secure = "SECURE" if network['security'] != 'Open' else "OPEN"
        
        # Main line with network name and signal - responsive positioning
        main_line = f"{ssid} ({signal}%)"
        main_surface = fonts['medium'].render(main_line, True, text_color)
        main_y = y_pos + (ui_scaler.scale(8) if ui_scaler else 8)
        screen.blit(main_surface, (list_margin + (ui_scaler.scale(10) if ui_scaler else 10), main_y))
        
        # Status line with responsive positioning
        if saved or secure != "OPEN":
            status_line = f"{saved} {secure}".strip()
            status_surface = fonts['small'].render(status_line, True, text_color)
            status_y = y_pos + (ui_scaler.scale(35) if ui_scaler else 35)
            screen.blit(status_surface, (list_margin + (ui_scaler.scale(10) if ui_scaler else 10), status_y))
        
        # Responsive signal strength bar
        bar_width = ui_scaler.scale(40) if ui_scaler else 40
        bar_height = ui_scaler.scale(8) if ui_scaler else 8
        bar_x = screen_width - sidebar_space - bar_width - (ui_scaler.scale(25) if ui_scaler else 25)
        bar_y = y_pos + (ui_scaler.scale(20) if ui_scaler else 20)
        
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
    
    # Responsive scroll indicators
    if len(networks) > max_visible:
        # Responsive scroll area background
        scroll_bg_rect = pygame.Rect(screen_width - sidebar_space + 10, content_start_y - 8, sidebar_space - 20, (max_visible * item_height) + 16)
        pygame.draw.rect(screen, config_module.Theme.MENU_SELECTED_BG, scroll_bg_rect, border_radius=5)
        
        # Up arrow if we can scroll up
        if scroll_offset > 0:
            up_arrow = fonts['medium'].render("^", True, config_module.Theme.FOREGROUND)
            up_y = content_start_y + (ui_scaler.scale(15) if ui_scaler else 15)
            up_rect = up_arrow.get_rect(center=(screen_width - sidebar_space//2, up_y))
            screen.blit(up_arrow, up_rect)
        
        # Down arrow if we can scroll down
        if scroll_offset + max_visible < len(networks):
            down_arrow = fonts['medium'].render("v", True, config_module.Theme.FOREGROUND)
            down_y = content_start_y + (max_visible * item_height) - (ui_scaler.scale(15) if ui_scaler else 15)
            down_rect = down_arrow.get_rect(center=(screen_width - sidebar_space//2, down_y))
            screen.blit(down_arrow, down_rect)
        
        # Position indicator in center
        scroll_info = f"{selected_index + 1}/{len(networks)}"
        scroll_surface = fonts['medium'].render(scroll_info, True, config_module.Theme.FOREGROUND)
        scroll_center_y = content_start_y + (max_visible * item_height) // 2
        scroll_rect = scroll_surface.get_rect(center=(screen_width - sidebar_space//2, scroll_center_y))
        screen.blit(scroll_surface, scroll_rect)
    
    # Responsive footer
    footer_y = screen_height - (ui_scaler.scale(35) if ui_scaler else 35)
    footer_text = ""
    footer_surface = fonts['medium'].render(footer_text, True, config_module.Theme.FOREGROUND)
    screen.blit(footer_surface, (title_margin, footer_y)) 