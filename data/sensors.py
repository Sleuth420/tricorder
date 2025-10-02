# --- data/sensors.py ---
# Handles raw data acquisition from the Sense HAT sensors

import logging
import datetime
import platform
import random
import time
import math
from config import sensors as sensor_config

# Get a logger for this module
logger = logging.getLogger(__name__)

# Debug flag for detailed sensor logging (set to False to disable)
SENSOR_DEBUG_LOGGING = True

# Attempt to import SenseHat, handle potential errors if library not installed
try:
    from sense_hat import SenseHat
except ImportError:
    logger.error("sense_hat library not found. Install using: sudo apt install sense-hat")
    SenseHat = None  # Set to None so checks below fail gracefully

# Global sense object
sense = None

# Windows development mode detection
IS_WINDOWS_DEV = platform.system() == "Windows"

# Mock data class definition
class MockSensorData:
    def __init__(self):
        self.base_temp = 38.0
        self.base_humidity = 45.0
        self.base_pressure = 1013.25
        self.orientation = {'pitch': 0.0, 'roll': 0.0, 'yaw': 0.0}
        self.acceleration = {'x': 0.0, 'y': 0.0, 'z': 1.0}
        self.start_time = time.time()
        
    def get_temperature(self):
        # Simulate daily temperature variation
        elapsed = time.time() - self.start_time
        daily_cycle = 2.0 * math.sin(elapsed / 10.0)  # 10 second cycle for demo
        noise = random.uniform(-0.5, 0.5)
        return self.base_temp + daily_cycle + noise
        
    def get_humidity(self):
        # Simulate humidity changes
        elapsed = time.time() - self.start_time
        variation = 5.0 * math.sin(elapsed / 15.0)  # Different cycle
        noise = random.uniform(-2.0, 2.0)
        return max(20.0, min(80.0, self.base_humidity + variation + noise))
        
    def get_pressure(self):
        # Simulate atmospheric pressure changes
        elapsed = time.time() - self.start_time
        variation = 3.0 * math.sin(elapsed / 20.0)
        noise = random.uniform(-1.0, 1.0)
        return self.base_pressure + variation + noise
        
    def get_orientation(self):
        # Check if dynamic mock data is enabled
        if not sensor_config.ENABLE_MOCK_SENSOR_DYNAMICS:
            # Return static values for testing
            orientation = {
                'pitch': 0.0,
                'roll': 0.0,
                'yaw': 0.0
            }
            return orientation
        
        # Simulate more stable orientation with smaller variations (mimics real SenseHat noise)
        elapsed = time.time() - self.start_time
        
        # Base orientation with small noise (similar to a stable device)
        base_pitch = 0.0  # Device lying flat
        base_roll = 0.0   # Device lying flat
        base_yaw = 0.0    # Facing north
        
        # Add small random noise (typical SenseHat jitter)
        noise_scale = 1.5  # Degrees of noise
        pitch_noise = random.uniform(-noise_scale, noise_scale)
        roll_noise = random.uniform(-noise_scale, noise_scale)
        yaw_noise = random.uniform(-noise_scale, noise_scale)
        
        # Add very slow drift for demonstration
        drift_scale = 2.0  # Maximum drift from center
        pitch_drift = drift_scale * math.sin(elapsed / 20.0)  # 20 second cycle
        roll_drift = drift_scale * math.cos(elapsed / 25.0)   # 25 second cycle
        yaw_drift = (elapsed * 0.5) % 360  # Very slow rotation
        
        orientation = {
            'pitch': (base_pitch + pitch_drift + pitch_noise) % 360,
            'roll': (base_roll + roll_drift + roll_noise) % 360,
            'yaw': (base_yaw + yaw_drift + yaw_noise) % 360
        }
        
        # Debug logging for mock sensor data
        if SENSOR_DEBUG_LOGGING:
            logger.info(f"MOCK ORIENTATION: pitch={orientation['pitch']:.2f}°, roll={orientation['roll']:.2f}°, yaw={orientation['yaw']:.2f}°")
        
        return orientation
        
    def get_acceleration(self):
        # Simulate small vibrations around gravity
        return {
            'x': random.uniform(-0.1, 0.1),
            'y': random.uniform(-0.1, 0.1),
            'z': 1.0 + random.uniform(-0.05, 0.05)
        }

# Initialize mock data for Windows development
mock_data = None
if IS_WINDOWS_DEV:
    mock_data = MockSensorData()
    logger.info("Windows development mode: Mock sensor data initialized")
    logger.info(f"IS_WINDOWS_DEV: {IS_WINDOWS_DEV}, mock_data: {mock_data}")
else:
    logger.info(f"Not Windows dev mode. IS_WINDOWS_DEV: {IS_WINDOWS_DEV}, platform: {platform.system()}")

def init_sensors():
    """
    Initializes the Sense HAT object.
    Returns True if successful, False otherwise.
    """
    global sense
    
    # On Windows, we still try to initialize real SenseHat but provide mock data
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
        if IS_WINDOWS_DEV:
            logger.info("Windows development mode: Using mock sensor data")
            logger.info(f"Mock data object: {mock_data}")
        return False

def get_temperature():
    """Get the temperature reading from the Sense HAT."""
    if not sense:
        # Return mock data on Windows for development
        if IS_WINDOWS_DEV and mock_data:
            return mock_data.get_temperature()
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
        # Return mock data on Windows for development
        if IS_WINDOWS_DEV and mock_data:
            return mock_data.get_humidity()
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
        # Return mock data on Windows for development
        if IS_WINDOWS_DEV and mock_data:
            return mock_data.get_pressure()
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
        # Return mock data on Windows for development
        if IS_WINDOWS_DEV and mock_data:
            return mock_data.get_orientation()
        logger.warning("Attempted to read orientation but Sense HAT is not available.")
        return None
        
    try:
        orientation = sense.get_orientation_degrees()
        
        # Debug logging for real sensor data
        if SENSOR_DEBUG_LOGGING and orientation:
            logger.info(f"REAL ORIENTATION: pitch={orientation.get('pitch', 'N/A'):.2f}°, roll={orientation.get('roll', 'N/A'):.2f}°, yaw={orientation.get('yaw', 'N/A'):.2f}°")
        
        return orientation
    except Exception as e:
        logger.error(f"Error reading orientation: {e}", exc_info=True)
        return None

def get_acceleration():
    """Get the acceleration reading from the Sense HAT."""
    if not sense:
        # Return mock data on Windows for development
        if IS_WINDOWS_DEV and mock_data:
            return mock_data.get_acceleration()
        logger.warning("Attempted to read acceleration but Sense HAT is not available. If Running on Windows this is expected")
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