# --- ui/display_manager.py ---
# Coordinates which view to show based on application state

import pygame
import logging
from models.app_state import STATE_MENU, STATE_DASHBOARD, STATE_SENSOR_VIEW, STATE_SYSTEM_INFO, STATE_SETTINGS
from ui.menu import draw_menu_screen
from ui.all_sensors_view import draw_all_sensors_view
from ui.sensor_view import draw_sensor_view

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
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            pygame.mouse.set_visible(False)
            logger.info("Display set to fullscreen mode.")
        else:
            screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
            logger.info(f"Display set to windowed mode ({config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}).")

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

def update_display(screen, app_state, sensor_values, sensor_history, fonts, config):
    """
    Updates the display based on the current application state.
    
    Args:
        screen (pygame.Surface): The screen to draw on
        app_state (AppState): The current application state
        sensor_values (dict): Dictionary of current sensor values
        sensor_history (ReadingHistory): Sensor reading history
        fonts (dict): Dictionary of loaded fonts
        config (module): Configuration module
        
    Returns:
        None
    """
    if not screen or not fonts:
        logger.error("Screen or fonts not initialized for drawing.")
        return
        
    # Draw the appropriate view based on app state
    if app_state.current_state == STATE_MENU:
        # Menu state shows sidebar with system info in main content
        draw_menu_screen(screen, app_state, fonts, config)
    elif app_state.current_state == STATE_DASHBOARD:
        draw_all_sensors_view(screen, app_state, sensor_values, sensor_history, fonts, config)
    elif app_state.current_state == STATE_SENSOR_VIEW:
        # For all sensors, use the standard sensor_view
        draw_sensor_view(screen, app_state, sensor_values, sensor_history, fonts, config)
    elif app_state.current_state == STATE_SYSTEM_INFO:
        # System info state shows system info full screen
        draw_menu_screen(screen, app_state, fonts, config)
    elif app_state.current_state == STATE_SETTINGS:
        # Settings state shows settings full screen
        draw_menu_screen(screen, app_state, fonts, config)
    else:
        logger.error(f"Unknown application state: {app_state.current_state}")
        # Draw fallback screen
        screen.fill(config.COLOR_BACKGROUND)
        error_text = fonts['medium'].render("Error: Unknown state", True, config.COLOR_ALERT)
        screen.blit(error_text, (screen.get_width()//2 - error_text.get_width()//2, screen.get_height()//2))
        
    # Update the display
    pygame.display.flip() 