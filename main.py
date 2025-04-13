# --- main.py ---
# Main application file for the Raspberry Pi tricorder

import sys
import pygame

# Import our modules
import config
import sensors
import display
import input_handler


def main():
    """Main function to run the tricorder application."""
    print("Starting tricorder Application...")

    # Initialize Display (Pygame)
    screen, clock, fonts = display.init_display()
    if not screen:
        print("Fatal Error: Could not initialize display. Exiting.")
        sys.exit(1)

    # Initialize Sensors
    sensors_active = sensors.init_sensors()
    if not sensors_active:
        print("Warning: Could not initialize Sense HAT. Sensor readings will show errors.")

    # Application state variables
    running = True
    current_mode_index = 0
    num_modes = len(config.SENSOR_MODES)
    is_frozen = False               # State for freeze/unfreeze
    last_value = "N/A"              # Store last readings for frozen display
    last_unit = ""
    last_note = ""

    print("Entering main loop...")
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
            running = False
        elif action == "NEXT":
            current_mode_index = (current_mode_index + 1) % num_modes
            is_frozen = False  # Unfreeze when changing mode
            mode_changed = True
        elif action == "PREV":
            current_mode_index = (current_mode_index - 1 + num_modes) % num_modes
            is_frozen = False # Unfreeze when changing mode
            mode_changed = True
        elif action == "SELECT":
            # Toggle the frozen state
            is_frozen = not is_frozen
            print(f"Display Frozen: {is_frozen}")
            # When freezing, the current data is already stored/displayed
            # When unfreezing, the next loop iteration will fetch fresh data

        # 2. Get Data
        # -----------
        # Determine the current mode name *after* potential changes
        current_mode_name = config.SENSOR_MODES[current_mode_index]

        # Only read sensors if not frozen OR if the mode just changed
        if not is_frozen or mode_changed:
            if sensors_active:
                value, unit, note = sensors.get_sensor_data(current_mode_name)
            else:
                value, unit, note = "Error", "", "Sensor Offline"
            # Store these latest readings
            last_value, last_unit, last_note = value, unit, note
        else:
            # Use the stored values if frozen and mode didn't change
            value, unit, note = last_value, last_unit, last_note

        # 3. Update Display
        # -----------------
        # Pass the frozen status to the display function
        display.draw_ui(screen, current_mode_name, value, unit, note, is_frozen)

        # Actually draw everything to the screen
        pygame.display.flip()

        # 4. Control Frame Rate
        # ---------------------
        clock.tick(config.FPS)

    # --- End of main loop ---
    print("Exiting main loop.")

    # Cleanup
    sensors.cleanup_sensors()
    pygame.quit()
    print("tricorder Application Closed.")
    sys.exit(0)


# Ensure the main function runs only when the script is executed directly
if __name__ == '__main__':
    main()
