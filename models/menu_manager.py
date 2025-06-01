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
        self.menu_index = 0
        self.secret_menu_index = 0
        
        # Generate menu items
        self.main_menu_items = self._generate_main_menu_items()
        self.sensors_menu_items = self._generate_sensors_menu_items()
        self.secret_menu_items = self._generate_secret_menu_items()
        
        # Menu navigation stack for hierarchical menus
        self.current_menu = self.main_menu_items
        self.menu_stack = []
        
        # Find settings menu index for secret combo
        self.settings_menu_index = self._find_settings_menu_index()
        
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
        
    def _find_settings_menu_index(self):
        """Find the index of the Settings menu item for secret combo detection."""
        for i, item in enumerate(self.main_menu_items):
            if item.name == "Settings":
                logger.info(f"Found Settings menu item at index: {i}")
                return i
        
        logger.warning("Could not find 'Settings' in main menu items for secret combo.")
        return -1
        
    def navigate_next(self, current_state):
        """
        Navigate to the next menu item.
        
        Args:
            current_state (str): Current application state
            
        Returns:
            bool: True if navigation occurred
        """
        menu_items = self._get_current_menu_items(current_state)
        if not menu_items:
            return False
            
        if current_state == STATE_SECRET_GAMES:
            self.secret_menu_index = (self.secret_menu_index + 1) % len(menu_items)
            logger.debug(f"Secret Menu NEXT: index={self.secret_menu_index}, "
                        f"item='{menu_items[self.secret_menu_index].name}'")
        else:
            self.menu_index = (self.menu_index + 1) % len(menu_items)
            logger.debug(f"Menu NEXT: index={self.menu_index}, "
                        f"item='{menu_items[self.menu_index].name}'")
        return True
        
    def navigate_prev(self, current_state):
        """
        Navigate to the previous menu item.
        
        Args:
            current_state (str): Current application state
            
        Returns:
            bool: True if navigation occurred
        """
        menu_items = self._get_current_menu_items(current_state)
        if not menu_items:
            return False
            
        if current_state == STATE_SECRET_GAMES:
            self.secret_menu_index = (self.secret_menu_index - 1 + len(menu_items)) % len(menu_items)
            logger.debug(f"Secret Menu PREV: index={self.secret_menu_index}, "
                        f"item='{menu_items[self.secret_menu_index].name}'")
        else:
            self.menu_index = (self.menu_index - 1 + len(menu_items)) % len(menu_items)
            logger.debug(f"Menu PREV: index={self.menu_index}, "
                        f"item='{menu_items[self.menu_index].name}'")
        return True
        
    def get_selected_item(self, current_state):
        """
        Get the currently selected menu item.
        
        Args:
            current_state (str): Current application state
            
        Returns:
            MenuItem: The selected menu item, or None
        """
        menu_items = self._get_current_menu_items(current_state)
        if not menu_items:
            return None
            
        if current_state == STATE_SECRET_GAMES:
            return menu_items[self.secret_menu_index]
        else:
            return menu_items[self.menu_index]
            
    def enter_submenu(self, submenu_items):
        """
        Enter a submenu.
        
        Args:
            submenu_items (list): The submenu items to enter
            
        Returns:
            bool: True if submenu was entered
        """
        self.menu_stack.append((self.current_menu, self.menu_index))
        self.current_menu = submenu_items
        self.menu_index = 0
        logger.info("Entered submenu")
        return True
        
    def exit_submenu(self):
        """
        Exit the current submenu and return to the parent menu.
        
        Returns:
            bool: True if submenu was exited
        """
        if self.menu_stack:
            previous_menu, previous_index = self.menu_stack.pop()
            self.current_menu = previous_menu
            self.menu_index = previous_index
            logger.info("Exited submenu")
            return True
        return False
        
    def _get_current_menu_items(self, current_state):
        """Get the current menu items based on state."""
        if current_state == STATE_MENU:
            return self.current_menu
        elif current_state == STATE_SENSORS_MENU:
            return self.sensors_menu_items
        elif current_state == STATE_SECRET_GAMES:
            return self.secret_menu_items
        return []
        
    def get_current_menu_items(self, current_state):
        """Public method to get current menu items."""
        return self._get_current_menu_items(current_state)
        
    def get_current_menu_index(self, current_state):
        """
        Get the current menu index for the given state.
        
        Args:
            current_state (str): Current application state
            
        Returns:
            int: Current menu index
        """
        if current_state == STATE_SECRET_GAMES:
            return self.secret_menu_index
        else:
            return self.menu_index
            
    def set_current_menu_index(self, current_state, value):
        """
        Set the current menu index for the given state.
        
        Args:
            current_state (str): Current application state
            value (int): New menu index value
        """
        if current_state == STATE_SECRET_GAMES:
            self.secret_menu_index = value
        else:
            self.menu_index = value
            
    def get_settings_menu_index(self):
        """Get the settings menu index for secret combo detection."""
        return self.settings_menu_index 