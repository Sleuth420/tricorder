# --- ui/views/settings/sound_test_view.py ---
# Handles rendering of the sound test screen

import pygame
import logging
from ui.components.menus.list_menu_base import draw_simple_list_menu
from ui.components.text.text_display import render_footer, render_text
from ui.views.settings.audio_test_screen import draw_audio_test_screen
from ui.views.settings.audio_diagnostics_screen import draw_audio_diagnostics_screen
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
        screen_width = ui_scaler.screen_width if ui_scaler else screen.get_width()
        screen_height = ui_scaler.screen_height if ui_scaler else screen.get_height()
        safe_rect = ui_scaler.get_safe_area_rect() if (ui_scaler and ui_scaler.safe_area_enabled) else pygame.Rect(0, 0, screen_width, screen_height)
        error_msg = "AudioManager not available in AppState"
        logger.error(error_msg)
        font_medium = fonts['medium']
        err_surf = font_medium.render(error_msg, True, config_module.Theme.ALERT)
        err_rect = err_surf.get_rect(center=(safe_rect.centerx, safe_rect.centery))
        screen.blit(err_surf, err_rect)
        labels = config_module.get_control_labels()
        render_footer(screen, f"Error - Press {labels['back']}", fonts, config_module.Theme.FOREGROUND, screen_width, screen_height, ui_scaler=ui_scaler, content_center_x=safe_rect.centerx)
        return

    # Check if we should show the dedicated test screen
    if hasattr(app_state, 'show_audio_test_screen') and app_state.show_audio_test_screen:
        draw_audio_test_screen(screen, app_state, fonts, config_module, ui_scaler)
        return
    
    # Check if we should show the diagnostics screen
    if hasattr(app_state, 'show_audio_diagnostics_screen') and app_state.show_audio_diagnostics_screen:
        draw_audio_diagnostics_screen(screen, app_state, fonts, config_module, ui_scaler)
        return

    # Get current selection index from app_state
    current_selection_idx = getattr(app_state, 'sound_test_option_index', 0)
    
    # Define sound test menu items
    sound_test_items = [
        "Advanced Audio Test",
        "Quick Test Sound",
        "Audio Status Info",
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
        footer_hint=f"{config_module.get_control_labels()['select']} to test audio",
        ui_scaler=ui_scaler
    )
