# --- models/state_manager.py ---
# Manages application state transitions and coordination

import logging

# Import state constants - avoiding circular import by importing from the module that will define them
STATE_MENU = "MENU"
STATE_SENSORS_MENU = "SENSORS_MENU"
STATE_DASHBOARD = "DASHBOARD"
STATE_SENSOR_VIEW = "SENSOR"
STATE_SYSTEM_INFO = "SYSTEM"
STATE_SETTINGS = "SETTINGS"
STATE_SECRET_GAMES = "SECRET_GAMES"
STATE_PONG_ACTIVE = "PONG_ACTIVE"
STATE_SCHEMATICS = "SCHEMATICS"
STATE_SHIP_MENU = "SHIP_MENU"

logger = logging.getLogger(__name__)

class StateManager:
    """Manages application state transitions and coordination between components."""
    
    def __init__(self, config_module):
        """
        Initialize the state manager.
        
        Args:
            config_module: The configuration module
        """
        self.config = config_module
        self.current_state = STATE_MENU
        self.previous_state = None
        
    def transition_to(self, new_state, context=None):
        """
        Transition to a new state.
        
        Args:
            new_state (str): The state to transition to
            context (dict, optional): Additional context for the transition
            
        Returns:
            bool: True if state changed
        """
        if self.current_state == new_state:
            return False
            
        logger.info(f"State transition: {self.current_state} -> {new_state}")
        self.previous_state = self.current_state
        self.current_state = new_state
        return True
        
    def return_to_previous(self):
        """
        Return to the previous state.
        
        Returns:
            bool: True if state changed
        """
        if self.previous_state:
            return self.transition_to(self.previous_state)
        else:
            return self.transition_to(STATE_MENU)
            
    def return_to_menu(self):
        """
        Return to the main menu.
        
        Returns:
            bool: True if state changed
        """
        return self.transition_to(STATE_MENU) 