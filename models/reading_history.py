# --- models/reading_history.py ---
# Manages sensor reading history for graphing

import collections
import logging
import config as app_config # Import config for sensor mode constants

logger = logging.getLogger(__name__)

class ReadingHistory:
    """Maintains history of sensor readings for graphing."""
    
    def __init__(self, sensor_modes, history_size=60):
        """
        Initialize the reading history.
        
        Args:
            sensor_modes (list): List of sensor mode constants (e.g., app_config.SENSOR_TEMPERATURE)
            history_size (int): Number of readings to keep in history
        """
        self.history_size = history_size
        self.sensor_data = {}
        
        # Initialize history buffers for each sensor mode
        for mode_key in sensor_modes: # mode_key is a constant like app_config.SENSOR_TEMPERATURE
            self.sensor_data[mode_key] = collections.deque(maxlen=history_size)
            # Pre-fill with None to indicate no data yet
            for _ in range(history_size):
                self.sensor_data[mode_key].append(None)
                
        logger.debug(f"Initialized reading history for {len(sensor_modes)} sensor modes")
    
    def add_reading(self, mode_key, value):
        """
        Add a reading to the history for a specific sensor mode.
        
        Args:
            mode_key (str): The sensor mode constant (e.g., app_config.SENSOR_TEMPERATURE)
            value: The value to add. For ACCELERATION, this might be the dict from sensors.py.
                   For others, it's expected to be a numeric value or None.
        """
        if mode_key not in self.sensor_data:
            logger.warning(f"Attempted to add reading for unknown mode: {mode_key}")
            return
            
        # For ACCELERATION, we expect the raw dict from sensors.py, and store just the X component for graphing for now.
        # This specific handling for 'x' might need to be more flexible if other components are graphed.
        if mode_key == app_config.SENSOR_ACCELERATION and isinstance(value, dict):
            try:
                # Store just the X value from the raw acceleration dict for line graph history
                # VerticalBarGraph in sensor_view.py will pick its component ('y') from SENSOR_DISPLAY_PROPERTIES.
                # This part is a bit inconsistent: line graph history gets X, VBar gets Y. 
                # TODO: Consolidate which component of ACCELERATION is used for generic history if line graph is still used.
                # For now, matching old behavior for line graph history.
                self.sensor_data[mode_key].append(value.get('x')) 
                logger.debug(f"Added acceleration X reading to history: {value.get('x')}")
                return
            except (KeyError, TypeError) as e:
                logger.error(f"Error processing acceleration data for history: {e}")
                self.sensor_data[mode_key].append(None)
                return
                
        # Try to convert to float for other numerical modes
        if value is not None:
            try:
                # Skip for CLOCK mode which shouldn't be graphed numerically
                if mode_key == app_config.SENSOR_CLOCK:
                    self.sensor_data[mode_key].append(None) # CLOCK has no numeric history
                    return
                    
                numeric_value = float(value)
                self.sensor_data[mode_key].append(numeric_value)
                # logger.debug(f"Added {mode_key} reading to history: {numeric_value}") # Can be spammy
            except (ValueError, TypeError):
                logger.debug(f"Non-numeric {mode_key} reading for history, storing None: {value}")
                self.sensor_data[mode_key].append(None)
        else:
            self.sensor_data[mode_key].append(None)
            
    def get_history(self, mode_key):
        """
        Get the history for a specific sensor mode.
        
        Args:
            mode_key (str): The sensor mode constant (e.g., app_config.SENSOR_TEMPERATURE)
            
        Returns:
            list: List of readings for the specified mode
        """
        if mode_key not in self.sensor_data:
            logger.warning(f"Requested history for unknown mode: {mode_key}")
            return []
            
        return list(self.sensor_data[mode_key]) 