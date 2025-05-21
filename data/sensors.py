# --- data/sensors.py ---
# Handles raw data acquisition from the Sense HAT sensors

import logging
import datetime

# Get a logger for this module
logger = logging.getLogger(__name__)

# Attempt to import SenseHat, handle potential errors if library not installed
try:
    from sense_hat import SenseHat
except ImportError:
    logger.error("sense_hat library not found. Install using: sudo apt install sense-hat")
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
            
            # Joystick direction callbacks have been REMOVED.
            # We will rely solely on sense.stick.get_events() in input_handler.py
            # to capture all joystick activity.
            
            # Clear any pending joystick events from the queue before starting.
            # This ensures we only process events that occur after this initialization.
            if sense and hasattr(sense, 'stick'): # Ensure sense and stick are valid
                sense.stick.get_events() 
            
            logger.info("Sense HAT initialized successfully. Joystick events will be read via get_events().")
            return True
        except Exception as e:
            logger.error(f"Error initializing Sense HAT: {e}", exc_info=True)
            sense = None
            return False
    else:
        logger.warning("Sense HAT library not available. Cannot initialize sensors.")
        return False

def get_temperature():
    """Get the temperature reading from the Sense HAT."""
    if not sense:
        logger.warning("Attempted to read temperature but Sense HAT is not available.")
        return None
        
    try:
        return sense.get_temperature()
    except Exception as e:
        logger.error(f"Error reading temperature: {e}", exc_info=True)
        return None

def get_humidity():
    """Get the humidity reading from the Sense HAT."""
    if not sense:
        logger.warning("Attempted to read humidity but Sense HAT is not available.")
        return None
        
    try:
        return sense.get_humidity()
    except Exception as e:
        logger.error(f"Error reading humidity: {e}", exc_info=True)
        return None

def get_pressure():
    """Get the pressure reading from the Sense HAT."""
    if not sense:
        logger.warning("Attempted to read pressure but Sense HAT is not available.")
        return None
        
    try:
        return sense.get_pressure()
    except Exception as e:
        logger.error(f"Error reading pressure: {e}", exc_info=True)
        return None

def get_orientation():
    """Get the orientation reading from the Sense HAT."""
    if not sense:
        logger.warning("Attempted to read orientation but Sense HAT is not available.")
        return None
        
    try:
        return sense.get_orientation_degrees()
    except Exception as e:
        logger.error(f"Error reading orientation: {e}", exc_info=True)
        return None

def get_acceleration():
    """Get the acceleration reading from the Sense HAT."""
    if not sense:
        logger.warning("Attempted to read acceleration but Sense HAT is not available.")
        return None
        
    try:
        return sense.get_accelerometer_raw()
    except Exception as e:
        logger.error(f"Error reading acceleration: {e}", exc_info=True)
        return None

def cleanup_sensors():
    """
    Performs any necessary cleanup for the Sense HAT (like clearing the matrix).
    """
    if sense:
        try:
            sense.clear()  # Clear the 8x8 LED matrix
            logger.info("Sense HAT cleared.")
        except Exception as e:
            logger.error(f"Error clearing Sense HAT: {e}", exc_info=True)