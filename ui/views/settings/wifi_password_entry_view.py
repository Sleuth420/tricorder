# --- ui/views/settings/wifi_password_entry_view.py ---
# Handles rendering of the WiFi password entry screen

import pygame
import logging

logger = logging.getLogger(__name__)

def draw_wifi_password_entry_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the WiFi password entry screen with character selector optimized for screen size.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        ui_scaler (UIScaler, optional): UI scaling system for responsive design
    """
    try:
        # Get the password entry manager
        password_manager = app_state.password_entry_manager
        if not password_manager:
            logger.error("Password entry manager not available")
            screen.fill(config_module.Theme.BACKGROUND)
            
            # Draw error message
            error_font = fonts.get('medium', fonts.get('default'))
            error_surface = error_font.render("Password Entry Error", True, config_module.Theme.ALERT)
            error_rect = error_surface.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
            screen.blit(error_surface, error_rect)
            return

        # Initialize fonts only once when the character selector is first created
        # This avoids updating fonts on every frame
        if (hasattr(password_manager, 'character_selector') and 
            password_manager.character_selector and 
            not hasattr(password_manager.character_selector, '_fonts_initialized')):
            password_manager.character_selector.set_fonts(fonts)
            password_manager.character_selector._fonts_initialized = True

        # Set UIScaler on character selector UI component directly
        # (UI concerns handled in UI layer, not in models)
        if ui_scaler and hasattr(password_manager, 'character_selector') and password_manager.character_selector:
            if hasattr(password_manager.character_selector, 'set_ui_scaler'):
                password_manager.character_selector.set_ui_scaler(ui_scaler)

        # Use the character selector's draw method which now handles small screen optimization
        password_manager.draw(screen)
        
        logger.debug("WiFi password entry view drawn successfully")
        
    except Exception as e:
        logger.error(f"Error drawing WiFi password entry view: {e}", exc_info=True)
        
        # Draw fallback error display
        screen.fill(config_module.Theme.BACKGROUND)
        error_font = fonts.get('medium', fonts.get('default', pygame.font.Font(None, 20)))
        error_surface = error_font.render(f"Display Error: {str(e)[:30]}", True, config_module.Theme.ALERT)
        error_rect = error_surface.get_rect(center=(screen.get_width()//2, screen.get_height()//2))
        screen.blit(error_surface, error_rect) 