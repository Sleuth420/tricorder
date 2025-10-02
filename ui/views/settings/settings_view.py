# --- ui/views/settings/settings_view.py ---
# Handles rendering of the settings screen using shared list menu component

import pygame
import logging
from ui.components.menus.list_menu_base import draw_simple_list_menu
# import config as app_config # Not strictly needed if config_module is always passed and used

logger = logging.getLogger(__name__)

# Removed TEMP_SETTINGS_MENU_ITEMS and TEMP_SELECTED_INDEX
# The view will now get these from app_state, which gets them from MenuManager

def draw_settings_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the settings screen content using the shared list menu component.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
        ui_scaler (UIScaler, optional): UI scaling system for responsive design
    """
    # Add update available header if needed
    if hasattr(app_state, 'update_available') and app_state.update_available:
        screen.fill(config_module.Theme.BACKGROUND)
        header_text = "[UPDATE AVAILABLE]"
        header_surface = fonts['medium'].render(header_text, True, config_module.Theme.ALERT)
        screen.blit(header_surface, (20, 20))
        
        # Adjust content area down
        content_rect = pygame.Rect(0, 60, screen.get_width(), screen.get_height() - 60)
        # Create subsurface for the menu
        menu_screen = screen.subsurface(content_rect)
    else:
        menu_screen = screen
        content_rect = None
    
    # Get menu items and selection from app_state
    menu_items = app_state.get_current_menu_items()
    selected_index = app_state.get_current_menu_index()
    
    # Use the shared list menu component
    draw_simple_list_menu(
        screen=menu_screen,
        title="Settings",
        menu_items=menu_items,
        selected_index=selected_index,
        fonts=fonts,
        config_module=config_module,
        footer_hint=None,  # No footer for settings
        ui_scaler=ui_scaler
    ) 