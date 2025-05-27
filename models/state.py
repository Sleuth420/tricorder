"""
State model that holds application state data.
"""

import logging

logger = logging.getLogger(__name__)

class State:
    """
    Application state model.
    
    This class holds the state data for the application, but does not
    contain any state transition logic (that's in StateMachine).
    """
    
    def __init__(self):
        """Initialize the application state."""
        # Currently selected menu item
        self.selected_menu_index = 0
        
        # Currently active sensor (for sensor views)
        self.current_sensor = None
        
        # Whether sensor readings are frozen
        self.is_frozen = False
        
        # Auto-cycle settings for dashboard
        self.auto_cycle = True
        self.cycle_index = 0
        self.last_cycle_time = 0
        
        logger.debug("State initialized")
        
    def select_menu_item(self, index):
        """
        Select a menu item by index.
        
        Args:
            index (int): Index of the menu item to select
            
        Returns:
            bool: True if the selection changed
        """
        if self.selected_menu_index == index:
            return False
            
        self.selected_menu_index = index
        logger.debug(f"Selected menu item at index {index}")
        return True
        
    def set_current_sensor(self, sensor):
        """
        Set the current sensor.
        
        Args:
            sensor (str): Sensor name
            
        Returns:
            bool: True if the sensor changed
        """
        if self.current_sensor == sensor:
            return False
            
        self.current_sensor = sensor
        logger.debug(f"Current sensor set to {sensor}")
        return True
        
    def set_frozen(self, frozen):
        """
        Set the frozen state.
        
        Args:
            frozen (bool): Whether to freeze sensor readings
            
        Returns:
            bool: True if the frozen state changed
        """
        if self.is_frozen == frozen:
            return False
            
        self.is_frozen = frozen
        
        # Update auto-cycle state
        if self.is_frozen:
            self.auto_cycle = False
        
        logger.debug(f"Frozen state set to {frozen}")
        return True
        
    def set_auto_cycle(self, enabled):
        """
        Set the auto-cycle state.
        
        Args:
            enabled (bool): Whether to enable auto-cycling
            
        Returns:
            bool: True if the auto-cycle state changed
        """
        if self.auto_cycle == enabled:
            return False
            
        self.auto_cycle = enabled
        
        # Update frozen state
        if self.auto_cycle:
            self.is_frozen = False
            
        logger.debug(f"Auto-cycle set to {enabled}")
        return True
        
    def reset_cycle_time(self, current_time):
        """
        Reset the cycle time.
        
        Args:
            current_time (float): Current time in seconds
        """
        self.last_cycle_time = current_time
        
    def should_cycle(self, current_time, cycle_interval):
        """
        Check if it's time to cycle to the next sensor.
        
        Args:
            current_time (float): Current time in seconds
            cycle_interval (float): Cycle interval in seconds
            
        Returns:
            bool: True if it's time to cycle
        """
        return (self.auto_cycle and 
                not self.is_frozen and 
                current_time - self.last_cycle_time >= cycle_interval) 