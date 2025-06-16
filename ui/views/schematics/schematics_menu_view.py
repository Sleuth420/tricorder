# --- ui/views/schematics_menu_view.py ---
# Handles rendering of the schematics selection submenu

import pygame
import logging
from ui.components.menus.list_menu_base import draw_scrollable_list_menu

logger = logging.getLogger(__name__)

def draw_schematics_menu_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the schematics selection submenu view using the standardized list menu component.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        ui_scaler (UIScaler): The UI scaler
        
    Returns:
        None
    """
    # Get menu items and selection from app state
    menu_items = app_state.get_current_menu_items()
    selected_index = app_state.get_current_menu_index()
    
    # Generate footer hint
    key_prev = pygame.key.name(config_module.KEY_PREV).upper()
    key_next = pygame.key.name(config_module.KEY_NEXT).upper()
    key_select = pygame.key.name(config_module.KEY_SELECT).upper()
    footer_hint = f"< {key_prev}=Up | {key_next}=Down | {key_select}=Select >"
    
    # Use the standardized list menu component
    draw_scrollable_list_menu(
        screen=screen,
        title="Schematics",
        menu_items=menu_items,
        selected_index=selected_index,
        fonts=fonts,
        config_module=config_module,
        footer_hint=footer_hint,
        item_style="simple",
        ui_scaler=ui_scaler
    ) 