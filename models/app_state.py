# --- models/app_state.py ---
# Manages application state and navigation

import logging

logger = logging.getLogger(__name__)

# Application states
STATE_MENU = "MENU"           # Main menu
STATE_DASHBOARD = "DASHBOARD" # Dashboard/auto-cycling view
STATE_SENSOR_VIEW = "SENSOR"  # Individual sensor view

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
            {"name": "Dashboard", "state": STATE_DASHBOARD, "sensor": None},
            {"name": "Temperature", "state": STATE_SENSOR_VIEW, "sensor": "TEMPERATURE"},
            {"name": "Humidity", "state": STATE_SENSOR_VIEW, "sensor": "HUMIDITY"},
            {"name": "Pressure", "state": STATE_SENSOR_VIEW, "sensor": "PRESSURE"},
            {"name": "Orientation", "state": STATE_SENSOR_VIEW, "sensor": "ORIENTATION"},
            {"name": "Acceleration", "state": STATE_SENSOR_VIEW, "sensor": "ACCELERATION"},
            {"name": "Clock", "state": STATE_SENSOR_VIEW, "sensor": "CLOCK"},
            {"name": "System Info", "state": STATE_MENU, "submenu": [
                {"name": "CPU Usage", "state": STATE_SENSOR_VIEW, "sensor": "CPU_USAGE"},
                {"name": "Memory Usage", "state": STATE_SENSOR_VIEW, "sensor": "MEMORY_USAGE"},
                {"name": "Disk Usage", "state": STATE_SENSOR_VIEW, "sensor": "DISK_USAGE"},
                {"name": "Back", "state": STATE_MENU, "sensor": None, "back": True}
            ]}
        ]
        
        # Track menu hierarchy
        self.current_menu = self.menu_items
        self.menu_stack = []  # Stack to track menu hierarchy
        
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
            
            # Check if this is a "Back" item
            if item.get("back", False):
                # Go back to parent menu if we have one
                if self.menu_stack:
                    self.current_menu = self.menu_stack.pop()
                    self.menu_index = 0  # Reset to top of parent menu
                    logger.debug("Menu navigation: Back to parent menu")
                return True
                
            # Check if this item has a submenu
            if "submenu" in item:
                # Push current menu to stack and navigate to submenu
                self.menu_stack.append(self.current_menu)
                self.current_menu = item["submenu"]
                self.menu_index = 0  # Start at first item in submenu
                logger.debug(f"Menu navigation: Enter submenu {item['name']}")
                return True
                
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
            # Cycle to next sensor in list
            # Check if we are in a submenu context first (optional, depends on how deep we want cycling)
            sensors = self.config.SENSOR_MODES
            try:
                curr_idx = sensors.index(self.current_sensor)
                self.current_sensor = sensors[(curr_idx + 1) % len(sensors)]
                self.is_frozen = False  # Unfreeze when changing
                logger.debug(f"Sensor view: Next -> {self.current_sensor}")
                return True
            except ValueError:
                logger.warning(f"Current sensor {self.current_sensor} not in SENSOR_MODES list for cycling.")
                return False
        elif action == "PREV":
            # If we entered this sensor view from a menu, PREV acts as BACK
            if self.previous_state == STATE_MENU:
                # Restore the previous state (which should be the menu)
                self.current_state = self.previous_state
                # self.previous_state = STATE_SENSOR_VIEW # Update previous state for clarity
                self.current_sensor = None # Clear the specific sensor context
                self.is_frozen = False # Ensure unfrozen when returning to menu
                logger.debug("Sensor view: Back to menu")
                return True
            else:
                # Otherwise (e.g., if we somehow got here from dashboard), cycle to previous sensor
                sensors = self.config.SENSOR_MODES
                try:
                    curr_idx = sensors.index(self.current_sensor)
                    self.current_sensor = sensors[(curr_idx - 1) % len(sensors)]
                    self.is_frozen = False  # Unfreeze when changing
                    logger.debug(f"Sensor view: Prev -> {self.current_sensor}")
                    return True
                except ValueError:
                    logger.warning(f"Current sensor {self.current_sensor} not in SENSOR_MODES list for cycling.")
                    return False # No change if sensor not found

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