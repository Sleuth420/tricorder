# --- ui/views/settings/sound_test_view.py ---
# Handles rendering of the sound test screen

import pygame
import logging
from ui.components.menus.list_menu_base import draw_simple_list_menu
from ui.components.text.text_display import render_footer, render_text
from ui.views.settings.audio_test_screen import draw_audio_test_screen
import config as app_config

logger = logging.getLogger(__name__)

def draw_sound_test_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the sound test screen content - either simple menu or dedicated test screen.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
        ui_scaler (UIScaler, optional): UI scaling system for responsive design
    """
    # Check if AudioManager is available
    if not hasattr(app_state, 'audio_manager') or not app_state.audio_manager:
        screen.fill(config_module.Theme.BACKGROUND)
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        
        error_msg = "AudioManager not available in AppState"
        logger.error(error_msg)
        font_medium = fonts['medium']
        err_surf = font_medium.render(error_msg, True, config_module.Theme.ALERT)
        screen.blit(err_surf, (screen_width // 2 - err_surf.get_width() // 2, screen_height // 2))
        render_footer(screen, "Error - Press Back", fonts, config_module.Theme.FOREGROUND, screen_width, screen_height)
        return

    # Check if we should show the dedicated test screen
    if hasattr(app_state, 'show_audio_test_screen') and app_state.show_audio_test_screen:
        draw_audio_test_screen(screen, app_state, fonts, config_module, ui_scaler)
        return

    # Get current selection index from app_state
    current_selection_idx = getattr(app_state, 'sound_test_option_index', 0)
    
    # Define sound test menu items
    sound_test_items = [
        "Advanced Audio Test",
        "Quick Test Sound",
        "Stop Music", 
        "<- Back to Settings"
    ]
    
    # Use the shared list menu component
    draw_simple_list_menu(
        screen=screen,
        title="Sound Test",
        menu_items=sound_test_items,
        selected_index=current_selection_idx,
        fonts=fonts,
        config_module=config_module,
        footer_hint="Select to test audio",
        ui_scaler=ui_scaler
    )
