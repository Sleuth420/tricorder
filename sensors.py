# --- sensors.py ---
# Handles interaction with the Sense HAT sensors

import logging # Add logging import
import datetime # For clock display
import os # For file system information
import platform # For system information

# Get a logger for this module
logger = logging.getLogger(__name__)

# Try to import psutil for system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
    logger.info("psutil library successfully imported for system monitoring.")
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil library not found. System monitoring will be limited.")

# Attempt to import SenseHat, handle potential errors if library not installed
try:
    from sense_hat import SenseHat
except ImportError:
    logger.error("sense_hat library not found. Install using: sudo apt install sense-hat") # Changed from print
    SenseHat = None  # Set to None so checks below fail gracefully

# Global sense object
sense = None


def init_sensors():
    """
    Initializes the Sense HAT object.
    Returns True if successful, False otherwise.
    """
    global sense
    if SenseHat:
        try:
            sense = SenseHat()
            sense.low_light = True  # Optional: Dim the 8x8 matrix if distracting
            logger.info("Sense HAT initialized successfully.") # Changed from print
            return True
        except Exception as e:
            logger.error(f"Error initializing Sense HAT: {e}", exc_info=True) # Changed from print
            sense = None
            return False
    else:
        logger.warning("Sense HAT library not available. Cannot initialize sensors.") # Changed from print
        return False


