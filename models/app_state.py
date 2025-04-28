# --- models/app_state.py ---
# Manages application state and navigation

import logging

logger = logging.getLogger(__name__)

# Application states
STATE_MENU = "MENU"           # Main menu
STATE_DASHBOARD = "DASHBOARD" # Dashboard/auto-cycling view
STATE_SENSOR_VIEW = "SENSOR"  # Individual sensor view
STATE_SYSTEM_INFO = "SYSTEM"  # System info view

class AppState:
    """Manages the state of the application and navigation."""
    
    def __init__(self, config):
        """
        Initialize the application state.
        
        Args:
            config: The configuration module
        """
        self.config = config
        self.current_state = STATE_MENU
        self.previous_state = None
        
        # Menu state
        self.menu_index = 0
        self.menu_items = [
            {"name": "Temperature", "state": STATE_SENSOR_VIEW, "sensor": "TEMPERATURE"},
            {"name": "Humidity", "state": STATE_SENSOR_VIEW, "sensor": "HUMIDITY"},
            {"name": "Pressure", "state": STATE_SENSOR_VIEW, "sensor": "PRESSURE"},
            {"name": "Orientation", "state": STATE_SENSOR_VIEW, "sensor": "ORIENTATION"},
            {"name": "Acceleration", "state": STATE_SENSOR_VIEW, "sensor": "ACCELERATION"},
            {"name": "All Sensors", "state": STATE_DASHBOARD, "sensor": None},
            {"name": "System Info", "state": STATE_SYSTEM_INFO, "sensor": None}
        ]
        
        # Track menu hierarchy - no more submenu structure
        self.current_menu = self.menu_items
        self.menu_stack = []  # Stack to track menu hierarchy, but we won't use it for now
        
        # Sensor view state
        self.current_sensor = None
        self.is_frozen = False
        self.auto_cycle = True
        self.last_cycle_time = 0
        self.cycle_index = 0
        
    def handle_input(self, action):
        """
        Handle user input based on current state.
        
        Args:
            action (str): The action to handle ("PREV", "NEXT", "SELECT", or None)
            
        Returns:
            bool: True if state changed, False otherwise
        """
        if action is None:
            return False
            
        state_changed = False
        
        # Handle based on current state
        if self.current_state == STATE_MENU:
            state_changed = self._handle_menu_input(action)
        elif self.current_state == STATE_DASHBOARD:
            state_changed = self._handle_dashboard_input(action)
        elif self.current_state == STATE_SENSOR_VIEW:
            state_changed = self._handle_sensor_input(action)
        elif self.current_state == STATE_SYSTEM_INFO:
            state_changed = self._handle_system_info_input(action)
            
        if state_changed:
            logger.debug(f"State changed: {self.previous_state} -> {self.current_state}")
            
        return state_changed
    
    def _handle_menu_input(self, action):
        """Handle input in menu state."""
        if action == "NEXT":
            # Go to next menu item
            self.menu_index = (self.menu_index + 1) % len(self.current_menu)
            logger.debug(f"Menu navigation: NEXT -> {self.current_menu[self.menu_index]['name']}")
            return True
        elif action == "PREV":
            # Go to previous menu item
            self.menu_index = (self.menu_index - 1) % len(self.current_menu)
            logger.debug(f"Menu navigation: PREV -> {self.current_menu[self.menu_index]['name']}")
            return True
        elif action == "SELECT":
            # Select current menu item
            item = self.current_menu[self.menu_index]
            
            # If not a submenu, transition to the appropriate state
            self.previous_state = self.current_state
            self.current_state = item["state"]
            
            # If transitioning to a sensor view, set the current sensor
            if self.current_state == STATE_SENSOR_VIEW:
                self.current_sensor = item["sensor"]
                self.is_frozen = False  # Reset frozen state
                logger.debug(f"Transition to sensor view: {self.current_sensor}")
            elif self.current_state == STATE_DASHBOARD:
                self.auto_cycle = True
                self.cycle_index = 0
                logger.debug("Transition to dashboard view")
            elif self.current_state == STATE_SYSTEM_INFO:
                logger.debug("Transition to system info view")
                
            return True
        
        return False
    
    def _handle_dashboard_input(self, action):
        """Handle input in dashboard state."""
        if action == "SELECT":
            # Toggle freeze state
            self.is_frozen = not self.is_frozen
            self.auto_cycle = not self.is_frozen
            logger.debug(f"Dashboard: {'Frozen' if self.is_frozen else 'Unfrozen'}")
            return True
        elif action == "NEXT" or action == "PREV":
            # Return to menu
            self.previous_state = self.current_state
            self.current_state = STATE_MENU
            logger.debug("Dashboard: Return to menu")
            return True
        
        return False
    
    def _handle_sensor_input(self, action):
        """Handle input in sensor view state."""
        if action == "SELECT":
            # Toggle freeze state
            self.is_frozen = not self.is_frozen
            logger.debug(f"Sensor view: {'Frozen' if self.is_frozen else 'Unfrozen'}")
            return True
        elif action == "NEXT":
            # Return to menu, we're not cycling through sensors now
            self.previous_state = self.current_state
            self.current_state = STATE_MENU
            logger.debug("Sensor view: Return to menu")
            return True
        elif action == "PREV":
            # Return to menu
            self.previous_state = self.current_state
            self.current_state = STATE_MENU
            logger.debug("Sensor view: Return to menu")
            return True

        return False
        
    def _handle_system_info_input(self, action):
        """Handle input in system info view state."""
        if action == "SELECT":
            # Toggle freeze state for system info
            self.is_frozen = not self.is_frozen
            logger.debug(f"System info: {'Frozen' if self.is_frozen else 'Unfrozen'}")
            return True
        elif action == "NEXT" or action == "PREV":
            # Return to menu
            self.previous_state = self.current_state
            self.current_state = STATE_MENU
            logger.debug("System info: Return to menu")
            return True
        
        return False
    
    def get_current_menu_items(self):
        """Get the list of currently visible menu items."""
        return self.current_menu
    
    def get_current_menu_index(self):
        """Get the index of the currently selected menu item."""
        return self.menu_index
    
    def auto_cycle_dashboard(self, current_time):
        """
        Check if it's time to cycle to the next sensor in dashboard mode.
        
        Args:
            current_time (float): The current time in seconds
            
        Returns:
            bool: True if the cycle was performed, False otherwise
        """
        if (self.current_state != STATE_DASHBOARD or 
            self.is_frozen or 
            not self.auto_cycle):
            return False
            
        # Check if enough time has passed to cycle
        if current_time - self.last_cycle_time >= self.config.AUTO_CYCLE_INTERVAL:
            # Cycle to next sensor
            sensors = self.config.SENSOR_MODES
            self.cycle_index = (self.cycle_index + 1) % len(sensors)
            self.current_sensor = sensors[self.cycle_index]
            self.last_cycle_time = current_time
            logger.debug(f"Auto-cycling to {self.current_sensor}")
            return True
            
        return False 