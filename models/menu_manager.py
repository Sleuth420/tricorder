# --- models/menu_manager.py ---
# Manages menu navigation and menu item generation

import logging
from .menu_item import MenuItem
# State constants - defined locally to avoid circular imports
STATE_MENU = "MENU"
STATE_SENSORS_MENU = "SENSORS_MENU"
STATE_DASHBOARD = "DASHBOARD"
STATE_SENSOR_VIEW = "SENSOR"
STATE_SYSTEM_INFO = "SYSTEM"
STATE_SETTINGS = "SETTINGS"
STATE_SECRET_GAMES = "SECRET_GAMES"
STATE_SCHEMATICS = "SCHEMATICS"

# Import new settings states
STATE_SETTINGS_WIFI = "SETTINGS_WIFI"
STATE_SETTINGS_BLUETOOTH = "SETTINGS_BLUETOOTH"
STATE_SETTINGS_DEVICE = "SETTINGS_DEVICE"
STATE_SETTINGS_DISPLAY = "SETTINGS_DISPLAY"

import config as app_config

logger = logging.getLogger(__name__)

class MenuManager:
    """Manages menu navigation and menu item generation."""
    
    def __init__(self, config_module):
        """
        Initialize the menu manager.
        
        Args:
            config_module: The configuration module
        """
        self.config = config_module
        
        # Menu state
        self.menu_index = 0             # Index for the current menu on top of the stack
        self.secret_menu_index = 0      # Dedicated index for the secret menu
        
        # Generate menu items
        self.main_menu_items = self._generate_main_menu_items()
        self.sensors_menu_items = self._generate_sensors_menu_items()
        self.secret_menu_items = self._generate_secret_menu_items()
        self.settings_menu_items = self._generate_settings_menu_items() # New settings menu
        
        # Menu navigation stack for hierarchical menus
        # Each element is a tuple: (list_of_menu_items, current_index_in_that_list)
        self.menu_stack = [] 
        self.current_menu_definition = self.main_menu_items # Start with main menu

        # Find settings menu index for secret combo (remains relevant for main menu)
        self.settings_main_menu_idx = self._find_settings_main_menu_idx()

    def _generate_main_menu_items(self):
        """Dynamically generates main menu items."""
        items = []
        
        # Add the "Systems" item first
        items.append(MenuItem(
            name="Systems", 
            target_state=STATE_SYSTEM_INFO, 
            color_key="SIDEBAR_SYSTEM"
        ))

        # Add the "Sensors" submenu item
        items.append(MenuItem(
            name="Sensors", 
            target_state=STATE_SENSORS_MENU, 
            color_key="SIDEBAR_TEMP"
        ))

        # Add other non-sensor items
        items.append(MenuItem(
            name="Sweep", 
            target_state=STATE_DASHBOARD, 
            color_key="SIDEBAR_ALL"
        ))
        items.append(MenuItem(
            name="Schematics", 
            target_state=STATE_SCHEMATICS, 
            color_key="SIDEBAR_SCHEMATICS"
        ))
        items.append(MenuItem(
            name="Settings", 
            target_state=STATE_SETTINGS, 
            color_key="SIDEBAR_SETTINGS"
        ))

        return items

    def _generate_sensors_menu_items(self):
        """Generates the sensors submenu items from config.SENSOR_DISPLAY_PROPERTIES."""
        items = []
        
        # Define system sensor keys that should not appear in the sensors submenu
        system_sensor_keys = {
            self.config.SENSOR_CLOCK,
            self.config.SENSOR_CPU_USAGE,
            self.config.SENSOR_MEMORY_USAGE,
            self.config.SENSOR_DISK_USAGE
        }

        # Add environmental sensors to the submenu
        for sensor_key in self.config.SENSOR_MODES:
            if sensor_key in system_sensor_keys:
                continue

            props = self.config.SENSOR_DISPLAY_PROPERTIES.get(sensor_key)
            if props:
                item_data = {"sensor_type": sensor_key}
                items.append(MenuItem(
                    name=props["display_name"],
                    target_state=STATE_SENSOR_VIEW,
                    data=item_data,
                    color_key=props.get("color_key")
                ))
                
        return items
        
    def _generate_secret_menu_items(self):
        """Generates the secret games menu items."""
        return [
            MenuItem(
                name="Pong", 
                action_name=app_config.ACTION_LAUNCH_PONG, 
                image_path="assets/images/spork.png"
            ),
            MenuItem(
                name="Tetris", 
                action_name=app_config.ACTION_LAUNCH_TETRIS, 
                image_path="assets/images/spork.png"
            ),
            MenuItem(
                name="Quit", 
                action_name=app_config.ACTION_RETURN_TO_MENU, 
                image_path=None
            )
        ]
        
    def _generate_settings_menu_items(self):
        """Generates the settings category menu items."""
        items = [
            MenuItem(
                name="WiFi Settings",
                target_state=STATE_SETTINGS_WIFI,
                color_key="SIDEBAR_SYSTEM" # Example color
            ),
            MenuItem(
                name="Bluetooth Settings",
                target_state=STATE_SETTINGS_BLUETOOTH,
                color_key="SIDEBAR_SYSTEM" # Example color
            ),
            MenuItem(
                name="Device Settings",
                target_state=STATE_SETTINGS_DEVICE,
                color_key="SIDEBAR_SYSTEM" # Example color
            ),
            MenuItem(
                name="Display Settings", # For Auto-Cycle Interval
                target_state=STATE_SETTINGS_DISPLAY,
                color_key="SIDEBAR_SYSTEM" # Example color
            ),
            MenuItem(
                name="<- Back", # New Back item
                target_state=STATE_MENU, # Goes directly to main menu
                color_key="SIDEBAR_SETTINGS" # Consistent color
            )
        ]
        logger.debug(f"Generated settings menu items: {[item.name for item in items]}")
        return items
        
    def _find_settings_main_menu_idx(self):
        """Find the index of the Settings menu item in the main_menu_items for secret combo detection."""
        for i, item in enumerate(self.main_menu_items):
            if item.name == "Settings":
                logger.info(f"Found Settings menu item in main_menu_items at index: {i}")
                return i
        
        logger.warning("Could not find 'Settings' in main_menu_items for secret combo.")
        return -1
        
    def navigate_next(self, current_state):
        """
        Navigate to the next menu item in the currently active menu.
        """
        active_menu_items = self._get_menu_items_for_state(current_state)
        if not active_menu_items:
            return False
            
        if current_state == STATE_SECRET_GAMES:
            self.secret_menu_index = (self.secret_menu_index + 1) % len(active_menu_items)
            logger.debug(f"Secret Menu NEXT: index={self.secret_menu_index}, item='{active_menu_items[self.secret_menu_index].name}'")
        else: # Handles main menu, sensors menu, and now settings menu via menu_stack
            self.menu_index = (self.menu_index + 1) % len(active_menu_items)
            logger.debug(f"Menu NEXT ({current_state}): index={self.menu_index}, item='{active_menu_items[self.menu_index].name}'")
        return True
        
    def navigate_prev(self, current_state):
        """
        Navigate to the previous menu item in the currently active menu.
        """
        active_menu_items = self._get_menu_items_for_state(current_state)
        if not active_menu_items:
            return False
            
        if current_state == STATE_SECRET_GAMES:
            self.secret_menu_index = (self.secret_menu_index - 1 + len(active_menu_items)) % len(active_menu_items)
            logger.debug(f"Secret Menu PREV: index={self.secret_menu_index}, item='{active_menu_items[self.secret_menu_index].name}'")
        else: # Handles main menu, sensors menu, and now settings menu via menu_stack
            self.menu_index = (self.menu_index - 1 + len(active_menu_items)) % len(active_menu_items)
            logger.debug(f"Menu PREV ({current_state}): index={self.menu_index}, item='{active_menu_items[self.menu_index].name}'")
        return True
        
    def get_selected_item(self, current_state):
        """
        Get the currently selected menu item from the active menu.
        """
        active_menu_items = self._get_menu_items_for_state(current_state)
        if not active_menu_items:
            return None
            
        idx_to_use = self.secret_menu_index if current_state == STATE_SECRET_GAMES else self.menu_index
        
        if 0 <= idx_to_use < len(active_menu_items):
            return active_menu_items[idx_to_use]
        logger.warning(f"Selected index {idx_to_use} out of bounds for {current_state} menu with {len(active_menu_items)} items.")
        return None
            
    def enter_submenu(self, new_menu_items_list, parent_state_to_push_on_stack, new_submenu_state_name_for_logging):
        """
        Enter a submenu, pushing the current (parent) menu and index onto the stack.
        
        Args:
            new_menu_items_list (list): The MenuItem list for the submenu to enter.
            parent_state_to_push_on_stack (str): The state name of the current menu (which is becoming the parent).
            new_submenu_state_name_for_logging (str): The name of the state associated with the new submenu being entered.
                                                     Used for logging/debugging.
            
        Returns:
            bool: True if submenu was entered.
        """
        # Push the PARENT menu's definition, its current index, and its state name onto the stack
        self.menu_stack.append((self.current_menu_definition, self.menu_index, parent_state_to_push_on_stack))
        
        # Now, set the MenuManager's current definition and index for the NEW submenu
        self.current_menu_definition = new_menu_items_list
        self.menu_index = 0 # Reset index for the new menu
        
        logger.info(f"Entered submenu for state: {new_submenu_state_name_for_logging}. Parent was {parent_state_to_push_on_stack}. Stack depth: {len(self.menu_stack)}")
        return True
        
    def exit_submenu(self):
        """
        Exit the current submenu and return to the parent menu.
        The state transition itself is handled by AppState.
        
        Returns:
            str: The state name of the menu we are returning to, or None if stack is empty.
        """
        if self.menu_stack:
            previous_menu_def, previous_index, previous_state_name = self.menu_stack.pop()
            self.current_menu_definition = previous_menu_def
            self.menu_index = previous_index
            logger.info(f"Exited submenu. Returning to menu for state: {previous_state_name}. Stack depth: {len(self.menu_stack)}")
            return previous_state_name
        logger.warning("Attempted to exit submenu, but menu stack is empty.")
        return None # Should ideally return to main menu state or similar default
        
    def _get_menu_items_for_state(self, current_state):
        """Helper to get the list of MenuItems for the current state/menu."""
        if current_state == STATE_MENU:
            # If menu_stack is empty, this is the main menu. Otherwise, it's a submenu navigated to from main.
            return self.current_menu_definition # This will be main_menu_items if stack is empty
        elif current_state == STATE_SENSORS_MENU:
            return self.sensors_menu_items # Sensors menu is directly managed
        elif current_state == STATE_SECRET_GAMES:
            return self.secret_menu_items # Secret games menu is directly managed
        elif current_state == STATE_SETTINGS: # This is the main settings category menu
            return self.settings_menu_items
        # For sub-settings states like STATE_SETTINGS_WIFI, they might have their own menus
        # or they might be views without menus. If they have menus, this method needs expansion
        # or the AppState needs to ensure MenuManager is correctly set up when transitioning.
        # For now, sub-settings views are assumed not to be menus themselves handled by this part of MenuManager.
        # The current_menu_definition on the stack handles current items for stacked menus.
        
        # If current_state is STATE_SETTINGS_WIFI, it doesn't have its own menu list in MenuManager directly.
        # Its items are handled by WifiManager. So, return an empty list or specific items if needed.
        if current_state == STATE_SETTINGS_WIFI:
            # This view is managed by WifiManager, not a menu list here.
            # AppState will fetch options from WifiManager for the view.
            return [] # Or None, depending on how AppState/DisplayManager handles it.

        # Fallback for states that are currently on the menu_stack (submenus of main menu)
        if self.menu_stack:
             # The top of the stack's definition is what we are currently in theory.
             # However, current_menu_definition should ALREADY point to the correct list.
             pass

        # If the state implies it's a menu managed by the stack, current_menu_definition should be correct.
        # This logic primarily relies on AppState calling enter_submenu/exit_submenu correctly.
        return self.current_menu_definition

    def get_current_menu_items(self, current_state): # Public access, calls helper
        """Public method to get current menu items."""
        return self._get_menu_items_for_state(current_state)
        
    def get_current_menu_index(self, current_state):
        """
        Get the current menu index for the given state.
        This now primarily returns self.menu_index for stack-managed menus
        or specific indices for non-stacked menus like secret_menu.
        """
        if current_state == STATE_SECRET_GAMES:
            return self.secret_menu_index
        # For STATE_MENU, STATE_SENSORS_MENU, STATE_SETTINGS, and any submenus managed by the stack:
        return self.menu_index 
            
    def set_current_menu_index(self, current_state, value):
        """
        Set the current menu index for the given state.
        """
        if current_state == STATE_SECRET_GAMES:
            self.secret_menu_index = value
        elif current_state == STATE_SETTINGS_WIFI: # Added handling for STATE_SETTINGS_WIFI
            # Wifi settings view uses its own index in WifiManager, not here.
            # This might log a warning or do nothing, as AppState should delegate to WifiManager.
            logger.debug(f"Attempted to set menu index for STATE_SETTINGS_WIFI in MenuManager. Should be handled by WifiManager.")
            pass 
        else: # For main_menu, sensors_menu, settings_menu and stacked submenus
            active_menu = self._get_menu_items_for_state(current_state)
            if active_menu: # Ensure menu exists before trying to set index
                 self.menu_index = value % len(active_menu) if len(active_menu) > 0 else 0
            else:
                self.menu_index = 0


    def get_settings_main_menu_idx(self):
        """Get the settings menu index for secret combo detection (from main menu)."""
        return self.settings_main_menu_idx

    def reset_to_main_menu(self):
        """Resets the menu manager to the main menu state."""
        self.menu_stack.clear()
        self.current_menu_definition = self.main_menu_items
        self.menu_index = 0 # Reset to the first item of the main menu
        logger.info("MenuManager reset to main menu.") 