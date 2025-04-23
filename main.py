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
from ui.display_manager import init_display, update_display
from input.input_handler import process_input

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
        action = process_input(events, config)
        
        if action == "QUIT":
            logger.info("QUIT action received. Exiting.")
            running = False
        else:
            # Let the app state handle navigation actions
            app_state.handle_input(action)
        
        # 2. Update app state for auto-cycling if in dashboard mode
        # --------------------------------------------------------
        current_time = time.time()
        app_state.auto_cycle_dashboard(current_time)
        
        # 3. Read Sensor Data
        # -------------------
        # Should we read new sensor data?
        should_read_sensors = not app_state.is_frozen or current_time - app_state.last_reading_time >= 1.0
        
        if should_read_sensors:
            app_state.last_reading_time = current_time
            
            # Read all sensor data
            # Temperature
            temp = sensors.get_temperature()
            if temp is not None:
                sensor_values["TEMPERATURE"] = (f"{temp:.1f}", "°C", "")
                reading_history.add_reading("TEMPERATURE", temp)
            else:
                sensor_values["TEMPERATURE"] = ("Error", "", "Sensor N/A")
                reading_history.add_reading("TEMPERATURE", None)
                
            # Humidity
            humidity = sensors.get_humidity()
            if humidity is not None:
                sensor_values["HUMIDITY"] = (f"{humidity:.1f}", "%", "")
                reading_history.add_reading("HUMIDITY", humidity)
            else:
                sensor_values["HUMIDITY"] = ("Error", "", "Sensor N/A")
                reading_history.add_reading("HUMIDITY", None)
                
            # Pressure
            pressure = sensors.get_pressure()
            if pressure is not None:
                sensor_values["PRESSURE"] = (f"{pressure:.1f}", "mbar", "")
                reading_history.add_reading("PRESSURE", pressure)
            else:
                sensor_values["PRESSURE"] = ("Error", "", "Sensor N/A")
                reading_history.add_reading("PRESSURE", None)
                
            # Orientation
            orientation = sensors.get_orientation()
            if orientation is not None:
                value_str = f"P:{orientation['pitch']:.0f} R:{orientation['roll']:.0f}"
                sensor_values["ORIENTATION"] = (value_str, "deg", "")
                # Just store pitch for graphing
                reading_history.add_reading("ORIENTATION", orientation['pitch'])
            else:
                sensor_values["ORIENTATION"] = ("Error", "", "Sensor N/A")
                reading_history.add_reading("ORIENTATION", None)
                
            # Acceleration
            acceleration = sensors.get_acceleration()
            if acceleration is not None:
                value_str = f"X:{acceleration['x']:.2f} Y:{acceleration['y']:.2f}"
                note = f"Z:{acceleration['z']:.2f}G"
                sensor_values["ACCELERATION"] = (value_str, "G", note)
                reading_history.add_reading("ACCELERATION", acceleration)
            else:
                sensor_values["ACCELERATION"] = ("Error", "", "Sensor N/A")
                reading_history.add_reading("ACCELERATION", None)
                
            # Clock
            now = system_info.get_current_time()
            if now is not None:
                value_str = now.strftime("%H:%M:%S")
                note = now.strftime("%a %d %b %Y")
                sensor_values["CLOCK"] = (value_str, "", note)
                reading_history.add_reading("CLOCK", None)  # No numeric data to graph
            else:
                sensor_values["CLOCK"] = ("Error", "", "Clock N/A")
                reading_history.add_reading("CLOCK", None)
                
            # CPU Usage
            cpu_percent, cpu_info = system_info.get_cpu_usage()
            if cpu_percent is not None:
                value_str = f"{cpu_percent:.1f}"
                note = ""
                if cpu_info:
                    info_type, info_value = cpu_info
                    if info_type == "temperature":
                        note = f"Temp: {info_value:.1f}°C"
                    elif info_type == "cores":
                        note = f"Cores: {info_value}"
                        
                sensor_values["CPU_USAGE"] = (value_str, "%", note)
                reading_history.add_reading("CPU_USAGE", cpu_percent)
            else:
                sensor_values["CPU_USAGE"] = ("N/A", "%", "psutil not available")
                reading_history.add_reading("CPU_USAGE", None)
                
            # Memory Usage
            mem_percent, mem_used, mem_total = system_info.get_memory_usage()
            if mem_percent is not None:
                value_str = f"{mem_percent:.1f}"
                note = f"{mem_used:.0f}MB/{mem_total:.0f}MB"
                sensor_values["MEMORY_USAGE"] = (value_str, "%", note)
                reading_history.add_reading("MEMORY_USAGE", mem_percent)
            else:
                sensor_values["MEMORY_USAGE"] = ("N/A", "%", "psutil not available")
                reading_history.add_reading("MEMORY_USAGE", None)
                
            # Disk Usage
            disk_percent, disk_used, disk_total = system_info.get_disk_usage()
            if disk_percent is not None:
                value_str = f"{disk_percent:.1f}"
                note = f"{disk_used:.1f}GB/{disk_total:.1f}GB"
                sensor_values["DISK_USAGE"] = (value_str, "%", note)
                reading_history.add_reading("DISK_USAGE", disk_percent)
            else:
                sensor_values["DISK_USAGE"] = ("N/A", "%", "psutil not available")
                reading_history.add_reading("DISK_USAGE", None)
        
        # 4. Update Display
        # -----------------
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
