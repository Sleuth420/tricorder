# --- ui/display_manager.py ---
# Coordinates which view to show based on application state

import pygame
import logging
from models.app_state import STATE_MENU, STATE_DASHBOARD, STATE_SENSOR_VIEW, STATE_SYSTEM_INFO, STATE_SETTINGS, STATE_SECRET_GAMES, STATE_PONG_ACTIVE, STATE_SCHEMATICS, STATE_SHIP_MENU, STATE_SENSORS_MENU, STATE_SETTINGS_DISPLAY, STATE_SETTINGS_DEVICE, STATE_CONFIRM_REBOOT, STATE_CONFIRM_SHUTDOWN, STATE_CONFIRM_RESTART_APP, STATE_SELECT_COMBO_DURATION, STATE_SETTINGS_WIFI, STATE_SETTINGS_WIFI_NETWORKS, STATE_WIFI_PASSWORD_ENTRY
from ui.menu import draw_menu_screen
from ui.views.sensor_view import draw_sensor_view
from ui.views.system_info_view import draw_system_info_view
from ui.views.settings.settings_view import draw_settings_view
from ui.views.secret_games_view import draw_secret_games_view
from ui.views.tricorder_schematics import draw_schematics_view
from ui.views.ship_menu_view import draw_ship_menu_view
from ui.views.sensors_menu_view import draw_sensors_menu_view
from ui.views.settings.display_settings_view import draw_display_settings_view
from ui.views.settings.device_settings_view import draw_device_settings_view
from ui.views.settings.confirmation_view import draw_confirmation_view
from ui.views.settings.select_combo_duration_view import draw_select_combo_duration_view
from ui.views.settings.wifi_settings_view import draw_wifi_settings_view, draw_wifi_networks_view
from ui.views.settings.wifi_password_entry_view import draw_wifi_password_entry_view

# Temporary placeholder function until schematics_view.py is created
# def draw_schematics_view(screen, app_state, fonts, config_module):
#     logger.info("Placeholder for draw_schematics_view called.")
#     screen.fill(config_module.Theme.BACKGROUND)
#     text_surface = fonts['large'].render("Schematics View (WIP)", True, config_module.Theme.TEXT_ACCENT)
#     screen.blit(text_surface, (50, 50))

logger = logging.getLogger(__name__)

def init_display():
    """
    Initializes Pygame and the display window. Loads fonts.

    Returns:
        tuple: (screen_surface, clock_object, loaded_fonts_dict) or (None, None, None) on failure.
    """
    fonts = {}
    try:
        pygame.init()
        pygame.display.set_caption("Tricorder")
        
        import config  # Import here to avoid circular imports
        
        if config.FULLSCREEN:
            # MODIFIED LINE: Explicitly request config.SCREEN_WIDTH and config.SCREEN_HEIGHT
            screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.FULLSCREEN)
            logger.info(f"Display set to fullscreen mode, requesting {config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}.") # Updated log
        else:
            screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            logger.info(f"Display set to windowed mode ({config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}).")
        
        # Hide mouse cursor for kiosk mode (both fullscreen and windowed)
        pygame.mouse.set_visible(False)
        logger.info("Mouse cursor hidden for kiosk mode")

        # Load fonts
        try:
            fonts['large'] = pygame.font.Font(config.FONT_PRIMARY_PATH, config.FONT_SIZE_LARGE)
            fonts['medium'] = pygame.font.Font(config.FONT_PRIMARY_PATH, config.FONT_SIZE_MEDIUM)
            fonts['small'] = pygame.font.Font(config.FONT_PRIMARY_PATH, config.FONT_SIZE_SMALL)
            logger.info(f"Custom font '{config.FONT_PRIMARY_PATH}' loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not load custom font ('{config.FONT_PRIMARY_PATH}'): {e}. Using default font.")
            fonts['large'] = pygame.font.SysFont(None, config.FONT_SIZE_LARGE)
            fonts['medium'] = pygame.font.SysFont(None, config.FONT_SIZE_MEDIUM)
            fonts['small'] = pygame.font.SysFont(None, config.FONT_SIZE_SMALL)
            
        # Make sure there's a default font for fallback
        fonts['default'] = fonts['medium']

        clock = pygame.time.Clock()
        logger.info("Pygame display and clock initialized.")
        return screen, clock, fonts

    except Exception as e:
        logger.error(f"Error initializing display: {e}", exc_info=True)
        pygame.quit()
        return None, None, None

