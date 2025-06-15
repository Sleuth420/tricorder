# --- ui/views/settings/settings_view.py ---
# Handles rendering of the settings screen using shared list menu component

import pygame
import logging
from ui.components.list_menu_base import draw_simple_list_menu
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
    # Get menu items and selection from app_state
    menu_items = app_state.get_current_menu_items()
    selected_index = app_state.get_current_menu_index()
    
    # Use the shared list menu component
    draw_simple_list_menu(
        screen=screen,
        title="Settings",
        menu_items=menu_items,
        selected_index=selected_index,
        fonts=fonts,
        config_module=config_module,
        footer_hint=None,  # No footer for settings
        ui_scaler=ui_scaler
    ) 