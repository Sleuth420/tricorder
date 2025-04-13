# --- sensors.py ---
# Handles interaction with the Sense HAT sensors

# Attempt to import SenseHat, handle potential errors if library not installed
try:
    from sense_hat import SenseHat
except ImportError:
    print("Error: sense_hat library not found.")
    print("Install using: sudo apt install sense-hat")
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
            print("Sense HAT initialized successfully.")
            return True
        except Exception as e:
            print(f"Error initializing Sense HAT: {e}")
            sense = None
            return False
    else:
        print("Sense HAT library not available.")
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
    if not sense:
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
        # --- Add other sensor modes here if needed ---
        # elif mode_name == "ACCELERATION":
        #     accel = sense.get_accelerometer_raw()
        #     value_str = f"X:{accel['x']:.2f} Y:{accel['y']:.2f}"
        #     unit = "G"
        else:
            value_str = "Unknown Mode"
            unit = ""

    except Exception as e:
        print(f"Error reading sensor {mode_name}: {e}")
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
            print("Sense HAT cleared.")
        except Exception as e:
            print(f"Error clearing Sense HAT: {e}")
