# --- models/app_state.py ---
# Application state management using component managers

import logging
import time
import os # For device actions
from .state_manager import StateManager
from .input_manager import InputManager
from .menu_manager import MenuManager
from .game_manager import GameManager
from .settings_manager import SettingsManager
from .device_manager import DeviceManager
from .wifi_manager import WifiManager, WIFI_ACTION_TOGGLE, WIFI_ACTION_BACK_TO_SETTINGS # Import WifiManager and relevant actions
import config as app_config

# Application state constants
STATE_MENU = "MENU"           # Main menu
STATE_SENSORS_MENU = "SENSORS_MENU"  # Sensors submenu
STATE_DASHBOARD = "DASHBOARD" # Dashboard/auto-cycling view
STATE_SENSOR_VIEW = "SENSOR"  # Individual sensor view
STATE_SYSTEM_INFO = "SYSTEM"  # System info view
STATE_SETTINGS = "SETTINGS"   # Main settings category menu
STATE_SECRET_GAMES = "SECRET_GAMES" # Secret menu
STATE_PONG_ACTIVE = "PONG_ACTIVE" # Pong game
STATE_SCHEMATICS = "SCHEMATICS" # Schematics viewer

# New Settings Sub-View States
STATE_SETTINGS_WIFI = "SETTINGS_WIFI"
STATE_SETTINGS_BLUETOOTH = "SETTINGS_BLUETOOTH"
STATE_SETTINGS_DEVICE = "SETTINGS_DEVICE"
STATE_SETTINGS_DISPLAY = "SETTINGS_DISPLAY"
STATE_SELECT_COMBO_DURATION = "SELECT_COMBO_DURATION" # New state for selecting combo duration

# Confirmation States (New)
STATE_CONFIRM_REBOOT = "CONFIRM_REBOOT"
STATE_CONFIRM_SHUTDOWN = "CONFIRM_SHUTDOWN"
STATE_CONFIRM_RESTART_APP = "CONFIRM_RESTART_APP"



logger = logging.getLogger(__name__)

