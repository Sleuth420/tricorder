# --- ui/display_manager.py ---
# Coordinates which view to show based on application state

import pygame
import logging
from models.app_state import STATE_MENU, STATE_DASHBOARD, STATE_SENSOR_VIEW, STATE_SYSTEM_INFO, STATE_SETTINGS, STATE_SECRET_GAMES, STATE_PONG_ACTIVE, STATE_BREAKOUT_ACTIVE, STATE_SNAKE_ACTIVE, STATE_SCHEMATICS, STATE_SCHEMATICS_MENU, STATE_SENSORS_MENU, STATE_SETTINGS_DISPLAY, STATE_SETTINGS_DEVICE, STATE_SETTINGS_CONTROLS, STATE_SETTINGS_UPDATE, STATE_SETTINGS_SOUND_TEST, STATE_SETTINGS_DEBUG_OVERLAY, STATE_SETTINGS_LOG_VIEWER, STATE_CONFIRM_REBOOT, STATE_CONFIRM_SHUTDOWN, STATE_CONFIRM_RESTART_APP, STATE_SELECT_COMBO_DURATION, STATE_SETTINGS_WIFI, STATE_SETTINGS_WIFI_NETWORKS, STATE_WIFI_PASSWORD_ENTRY, STATE_LOADING
from ui.menu import draw_menu_screen
from ui.views.sensors.sensor_view import draw_sensor_view
from ui.views.system.system_info_view import draw_system_info_view
from ui.views.settings.settings_view import draw_settings_view
from ui.views.games.secret_games_view import draw_secret_games_view
from ui.views.schematics.schematics_3d_viewer import draw_schematics_view
from ui.views.sensors.sensors_menu_view import draw_sensors_menu_view
from ui.views.settings.display_settings_view import draw_display_settings_view
from ui.views.settings.device_settings_view import draw_device_settings_view
from ui.views.settings.controls_view import draw_controls_view
from ui.views.settings.confirmation_view import draw_confirmation_view
from ui.views.settings.select_combo_duration_view import draw_select_combo_duration_view
from ui.views.settings.wifi_settings_view import draw_wifi_settings_view, draw_wifi_networks_view
from ui.views.settings.wifi_password_entry_view import draw_wifi_password_entry_view
from ui.views.settings.update_view import draw_update_view
from ui.views.settings.sound_test_view import draw_sound_test_view
from ui.views.settings.debug_overlay_view import draw_debug_overlay_view
from ui.views.settings.log_viewer_view import draw_log_viewer_view
from ui.views.schematics.schematics_menu_view import draw_schematics_menu_view

# Import UIScaler for centralized scaling
from utils.ui_scaler import UIScaler

# Temporary placeholder function until schematics_view.py is created
# def draw_schematics_view(screen, app_state, fonts, config_module):
#     logger.info("Placeholder for draw_schematics_view called.")
#     screen.fill(config_module.Theme.BACKGROUND)
#     text_surface = fonts['large'].render("Schematics View (WIP)", True, config_module.Theme.TEXT_ACCENT)
#     screen.blit(text_surface, (50, 50))

logger = logging.getLogger(__name__)

# Global variables to track display mode and UIScaler
current_display_mode = "NORMAL"  # "NORMAL" or "OPENGL"
opengl_screen = None
ui_scaler = None  # Global UIScaler instance

