# --- ui/display_manager.py ---
# Coordinates which view to show based on application state

import pygame
import logging
from models.app_state import STATE_MENU, STATE_DASHBOARD, STATE_SENSOR_VIEW, STATE_SYSTEM_INFO, STATE_SETTINGS, STATE_SECRET_GAMES, STATE_PONG_ACTIVE, STATE_BREAKOUT_ACTIVE, STATE_SNAKE_ACTIVE, STATE_TETRIS_ACTIVE, STATE_SCHEMATICS, STATE_SCHEMATICS_MENU, STATE_SCHEMATICS_CATEGORY, STATE_MEDIA_PLAYER, STATE_ST_WIKI, STATE_SENSORS_MENU, STATE_SETTINGS_DISPLAY, STATE_SETTINGS_DEVICE, STATE_SETTINGS_CONTROLS, STATE_SETTINGS_UPDATE, STATE_SETTINGS_STAPI, STATE_SETTINGS_SOUND_TEST, STATE_SETTINGS_DEBUG, STATE_SETTINGS_DEBUG_OVERLAY, STATE_SETTINGS_LOG_VIEWER, STATE_CONFIRM_REBOOT, STATE_CONFIRM_SHUTDOWN, STATE_CONFIRM_RESTART_APP, STATE_SELECT_COMBO_DURATION, STATE_SETTINGS_VOLUME, STATE_DISPLAY_CYCLE_INTERVAL, STATE_SETTINGS_WIFI, STATE_SETTINGS_WIFI_NETWORKS, STATE_WIFI_PASSWORD_ENTRY, STATE_SETTINGS_BLUETOOTH, STATE_SETTINGS_BLUETOOTH_DEVICES, STATE_LOADING
from ui.menu import draw_menu_screen
from ui.views.sensors.sensor_view import draw_sensor_view
from ui.views.system.system_info_view import draw_system_info_view
from ui.views.settings.settings_view import draw_settings_view
from ui.views.games.secret_games_view import draw_secret_games_view
from ui.views.schematics.schematics_3d_viewer import draw_schematics_view
from ui.views.sensors.sensors_menu_view import draw_sensors_menu_view
from ui.views.settings.display_settings_view import draw_display_settings_view, draw_display_cycle_interval_view
from ui.views.settings.device_settings_view import draw_device_settings_view
from ui.views.settings.controls_view import draw_controls_view
from ui.views.settings.confirmation_view import draw_confirmation_view
from ui.views.settings.select_combo_duration_view import draw_select_combo_duration_view
from ui.views.settings.volume_settings_view import draw_volume_settings_view
from ui.views.settings.wifi_settings_view import draw_wifi_settings_view, draw_wifi_networks_view
from ui.views.settings.wifi_password_entry_view import draw_wifi_password_entry_view
from ui.views.settings.bluetooth_settings_view import draw_bluetooth_settings_view
from ui.views.settings.bluetooth_devices_view import draw_bluetooth_devices_view
from ui.views.settings.update_view import draw_update_view
from ui.views.settings.sound_test_view import draw_sound_test_view
from ui.views.settings.debug_settings_view import draw_debug_settings_view
from ui.views.settings.debug_overlay_view import draw_debug_overlay_view
from ui.views.settings.log_viewer_view import draw_log_viewer_view
from ui.views.schematics.schematics_menu_view import draw_schematics_menu_view
from ui.views.schematics.schematics_category_view import draw_schematics_category_view
from ui.views.schematics.media_player_view import draw_media_player_view
from ui.views.schematics.star_trek_wiki_view import draw_star_trek_wiki_view
from ui.views.settings.stapi_settings_view import draw_stapi_settings_view

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

    # set_mode() resets SDL cursor visibility; re-hide for kiosk mode
    pygame.mouse.set_visible(False)
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

        # set_mode() resets SDL cursor visibility; re-hide for kiosk mode
        pygame.mouse.set_visible(False)

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

