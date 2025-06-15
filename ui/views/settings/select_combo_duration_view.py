# --- ui/views/settings/select_combo_duration_view.py ---
# View for selecting the secret combo hold duration

import pygame
import logging
from ui.components.menus.list_menu_base import draw_simple_list_menu
import config as app_config # For SECRET_COMBO_DURATION_OPTIONS and Theme
from ui.components.text.text_display import render_footer, render_title # render_text_with_selection_indicator is not standard

logger = logging.getLogger(__name__)

def draw_select_combo_duration_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draws the screen for selecting the secret combo hold duration using the shared list menu component.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
        ui_scaler (UIScaler, optional): UI scaling system for responsive design
    """
    # Get current selection index from app_state
    current_selection_idx = getattr(app_state, 'combo_duration_selection_index', 0)
    
    # Convert duration options to formatted menu items
    options_list = app_config.SECRET_COMBO_DURATION_OPTIONS
    menu_items = [f"{option_value:.1f}s" for option_value in options_list]
    
    # Use the shared list menu component
    draw_simple_list_menu(
        screen=screen,
        title="Secret Combo Duration",
        menu_items=menu_items,
        selected_index=current_selection_idx,
        fonts=fonts,
        config_module=config_module,
        footer_hint=None,  # No footer for this view
        ui_scaler=ui_scaler
    ) 