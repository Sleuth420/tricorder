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
    # back_action_name = pygame.key.name(config_module.INPUT_ACTION_BACK).upper() # This is not a key

    hint = f"< {key_prev_name}=Up | {key_select_name}=Select | {key_next_name}=Down | Hold {key_prev_name}=Back >"

    render_footer(
        screen, hint, fonts,
        config_module.Theme.FOREGROUND,
        screen_width, screen_height
    ) 