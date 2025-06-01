# --- models/app_state.py ---
# Application state management using component managers

import logging
import time
import os # For device actions
from .state_manager import StateManager
from .input_manager import InputManager
from .menu_manager import MenuManager
from .game_manager import GameManager
import config as app_config
import platform
import sys
import pygame
import subprocess

# Import for AUTO_CYCLE_INTERVAL_OPTIONS - consider moving this to config
# from ui.views.settings.display_settings_view import AUTO_CYCLE_INTERVAL_OPTIONS
from config import AUTO_CYCLE_INTERVAL_OPTIONS # Corrected import
from ui.views.settings.device_settings_view import DEVICE_ACTION_ITEMS # New import

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

# Confirmation States (New)
STATE_CONFIRM_REBOOT = "CONFIRM_REBOOT"
STATE_CONFIRM_SHUTDOWN = "CONFIRM_SHUTDOWN"
STATE_CONFIRM_RESTART_APP = "CONFIRM_RESTART_APP"

# Action Constants for Device Settings (can be moved to config.input later)
ACTION_REBOOT_DEVICE = "REBOOT_DEVICE"
ACTION_SHUTDOWN_DEVICE = "SHUTDOWN_DEVICE"
ACTION_RESTART_APP = "RESTART_APP" # New action

# Confirmation Options (New)
CONFIRMATION_OPTIONS = ["Yes", "No"]

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
        
        # Set up cross-component dependencies
        self.input_manager.set_settings_menu_index(
            self.menu_manager.get_settings_main_menu_idx()
        )
        
        # Sensor and view state
        self.current_sensor = None
        self.is_frozen = False
        self.auto_cycle = True # Default for dashboard
        self.last_cycle_time = 0
        self.cycle_index = 0 # For dashboard cycling
        self.last_reading_time = 0.0

        # Index for display settings options
        self.display_settings_option_index = 0
        # Initialize with current config value if possible
        try:
            current_interval = self.config.AUTO_CYCLE_INTERVAL
            if current_interval in AUTO_CYCLE_INTERVAL_OPTIONS:
                self.display_settings_option_index = AUTO_CYCLE_INTERVAL_OPTIONS.index(current_interval)
        except (ValueError, AttributeError):
            logger.warning(f"Could not find current AUTO_CYCLE_INTERVAL {self.config.AUTO_CYCLE_INTERVAL} in options, defaulting index to 0.")
            self.display_settings_option_index = 0
        
        # Index for device settings options (New)
        self.device_settings_option_index = 0

        # Index for confirmation options (0 for Yes/Confirm, 1 for No/Cancel)
        self.confirmation_option_index = 0 
        self.pending_device_action = None # Stores the action to confirm (e.g., ACTION_REBOOT_DEVICE)
        
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
                    press_duration >= self.config.SECRET_HOLD_DURATION):
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
        if (self.input_manager.check_long_press_duration()):
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
            self.input_manager.reset_long_press_timer()

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
            elif current_st in [STATE_SETTINGS_WIFI, STATE_SETTINGS_BLUETOOTH, STATE_SETTINGS_DEVICE, STATE_SETTINGS_DISPLAY]:
                logger.info(f"BACK from {current_st}, returning to STATE_SETTINGS")
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
        elif current_st in [STATE_CONFIRM_REBOOT, STATE_CONFIRM_SHUTDOWN, STATE_CONFIRM_RESTART_APP]:
            state_changed = self._handle_confirmation_input(action)
        elif current_st == STATE_SECRET_GAMES:
            state_changed = self._handle_secret_games_input(action)
        elif current_st in [STATE_DASHBOARD, STATE_SENSOR_VIEW, STATE_SYSTEM_INFO]:
            state_changed = self._handle_view_input(action)
        elif current_st in [STATE_SETTINGS_WIFI, STATE_SETTINGS_BLUETOOTH]: # Removed DEVICE from here
            logger.debug(f"Input action '{action}' in state {current_st} - to be implemented by sub-view handler.")
            pass
            
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
        """Handle input for the Display Settings view (STATE_SETTINGS_DISPLAY)."""
        state_changed = False
        if action == app_config.INPUT_ACTION_NEXT:
            self.display_settings_option_index = (self.display_settings_option_index + 1) % len(AUTO_CYCLE_INTERVAL_OPTIONS)
            logger.debug(f"Display Settings NEXT: index={self.display_settings_option_index}, value={AUTO_CYCLE_INTERVAL_OPTIONS[self.display_settings_option_index]}s")
            state_changed = True # UI needs to redraw to show new selection
        elif action == app_config.INPUT_ACTION_PREV:
            self.display_settings_option_index = (self.display_settings_option_index - 1 + len(AUTO_CYCLE_INTERVAL_OPTIONS)) % len(AUTO_CYCLE_INTERVAL_OPTIONS)
            logger.debug(f"Display Settings PREV: index={self.display_settings_option_index}, value={AUTO_CYCLE_INTERVAL_OPTIONS[self.display_settings_option_index]}s")
            state_changed = True # UI needs to redraw
        elif action == app_config.INPUT_ACTION_SELECT:
            state_changed = self._apply_display_settings()
        # INPUT_ACTION_BACK is handled by _process_action to go back to STATE_SETTINGS
        return state_changed

    def _apply_display_settings(self):
        """Apply the selected display settings (e.g., auto-cycle interval)."""
        selected_option = AUTO_CYCLE_INTERVAL_OPTIONS[self.display_settings_option_index]
        
        if isinstance(selected_option, str) and selected_option == "<- Back to Main Menu":
            logger.info("Display Settings: Action Go To Main Menu selected.")
            self.menu_manager.reset_to_main_menu() # Use the new reset method
            return self.state_manager.transition_to(STATE_MENU)
        elif isinstance(selected_option, int):
            # Directly modify the config object. For persistence, this would need to write to a file.
            try:
                self.config.AUTO_CYCLE_INTERVAL = selected_option
                logger.info(f"Applied new Auto-Cycle Interval: {selected_option}s")
                # Optionally, provide user feedback on screen (e.g., a temporary message)
                # For now, the change will be reflected when the dashboard is next active.
                return True # Indicates a change that might need UI update or confirmation
            except Exception as e:
                logger.error(f"Error applying display setting: {e}")
                return False
        else:
            logger.warning(f"Unknown option type in display settings: {selected_option}")
            return False

    def _handle_device_settings_input(self, action):
        """Handle input for the Device Settings view (STATE_SETTINGS_DEVICE)."""
        state_changed = False
        if action == app_config.INPUT_ACTION_NEXT:
            self.device_settings_option_index = (self.device_settings_option_index + 1) % len(DEVICE_ACTION_ITEMS)
            logger.debug(f"Device Settings NEXT: index={self.device_settings_option_index}, action='{DEVICE_ACTION_ITEMS[self.device_settings_option_index]['name']}'")
            state_changed = True # UI needs to redraw
        elif action == app_config.INPUT_ACTION_PREV:
            self.device_settings_option_index = (self.device_settings_option_index - 1 + len(DEVICE_ACTION_ITEMS)) % len(DEVICE_ACTION_ITEMS)
            logger.debug(f"Device Settings PREV: index={self.device_settings_option_index}, action='{DEVICE_ACTION_ITEMS[self.device_settings_option_index]['name']}'")
            state_changed = True # UI needs to redraw
        elif action == app_config.INPUT_ACTION_SELECT:
            state_changed = self._trigger_device_action()
        # INPUT_ACTION_BACK is handled by _process_action to go back to STATE_SETTINGS
        return state_changed

    def _trigger_device_action(self):
        """Transitions to a confirmation state for the selected device action."""
        if not (0 <= self.device_settings_option_index < len(DEVICE_ACTION_ITEMS)):
            logger.error(f"Invalid device_settings_option_index: {self.device_settings_option_index}")
            return False

        selected_action_details = DEVICE_ACTION_ITEMS[self.device_settings_option_index]
        action_type = selected_action_details["action"]
        logger.info(f"Device action selected, transitioning to confirmation: {action_type}")

        if action_type == ACTION_REBOOT_DEVICE:
            self.pending_device_action = ACTION_REBOOT_DEVICE # Store what we are confirming
            return self.state_manager.transition_to(STATE_CONFIRM_REBOOT)
        elif action_type == ACTION_SHUTDOWN_DEVICE:
            self.pending_device_action = ACTION_SHUTDOWN_DEVICE
            return self.state_manager.transition_to(STATE_CONFIRM_SHUTDOWN)
        elif action_type == ACTION_RESTART_APP:
            self.pending_device_action = ACTION_RESTART_APP
            return self.state_manager.transition_to(STATE_CONFIRM_RESTART_APP)
        elif action_type == app_config.ACTION_GO_TO_MAIN_MENU:
            logger.info("Device Settings: Action Go To Main Menu selected.")
            self.menu_manager.reset_to_main_menu() # Use the new reset method
            return self.state_manager.transition_to(STATE_MENU)
        else:
            logger.warning(f"Unknown device action type for confirmation: {action_type}")
        return False

    # --- Confirmation Screen Input Handling (New) ---
    def _handle_confirmation_input(self, action):
        state_changed = False
        if action == app_config.INPUT_ACTION_NEXT or action == app_config.INPUT_ACTION_PREV:
            # Toggle between 0 (Yes) and 1 (No)
            self.confirmation_option_index = 1 - self.confirmation_option_index 
            logger.debug(f"Confirmation option toggled to: {CONFIRMATION_OPTIONS[self.confirmation_option_index]}")
            state_changed = True # UI needs to redraw
        elif action == app_config.INPUT_ACTION_SELECT: # Corresponds to "Yes" or "Confirm"
            if self.confirmation_option_index == 0: # 0 is "Yes"
                if hasattr(self, 'pending_device_action') and self.pending_device_action:
                    self._execute_pending_device_action()
                    state_changed = True 
                else:
                    logger.warning("Confirmation selected (Yes), but no pending_device_action found.")
                    state_changed = self.state_manager.transition_to(STATE_SETTINGS_DEVICE) 
            else: # 1 is "No"
                logger.info(f"Device action cancelled (No selected) from {self.current_state}.")
                self.pending_device_action = None
                state_changed = self.state_manager.transition_to(STATE_SETTINGS_DEVICE)
        elif action == app_config.INPUT_ACTION_BACK: # Corresponds to "No" or "Cancel"
            logger.info(f"Device action cancelled (Back action) from {self.current_state}.")
            self.pending_device_action = None
            state_changed = self.state_manager.transition_to(STATE_SETTINGS_DEVICE)
        return state_changed

    def _execute_pending_device_action(self):
        action_to_execute = getattr(self, 'pending_device_action', None)
        if not action_to_execute:
            logger.error("Attempted to execute pending device action, but none was set.")
            return False # Indicate failure or no action taken

        logger.info(f"Executing confirmed device action: {action_to_execute}")
        self.pending_device_action = None # Clear after fetching

        state_changed_to_settings = False

        if action_to_execute == ACTION_REBOOT_DEVICE:
            if platform.system() == "Linux":
                logger.warning("Device reboot initiated (Linux).")
                os.system("sudo reboot")
                pygame.event.post(pygame.event.Event(pygame.QUIT)) # Quit app
            elif platform.system() == "Windows":
                logger.warning("Reboot action is disabled on Windows for safety in this application.")
                # Transition back to device settings instead of rebooting Windows
                # self.state_manager.transition_to(STATE_SETTINGS_DEVICE) # This would be immediate
                # For now, let's post a quit to simulate the app closing as if it did reboot
                # but without actually rebooting the OS.
                # A better UX would be a message and return to settings.
                # Forcing a quit to test the flow.
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                return True # Indicate an action (quitting) was taken
            return True # Indicate an action was processed

        elif action_to_execute == ACTION_SHUTDOWN_DEVICE:
            if platform.system() == "Linux":
                logger.warning("Device shutdown initiated (Linux).")
                os.system("sudo shutdown now")
                pygame.event.post(pygame.event.Event(pygame.QUIT)) # Quit app
            elif platform.system() == "Windows":
                logger.warning("Shutdown action is disabled on Windows for safety in this application.")
                # Similar to reboot, simulate app closing without actual OS shutdown.
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                return True # Indicate an action (quitting) was taken
            return True # Indicate an action was processed

        elif action_to_execute == ACTION_RESTART_APP:
            logger.warning("Application restart initiated.")
            try:
                pygame.quit() # Cleanly quit pygame first
                
                if platform.system() == "Windows":
                    # On Windows, paths with spaces need careful handling for spawning new processes.
                    # subprocess.Popen is generally more robust.
                    # We also need to ensure the new process is detached and doesn't open a new console.
                    import subprocess
                    # sys.argv[0] is the script name (e.g., main.py)
                    # sys.executable is the python interpreter
                    cmd = [sys.executable] + sys.argv
                    logger.info(f"Restarting (Windows) with: {cmd}")
                    # Use DETACHED_PROCESS to avoid creating a new console window
                    subprocess.Popen(cmd, creationflags=subprocess.DETACHED_PROCESS)
                    sys.exit(0) # Current process should exit cleanly
                else:
                    # For Linux/macOS, os.execv is fine and replaces the current process.
                    args = [sys.executable] + sys.argv 
                    logger.info(f"Restarting (Linux/Unix) with: os.execv({sys.executable}, {args})")
                    os.execv(sys.executable, args)
            except Exception as e:
                logger.error(f"Failed to restart application: {e}", exc_info=True)
                sys.exit(1) # If restart fails, exit with an error
            # For os.execv, this part is not reached. For Popen, current process exits above.
            return True 

        else:
            logger.warning(f"Unknown pending device action to execute: {action_to_execute}")
            return False

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