# --- ui/views/settings/display_settings_view.py ---
# Handles rendering of the display settings screen

import pygame
import logging
from ui.components.menus.list_menu_base import draw_simple_list_menu
from ui.components.text.text_display import render_footer, render_text
# import config as app_config # For accessing current interval and action names
# We will use config_module passed in, but need options for iteration
from config import AUTO_CYCLE_INTERVAL_OPTIONS # Import directly for iterating options

logger = logging.getLogger(__name__)

# Define available auto-cycle intervals - REMOVED, will import from config
# AUTO_CYCLE_INTERVAL_OPTIONS = [1, 5, 10, 15] # Seconds

def draw_display_settings_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the display settings screen content using the shared list menu component.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
        ui_scaler (UIScaler, optional): UI scaling system for responsive design
    """
    # Get current selection index from app_state
    current_selection_idx = getattr(app_state, 'display_settings_option_index', 0)
    
    # Convert options to menu items with proper formatting
    menu_items = []
    for option_value in AUTO_CYCLE_INTERVAL_OPTIONS:
        if isinstance(option_value, int):
            menu_items.append(f"{option_value}s")
        else:  # It's a string, like "Back to Main Menu"
            menu_items.append(option_value)
    
    # Use the shared list menu component
    draw_simple_list_menu(
        screen=screen,
        title="Display Settings",
        menu_items=menu_items,
        selected_index=current_selection_idx,
        fonts=fonts,
        config_module=config_module,
        footer_hint=None,  # No footer for this view
        ui_scaler=ui_scaler
    ) 