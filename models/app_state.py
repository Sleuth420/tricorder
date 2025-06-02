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
from .wifi_manager import WifiManager, WIFI_ACTION_TOGGLE, WIFI_ACTION_BACK_TO_SETTINGS, WIFI_ACTION_BROWSE_NETWORKS, WIFI_ACTION_BACK_TO_WIFI, WIFI_ACTION_CONNECT_TO_NETWORK, WIFI_ACTION_ENTER_PASSWORD # Import WifiManager and relevant actions
from .password_entry_manager import PasswordEntryManager
from .input_router import InputRouter
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
STATE_SHIP_MENU = "SHIP_MENU" # Ship selection menu

# New Settings Sub-View States
STATE_SETTINGS_WIFI = "SETTINGS_WIFI"
STATE_SETTINGS_BLUETOOTH = "SETTINGS_BLUETOOTH"
STATE_SETTINGS_DEVICE = "SETTINGS_DEVICE"
STATE_SETTINGS_DISPLAY = "SETTINGS_DISPLAY"
STATE_SELECT_COMBO_DURATION = "SELECT_COMBO_DURATION" # New state for selecting combo duration

# WiFi Sub-States
STATE_SETTINGS_WIFI_NETWORKS = "SETTINGS_WIFI_NETWORKS"  # Browse available networks
STATE_WIFI_PASSWORD_ENTRY = "WIFI_PASSWORD_ENTRY"  # Enter password for WiFi connection

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
        
        # Ship selection data for 3D viewer
        self.selected_ship_data = None
        self.menu_manager = MenuManager(config_module)
        self.game_manager = GameManager(config_module, screen_width, screen_height)
        self.settings_manager = SettingsManager(config_module)
        self.device_manager = DeviceManager(config_module)
        self.wifi_manager = WifiManager(config_module) # Instantiate WifiManager (no command func needed)
        # Password entry manager - initialized with screen dimensions
        import pygame
        screen_rect = pygame.Rect(0, 0, screen_width, screen_height)
        self.password_entry_manager = PasswordEntryManager(config_module, screen_rect, None)  # Fonts will be set later
        
        # Initialize input router
        self.input_router = InputRouter(self)
        
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
                    elif self.current_state == STATE_WIFI_PASSWORD_ENTRY:
                        # Handle joystick navigation for password entry
                        direction = result.get('direction')
                        if direction in ['up', 'down', 'left', 'right']:
                            direction_map = {'up': 'UP', 'down': 'DOWN', 'left': 'LEFT', 'right': 'RIGHT'}
                            if self.password_entry_manager:
                                self.password_entry_manager.handle_joystick_input(direction_map[direction])
                        else:
                            state_changed_by_action = self._route_action(action_name) or state_changed_by_action
                    else:
                        state_changed_by_action = self._route_action(action_name) or state_changed_by_action

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
                        state_changed_by_action = self._route_action(app_config.INPUT_ACTION_SELECT) or state_changed_by_action
                
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
            state_changed = self._route_action(action_name)
                
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

    def _route_action(self, action):
        """Route an action to the appropriate handler using the input router."""
        return self.input_router.route_action(action, self.current_state)

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
                handled_by_back_action = self._route_action(app_config.INPUT_ACTION_BACK)
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