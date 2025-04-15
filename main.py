# --- main.py ---
# Main application file for the Raspberry Pi tricorder

import sys
import pygame
import logging # Add logging import
import time # Add time import for auto-cycle timing
import collections # Add for deque to store history

# Import our modules
import config
import sensors
import display
import input_handler
import logging_config # Import logging configuration

# Get a logger for this module
logger = logging.getLogger(__name__)

def main():
    """Main function to run the tricorder application."""
    # --- Initialize Logging First ---
    logging_config.setup_logging() # Setup logging before anything else
    logger.info("Starting tricorder Application...") # Changed from print

    # Initialize Display (Pygame)
    screen, clock, fonts = display.init_display()
    if not screen:
        logger.critical("Fatal Error: Could not initialize display. Exiting.") # Changed from print
        sys.exit(1)
    logger.info("Display initialized successfully.") # Added info log

    # Initialize Sensors
    sensors_active = sensors.init_sensors()
    if not sensors_active:
        logger.warning("Could not initialize Sense HAT. Sensor readings will show errors.") # Changed from print
    else:
        logger.info("Sensors initialized successfully.") # Added info log

    # Initialize history buffers for each sensor mode
    history_size = config.GRAPH_HISTORY_SIZE  # Use configured history size
    sensor_history = {}
    for mode in config.SENSOR_MODES:
        sensor_history[mode] = collections.deque(maxlen=history_size)
        # Pre-fill with None to indicate no data yet
        for _ in range(history_size):
            sensor_history[mode].append(None)

    # Application state variables
    running = True
    current_mode_index = 0
    num_modes = len(config.SENSOR_MODES)
    is_frozen = False               # State for freeze/unfreeze
    last_value = "N/A"              # Store last readings for frozen display
    last_unit = ""
    last_note = ""
    auto_cycle = True               # Add flag to control auto-cycling
    last_cycle_time = time.time()   # Track when we last changed screens
    auto_cycle_interval = 15        # Seconds between auto-cycling
    last_reading_time = time.time() # Track when we last took a sensor reading

    logger.info("Entering main loop...") # Changed from print
    # Main Application Loop
    while running:
        # 1. Handle Input
        # ----------------
        events = pygame.event.get()
        action = input_handler.process_input(events)

        # Store previous mode index in case we need it (e.g., if SELECT logic depended on it)
        # prev_mode_index = current_mode_index

        mode_changed = False  # Flag to force data refresh if mode changes
        if action == "QUIT":
            logger.info("QUIT action received. Exiting.")
            running = False
        elif action == "NEXT":
            current_mode_index = (current_mode_index + 1) % num_modes
            is_frozen = False  # Unfreeze when changing mode
            mode_changed = True
            last_cycle_time = time.time()  # Reset auto-cycle timer on manual navigation
            logger.debug(f"Action: NEXT. New mode index: {current_mode_index}. Unfrozen.")
        elif action == "PREV":
            current_mode_index = (current_mode_index - 1 + num_modes) % num_modes
            is_frozen = False # Unfreeze when changing mode
            mode_changed = True
            last_cycle_time = time.time()  # Reset auto-cycle timer on manual navigation
            logger.debug(f"Action: PREV. New mode index: {current_mode_index}. Unfrozen.")
        elif action == "SELECT":
            # Toggle the frozen state
            is_frozen = not is_frozen
            if is_frozen:
                auto_cycle = False  # Disable auto-cycling when frozen
                logger.info("Display frozen - auto-cycling disabled")
            else:
                auto_cycle = True   # Re-enable auto-cycling when unfrozen
                last_cycle_time = time.time()  # Reset auto-cycle timer
                logger.info("Display unfrozen - auto-cycling enabled")
            logger.info(f"Action: SELECT. Display Frozen toggled to: {is_frozen}") # Changed from print
            # When freezing, the current data is already stored/displayed
            # When unfreezing, the next loop iteration will fetch fresh data

        # Check for auto-cycling if enabled and not frozen
        current_time = time.time()
        if auto_cycle and not is_frozen and (current_time - last_cycle_time >= auto_cycle_interval):
            current_mode_index = (current_mode_index + 1) % num_modes
            mode_changed = True
            last_cycle_time = current_time
            logger.info(f"Auto-cycling to next mode: {config.SENSOR_MODES[current_mode_index]}")

        # 2. Get Data
        # -----------
        # Determine the current mode name *after* potential changes
        current_mode_name = config.SENSOR_MODES[current_mode_index]
        if mode_changed:
             logger.info(f"Mode changed to: {current_mode_name}")

        # Only read sensors if not frozen OR if the mode just changed
        # Also update readings periodically (once per second) to fill the history buffer
        current_time = time.time()
        should_read_sensors = (not is_frozen or mode_changed) or (current_time - last_reading_time >= 1.0)
        
        if should_read_sensors:
            last_reading_time = current_time
            if sensors_active:
                # Read all sensor modes to update all history buffers
                for mode in config.SENSOR_MODES:
                    value, unit, note = sensors.get_sensor_data(mode)
                    # Only store numerical values in history
                    try:
                        numeric_value = float(value)
                        sensor_history[mode].append(numeric_value)
                    except (ValueError, TypeError):
                        # If value isn't numeric, store None to indicate gap in data
                        sensor_history[mode].append(None)
                    
                    # If this is the current mode, store for display
                    if mode == current_mode_name:
                        if not is_frozen or mode_changed:
                            last_value, last_unit, last_note = value, unit, note
                
                logger.debug(f"Read sensor '{current_mode_name}': Value={last_value}, Unit={last_unit}, Note={last_note}")
            else:
                value, unit, note = "Error", "", "Sensor Offline"
                # Add None to history for all modes
                for mode in config.SENSOR_MODES:
                    sensor_history[mode].append(None)
                logger.warning(f"Sensor inactive, using default error values for mode '{current_mode_name}'.")
                # Store these latest readings
                last_value, last_unit, last_note = value, unit, note
        else:
            # Use the stored values if frozen and mode didn't change
            value, unit, note = last_value, last_unit, last_note
            logger.debug(f"Display frozen. Using last values for '{current_mode_name}': Value={last_value}, Unit={last_unit}, Note={last_note}")


        # 3. Update Display
        # -----------------
        # Pass the frozen status and history to the display function
        current_history = list(sensor_history[current_mode_name])
        display.draw_ui(screen, current_mode_name, value, unit, note, is_frozen, auto_cycle, current_history)

        # Actually draw everything to the screen
        pygame.display.flip()

        # 4. Control Frame Rate
        # ---------------------
        clock.tick(config.FPS)

    # --- End of main loop ---
    logger.info("Exiting main loop.") # Changed from print

    # Cleanup
    sensors.cleanup_sensors()
    pygame.quit()
    logger.info("tricorder Application Closed.") # Changed from print
    sys.exit(0)


# Ensure the main function runs only when the script is executed directly
if __name__ == '__main__':
    main()
