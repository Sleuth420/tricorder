# --- ui/views/settings/device_settings_view.py ---
# Handles rendering of the device settings screen (Reboot/Shutdown)

import pygame
import logging
from ui.components.text_display import render_footer, render_text
import config as app_config # For action names

logger = logging.getLogger(__name__)

# Define device action menu items
# These correspond to actions AppState will handle
DEVICE_ACTION_ITEMS = [
    {"name": "Reboot Device", "action": "REBOOT_DEVICE"}, # Action name for AppState
    {"name": "Shutdown Device", "action": "SHUTDOWN_DEVICE"},
    {"name": "Restart Application", "action": "RESTART_APP"}, # New item
    {"name": "Secret Combo Timer", "action": app_config.ACTION_SELECT_COMBO_DURATION}, # New item
    {"name": "<- Back to Main Menu", "action": app_config.ACTION_GO_TO_MAIN_MENU} # Updated item with simpler arrow
]

def draw_device_settings_view(screen, app_state, fonts, config_module):
    """
    Draw the device settings screen content.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
    """
    screen.fill(config_module.Theme.BACKGROUND)
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    rect = pygame.Rect(0, 0, screen_width, screen_height)

    header_height = config_module.HEADER_HEIGHT
    header_rect = pygame.Rect(rect.left, rect.top, rect.width, header_height)
    pygame.draw.rect(screen, config_module.Theme.BACKGROUND, header_rect)

    font_small = fonts['small']
    header_text_str = "Device Settings"
    header_text_color = config_module.Theme.ACCENT
    header_text = font_small.render(header_text_str, True, header_text_color)
    screen.blit(header_text, (rect.left + 20, header_rect.centery - header_text.get_height() // 2))

    content_y = rect.top + header_height + 20
    
    font_medium = fonts['medium']
    item_height_padding = 20 
    item_text_height = font_medium.get_height()
    effective_item_height = item_text_height + item_height_padding
    y_offset = content_y + 20

    # This index should come from app_state, e.g., app_state.device_settings_option_index
    current_selection_idx = getattr(app_state, 'device_settings_option_index', 0)

    for i, item_data in enumerate(DEVICE_ACTION_ITEMS):
        item_name = item_data["name"]
        text_color = config_module.Theme.FOREGROUND
        
        selection_bg_rect = pygame.Rect(
            rect.left + 30, 
            y_offset - (item_height_padding // 2),   
            rect.width - 60,
            effective_item_height 
        )

        if i == current_selection_idx:
            text_color = config_module.Theme.MENU_SELECTED_TEXT
            bg_color_selected = config_module.Theme.MENU_SELECTED_BG
            pygame.draw.rect(screen, bg_color_selected, selection_bg_rect, border_radius=5)

        item_text_surface = font_medium.render(item_name, True, text_color)
        item_text_rect = item_text_surface.get_rect(
            centery=y_offset + (item_text_height //2) ,
            left=rect.left + 40 
        )
        screen.blit(item_text_surface, item_text_rect)
        
        y_offset += effective_item_height + 10

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