def init_display():
    """
    Initializes Pygame and the display window. Loads fonts and creates UIScaler.

    Returns:
        tuple: (screen_surface, clock_object, loaded_fonts_dict, ui_scaler_instance) or (None, None, None, None) on failure.
    """
    global ui_scaler
    fonts = {}
    try:
        pygame.init()
        pygame.display.set_caption("Tricorder")
        
        # Initialize audio subsystem
        try:
            import config
            pygame.mixer.init(
                frequency=config.AUDIO_FREQUENCY,
                size=-16,  # 16-bit signed
                channels=2,  # Stereo
                buffer=config.AUDIO_BUFFER_SIZE
            )
            logger.info("Pygame audio initialized successfully")
        except pygame.error as e:
            logger.warning(f"Could not initialize pygame audio: {e}")
        except Exception as e:
            logger.warning(f"Audio initialization error: {e}")
        
        import config  # Import here to avoid circular imports
        
        # Start with normal display mode
        screen = _init_normal_display(config)
        
        # Create UIScaler with actual screen dimensions
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        ui_scaler = UIScaler(screen_width, screen_height, config)
        logger.info(f"UIScaler created: {screen_width}x{screen_height}, scale_factor={ui_scaler.scale_factor:.2f}")
        
        # Hide mouse cursor for kiosk mode (both fullscreen and windowed)
        pygame.mouse.set_visible(False)
        logger.info("Mouse cursor hidden for kiosk mode")

        # Load fonts
        try:
            fonts['large'] = pygame.font.Font(config.FONT_PRIMARY_PATH, config.FONT_SIZE_LARGE)
            fonts['medium'] = pygame.font.Font(config.FONT_PRIMARY_PATH, config.FONT_SIZE_MEDIUM)
            fonts['small'] = pygame.font.Font(config.FONT_PRIMARY_PATH, config.FONT_SIZE_SMALL)
            fonts['tiny'] = pygame.font.Font(config.FONT_PRIMARY_PATH, config.FONT_SIZE_TINY)
            logger.info(f"Custom font '{config.FONT_PRIMARY_PATH}' loaded successfully.")
        except Exception as e:
            logger.warning(f"Could not load custom font ('{config.FONT_PRIMARY_PATH}'): {e}. Using default font.")
            fonts['large'] = pygame.font.SysFont(None, config.FONT_SIZE_LARGE)
            fonts['medium'] = pygame.font.SysFont(None, config.FONT_SIZE_MEDIUM)
            fonts['small'] = pygame.font.SysFont(None, config.FONT_SIZE_SMALL)
            fonts['tiny'] = pygame.font.SysFont(None, config.FONT_SIZE_TINY)
            
        # Make sure there's a default font for fallback
        fonts['default'] = fonts['medium']

        clock = pygame.time.Clock()
        logger.info("Pygame display and clock initialized.")
        return screen, clock, fonts, ui_scaler

    except Exception as e:
        logger.error(f"Error initializing display: {e}", exc_info=True)
        pygame.quit()
        return None, None, None, None

def _init_normal_display(config):
    """Initialize normal pygame display mode."""
    global current_display_mode
    
    if config.FULLSCREEN:
        screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), pygame.FULLSCREEN)
        logger.info(f"Display set to fullscreen mode, requesting {config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}.")
    else:
        screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        logger.info(f"Display set to windowed mode ({config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}).")
    
    current_display_mode = "NORMAL"
    return screen

