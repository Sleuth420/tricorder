# --- models/app_state.py ---
# Manages application state and navigation

import logging
import time # Import time for last_reading_time initialization
import pygame # Import pygame for key codes
# Import PongGame
from games.pong import PongGame
# Import MenuItem dataclass
from .menu_item import MenuItem # Assuming menu_item.py is in the same directory (models)
# Import config for sensor mode constants and action name constants
import config as app_config # Use an alias to avoid conflict with self.config

logger = logging.getLogger(__name__)

# Application states (remains as string literals, used internally and by display_manager)
STATE_MENU = "MENU"           # Main menu
STATE_DASHBOARD = "DASHBOARD" # Dashboard/auto-cycling view
STATE_SENSOR_VIEW = "SENSOR"  # Individual sensor view
STATE_SYSTEM_INFO = "SYSTEM"  # System info view
STATE_SETTINGS = "SETTINGS"   # Settings view
STATE_SECRET_GAMES = "SECRET_GAMES" # New state for secret menu
STATE_PONG_ACTIVE = "PONG_ACTIVE" # New state for Pong game

class AppState:
    """Manages the state of the application and navigation."""
    
    def __init__(self, config_module): # config_module is the actual config.py module
        """
        Initialize the application state.
        
        Args:
            config_module: The configuration module (config.py)
        """
        self.config = config_module # Store the passed config module
        self.current_state = STATE_MENU
        self.previous_state = None
        self.last_reading_time = 0.0 # Initialize last reading time
        
        # Input state for combo detection
        self.keys_held = set()
        self.secret_combo_start_time = None
        self.key_prev_press_start_time = None # Track start time for KEY_PREV long press

        # Menu state
        self.menu_index = 0
        # Main menu items - To be dynamically generated
        self.menu_items = self._generate_main_menu_items()
        
        # Track menu hierarchy - no more submenu structure
        self.current_menu = self.menu_items # This will now hold MenuItem objects
        self.menu_stack = []  # Stack to track menu hierarchy, but we won't use it for now
        
        # Sensor view state
        self.current_sensor = None # This will store the sensor_type constant like app_config.SENSOR_TEMPERATURE
        self.is_frozen = False
        self.auto_cycle = True
        self.last_cycle_time = 0
        self.cycle_index = 0

        # Secret Games Menu state
        self.secret_menu_index = 0
        self.secret_menu_items = [
            MenuItem(name="Pong", action_name=app_config.ACTION_LAUNCH_PONG, image_path="images/spork.png"),
            MenuItem(name="Tetris", action_name=app_config.ACTION_LAUNCH_TETRIS, image_path="images/spork.png"),
            MenuItem(name="Quit", action_name=app_config.ACTION_RETURN_TO_MENU, image_path=None)
        ]
        self.active_pong_game = None

        # Find the index for the "Settings" menu item for combo check
        self.settings_menu_index = -1
        for i, item in enumerate(self.menu_items):
            if item.name == "Settings": # Assuming "Settings" is still the name from SENSOR_DISPLAY_PROPERTIES
                self.settings_menu_index = i
                break
        if self.settings_menu_index == -1:
            logger.warning("Could not find 'Settings' in dynamically generated menu_items for secret combo.")
        else:
            logger.info(f"Found Settings menu item at index: {self.settings_menu_index}")

    def _generate_main_menu_items(self):
        """Dynamically generates main menu items from config.SENSOR_DISPLAY_PROPERTIES."""
        items = []
        # Define system sensor keys that are covered by the "Systems" menu item (STATE_SYSTEM_INFO)
        # and should not get their own individual top-level menu items.
        system_sensor_keys = {
            self.config.SENSOR_CLOCK,
            self.config.SENSOR_CPU_USAGE,
            self.config.SENSOR_MEMORY_USAGE,
            self.config.SENSOR_DISK_USAGE
        }

        # Add the "Systems" item first.
        items.append(MenuItem(name="Systems", target_state=STATE_SYSTEM_INFO, color_key="SIDEBAR_SYSTEM"))

        # Add environmental sensors next
        for sensor_key in self.config.SENSOR_MODES: # Iterate through defined sensor modes
            if sensor_key in system_sensor_keys: # Skip system-specific sensors for individual menu items
                continue

            props = self.config.SENSOR_DISPLAY_PROPERTIES.get(sensor_key)
            if props:
                # Default target state for individual sensor menu items is SENSOR_VIEW
                target_st = STATE_SENSOR_VIEW
                item_data = {"sensor_type": sensor_key}

                items.append(MenuItem(
                    name=props["display_name"],
                    target_state=target_st,
                    data=item_data,
                    color_key=props.get("color_key")
                ))
                
        # Add other non-sensor items last
        items.append(MenuItem(name="Sweep", target_state=STATE_DASHBOARD, color_key="SIDEBAR_ALL"))
        items.append(MenuItem(name="Settings", target_state=STATE_SETTINGS, color_key="SIDEBAR_SETTINGS"))

        return items
        
    def _check_secret_combo_conditions(self):
        """Check if conditions are met to START the secret combo timer."""
        required_keys = {self.config.KEY_PREV, self.config.KEY_NEXT}
        state_ok = self.current_state == STATE_MENU
        index_ok = self.menu_index == self.settings_menu_index
        keys_ok = required_keys.issubset(self.keys_held)
        logger.debug(f"Combo check: state='{self.current_state}'({state_ok}), index={self.menu_index}({index_ok}), settings_idx={self.settings_menu_index}, keys={self.keys_held}({keys_ok})")
        return state_ok and index_ok and keys_ok

    def _activate_secret_menu(self):
        """Transition to the secret menu state."""
        logger.info("Secret combo duration met! Activating secret games menu.")
        self.previous_state = self.current_state
        self.current_state = STATE_SECRET_GAMES
        self.secret_combo_start_time = None # Reset timer
        return True # State changed

    def handle_input(self, input_results):
        state_changed_by_action = False
        combo_potentially_active = bool(self.secret_combo_start_time)

        for result in input_results:
            event_type = result['type']
            key = result.get('key') 
            action_name = result.get('action') # This is INPUT_ACTION_PREV etc.

            if event_type == 'QUIT':
                pass # Main loop handles this via running = False

            elif event_type == 'KEYDOWN':
                self.keys_held.add(key)
                logger.debug(f"KEYDOWN: key={key}. keys_held={self.keys_held}")

                if key == self.config.KEY_PREV and self.key_prev_press_start_time is None:
                    self.key_prev_press_start_time = time.time()
                    logger.debug("KEY_PREV press timer started.")

                if not self.secret_combo_start_time and self._check_secret_combo_conditions():
                    logger.info("SECRET COMBO TIMER STARTED")
                    self.secret_combo_start_time = time.time()
                    combo_potentially_active = True 
                # No direct PONG input handling here on KeyDown - PongGame.update uses keys_held

            elif event_type == 'KEYUP':
                combo_was_active = bool(self.secret_combo_start_time)
                if key in self.keys_held:
                    self.keys_held.remove(key)
                logger.debug(f"KEYUP: key={key}. keys_held={self.keys_held}")

                if self.secret_combo_start_time and (key == self.config.KEY_PREV or key == self.config.KEY_NEXT):
                    logger.info("SECRET COMBO TIMER RESET (Key Up)")
                    self.secret_combo_start_time = None
                    combo_potentially_active = False
                
                if not combo_was_active: # Only process standard actions if combo wasn't just active/reset
                    if key == self.config.KEY_PREV and self.key_prev_press_start_time is not None:
                        press_duration = time.time() - self.key_prev_press_start_time
                        self.key_prev_press_start_time = None 
                        logger.debug("KEY_PREV released, timer reset.")
                        if self.current_state == STATE_PONG_ACTIVE and self.active_pong_game and self.active_pong_game.paused and action_name == app_config.INPUT_ACTION_PREV:
                            logger.info("PREV key released in paused Pong. Unpausing.")
                            self.active_pong_game.toggle_pause()
                            state_changed_by_action = True
                        elif self.current_state in [STATE_MENU, STATE_SECRET_GAMES] and press_duration < self.config.INPUT_LONG_PRESS_DURATION and action_name == app_config.INPUT_ACTION_PREV:
                            logger.debug(f"Short press PREV in {self.current_state} state: processing PREV action on KeyUp.")
                            state_changed_by_action = self._process_action(app_config.INPUT_ACTION_PREV) or state_changed_by_action
                        
                    elif key == self.config.KEY_NEXT and action_name == app_config.INPUT_ACTION_NEXT:
                         if self.current_state == STATE_PONG_ACTIVE and self.active_pong_game and self.active_pong_game.paused:
                             logger.info("NEXT key released in paused Pong. Quitting game.")
                             if self.previous_state:
                                 self.current_state = self.previous_state
                             else:
                                 self.current_state = STATE_MENU 
                             self.previous_state = STATE_PONG_ACTIVE
                             self.active_pong_game = None 
                             state_changed_by_action = True
                             logger.debug(f"State changed via NEXT (Quit) in paused Pong: -> {self.current_state}")
                         elif self.current_state in [STATE_MENU, STATE_SECRET_GAMES]:
                             logger.debug(f"Short press NEXT in {self.current_state} state: processing NEXT action on KeyUp.")
                             state_changed_by_action = self._process_action(app_config.INPUT_ACTION_NEXT) or state_changed_by_action

                    elif key == self.config.KEY_SELECT and action_name == app_config.INPUT_ACTION_SELECT:
                         if self.current_state == STATE_PONG_ACTIVE and self.active_pong_game:
                             logger.info("SELECT key released in Pong. Toggling pause.")
                             self.active_pong_game.toggle_pause()
                             state_changed_by_action = True 
                         else: 
                             logger.debug("Short press SELECT: processing SELECT action on KeyUp.")
                             state_changed_by_action = self._process_action(app_config.INPUT_ACTION_SELECT) or state_changed_by_action
                    
                    elif action_name == app_config.INPUT_ACTION_BACK: # Handle JOY_LEFT mapped to BACK
                        # Allow back from most states except main menu and active (unpaused) pong
                        if self.current_state not in [STATE_MENU, STATE_PONG_ACTIVE, STATE_SECRET_GAMES]:
                            logger.info(f"BACK action triggered by key {key} in state {self.current_state}. Returning to menu.")
                            state_changed_by_action = self._return_to_menu() or state_changed_by_action
                        elif self.current_state == STATE_SECRET_GAMES:
                             # In secret games menu, BACK action might be identical to selecting "Quit" menu item.
                             # Or, we can make it a dedicated back. For now, let it be handled by its own menu items.
                             logger.debug(f"BACK action triggered in {self.current_state}, typically handled by menu item.")
                             pass # Let specific menu logic handle it if needed or do nothing.
                        # In PONG_ACTIVE, back is handled by KEY_NEXT when paused, or not at all if active.
                        # In MENU, there's nowhere to go "back" to via this action.

        return state_changed_by_action

    def update(self):
        state_changed = False
        if self.secret_combo_start_time:
            current_time = time.time()
            duration = current_time - self.secret_combo_start_time
            required_duration = self.config.SECRET_HOLD_DURATION
            logger.debug(f"Checking combo timer: duration={duration:.2f}, required={required_duration}")
            if duration >= required_duration:
                state_changed = self._activate_secret_menu()
                if state_changed:
                    return state_changed

        if self.key_prev_press_start_time is not None:
            hold_duration = time.time() - self.key_prev_press_start_time
            if hold_duration >= self.config.INPUT_LONG_PRESS_DURATION:
                if self.current_state != STATE_PONG_ACTIVE and self.current_state not in [STATE_MENU, STATE_SECRET_GAMES]: 
                    logger.info(f"Long press KEY_PREV detected in state {self.current_state}. Returning to menu.")
                    state_changed = self._return_to_menu()
                else:
                    logger.debug(f"Long press KEY_PREV in {self.current_state} state - ignored for back action.")
                self.key_prev_press_start_time = None 
        return state_changed

    def _process_action(self, action):
        state_changed = False
        # Use action constants for comparison
        if self.current_state == STATE_MENU:
            state_changed = self._handle_menu_input(action)
        elif self.current_state == STATE_DASHBOARD:
            state_changed = self._handle_dashboard_input(action)
        elif self.current_state == STATE_SENSOR_VIEW:
            state_changed = self._handle_sensor_input(action)
        elif self.current_state == STATE_SYSTEM_INFO:
            state_changed = self._handle_system_info_input(action)
        elif self.current_state == STATE_SETTINGS:
            state_changed = self._handle_settings_input(action)
        elif self.current_state == STATE_SECRET_GAMES:
            state_changed = self._handle_secret_games_input(action)
        return state_changed

    def _return_to_menu(self):
        self.previous_state = self.current_state
        self.current_state = STATE_MENU
        logger.debug(f"{self.previous_state}: Return to menu")
        return True
    
    def _handle_menu_input(self, action):
        if not self.menu_items: return False
        num_items = len(self.menu_items)
        if action == app_config.INPUT_ACTION_NEXT:
            self.menu_index = (self.menu_index + 1) % num_items
            logger.debug(f"Menu NEXT: index={self.menu_index}, item='{self.menu_items[self.menu_index].name}'")
        elif action == app_config.INPUT_ACTION_PREV:
            self.menu_index = (self.menu_index - 1 + num_items) % num_items
            logger.debug(f"Menu PREV: index={self.menu_index}, item='{self.menu_items[self.menu_index].name}'")
        elif action == app_config.INPUT_ACTION_SELECT:
            selected_item = self.menu_items[self.menu_index]
            logger.info(f"Menu SELECT: item='{selected_item.name}'")
            if selected_item.target_state:
                self.previous_state = self.current_state
                self.current_state = selected_item.target_state
                if selected_item.target_state == STATE_SENSOR_VIEW and selected_item.data and "sensor_type" in selected_item.data:
                    self.current_sensor = selected_item.data["sensor_type"] # sensor_type is a constant
                    logger.info(f"Transitioning to SENSOR_VIEW for sensor: {self.current_sensor}")
                else:
                    self.current_sensor = None 
                return True 
        return False 
    
    def _handle_common_select_action(self, view_name):
        """Common handler for SELECT action that toggles freeze."""
        self.is_frozen = not self.is_frozen
        logger.debug(f"{view_name}: {'Frozen' if self.is_frozen else 'Unfrozen'} by SELECT action.")
        return True # Indicates a UI update might be needed due to freeze status change

    def _handle_dashboard_input(self, action):
        if action == app_config.INPUT_ACTION_SELECT:
            self.auto_cycle = not self.auto_cycle # Toggle auto_cycle as well for dashboard
            return self._handle_common_select_action("Dashboard")
        return False
    
    def _handle_sensor_input(self, action):
        if action == app_config.INPUT_ACTION_SELECT:
            return self._handle_common_select_action("Sensor View")
        return False
        
    def _handle_system_info_input(self, action):
        if action == app_config.INPUT_ACTION_SELECT:
            return self._handle_common_select_action("System Info")
        return False
    
    def _handle_settings_input(self, action):
        if action == app_config.INPUT_ACTION_SELECT:
            # Placeholder for actual settings change logic
            # For now, it also toggles freeze like other views.
            logger.debug(f"Settings: SELECT pressed. Future: modify settings.")
            return self._handle_common_select_action("Settings")
        return False
    
    def _handle_secret_games_input(self, action):
        if not self.secret_menu_items: return False
        num_items = len(self.secret_menu_items)
        if action == app_config.INPUT_ACTION_NEXT:
            self.secret_menu_index = (self.secret_menu_index + 1) % num_items
            logger.debug(f"Secret Menu NEXT: index={self.secret_menu_index}, item='{self.secret_menu_items[self.secret_menu_index].name}'")
        elif action == app_config.INPUT_ACTION_PREV:
            self.secret_menu_index = (self.secret_menu_index - 1 + num_items) % num_items
            logger.debug(f"Secret Menu PREV: index={self.secret_menu_index}, item='{self.secret_menu_items[self.secret_menu_index].name}'")
        elif action == app_config.INPUT_ACTION_SELECT:
            selected_item = self.secret_menu_items[self.secret_menu_index]
            logger.info(f"Secret Menu SELECT: item='{selected_item.name}' with action='{selected_item.action_name}'")
            
            if selected_item.action_name == app_config.ACTION_LAUNCH_PONG:
                logger.info("Launching Pong...")
                self.previous_state = self.current_state
                self.current_state = STATE_PONG_ACTIVE
                self.active_pong_game = PongGame(self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT, self.config)
                return True 
            elif selected_item.action_name == app_config.ACTION_LAUNCH_TETRIS:
                logger.warning("Tetris launch selected, but not yet implemented.")
                pass 
            elif selected_item.action_name == app_config.ACTION_RETURN_TO_MENU:
                logger.info("Returning to main menu from secret menu.")
                if self.previous_state and self.previous_state != STATE_SECRET_GAMES:
                    self.current_state = self.previous_state 
                else:
                    self.current_state = STATE_MENU 
                self.previous_state = STATE_SECRET_GAMES 
                self.secret_combo_start_time = None 
                return True 
        return False 
    
    def get_current_menu_items(self):
        if self.current_state == STATE_MENU:
            return self.menu_items
        elif self.current_state == STATE_SECRET_GAMES:
            return self.secret_menu_items
        return [] 

    def get_current_menu_index(self):
        if self.current_state == STATE_MENU:
            return self.menu_index
        elif self.current_state == STATE_SECRET_GAMES:
            return self.secret_menu_index
        return 0 
    
    def auto_cycle_dashboard(self, current_time):
        if (self.current_state != STATE_DASHBOARD or self.is_frozen or not self.auto_cycle):
            return False
            
        if current_time - self.last_cycle_time >= self.config.AUTO_CYCLE_INTERVAL:
            dashboard_sensors = [ 
                key for key in self.config.SENSOR_MODES 
                if self.config.SENSOR_DISPLAY_PROPERTIES.get(key, {}).get("graph_type") != "NONE" and key != app_config.SENSOR_CLOCK
            ]
            if not dashboard_sensors:
                logger.warning("No sensors defined for dashboard cycling based on SENSOR_DISPLAY_PROPERTIES.")
                return False

            self.cycle_index = (self.cycle_index + 1) % len(dashboard_sensors)
            self.current_sensor = dashboard_sensors[self.cycle_index] # current_sensor is a constant
            self.last_cycle_time = current_time
            logger.debug(f"Auto-cycling to {self.current_sensor}")
            return True
        return False 