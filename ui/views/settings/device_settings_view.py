# --- ui/views/settings/device_settings_view.py ---
# Handles rendering of the device settings screen (Reboot/Shutdown)

import pygame
import logging
from ui.components.menus.list_menu_base import draw_simple_list_menu
from ui.components.text.text_display import render_footer, render_text
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

def draw_device_settings_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the device settings screen content using the shared list menu component.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
        ui_scaler (UIScaler, optional): UI scaling system for responsive design
    """
    # Get current selection index from app_state
    current_selection_idx = getattr(app_state, 'device_settings_option_index', 0)
    
    # Extract just the names for the list menu component
    menu_items = [item_data["name"] for item_data in DEVICE_ACTION_ITEMS]
    
    # Use the shared list menu component
    draw_simple_list_menu(
        screen=screen,
        title="Device Settings",
        menu_items=menu_items,
        selected_index=current_selection_idx,
        fonts=fonts,
        config_module=config_module,
        footer_hint=None,  # No footer for this view
        ui_scaler=ui_scaler
    ) 