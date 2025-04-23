# --- models/reading_history.py ---
# Manages sensor reading history for graphing

import collections
import logging

logger = logging.getLogger(__name__)

class ReadingHistory:
    """Maintains history of sensor readings for graphing."""
    
    def __init__(self, sensor_modes, history_size=60):
        """
        Initialize the reading history.
        
        Args:
            sensor_modes (list): List of sensor mode names
            history_size (int): Number of readings to keep in history
        """
        self.history_size = history_size
        self.sensor_data = {}
        
        # Initialize history buffers for each sensor mode
        for mode in sensor_modes:
            self.sensor_data[mode] = collections.deque(maxlen=history_size)
            # Pre-fill with None to indicate no data yet
            for _ in range(history_size):
                self.sensor_data[mode].append(None)
                
        logger.debug(f"Initialized reading history for {len(sensor_modes)} sensor modes")
    
    def add_reading(self, mode_name, value):
        """
        Add a reading to the history for a specific sensor mode.
        
        Args:
            mode_name (str): The sensor mode name
            value: The value to add (will be converted to float if possible)
        """
        if mode_name not in self.sensor_data:
            logger.warning(f"Attempted to add reading for unknown mode: {mode_name}")
            return
            
        # For ACCELERATION, we only store the X component for graphing
        if mode_name == "ACCELERATION" and isinstance(value, dict):
            try:
                # Store just the X value for graphing
                self.sensor_data[mode_name].append(value['x'])
                logger.debug(f"Added acceleration X reading: {value['x']}")
                return
            except (KeyError, TypeError) as e:
                logger.error(f"Error processing acceleration data: {e}")
                self.sensor_data[mode_name].append(None)
                return
                
        # Try to convert to float for numerical modes
        if value is not None:
            try:
                # Skip for CLOCK mode which shouldn't be graphed numerically
                if mode_name == "CLOCK":
                    self.sensor_data[mode_name].append(None)
                    return
                    
                numeric_value = float(value)
                self.sensor_data[mode_name].append(numeric_value)
                logger.debug(f"Added {mode_name} reading: {numeric_value}")
            except (ValueError, TypeError):
                logger.debug(f"Non-numeric {mode_name} reading, storing None")
                self.sensor_data[mode_name].append(None)
        else:
            self.sensor_data[mode_name].append(None)
            
    def get_history(self, mode_name):
        """
        Get the history for a specific sensor mode.
        
        Args:
            mode_name (str): The sensor mode name
            
        Returns:
            list: List of readings for the specified mode
        """
        if mode_name not in self.sensor_data:
            logger.warning(f"Requested history for unknown mode: {mode_name}")
            return []
            
        return list(self.sensor_data[mode_name]) 