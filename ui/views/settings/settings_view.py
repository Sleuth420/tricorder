# --- ui/views/settings/settings_view.py ---
# Handles rendering of the settings screen

import pygame
import logging
from ui.components.text_display import render_footer, render_text # Added render_text
# import config as app_config # Not strictly needed if config_module is always passed and used

logger = logging.getLogger(__name__)

# Removed TEMP_SETTINGS_MENU_ITEMS and TEMP_SELECTED_INDEX
# The view will now get these from app_state, which gets them from MenuManager

def draw_settings_view(screen, app_state, fonts, config_module):
    """
    Draw the settings screen content, now as a menu.

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
    header_text_str = "Settings"
    # Frozen state might not be applicable directly to the settings menu itself,
    # but could be if a sub-setting view has a "frozen" concept.
    # if app_state.is_frozen: # Keep for now if relevant later
    #     header_text_str += " [FROZEN]"
    header_text_color = config_module.Theme.ACCENT
    header_text = font_small.render(header_text_str, True, header_text_color)
    screen.blit(header_text, (rect.left + 20, header_rect.centery - header_text.get_height() // 2))

    content_y = rect.top + header_height + 20
    footer_height_calc = config_module.FONT_SIZE_SMALL * 3
    # content_height = rect.height - header_height - 20 - footer_height_calc # Not strictly needed for list

    # Menu items rendering
    font_medium = fonts['medium']
    item_height_padding = 20 # Total padding (top+bottom) for each item visual block
    item_text_height = font_medium.get_height()
    effective_item_height = item_text_height + item_height_padding
    
    # Get actual menu items and selected index from app_state
    menu_items_to_render = app_state.get_current_menu_items() # From MenuManager via AppState
    current_selection_index = app_state.get_current_menu_index() # From MenuManager via AppState

    y_offset = content_y + 20 # Start Y for the first item

    for i, menu_item_obj in enumerate(menu_items_to_render): # menu_item_obj is a MenuItem instance
        item_name = menu_item_obj.name
        
        text_color = config_module.Theme.FOREGROUND
        # bg_color = config_module.Theme.BACKGROUND # Default background, no explicit bg for non-selected

        if i == current_selection_index:
            text_color = config_module.Theme.MENU_SELECTED_TEXT
            bg_color_selected = config_module.Theme.MENU_SELECTED_BG
            
            selection_bg_rect = pygame.Rect(
                rect.left + 30, 
                y_offset - (item_height_padding // 2),   
                rect.width - 60,
                effective_item_height 
            )
            pygame.draw.rect(screen, bg_color_selected, selection_bg_rect, border_radius=5)

        item_text_surface = font_medium.render(item_name, True, text_color)
        item_text_rect = item_text_surface.get_rect(
            centery=y_offset + (item_text_height //2) ,
            left=rect.left + 40 
        )
        screen.blit(item_text_surface, item_text_rect)
        
        y_offset += effective_item_height + 10 # Spacing between items

    key_prev_name = pygame.key.name(config_module.KEY_PREV).upper()
    key_next_name = pygame.key.name(config_module.KEY_NEXT).upper()
    key_select_name = pygame.key.name(config_module.KEY_SELECT).upper()
    
    hint = ""

    render_footer(
        screen, hint, fonts,
        config_module.Theme.FOREGROUND,
        screen_width, screen_height
    ) 