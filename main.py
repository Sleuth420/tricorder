# --- main.py ---
# Main application file for the Raspberry Pi tricorder
# Now with menu-based navigation and modular structure

import sys
import pygame
import logging
import time
import platform

# Import configuration and logging modules
import config
import logging_config

# Import application components from the new modular structure
from models.app_state import AppState
from models.reading_history import ReadingHistory
from data import sensors
from data import system_info
# Import the new data updater function
from data.data_updater import update_all_data
from ui.display_manager import init_display, update_display
from input.input_handler import process_input
# Import state constants needed here
from models.app_state import STATE_PONG_ACTIVE

# Get a logger for this module
logger = logging.getLogger(__name__)

def main():
    """Main function to run the tricorder application."""
    # --- Initialize Logging First ---
    logging_config.setup_logging()
    logger.info("Starting tricorder Application...")
    
    # Log system information
    logger.info(f"Platform: {platform.platform()}")
    logger.info(f"Python version: {platform.python_version()}")
    logger.info(f"Display size: {config.SCREEN_WIDTH}x{config.SCREEN_HEIGHT}, Fullscreen: {config.FULLSCREEN}")
    logger.info(f"Available sensor modes: {', '.join(config.SENSOR_MODES)}")
    
    # Initialize Models
    app_state = AppState(config)
    reading_history = ReadingHistory(config.SENSOR_MODES, config.GRAPH_HISTORY_SIZE)
    logger.info("Application state and reading history initialized.")

    # Initialize Display (Pygame)
    screen, clock, fonts = init_display()
    if not screen:
        logger.critical("Fatal Error: Could not initialize display. Exiting.")
        sys.exit(1)
    logger.info("Display initialized successfully.")

    # Initialize Sensors
    sensors_active = sensors.init_sensors()
    if not sensors_active:
        logger.warning("Could not initialize Sense HAT. Sensor readings will show errors.")
    else:
        logger.info("Sensors initialized successfully.")
    
    # Dictionary to store current sensor values
    sensor_values = {}
    
    # Main Application Loop
    running = True
    logger.info("Entering main loop...")
    
    while running:
        # 1. Handle Input
        # ----------------
        events = pygame.event.get()
        input_results = process_input(events, config)

        # Check for QUIT event separately
        should_quit = any(result['type'] == 'QUIT' for result in input_results)
        if should_quit:
            logger.info("QUIT action received. Exiting.")
            running = False
            continue # Skip rest of the loop iteration

        # Pass detailed input results to app_state
        # Note: state changes from regular actions are handled here, but not logged
        # immediately. Secret combo state changes happen in app_state.update()
        app_state.handle_input(input_results)

        # 2. Update App State (Timers, Auto-Cycle)
        # ------------------------------------------
        current_time = time.time()
        app_state.auto_cycle_dashboard(current_time)
        app_state.update() # Check timers (secret combo, long press)

        # Update active game if necessary
        if app_state.current_state == STATE_PONG_ACTIVE and app_state.active_pong_game:
            app_state.active_pong_game.update(app_state.keys_held)

        # 3. Read Sensor Data (delegated) - Only if not in game
        # --------------------------------
        if app_state.current_state != STATE_PONG_ACTIVE:
            # Determine if we should read new sensor data based on frozen state and time interval
            # Use a simple 1-second interval for updates when not frozen
            should_read_sensors = not app_state.is_frozen or (current_time - app_state.last_reading_time >= 1.0)

            if should_read_sensors:
                # Update the last reading time in AppState
                app_state.last_reading_time = current_time
                # Call the centralized data updater function
                update_all_data(sensor_values, reading_history, config)
        
        # 4. Update Display
        # -----------------
        # Display manager handles routing based on app_state.current_state
        update_display(screen, app_state, sensor_values, reading_history, fonts, config)
        
        # 5. Control Frame Rate
        # ---------------------
        clock.tick(config.FPS)

    # --- End of main loop ---
    logger.info("Exiting main loop.")

    # Cleanup
    sensors.cleanup_sensors()
    pygame.quit()
    logger.info("tricorder Application Closed.")
    sys.exit(0)


# Ensure the main function runs only when the script is executed directly
if __name__ == '__main__':
    main()