def _draw_game_into_display(screen, game, fonts, config_module, ui_scaler):
    """Draw the game onto the screen using the app safe area when enabled (games use our UI)."""
    if ui_scaler and getattr(ui_scaler, 'safe_area_enabled', False):
        game_rect = ui_scaler.get_safe_area_rect()
        game_surface = screen.subsurface(game_rect)
        game.draw(game_surface, fonts, config_module)
    else:
        game.draw(screen, fonts, config_module)

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

    # Re-hide mouse cursor every frame (kiosk mode). VLC detach, games, and display mode
    # switches can cause SDL/OS to show the cursor again; re-assert hidden here.
    pygame.mouse.set_visible(False)
    
    # Handle UI component setup for managers that need UI components
    # Note: We handle UI components here in display_manager, not in the models themselves
    # This keeps models pure (data/business logic only) and UI concerns in UI layer
    
    # Check if we need to switch display modes
    screen = _switch_display_mode_if_needed(app_state)
    if not screen:
        logger.error("Failed to get valid display surface")
        return
        
    # Normal background fill (skip when media player is showing video to avoid flicker:
    # VLC draws into the same window; clearing every frame fights VLC on Pi/X11)
    show_video = (
        app_state.current_state == STATE_MEDIA_PLAYER
        and hasattr(app_state, "media_player_manager")
        and app_state.media_player_manager
        and (app_state.media_player_manager.is_playing() or app_state.media_player_manager.is_paused())
    )
    if not show_video:
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
    elif app_state.current_state == STATE_SCHEMATICS_CATEGORY:
        # Schematics category: Schematics | Media Player
        draw_schematics_category_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_MEDIA_PLAYER:
        # Media player: embed VLC in our window (same as 3D schematics)
        try:
            wm_info = pygame.display.get_wm_info()
            hwnd = wm_info.get("window")
            if hwnd is not None and hasattr(app_state, "media_player_manager") and app_state.media_player_manager:
                app_state.media_player_manager.set_window_handle(hwnd)
        except Exception:
            pass
        draw_media_player_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_ST_WIKI:
        draw_star_trek_wiki_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SECRET_GAMES:
        # Draw the secret games menu
        draw_secret_games_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_PONG_ACTIVE:
        if app_state.active_pong_game:
            screen.fill(config_module.Theme.BACKGROUND)
            _draw_game_into_display(screen, app_state.active_pong_game, fonts, config_module, current_ui_scaler)
        else:
            logger.error("In PONG_ACTIVE state but no active_pong_game instance found!")
            screen.fill(config_module.Theme.BACKGROUND)
            error_text = fonts['medium'].render("Error: Pong game not loaded", True, config_module.Theme.ALERT)
            cx = current_ui_scaler.screen_width // 2 if current_ui_scaler else screen.get_width() // 2
            cy = current_ui_scaler.screen_height // 2 if current_ui_scaler else screen.get_height() // 2
            screen.blit(error_text, (cx - error_text.get_width()//2, cy - error_text.get_height()//2))
    elif app_state.current_state == STATE_BREAKOUT_ACTIVE:
        if app_state.active_breakout_game:
            screen.fill(config_module.Theme.BACKGROUND)
            _draw_game_into_display(screen, app_state.active_breakout_game, fonts, config_module, current_ui_scaler)
        else:
            logger.error("In BREAKOUT_ACTIVE state but no active_breakout_game instance found!")
            screen.fill(config_module.Theme.BACKGROUND)
            error_text = fonts['medium'].render("Error: Breakout game not loaded", True, config_module.Theme.ALERT)
            cx = current_ui_scaler.screen_width // 2 if current_ui_scaler else screen.get_width() // 2
            cy = current_ui_scaler.screen_height // 2 if current_ui_scaler else screen.get_height() // 2
            screen.blit(error_text, (cx - error_text.get_width()//2, cy - error_text.get_height()//2))
    elif app_state.current_state == STATE_SNAKE_ACTIVE:
        if app_state.active_snake_game:
            screen.fill(config_module.Theme.BACKGROUND)
            _draw_game_into_display(screen, app_state.active_snake_game, fonts, config_module, current_ui_scaler)
        else:
            logger.error("In SNAKE_ACTIVE state but no active_snake_game instance found!")
            screen.fill(config_module.Theme.BACKGROUND)
            error_text = fonts['medium'].render("Error: Snake game not loaded", True, config_module.Theme.ALERT)
            cx = current_ui_scaler.screen_width // 2 if current_ui_scaler else screen.get_width() // 2
            cy = current_ui_scaler.screen_height // 2 if current_ui_scaler else screen.get_height() // 2
            screen.blit(error_text, (cx - error_text.get_width()//2, cy - error_text.get_height()//2))
    elif app_state.current_state == STATE_TETRIS_ACTIVE:
        if app_state.active_tetris_game:
            screen.fill(config_module.Theme.BACKGROUND)
            _draw_game_into_display(screen, app_state.active_tetris_game, fonts, config_module, current_ui_scaler)
        else:
            logger.error("In TETRIS_ACTIVE state but no active_tetris_game instance found!")
            screen.fill(config_module.Theme.BACKGROUND)
            error_text = fonts['medium'].render("Error: Tetris game not loaded", True, config_module.Theme.ALERT)
            cx = current_ui_scaler.screen_width // 2 if current_ui_scaler else screen.get_width() // 2
            cy = current_ui_scaler.screen_height // 2 if current_ui_scaler else screen.get_height() // 2
            screen.blit(error_text, (cx - error_text.get_width()//2, cy - error_text.get_height()//2))
    elif app_state.current_state == STATE_SENSORS_MENU:
        # Draw the sensors menu
        draw_sensors_menu_view(screen, app_state, sensor_values, sensor_history, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SETTINGS_DISPLAY:
        draw_display_settings_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_DISPLAY_CYCLE_INTERVAL:
        draw_display_cycle_interval_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SETTINGS_DEVICE:
        draw_device_settings_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SETTINGS_CONTROLS:
        draw_controls_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SETTINGS_UPDATE:
        draw_update_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SETTINGS_STAPI:
        draw_stapi_settings_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SETTINGS_SOUND_TEST:
        draw_sound_test_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SETTINGS_DEBUG:
        draw_debug_settings_view(screen, app_state, fonts, config_module, current_ui_scaler)
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
    elif app_state.current_state == STATE_SETTINGS_VOLUME:
        draw_volume_settings_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SETTINGS_WIFI:
        draw_wifi_settings_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SETTINGS_BLUETOOTH:
        draw_bluetooth_settings_view(screen, app_state, fonts, config_module, current_ui_scaler)
    elif app_state.current_state == STATE_SETTINGS_BLUETOOTH_DEVICES:
        draw_bluetooth_devices_view(screen, app_state, fonts, config_module, current_ui_scaler)
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
            cx = current_ui_scaler.screen_width // 2 if current_ui_scaler else screen.get_width() // 2
            cy = current_ui_scaler.screen_height // 2 if current_ui_scaler else screen.get_height() // 2
            screen.blit(error_text, (cx - error_text.get_width()//2, cy - error_text.get_height()//2))
    else:
        logger.error(f"Unknown application state: {app_state.current_state}")
        # Draw fallback screen
        screen.fill(config_module.Theme.BACKGROUND)
        error_text = fonts['medium'].render("Error: Unknown state", True, config_module.Theme.ALERT)
        cx = current_ui_scaler.screen_width // 2 if current_ui_scaler else screen.get_width() // 2
        cy = current_ui_scaler.screen_height // 2 if current_ui_scaler else screen.get_height() // 2
        screen.blit(error_text, (cx - error_text.get_width()//2, cy - error_text.get_height()//2))
    # When VLC is showing video it draws directly into the window; do not overwrite with
    # Pygame's surface (flip) or we get menu/video flashing every frame.
    if not show_video:
        # Update and draw debug overlay if enabled
        if hasattr(app_state, 'debug_overlay') and app_state.debug_overlay.enabled:
            app_state.debug_overlay.update()
            app_state.debug_overlay.draw(screen, fonts, config_module)

        # Apply rounded corner clipping to match curved screen protector
        if current_ui_scaler and current_ui_scaler.safe_area_enabled:
            mask_surface = pygame.Surface((current_ui_scaler.screen_width, current_ui_scaler.screen_height), pygame.SRCALPHA)
            mask_surface.fill((0, 0, 0, 0))  # Transparent

            # Draw rounded rectangle in white (visible area); use theme radius app-wide
            safe_rect = current_ui_scaler.get_safe_area_rect()
            corner_radius = getattr(config_module.Theme, 'CORNER_CURVE_RADIUS', 8)
            pygame.draw.rect(mask_surface, (255, 255, 255, 255), safe_rect, border_radius=corner_radius)

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