def update_display(screen, app_state, sensor_values, sensor_history, fonts, config_module):
    """
    Updates the display based on the current application state.
    
    Args:
        screen (pygame.Surface): The screen to draw on
        app_state (AppState): The current application state
        sensor_values (dict): Dictionary of current sensor values
        sensor_history (ReadingHistory): Sensor reading history
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
        
    Returns:
        None
    """
    if not screen or not fonts:
        logger.error("Screen or fonts not initialized for drawing.")
        return
        
    # Draw the appropriate view based on app state
    if app_state.current_state == STATE_MENU:
        # Menu state shows sidebar with system info in main content
        draw_menu_screen(screen, app_state, fonts, config_module, sensor_values)
    elif app_state.current_state == STATE_DASHBOARD:
        # Use the merged sensor view for the dashboard
        draw_sensor_view(screen, app_state, sensor_values, sensor_history, fonts, config_module)
    elif app_state.current_state == STATE_SENSOR_VIEW:
        # For all sensors, use the standard sensor_view
        draw_sensor_view(screen, app_state, sensor_values, sensor_history, fonts, config_module)
    elif app_state.current_state == STATE_SYSTEM_INFO:
        # System info state shows system info full screen using the new view
        draw_system_info_view(screen, app_state, sensor_values, fonts, config_module)
    elif app_state.current_state == STATE_SETTINGS:
        # Settings state shows settings full screen using the new view
        draw_settings_view(screen, app_state, fonts, config_module)
    elif app_state.current_state == STATE_SCHEMATICS:
        # Schematics state will show the 3D model viewer
        draw_schematics_view(screen, app_state, fonts, config_module)
    elif app_state.current_state == STATE_SHIP_MENU:
        # Ship selection menu
        draw_ship_menu_view(screen, app_state, fonts, config_module)
    elif app_state.current_state == STATE_SECRET_GAMES:
        # Draw the secret games menu
        draw_secret_games_view(screen, app_state, fonts, config_module)
    elif app_state.current_state == STATE_PONG_ACTIVE:
        # Draw the active Pong game
        if app_state.active_pong_game:
            # Clear background before drawing game
            screen.fill(config_module.Theme.BACKGROUND)
            app_state.active_pong_game.draw(screen, fonts, config_module)
        else:
            logger.error("In PONG_ACTIVE state but no active_pong_game instance found!")
            # Draw fallback screen (optional)
            screen.fill(config_module.Theme.BACKGROUND)
            error_text = fonts['medium'].render("Error: Pong game not loaded", True, config_module.Theme.ALERT)
            screen.blit(error_text, (screen.get_width()//2 - error_text.get_width()//2, screen.get_height()//2))
    elif app_state.current_state == STATE_SENSORS_MENU:
        # Draw the sensors menu
        draw_sensors_menu_view(screen, app_state, sensor_values, sensor_history, fonts, config_module)
    elif app_state.current_state == STATE_SETTINGS_DISPLAY:
        draw_display_settings_view(screen, app_state, fonts, config_module)
    elif app_state.current_state == STATE_SETTINGS_DEVICE:
        draw_device_settings_view(screen, app_state, fonts, config_module)
    elif app_state.current_state == STATE_CONFIRM_REBOOT:
        draw_confirmation_view(screen, app_state, fonts, config_module, message="Reboot Device?")
    elif app_state.current_state == STATE_CONFIRM_SHUTDOWN:
        draw_confirmation_view(screen, app_state, fonts, config_module, message="Shutdown Device?")
    elif app_state.current_state == STATE_CONFIRM_RESTART_APP:
        draw_confirmation_view(screen, app_state, fonts, config_module, message="Restart Application?")
    elif app_state.current_state == STATE_SELECT_COMBO_DURATION:
        draw_select_combo_duration_view(screen, app_state, fonts, config_module)
    elif app_state.current_state == STATE_SETTINGS_WIFI:
        draw_wifi_settings_view(screen, app_state, fonts, config_module)
    elif app_state.current_state == STATE_SETTINGS_WIFI_NETWORKS:
        draw_wifi_networks_view(screen, app_state, fonts, config_module)
    elif app_state.current_state == STATE_WIFI_PASSWORD_ENTRY:
        # Set fonts for password entry manager if not already set
        if not app_state.password_entry_manager.character_selector.fonts:
            app_state.password_entry_manager.character_selector.fonts = fonts
        draw_wifi_password_entry_view(screen, app_state, fonts, config_module)
    else:
        logger.error(f"Unknown application state: {app_state.current_state}")
        # Draw fallback screen
        screen.fill(config_module.Theme.BACKGROUND)
        error_text = fonts['medium'].render("Error: Unknown state", True, config_module.Theme.ALERT)
        screen.blit(error_text, (screen.get_width()//2 - error_text.get_width()//2, screen.get_height()//2))
        
    # Update the display
    pygame.display.flip()