def get_sensor_data(mode_name):
    """
    Reads data from the Sense HAT based on the specified mode.

    Args:
        mode_name (str): The name of the sensor mode (e.g., "TEMPERATURE").

    Returns:
        tuple: (formatted_value_string, unit_string, note_string)
               Returns ("Error", "", "Sensor N/A") if reading fails or sensor unavailable.
               The 'note_string' will currently always be empty unless specifically added below.
    """
    # Only check sense for sensor modes that require it
    sensor_modes = ["TEMPERATURE", "HUMIDITY", "PRESSURE", "ORIENTATION", "ACCELERATION"]
    if mode_name in sensor_modes and not sense:
        logger.warning(f"Attempted to read sensor '{mode_name}' but Sense HAT is not available.")
        return "Error", "", "Sensor N/A"

    value_str = "N/A"
    unit = ""
    note = ""  # Initialize note as empty string

    try:
        if mode_name == "TEMPERATURE":
            temp = sense.get_temperature()
            value_str = f"{temp:.1f}"
            unit = "°C"  # Or use "C" if degree symbol has issues
            # Note is intentionally left empty here now
        elif mode_name == "HUMIDITY":
            humidity = sense.get_humidity()
            value_str = f"{humidity:.1f}"
            unit = "%"
        elif mode_name == "PRESSURE":
            pressure = sense.get_pressure()
            value_str = f"{pressure:.1f}"
            unit = "mbar"
        elif mode_name == "ORIENTATION":
            o = sense.get_orientation_degrees()
            value_str = f"P:{o['pitch']:.0f} R:{o['roll']:.0f}"
            unit = "deg"
        # System information modes
        elif mode_name == "CLOCK":
            now = datetime.datetime.now()
            value_str = now.strftime("%H:%M:%S")
            unit = ""
            note = now.strftime("%a %d %b %Y")
        elif mode_name == "CPU_USAGE":
            # Calculate CPU usage percentage
            if PSUTIL_AVAILABLE:
                try:
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    value_str = f"{cpu_percent:.1f}"
                    unit = "%"
                    logger.debug(f"CPU usage: {cpu_percent:.1f}%")
                    
                    # Get CPU temperature if available (Raspberry Pi specific)
                    try:
                        if os.path.exists('/sys/class/thermal/thermal_zone0/temp'):
                            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                                temp = float(f.read()) / 1000.0
                            note = f"Temp: {temp:.1f}°C"
                            logger.debug(f"CPU temperature: {temp:.1f}°C")
                        else:
                            cores = psutil.cpu_count()
                            note = f"Cores: {cores}"
                            logger.debug(f"CPU cores: {cores}")
                    except Exception as e:
                        logger.warning(f"Could not read CPU temperature: {e}")
                        cores = psutil.cpu_count()
                        note = f"Cores: {cores}"
                except Exception as e:
                    logger.error(f"Error getting CPU usage: {e}")
                    value_str = "Error"
                    unit = "%"
                    note = "CPU read error"
            else:
                logger.debug("psutil not available for CPU monitoring")
                value_str = "N/A"
                unit = "%"
                note = "psutil not available"
        elif mode_name == "MEMORY_USAGE":
            if PSUTIL_AVAILABLE:
                try:
                    memory = psutil.virtual_memory()
                    value_str = f"{memory.percent:.1f}"
                    unit = "%"
                    # Convert bytes to megabytes for the note
                    used_mb = memory.used / (1024 * 1024)
                    total_mb = memory.total / (1024 * 1024)
                    note = f"{used_mb:.0f}MB/{total_mb:.0f}MB"
                    logger.debug(f"Memory usage: {memory.percent:.1f}% ({used_mb:.0f}MB/{total_mb:.0f}MB)")
                except Exception as e:
                    logger.error(f"Error getting memory usage: {e}")
                    value_str = "Error"
                    unit = "%"
                    note = "Memory read error"
            else:
                logger.debug("psutil not available for memory monitoring")
                value_str = "N/A"
                unit = "%"
                note = "psutil not available"
        elif mode_name == "DISK_USAGE":
            if PSUTIL_AVAILABLE:
                try:
                    disk = psutil.disk_usage('/')
                    value_str = f"{disk.percent:.1f}"
                    unit = "%"
                    # Convert bytes to gigabytes for the note
                    used_gb = disk.used / (1024 * 1024 * 1024)
                    total_gb = disk.total / (1024 * 1024 * 1024)
                    note = f"{used_gb:.1f}GB/{total_gb:.1f}GB"
                    logger.debug(f"Disk usage: {disk.percent:.1f}% ({used_gb:.1f}GB/{total_gb:.1f}GB)")
                except Exception as e:
                    logger.error(f"Error getting disk usage: {e}")
                    value_str = "Error"
                    unit = "%"
                    note = "Disk read error"
            else:
                logger.debug("psutil not available for disk monitoring")
                value_str = "N/A"
                unit = "%"
                note = "psutil not available"
        elif mode_name == "ACCELERATION":
            # Get acceleration data if Sense HAT is available
            if sense:
                accel = sense.get_accelerometer_raw()
                # Format for display - X and Y are the most interesting for handheld
                value_str = f"X:{accel['x']:.2f} Y:{accel['y']:.2f}"
                unit = "G"
                # Include Z in the note
                note = f"Z:{accel['z']:.2f}G"
            else:
                # Create simulated data for testing without hardware
                import random
                x = random.uniform(-0.5, 0.5)
                y = random.uniform(-0.5, 0.5)
                z = random.uniform(0.8, 1.2)  # Z often close to 1G due to gravity
                value_str = f"X:{x:.2f} Y:{y:.2f}"
                unit = "G"
                note = f"Z:{z:.2f}G (simulated)"
        # --- Add other sensor modes here if needed ---
        else:
            logger.warning(f"Requested unknown sensor mode: '{mode_name}'")
            value_str = "Unknown Mode"
            unit = ""

    except Exception as e:
        logger.error(f"Error reading sensor {mode_name}: {e}", exc_info=True) # Changed from print
        value_str = "Read Error"
        unit = ""

    # No specific notes being added currently, return the potentially updated value/unit and empty note
    return value_str, unit, note


def cleanup_sensors():
    """
    Performs any necessary cleanup for the Sense HAT (like clearing the matrix).
    """
    if sense:
        try:
            sense.clear()  # Clear the 8x8 LED matrix
            logger.info("Sense HAT cleared.") # Changed from print
        except Exception as e:
            logger.error(f"Error clearing Sense HAT: {e}", exc_info=True) # Changed from print