def _init_opengl_display(config):
    """Initialize OpenGL display mode."""
    global current_display_mode, opengl_screen, ui_scaler
    
    try:
        # Import OpenGL to check availability
        import OpenGL.GL as gl
        import OpenGL.GLU as glu
        
        if config.FULLSCREEN:
            opengl_screen = pygame.display.set_mode(
                (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), 
                pygame.FULLSCREEN | pygame.OPENGL | pygame.DOUBLEBUF
            )
        else:
            opengl_screen = pygame.display.set_mode(
                (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), 
                pygame.OPENGL | pygame.DOUBLEBUF
            )
        
        # Set up OpenGL viewport
        gl.glViewport(0, 0, config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
        
        # Update UIScaler if screen dimensions changed
        if ui_scaler:
            screen_width = opengl_screen.get_width()
            screen_height = opengl_screen.get_height()
            if screen_width != ui_scaler.screen_width or screen_height != ui_scaler.screen_height:
                ui_scaler = UIScaler(screen_width, screen_height, config)
                logger.info(f"UIScaler updated for OpenGL mode: {screen_width}x{screen_height}")
        
        current_display_mode = "OPENGL"
        logger.info("OpenGL display mode initialized")
        return opengl_screen
        
    except ImportError:
        logger.error("OpenGL not available, cannot switch to OpenGL mode")
        return None
    except Exception as e:
        logger.error(f"Failed to initialize OpenGL display: {e}")
        return None

def _needs_opengl_mode(app_state):
    """Check if current state needs OpenGL mode."""
    # Don't switch to OpenGL during loading - stay in pygame mode for loading screen
    if app_state.current_state == STATE_LOADING:
        return False
        
    if app_state.current_state == STATE_SCHEMATICS:
        # Check if current schematics model needs OpenGL rendering
        current_schematics_info = app_state.schematics_manager.get_current_schematics_info()
        if current_schematics_info:
            model_key = current_schematics_info.get('model_key')
            # OpenGL models need OpenGL mode
            if model_key in ['worf', 'apollo_1570', 'apollo_1701_refit']:
                return True
    return False

def _switch_display_mode_if_needed(app_state):
    """Switch display mode if needed for current state."""
    global current_display_mode, ui_scaler
    
    needs_opengl = _needs_opengl_mode(app_state)
    
    if needs_opengl and current_display_mode != "OPENGL":
        # Switch to OpenGL mode
        import config
        screen = _init_opengl_display(config)
        if screen:
            # Reset any existing OpenGL renderers since we have a new context
            if hasattr(app_state, 'schematics_manager'):
                if app_state.schematics_manager.opengl_renderer:
                    app_state.schematics_manager.opengl_renderer.reset_for_new_context()
                if app_state.schematics_manager.model_renderer:
                    app_state.schematics_manager.model_renderer.reset_for_new_context()
            logger.info("Switched to OpenGL display mode")
            return screen
        else:
            logger.warning("Failed to switch to OpenGL mode, staying in normal mode")
            return pygame.display.get_surface()
    
    elif not needs_opengl and current_display_mode != "NORMAL":
        # Switch back to normal mode
        import config
        screen = _init_normal_display(config)
        # Update UIScaler for normal mode
        if ui_scaler:
            screen_width = screen.get_width()
            screen_height = screen.get_height()
            if screen_width != ui_scaler.screen_width or screen_height != ui_scaler.screen_height:
                ui_scaler = UIScaler(screen_width, screen_height, config)
                logger.info(f"UIScaler updated for normal mode: {screen_width}x{screen_height}")
        logger.info("Switched back to normal display mode")
        return screen
    
    # No mode change needed
    return pygame.display.get_surface()

def update_display(screen, app_state, sensor_values, sensor_history, fonts, config_module, ui_scaler_instance=None):
    """
    Updates the display based on the current application state.
    
    Args:
        screen (pygame.Surface): The screen to draw on
        app_state (AppState): The current application state
        sensor_values (dict): Dictionary of current sensor values
        sensor_history (ReadingHistory): Sensor reading history
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
        ui_scaler_instance (UIScaler, optional): UI scaling system instance
        
    Returns:
        None
    """
    global ui_scaler
    
    if not screen or not fonts:
        logger.error("Screen or fonts not initialized for drawing.")
        return
    
    # Use provided UIScaler or fall back to global instance
    current_ui_scaler = ui_scaler_instance or ui_scaler
    if not current_ui_scaler:
        logger.warning("No UIScaler available, creating temporary instance")
        current_ui_scaler = UIScaler(screen.get_width(), screen.get_height(), config_module)
    
    # Handle UI component setup for managers that need UI components
    # Note: We handle UI components here in display_manager, not in the models themselves
    # This keeps models pure (data/business logic only) and UI concerns in UI layer
    
    # Check if we need to switch display modes
    screen = _switch_display_mode_if_needed(app_state)
    if not screen:
        logger.error("Failed to get valid display surface")
        return
        
    # Normal background fill
    screen.fill(config_module.Theme.BACKGROUND)

    # Draw the appropriate view based on app state
    if app_state.current_state == STATE_MENU:
        # Menu state shows sidebar with system info in main content
        draw_menu_screen(screen, app_state, fonts, config_module, sensor_values, current_ui_scaler)
    elif app_state.current_state == STATE_DASHBOARD:
        # Use the merged sensor view for the dashboard
        draw_sensor_view(screen, app_state, sensor_values, sensor_history, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SENSOR_VIEW:
        # For all sensors, use the standard sensor_view
        draw_sensor_view(screen, app_state, sensor_values, sensor_history, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SYSTEM_INFO:
        # System info state shows system info full screen using the new view
        draw_system_info_view(screen, app_state, sensor_values, fonts, config_module, ui_scaler=current_ui_scaler)
    elif app_state.current_state == STATE_SETTINGS:
        # Settings state shows settings full screen using the new view
        draw_settings_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SCHEMATICS:
        # Schematics state will show the 3D model viewer
        if current_display_mode == "OPENGL":
            # For OpenGL mode, we need special handling
            _render_opengl_schematics(screen, app_state, fonts, config_module, current_ui_scaler)
        else:
            # Normal mode rendering
            draw_schematics_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SCHEMATICS_MENU:
        # Schematics selection menu
        draw_schematics_menu_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SECRET_GAMES:
        # Draw the secret games menu
        draw_secret_games_view(screen, app_state, fonts, config_module, current_ui_scaler)
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
    elif app_state.current_state == STATE_BREAKOUT_ACTIVE:
        # Draw the active Breakout game
        if app_state.active_breakout_game:
            # Clear background before drawing game
            screen.fill(config_module.Theme.BACKGROUND)
            app_state.active_breakout_game.draw(screen, fonts, config_module)
        else:
            logger.error("In BREAKOUT_ACTIVE state but no active_breakout_game instance found!")
            # Draw fallback screen (optional)
            screen.fill(config_module.Theme.BACKGROUND)
            error_text = fonts['medium'].render("Error: Breakout game not loaded", True, config_module.Theme.ALERT)
            screen.blit(error_text, (screen.get_width()//2 - error_text.get_width()//2, screen.get_height()//2))
    elif app_state.current_state == STATE_SNAKE_ACTIVE:
        # Draw the active Snake game
        if app_state.active_snake_game:
            # Clear background before drawing game
            screen.fill(config_module.Theme.BACKGROUND)
            app_state.active_snake_game.draw(screen, fonts, config_module)
        else:
            logger.error("In SNAKE_ACTIVE state but no active_snake_game instance found!")
            # Draw fallback screen (optional)
            screen.fill(config_module.Theme.BACKGROUND)
            error_text = fonts['medium'].render("Error: Snake game not loaded", True, config_module.Theme.ALERT)
            screen.blit(error_text, (screen.get_width()//2 - error_text.get_width()//2, screen.get_height()//2))
    elif app_state.current_state == STATE_SENSORS_MENU:
        # Draw the sensors menu
        draw_sensors_menu_view(screen, app_state, sensor_values, sensor_history, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SETTINGS_DISPLAY:
        draw_display_settings_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SETTINGS_DEVICE:
        draw_device_settings_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SETTINGS_CONTROLS:
        draw_controls_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SETTINGS_UPDATE:
        draw_update_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SETTINGS_SOUND_TEST:
        draw_sound_test_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SETTINGS_DEBUG_OVERLAY:
        draw_debug_overlay_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SETTINGS_LOG_VIEWER:
        draw_log_viewer_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_CONFIRM_REBOOT:
        draw_confirmation_view(screen, app_state, fonts, config_module, message="Reboot Device?", ui_scaler=current_ui_scaler)
    elif app_state.current_state == STATE_CONFIRM_SHUTDOWN:
        draw_confirmation_view(screen, app_state, fonts, config_module, message="Shutdown Device?", ui_scaler=current_ui_scaler)
    elif app_state.current_state == STATE_CONFIRM_RESTART_APP:
        draw_confirmation_view(screen, app_state, fonts, config_module, message="Restart Application?", ui_scaler=current_ui_scaler)
    elif app_state.current_state == STATE_SELECT_COMBO_DURATION:
        draw_select_combo_duration_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SETTINGS_WIFI:
        draw_wifi_settings_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SETTINGS_WIFI_NETWORKS:
        draw_wifi_networks_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_WIFI_PASSWORD_ENTRY:
        # Set fonts for password entry manager if not already set
        if not app_state.password_entry_manager.character_selector.fonts:
            app_state.password_entry_manager.character_selector.fonts = fonts
        draw_wifi_password_entry_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_LOADING:
        # Draw loading screen - handle UI component setup here in display layer
        loading_screen = app_state.get_loading_screen()
        if loading_screen:
            # Set UIScaler on loading screen UI component directly
            if current_ui_scaler and hasattr(loading_screen, 'set_ui_scaler'):
                loading_screen.set_ui_scaler(current_ui_scaler)
            loading_screen.draw(screen, fonts)
        else:
            # Fallback if no loading screen
            screen.fill(config_module.Theme.BACKGROUND)
            error_text = fonts['medium'].render("Loading...", True, config_module.Theme.FOREGROUND)
            screen.blit(error_text, (screen.get_width()//2 - error_text.get_width()//2, screen.get_height()//2))
    else:
        logger.error(f"Unknown application state: {app_state.current_state}")
        # Draw fallback screen
        screen.fill(config_module.Theme.BACKGROUND)
        error_text = fonts['medium'].render("Error: Unknown state", True, config_module.Theme.ALERT)
        screen.blit(error_text, (screen.get_width()//2 - error_text.get_width()//2, screen.get_height()//2))
    
    # Update and draw debug overlay if enabled
    if hasattr(app_state, 'debug_overlay') and app_state.debug_overlay.enabled:
        app_state.debug_overlay.update()
        app_state.debug_overlay.draw(screen, fonts, config_module)
    
    # Apply rounded corner clipping to match curved screen protector
    if current_ui_scaler and current_ui_scaler.safe_area_enabled:
        # Create a mask surface for rounded corners
        mask_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        mask_surface.fill((0, 0, 0, 0))  # Transparent
        
        # Draw rounded rectangle in white (visible area)
        safe_rect = current_ui_scaler.get_safe_area_rect()
        pygame.draw.rect(mask_surface, (255, 255, 255, 255), safe_rect, border_radius=25)
        
        # Apply the mask to clip content to rounded corners
        screen.blit(mask_surface, (0, 0), special_flags=pygame.BLEND_MULT)
        
    # Update the display
    pygame.display.flip()

def _render_opengl_schematics(screen, app_state, fonts, config_module, ui_scaler):
    """Handle OpenGL rendering for schematics view with full UI controls."""
    # Import here to avoid circular imports
    from ui.views.schematics.schematics_3d_viewer import draw_schematics_view
    
    # Use the normal schematics view which handles all controls,
    # but the schematics manager will automatically use OpenGL rendering
    # when the current model is 'worf', 'apollo_1570', or 'apollo_1701_refit'
    draw_schematics_view(screen, app_state, fonts, config_module, ui_scaler)