class AppState:
    """
    Application state management using component managers.
    
    This class coordinates between different managers instead of handling
    everything directly, following the Single Responsibility Principle.
    """
    
    def __init__(self, config_module, screen_width, screen_height):
        """
        Initialize the application state.
        
        Args:
            config_module: The configuration module
            screen_width (int): The actual width of the screen
            screen_height (int): The actual height of the screen
        """
        self.config = config_module
        self.actual_screen_width = screen_width
        self.actual_screen_height = screen_height
        
        # Initialize component managers
        self.state_manager = StateManager(config_module)
        self.input_manager = InputManager(config_module)
        self.menu_manager = MenuManager(config_module)
        self.game_manager = GameManager(config_module, screen_width, screen_height)
        self.settings_manager = SettingsManager(config_module)
        self.device_manager = DeviceManager(config_module)
        self.wifi_manager = WifiManager(config_module) # Instantiate WifiManager (no command func needed)
        
        # Set up cross-component dependencies
        self.input_manager.set_settings_menu_index(
            self.menu_manager.get_settings_main_menu_idx()
        )
        
        # Core sensor and view state
        self.current_sensor = None
        self.is_frozen = False
        self.auto_cycle = True
        self.last_cycle_time = 0
        self.cycle_index = 0
        self.last_reading_time = 0.0
        
    @property
    def current_state(self):
        """Get the current application state."""
        return self.state_manager.current_state
        
    @property
    def previous_state(self):
        """Get the previous application state."""
        return self.state_manager.previous_state
        
    @property
    def keys_held(self):
        """Get the currently held keys."""
        return self.input_manager.keys_held
        
    @property
    def active_pong_game(self):
        """Get the active Pong game instance."""
        return self.game_manager.get_pong_game()

    @property
    def secret_menu_items(self):
        """Get secret menu items (compatibility property)."""
        return self.menu_manager.secret_menu_items
        
    @property
    def secret_menu_index(self):
        """Get secret menu index (compatibility property)."""
        return self.menu_manager.secret_menu_index

    # Settings Manager Properties for UI compatibility
    @property
    def display_settings_option_index(self):
        """Get display settings option index."""
        return self.settings_manager.display_settings_option_index
    
    @property
    def combo_duration_selection_index(self):
        """Get combo duration selection index."""
        return self.settings_manager.combo_duration_selection_index

    # Device Manager Properties for UI compatibility
    @property
    def device_settings_option_index(self):
        """Get device settings option index."""
        return self.device_manager.device_settings_option_index
    
    @property
    def confirmation_option_index(self):
        """Get confirmation option index."""
        return self.device_manager.confirmation_option_index
    
    @property
    def pending_device_action(self):
        """Get pending device action."""
        return self.device_manager.pending_device_action

    @property
    def menu_items(self):
        """Get current menu items (compatibility property)."""
        return self.menu_manager.get_current_menu_items(self.current_state)
        
    @property
    def menu_index(self):
        """Get current menu index (compatibility property)."""
        return self.menu_manager.get_current_menu_index(self.current_state)
        
    @menu_index.setter
    def menu_index(self, value):
        """Set current menu index (compatibility property)."""
        self.menu_manager.set_current_menu_index(self.current_state, value)

    def set_state(self, new_state):
        """Set the application state (compatibility method)."""
        # When entering WiFi settings, trigger a status check
        if new_state == STATE_SETTINGS_WIFI and self.current_state != STATE_SETTINGS_WIFI:
            if self.wifi_manager:
                self.wifi_manager.update_wifi_status() # WifiManager handles its own status update
        return self.state_manager.transition_to(new_state)

    def handle_input(self, input_results):
        """
        Handle input events using the input manager and route to appropriate handlers.
        
        Args:
            input_results (list): List of input event dictionaries
            
        Returns:
            bool: True if state changed
        """
        state_changed_by_action = False

        for result in input_results:
            event_type = result['type']
            key = result.get('key')
            action_name = result.get('action')

            if event_type == self.config.INPUT_ACTION_QUIT:
                logger.info(f"'{self.config.INPUT_ACTION_QUIT}' action type received")
                continue

            elif event_type == 'KEYDOWN':
                self.input_manager.handle_keydown(key)
                
                # Check for secret combo start (on main menu settings item)
                if (self.current_state == STATE_MENU and
                    not self.input_manager.secret_combo_start_time and
                    self.input_manager.check_secret_combo_conditions(
                        self.current_state, 
                        self.menu_manager.get_current_menu_index(STATE_MENU)
                    )):
                    self.input_manager.start_secret_combo_timer()
                    
            elif event_type == 'KEYUP':
                key_event = self.input_manager.handle_keyup(key)
                
                if not self.input_manager.secret_combo_start_time:
                    state_changed_by_action = self._handle_key_release(key, action_name) or state_changed_by_action
            
            elif event_type == 'JOYSTICK':
                if action_name:
                    if self.current_state == STATE_PONG_ACTIVE:
                        state_changed_by_action = self._handle_pong_joystick_input(action_name) or state_changed_by_action
                    else:
                        state_changed_by_action = self._process_action(action_name) or state_changed_by_action

            elif event_type == 'JOYSTICK_UP_HELD':
                if self.current_state == STATE_PONG_ACTIVE:
                    self.game_manager.handle_pong_input(app_config.INPUT_ACTION_PREV)
            
            elif event_type == 'JOYSTICK_DOWN_HELD':
                if self.current_state == STATE_PONG_ACTIVE:
                    self.game_manager.handle_pong_input(app_config.INPUT_ACTION_NEXT)

            elif event_type == 'JOYSTICK_MIDDLE_PRESS':
                self.input_manager.handle_joystick_press()
            
            elif event_type == 'JOYSTICK_MIDDLE_RELEASE':
                release_event = self.input_manager.handle_joystick_release()
                press_duration = release_event.get('press_duration', 0)
                
                current_state_before_select = self.current_state

                if (current_state_before_select == STATE_MENU and 
                    self.menu_manager.get_current_menu_index(STATE_MENU) == self.menu_manager.get_settings_main_menu_idx() and
                    press_duration >= self.config.CURRENT_SECRET_COMBO_DURATION):
                    logger.debug("Joystick long press for secret menu (on Settings item) handled by update()")
                elif current_state_before_select != STATE_SECRET_GAMES: 
                    logger.info(f"Joystick short press: Processing SELECT in {current_state_before_select}")
                    
                    if state_changed_by_action:
                        logger.info("State already changed in this input cycle. Skipping SELECT action.")
                    else:
                        state_changed_by_action = self._process_action(app_config.INPUT_ACTION_SELECT) or state_changed_by_action
                
        return state_changed_by_action
        
    def _handle_key_release(self, key, action_name):
        """Handle key release events."""
        state_changed = False
        
        if self.current_state == STATE_PONG_ACTIVE and self.active_pong_game:
            if self.active_pong_game.game_over and key == self.config.KEY_PREV:
                state_changed = self._quit_pong_to_menu()
            elif action_name:
                game_result = self.game_manager.handle_pong_input(action_name)
                if game_result == "QUIT_TO_MENU":
                    state_changed = self._quit_pong_to_menu()
                elif game_result:
                    state_changed = True
        
        # General key releases for menu navigation or back action
        elif action_name == app_config.INPUT_ACTION_BACK:
            if self.current_state not in [STATE_MENU, STATE_PONG_ACTIVE, STATE_SECRET_GAMES, STATE_SENSORS_MENU, STATE_SETTINGS]:
                state_changed = self.state_manager.return_to_previous()
                if not state_changed or not self.state_manager.previous_state:
                    state_changed = self.state_manager.return_to_menu()
        elif action_name:
            state_changed = self._process_action(action_name)
                
        return state_changed
        
    def _handle_pong_joystick_input(self, action_name):
        """Handle joystick input specifically for Pong game."""
        game_result = self.game_manager.handle_pong_input(action_name)
        
        if game_result == "QUIT_TO_MENU":
            return self._quit_pong_to_menu()
        elif game_result:
            return True
        return False
        
    def _quit_pong_to_menu(self):
        """Quit Pong game and return to menu."""
        target_state = STATE_MENU
        if self.previous_state and self.previous_state != STATE_PONG_ACTIVE:
            target_state = self.previous_state
        self.game_manager.close_current_game()
        return self.state_manager.transition_to(target_state)

    def update(self):
        """Update application state and check for timed events."""
        state_changed = False
        
        # Check secret combo duration (only from main menu on settings item)
        if (self.current_state == STATE_MENU and
            self.input_manager.check_secret_combo_duration() and
            self.input_manager.check_secret_combo_conditions(
                self.current_state,
                self.menu_manager.get_current_menu_index(STATE_MENU)
            )):
            logger.info("Secret combo detected! Activating secret games menu")
            state_changed = self.state_manager.transition_to(STATE_SECRET_GAMES)
            self.input_manager.reset_secret_combo()
            
        # Check joystick long press for secret menu (only from main menu on settings item)
        if (self.current_state == STATE_MENU and 
            self.menu_manager.get_current_menu_index(STATE_MENU) == self.menu_manager.get_settings_main_menu_idx() and
            self.input_manager.check_joystick_long_press(self.current_state)):
            logger.info("Joystick long press on Settings item detected! Activating secret games menu")
            state_changed = self.state_manager.transition_to(STATE_SECRET_GAMES)
            self.input_manager.reset_joystick_timer()
            
        if self.current_state == STATE_PONG_ACTIVE:
            self.game_manager.handle_continuous_pong_input(self.keys_held)
            
        # Check KEY_PREV long press for back to menu / previous state
        if self.input_manager.check_long_press_duration():
            # If a secret combo is currently being timed (i.e., secret_combo_start_time is not None),
            # prioritize that and don't trigger the independent 'Back' action from KEY_PREV.
            if self.input_manager.secret_combo_start_time is None:
                logger.info(f"KEY_PREV Long press detected in {self.current_state}.")
                handled_by_back_action = self._process_action(app_config.INPUT_ACTION_BACK)
                if not handled_by_back_action:
                    if self.current_state not in [STATE_MENU, STATE_PONG_ACTIVE, STATE_SECRET_GAMES]:
                        logger.info(f"Long press in view state {self.current_state}, returning to previous or menu.")
                        state_changed = self.state_manager.return_to_previous()
                        if not state_changed or not self.state_manager.previous_state:
                            state_changed = self.state_manager.return_to_menu()
                else:
                    state_changed = True
                self.input_manager.reset_long_press_timer() # Reset only if processed or intended to be processed

        return state_changed

    def _process_action(self, action):
        """Process input actions and route to appropriate handlers."""
        current_st = self.current_state
        state_changed = False

        if action == app_config.INPUT_ACTION_BACK:
            if current_st == STATE_SECRET_GAMES:
                state_changed = self.state_manager.return_to_menu()
            elif current_st == STATE_SENSORS_MENU:
                state_changed = self._handle_sensors_menu_back()
            elif current_st == STATE_SETTINGS:
                state_changed = self._handle_settings_main_menu_back()
            elif current_st in [STATE_SETTINGS_WIFI, STATE_SETTINGS_BLUETOOTH, STATE_SETTINGS_DEVICE, STATE_SETTINGS_DISPLAY, STATE_SELECT_COMBO_DURATION]:
                logger.info(f"BACK from {current_st}, returning to STATE_SETTINGS or specific parent")
                if current_st == STATE_SELECT_COMBO_DURATION:
                    state_changed = self.state_manager.transition_to(STATE_SETTINGS_DEVICE)
                else:
                    state_changed = self.state_manager.transition_to(STATE_SETTINGS)
            elif current_st not in [STATE_MENU, STATE_PONG_ACTIVE]:
                logger.info(f"BACK from {current_st} (general view), returning to previous or menu")
                state_changed = self.state_manager.return_to_previous()
                if not state_changed or not self.state_manager.previous_state:
                    state_changed = self.state_manager.return_to_menu()
            return state_changed
                
        if current_st == STATE_MENU:
            state_changed = self._handle_menu_input(action)
        elif current_st == STATE_SENSORS_MENU:
            state_changed = self._handle_sensors_menu_input(action)
        elif current_st == STATE_SETTINGS:
            state_changed = self._handle_settings_main_menu_input(action)
        elif current_st == STATE_SETTINGS_DISPLAY:
            state_changed = self._handle_display_settings_input(action)
        elif current_st == STATE_SETTINGS_DEVICE:
            state_changed = self._handle_device_settings_input(action)
        elif current_st == STATE_SELECT_COMBO_DURATION: # New state handler
            state_changed = self._handle_select_combo_duration_input(action)
        elif current_st in [STATE_CONFIRM_REBOOT, STATE_CONFIRM_SHUTDOWN, STATE_CONFIRM_RESTART_APP]:
            state_changed = self._handle_confirmation_input(action)
        elif current_st == STATE_SECRET_GAMES:
            state_changed = self._handle_secret_games_input(action)
        elif current_st in [STATE_DASHBOARD, STATE_SENSOR_VIEW, STATE_SYSTEM_INFO]:
            state_changed = self._handle_view_input(action)
        elif current_st == STATE_SETTINGS_WIFI: # Handler for WiFi settings
            state_changed = self._handle_wifi_settings_input(action)
            
        return state_changed
    
    def _handle_menu_input(self, action):
        """Handle input for the main menu."""
        if action == app_config.INPUT_ACTION_NEXT:
            return self.menu_manager.navigate_next(self.current_state)
        elif action == app_config.INPUT_ACTION_PREV:
            return self.menu_manager.navigate_prev(self.current_state)
        elif action == app_config.INPUT_ACTION_SELECT:
            return self._handle_menu_select()
        elif action == app_config.INPUT_ACTION_BACK and self.menu_manager.menu_stack: 
            previous_menu_state = self.menu_manager.exit_submenu()
            if previous_menu_state:
                return self.state_manager.transition_to(previous_menu_state)
            return self.state_manager.return_to_menu()
            
        return False
        
    def _handle_menu_select(self):
        """Handle main menu item selection."""
        selected_item = self.menu_manager.get_selected_item(self.current_state)
        if not selected_item: return False
            
        logger.info(f"Menu SELECT: item='{selected_item.name}', target='{selected_item.target_state}'")
        
        if selected_item.target_state == STATE_SENSORS_MENU:
            self.menu_manager.enter_submenu(self.menu_manager.sensors_menu_items, STATE_MENU, STATE_SENSORS_MENU)
            return self.state_manager.transition_to(STATE_SENSORS_MENU)
        elif selected_item.target_state == STATE_SETTINGS:
            self.menu_manager.enter_submenu(self.menu_manager.settings_menu_items, STATE_MENU, STATE_SETTINGS)
            return self.state_manager.transition_to(STATE_SETTINGS)
        elif selected_item.target_state:
            if selected_item.target_state == STATE_SENSOR_VIEW and selected_item.data:
                self.current_sensor = selected_item.data["sensor_type"]
                self._reset_view_state()
            elif selected_item.target_state == STATE_DASHBOARD:
                self._reset_view_state()
            return self.state_manager.transition_to(selected_item.target_state)
        return False

    def _handle_sensors_menu_input(self, action):
        """Handle input for the sensors submenu."""
        if action == app_config.INPUT_ACTION_NEXT:
            return self.menu_manager.navigate_next(self.current_state)
        elif action == app_config.INPUT_ACTION_PREV:
            return self.menu_manager.navigate_prev(self.current_state)
        elif action == app_config.INPUT_ACTION_SELECT:
            return self._handle_sensors_menu_select()
        return False
        
    def _handle_sensors_menu_select(self):
        """Handle sensors menu item selection."""
        selected_item = self.menu_manager.get_selected_item(self.current_state)
        if (selected_item and selected_item.target_state == STATE_SENSOR_VIEW and selected_item.data):
            self.current_sensor = selected_item.data["sensor_type"]
            self._reset_view_state()
            return self.state_manager.transition_to(STATE_SENSOR_VIEW)
        return False

    def _handle_sensors_menu_back(self):
        """Handle back navigation from sensors menu."""
        previous_menu_state_name = self.menu_manager.exit_submenu()
        if previous_menu_state_name:
            return self.state_manager.transition_to(previous_menu_state_name)
        return self.state_manager.return_to_menu()

    def _handle_settings_main_menu_input(self, action):
        """Handle input for the main settings category menu (STATE_SETTINGS)."""
        if action == app_config.INPUT_ACTION_NEXT:
            return self.menu_manager.navigate_next(self.current_state)
        elif action == app_config.INPUT_ACTION_PREV:
            return self.menu_manager.navigate_prev(self.current_state)
        elif action == app_config.INPUT_ACTION_SELECT:
            return self._handle_settings_main_menu_select()
        return False

    def _handle_settings_main_menu_select(self):
        """Handle selection from the main settings category menu."""
        selected_item = self.menu_manager.get_selected_item(self.current_state)
        if not selected_item or not selected_item.target_state:
            return False
        
        logger.info(f"Settings Menu SELECT: item='{selected_item.name}', target_state='{selected_item.target_state}'")
        
        # If selected item is to go back to main menu, reset menu manager fully
        if selected_item.target_state == STATE_MENU:
            self.menu_manager.reset_to_main_menu()
            
        return self.state_manager.transition_to(selected_item.target_state)

    def _handle_settings_main_menu_back(self):
        """Handle back navigation from the main settings category menu."""
        previous_menu_state_name = self.menu_manager.exit_submenu()
        if previous_menu_state_name:
            return self.state_manager.transition_to(previous_menu_state_name)
        return self.state_manager.return_to_menu()

    def _handle_display_settings_input(self, action):
        """Handle input for the Display Settings view - delegates to SettingsManager."""
        result = self.settings_manager.handle_display_settings_input(action)
        if result == "GO_TO_MAIN_MENU":
            self.menu_manager.reset_to_main_menu()
            return self.state_manager.transition_to(STATE_MENU)
        return result

    def _handle_device_settings_input(self, action):
        """Handle input for the Device Settings view - delegates to DeviceManager."""
        result = self.device_manager.handle_device_settings_input(action)
        if isinstance(result, str):
            if result == "GO_TO_MAIN_MENU":
                self.menu_manager.reset_to_main_menu()
                return self.state_manager.transition_to(STATE_MENU)
            elif result == "SELECT_COMBO_DURATION":
                return self.state_manager.transition_to(STATE_SELECT_COMBO_DURATION)
            elif result == "CONFIRM_REBOOT":
                return self.state_manager.transition_to(STATE_CONFIRM_REBOOT)
            elif result == "CONFIRM_SHUTDOWN":
                return self.state_manager.transition_to(STATE_CONFIRM_SHUTDOWN)
            elif result == "CONFIRM_RESTART_APP":
                return self.state_manager.transition_to(STATE_CONFIRM_RESTART_APP)
        return result

    def _handle_confirmation_input(self, action):
        """Handle confirmation input - delegates to DeviceManager."""
        result = self.device_manager.handle_confirmation_input(action)
        if result == "BACK_TO_DEVICE_SETTINGS":
            return self.state_manager.transition_to(STATE_SETTINGS_DEVICE)
        return result

    def _handle_secret_games_input(self, action):
        """Handle input for the secret games menu."""
        if action == app_config.INPUT_ACTION_NEXT:
            return self.menu_manager.navigate_next(self.current_state)
        elif action == app_config.INPUT_ACTION_PREV:
            return self.menu_manager.navigate_prev(self.current_state)
        elif action == app_config.INPUT_ACTION_SELECT:
            return self._handle_secret_games_select()
        return False
        
    def _handle_secret_games_select(self):
        """Handle secret games menu selection."""
        selected_item = self.menu_manager.get_selected_item(self.current_state)
        if not selected_item: return False
            
        logger.info(f"Secret Menu SELECT: {selected_item.name}")
        
        if selected_item.action_name == app_config.ACTION_LAUNCH_PONG:
            if self.game_manager.launch_pong():
                return self.state_manager.transition_to(STATE_PONG_ACTIVE)
        elif selected_item.action_name == app_config.ACTION_LAUNCH_TETRIS:
            pass 
        elif selected_item.action_name == app_config.ACTION_RETURN_TO_MENU:
            return self.state_manager.return_to_menu()
        return False
        
    def _handle_view_input(self, action):
        """Handle SELECT action for view states (dashboard, sensor view, system info) to freeze/unfreeze."""
        if action == app_config.INPUT_ACTION_SELECT:
            self.is_frozen = not self.is_frozen
            if self.current_state == STATE_DASHBOARD:
                self.auto_cycle = not self.auto_cycle
            logger.info(f"View State '{self.current_state}': {'Frozen' if self.is_frozen else 'Unfrozen'}. Auto-cycle: {self.auto_cycle if self.current_state == STATE_DASHBOARD else 'N/A'}")
            return True
        return False 
    
    def _reset_view_state(self):
        """Reset view state (frozen, auto_cycle) when entering a new view that uses these."""
        self.is_frozen = False
        self.auto_cycle = True
        logger.info("Reset view state (frozen=False, auto_cycle=True)")
    
    def auto_cycle_dashboard(self, current_time):
        """Handle dashboard auto-cycling."""
        if (self.current_state != STATE_DASHBOARD or self.is_frozen or not self.auto_cycle):
            return False
            
        if current_time - self.last_cycle_time >= self.config.AUTO_CYCLE_INTERVAL:
            dashboard_sensors = [ 
                key for key in self.config.SENSOR_MODES 
                if (self.config.SENSOR_DISPLAY_PROPERTIES.get(key, {}).get("graph_type") != "NONE" 
                    and key != app_config.SENSOR_CLOCK)
            ]
            if not dashboard_sensors: return False

            self.cycle_index = (self.cycle_index + 1) % len(dashboard_sensors)
            self.current_sensor = dashboard_sensors[self.cycle_index]
            self.last_cycle_time = current_time
            logger.debug(f"Auto-cycling to {self.current_sensor}")
            return True
        return False
        
    def get_current_menu_items(self):
        """Get current menu items (now calls MenuManager)."""
        return self.menu_manager.get_current_menu_items(self.current_state)
        
    def get_current_menu_index(self):
        """Get current menu index (now calls MenuManager)."""
        return self.menu_manager.get_current_menu_index(self.current_state)

    def _handle_select_combo_duration_input(self, action):
        """Handle combo duration input - delegates to SettingsManager."""
        result = self.settings_manager.handle_combo_duration_input(action)
        if result and action == app_config.INPUT_ACTION_SELECT:
            # After applying, go back to device settings
            return self.state_manager.transition_to(STATE_SETTINGS_DEVICE)
        return result

    def _handle_wifi_settings_input(self, action):
        """Handle input for the WiFi Settings view - delegates to WifiManager."""
        if not self.wifi_manager:
            logger.error("WifiManager not initialized in AppState, cannot handle WiFi settings input.")
            return self.state_manager.transition_to(STATE_SETTINGS) # Fallback

        # Get the specific action requested from WifiManager based on user's menu navigation (Next, Prev, Select)
        wifi_manager_action_result = self.wifi_manager.handle_input(action)

        if isinstance(wifi_manager_action_result, str): # WifiManager returns an action string when SELECT is pressed
            if wifi_manager_action_result == WIFI_ACTION_TOGGLE:
                logger.info("AppState: WIFI_ACTION_TOGGLE received. Calling wifi_manager.toggle_wifi()")
                self.wifi_manager.toggle_wifi() # WifiManager handles its own toggle and subsequent status update
                # The UI will refresh based on WifiManager's updated status_str on the next frame
                return True # Input was handled (action initiated)
            elif wifi_manager_action_result == WIFI_ACTION_BACK_TO_SETTINGS:
                return self.state_manager.transition_to(STATE_SETTINGS)
            # Add other actions like SCAN, CONNECT later if they return specific strings
            else:
                logger.warning(f"Unknown action string from WifiManager: {wifi_manager_action_result}")
                return False # Unrecognized action string
        
        # If wifi_manager_action_result is boolean, it means navigation occurred within wifi_manager (True) or not (False)
        return wifi_manager_action_result 