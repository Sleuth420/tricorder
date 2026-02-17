# --- ui/views/settings/settings_view.py ---
# Handles rendering of the settings screen using shared list menu component

import pygame
import logging
from ui.components.menus.list_menu_base import draw_simple_list_menu
from utils.ui_scaler import UIScaler
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
    # Add update available header if needed (respect safe area for curved bezel)
    menu_ui_scaler = ui_scaler
    if hasattr(app_state, 'update_available') and app_state.update_available:
        screen.fill(config_module.Theme.BACKGROUND)
        w = ui_scaler.screen_width if ui_scaler else screen.get_width()
        h = ui_scaler.screen_height if ui_scaler else screen.get_height()
        safe_rect = ui_scaler.get_safe_area_rect() if (ui_scaler and ui_scaler.safe_area_enabled) else pygame.Rect(0, 0, w, h)
        header_inset = max(ui_scaler.margin("small"), safe_rect.left) if ui_scaler else 20
        content_top = ui_scaler.scale(60) if ui_scaler else 60
        header_text = "[UPDATE AVAILABLE]"
        header_surface = fonts['medium'].render(header_text, True, config_module.Theme.ALERT)
        screen.blit(header_surface, (header_inset, safe_rect.top + (ui_scaler.margin("small") if ui_scaler else 8)))
        content_rect = pygame.Rect(safe_rect.left, content_top, safe_rect.width, safe_rect.bottom - content_top)
        menu_screen = screen.subsurface(content_rect)
        # Use a scaler for the content area so the list menu lays out for the reduced height
        # instead of full screen (avoids pushed/cramped layout)
        menu_ui_scaler = UIScaler(content_rect.width, content_rect.height, config_module)
    else:
        menu_screen = screen
    
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
        ui_scaler=menu_ui_scaler
    ) 