# --- ui/views/settings/debug_overlay_view.py ---
# Handles rendering of the debug overlay settings screen

import pygame
import logging
from ui.components.menus.list_menu_base import draw_simple_list_menu
from ui.components.text.text_display import render_footer, render_text
import config as app_config

logger = logging.getLogger(__name__)

def draw_debug_overlay_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the debug overlay settings screen content using the shared list menu component.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
        ui_scaler (UIScaler, optional): UI scaling system for responsive design
    """
    # Get current selection index from app_state
    current_selection_idx = getattr(app_state, 'debug_overlay_option_index', 0)
    
    # Get debug overlay state
    debug_enabled = app_state.debug_overlay.enabled
    
    # Define debug overlay menu items with current state
    debug_overlay_items = [
        f"Debug Overlay: {'ON' if debug_enabled else 'OFF'}",
        "<- Back to Settings"
    ]
    
    # Use the shared list menu component
    draw_simple_list_menu(
        screen=screen,
        title="Debug Overlay",
        menu_items=debug_overlay_items,
        selected_index=current_selection_idx,
        fonts=fonts,
        config_module=config_module,
        footer_hint=f"{config_module.get_control_labels()['select']} to toggle overlay",
        ui_scaler=ui_scaler
    )
