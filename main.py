# --- main.py ---
# Main application file for the Raspberry Pi tricorder
# Now with menu-based navigation and modular structure

import sys
import pygame
import logging
import time
import platform
import os
import threading

# Force SDL to use x11 video driver BEFORE pygame.init() - but only on Linux
if platform.system() == "Linux":
    os.environ["SDL_VIDEODRIVER"] = "x11"

# Import configuration and logging modules
import config
import logging_config

# Import application components from the new modular structure
from models.app_state import AppState, STATE_MENU, STATE_PONG_ACTIVE, STATE_BREAKOUT_ACTIVE, STATE_SNAKE_ACTIVE
from models.reading_history import ReadingHistory
from data import sensors
from data import system_info
# Import the new data updater function
from data.data_updater import update_all_data, update_sensors_by_schedule
from data.sense_hat_led import update_led_display
from ui.display_manager import init_display, update_display
from input.input_handler import process_input, init_joystick
from utils.error_handling import display_critical_error_on_screen
from ui.components.loading.main_loading_screen import draw_loading_screen, LoadingProgress, loading_worker

# Get a logger for this module
logger = logging.getLogger(__name__)

def main():
    """Main function to run the tricorder application."""
    logging_config.setup_logging()
    logger.info("Starting tricorder Application...")
    
    # Log version information
    from config import version
    version_info = version.get_version_info()
    logger.info(f"Build: {version_info['build_number']}")
    logger.info(f"Git commit: {version_info['commit_hash']}")
    
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Python version: {platform.python_version()}")
    logger.info(f"Display size: {config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}, Fullscreen: {config.FULLSCREEN}")
    logger.info(f"Available sensor modes: {', '.join(config.SENSOR_MODES)}")

    # Critical Initialization: Display
    screen, clock, fonts, ui_scaler = init_display()
    if not screen:
        logger.critical("Fatal Error: Could not initialize display. Application cannot continue.")
        sys.exit(1) # Exit if display fails - app is unusable
    logger.info("Display initialized successfully.")

    # Get actual screen dimensions after display initialization
    actual_screen_width = screen.get_width()
    actual_screen_height = screen.get_height()
    logger.info(f"Actual screen dimensions: {actual_screen_width}x{actual_screen_height}")

    # Initialize Models using the new modular architecture
    app_state = AppState(config, actual_screen_width, actual_screen_height)
    app_state.ui_scaler = ui_scaler  # So games and UI use safe area / scaling
    if hasattr(app_state, 'debug_overlay') and app_state.debug_overlay:
        app_state.debug_overlay.set_ui_scaler(ui_scaler)
    if hasattr(app_state, 'password_entry_manager') and app_state.password_entry_manager:
        app_state.password_entry_manager.set_ui_scaler(ui_scaler)
    reading_history = ReadingHistory(config.ALL_SENSOR_MODES, config.GRAPH_HISTORY_SIZE)
    logger.info("Application state and reading history initialized.")

    exit_code = 0
    try:
        # Non-critical Initializations (loading screen with splash, sensors)
        try:
            logo_splash = pygame.image.load(config.SPLASH_LOGO_PATH).convert_alpha()
            # Use UIScaler for logo size and position (best practice: no raw screen dimensions)
            target_width = ui_scaler.scale(160)  # ~50% of base 320
            aspect_ratio = logo_splash.get_height() / logo_splash.get_width()
            target_height = int(target_width * aspect_ratio)
            logo_splash = pygame.transform.smoothscale(logo_splash, (target_width, target_height))
            logo_center_x = ui_scaler.screen_width // 2
            logo_center_y = ui_scaler.scale(72)  # ~30% of base 240
            logo_rect = logo_splash.get_rect(center=(logo_center_x, logo_center_y))
            
            logger.info("Starting loading screen...")
            
            # Create progress tracker and start loading worker
            progress_tracker = LoadingProgress()
            progress_tracker.app_state = app_state  # Pass app_state for update check
            loading_thread = threading.Thread(target=loading_worker, args=(progress_tracker,))
            loading_thread.daemon = True
            loading_thread.start()
            
            # Loading screen loop - minimum duration from config
            loading_start_time = time.time()
            minimum_loading_time = config.LOADING_SCREEN_MIN_DURATION
            
            while True:
                current_time = time.time()
                elapsed_time = current_time - loading_start_time
                
                # Get current loading status
                current_lines, total_lines, stage, complete, scan_progress = progress_tracker.get_status()
                
                # Calculate progress (combination of time and completion)
                time_progress = min(elapsed_time / minimum_loading_time, 1.0)
                
                # If loading is complete and minimum time has passed
                if complete and elapsed_time >= minimum_loading_time:
                    progress = 1.0
                    draw_loading_screen(screen, fonts, logo_splash, logo_rect, progress, current_lines, total_lines, stage, ui_scaler, scan_progress, elapsed_time)
                    time.sleep(0.5)  # Brief pause to show 100%
                    break
                elif complete:
                    # Loading done but minimum time not reached - show time-based progress
                    progress = time_progress
                else:
                    # Loading not done - show partial progress based on time
                    progress = time_progress * 0.9  # Max 90% until actually complete
                
                # Draw the loading screen
                draw_loading_screen(screen, fonts, logo_splash, logo_rect, progress, current_lines, total_lines, stage, ui_scaler, scan_progress, elapsed_time)
                
                # Handle quit events during loading
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        logger.info("pygame.QUIT event received during loading. Exiting.")
                        pygame.quit()
                        sys.exit(0)
                
                # Small delay to prevent excessive CPU usage
                time.sleep(0.1)
            
            logger.info("Loading screen finished.")
            
        except Exception as e_splash:
            logger.warning(f"Could not load or display loading screen: {e_splash}", exc_info=True)

        try:
            sensors_active = sensors.init_sensors()
            if not sensors_active:
                logger.warning("Could not initialize Sense HAT. Sensor readings will show errors.")
            else:
                logger.info("Sensors initialized successfully.")
                # Initialize joystick after sensors are initialized
                if init_joystick():
                    logger.info("Joystick initialized successfully")
                else:
                    logger.warning("Could not initialize joystick")
        except Exception as e_sensors:
            logger.error(f"Error initializing sensors: {e_sensors}", exc_info=True)
            sensors_active = False # Assume sensors are not active if init fails

        sensor_values = {}
        running = True
        last_sensor_update_times = {}  # Track when we last updated each sensor
        # Initialize last update times for all sensors
        for sensor_key in config.ALL_SENSOR_MODES:
            last_sensor_update_times[sensor_key] = 0
        
        # Log sensor update intervals for debugging
        logger.info("Sensor update intervals:")
        for sensor_key in config.ALL_SENSOR_MODES:
            display_props = config.SENSOR_DISPLAY_PROPERTIES.get(sensor_key, {})
            interval = display_props.get("update_interval", config.DEFAULT_SENSOR_UPDATE_INTERVAL)
            graph_type = display_props.get("graph_type", "NONE")
            logger.info(f"  {sensor_key}: {interval}s ({graph_type})")
        
        logger.info("Entering main event loop...")

        # Main Application Loop
        while running:
            try: # Inner try-except for runtime errors to keep the application alive
                # 1. Handle Input
                events = pygame.event.get()
                for event in events:
                    if event.type == pygame.QUIT:
                        logger.info("pygame.QUIT event received. Exiting loop.")
                        running = False
                        break
                if not running: # If QUIT received, skip rest of this iteration and exit loop
                    continue

                input_results = process_input(events, config)
                app_state.handle_input(input_results)

                # 2. Update App State
                current_time = time.time()
                app_state.auto_cycle_dashboard(current_time)
                app_state.update()

                # 2.5. Check for WiFi scan completion (main thread)
                if hasattr(app_state, 'wifi_manager') and app_state.wifi_manager:
                    app_state.wifi_manager.check_scan_completion()

                if app_state.current_state == STATE_PONG_ACTIVE and app_state.active_pong_game:
                    app_state.game_manager.update_pong(app_state.keys_held)
                elif app_state.current_state == STATE_BREAKOUT_ACTIVE and app_state.active_breakout_game:
                    app_state.game_manager.update_breakout(app_state.keys_held)
                elif app_state.current_state == STATE_SNAKE_ACTIVE and app_state.active_snake_game:
                    app_state.game_manager.update_snake(app_state.keys_held)

                # 3. Read Sensor Data (per-sensor scheduled updates)
                if app_state.current_state not in [STATE_PONG_ACTIVE, STATE_BREAKOUT_ACTIVE, STATE_SNAKE_ACTIVE]:
                    # Only update sensors if not frozen
                    if not app_state.is_frozen:
                        updated_sensors = update_sensors_by_schedule(
                            sensor_values, reading_history, config, 
                            current_time, last_sensor_update_times, app_state.network_manager, app_state.system_info_manager
                        )
                        if updated_sensors:
                            app_state.last_reading_time = current_time
                
                # 4. Update Display
                update_display(screen, app_state, sensor_values, reading_history, fonts, config, ui_scaler)

                # 4.5. Sense HAT LED matrix (state-based patterns; throttled, no-op if no Sense HAT)
                update_led_display(app_state, sensor_values, config)

                # 5. Control Frame Rate
                clock.tick(config.FPS)

            except Exception as e_runtime: # Catch runtime errors within the main loop
                logger.critical(f"Runtime error in main loop: {e_runtime}", exc_info=True)
                error_messages = [
                    "Runtime Error Occurred:",
                    str(e_runtime)[:100], # Show first 100 chars of error
                    "Returning to main menu.",
                    "Check logs for full details."
                ]
                display_critical_error_on_screen(screen, fonts, config, error_messages, ui_scaler)
                
                # Reset to a safe state (main menu) and continue running
                app_state.state_manager.transition_to(STATE_MENU)
                logger.info("Reset state to MENU due to runtime error. Application continues.")
                time.sleep(1) # Brief pause to ensure error message is seen if rapidly re-triggering

        # --- End of 'while running' loop ---
        logger.info("Exiting main loop.")

    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received. Exiting application gracefully.")
        # exit_code remains 0 for a clean, developer-initiated exit
    except Exception as e_catastrophic:
        # This catches unhandled exceptions from the initialization phase (post-display)
        # or if something truly unexpected breaks out of the main loop's structure.
        logger.critical(f"Catastrophic application error: {e_catastrophic}", exc_info=True)
        error_messages = [
            "Catastrophic System Error:", 
            str(e_catastrophic)[:100],
            "Application will now exit.",
            "Check logs for details."
        ]
        display_critical_error_on_screen(screen, fonts, config, error_messages, ui_scaler)
        exit_code = 1 # Indicate an error exit
    finally:
        logger.info("Performing application cleanup...")
        try:
            # Only cleanup sensors if the module was loaded and init attempted
            if 'sensors' in sys.modules and 'sensors_active' in locals(): 
                sensors.cleanup_sensors()
                logger.info("Sensors cleanup called.")
        except Exception as e_cleanup_sensors:
            logger.error(f"Error during sensor cleanup: {e_cleanup_sensors}", exc_info=True)
        
        try:
            if pygame.get_init(): # Check if Pygame is initialized before quitting
                pygame.quit()
                logger.info("Pygame quit called.")
        except Exception as e_cleanup_pygame:
            logger.error(f"Error during pygame.quit(): {e_cleanup_pygame}", exc_info=True)
            
        logger.info(f"Tricorder Application Closed. Exit code: {exit_code}")

    sys.exit(exit_code)

# Ensure the main function runs only when the script is executed directly
if __name__ == '__main__':
    main()
