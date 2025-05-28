# --- models/app_state.py ---
# Application state management using component managers

import logging
import time
from .state_manager import StateManager
from .input_manager import InputManager
from .menu_manager import MenuManager
from .game_manager import GameManager
from .app_state_old import (
    STATE_MENU, STATE_SENSORS_MENU, STATE_DASHBOARD, STATE_SENSOR_VIEW,
    STATE_SYSTEM_INFO, STATE_SETTINGS, STATE_SECRET_GAMES, STATE_PONG_ACTIVE,
    STATE_SCHEMATICS
)
import config as app_config

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
            self.menu_manager.get_settings_menu_index()
        )
        
        # Sensor and view state
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
                
                # Check for secret combo start
                if (not self.input_manager.secret_combo_start_time and
                    self.input_manager.check_secret_combo_conditions(
                        self.current_state, 
                        self.menu_manager.get_current_menu_index(self.current_state)
                    )):
                    self.input_manager.start_secret_combo_timer()
                    
            elif event_type == 'KEYUP':
                key_event = self.input_manager.handle_keyup(key)
                
                # Handle key release actions for non-combo states
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
                
                # Capture state BEFORE any processing (like the original did)
                current_state_before_select = self.current_state

                if (current_state_before_select == STATE_MENU and 
                    press_duration >= self.config.SECRET_HOLD_DURATION):
                    logger.debug("Joystick long press for secret menu handled by update()")
                elif current_state_before_select != STATE_SECRET_GAMES: 
                    logger.info(f"Joystick short press: Processing SELECT in {current_state_before_select}")
                    
                    # Check if we already changed state in this input cycle
                    if state_changed_by_action:
                        logger.info("State already changed in this input cycle. Skipping SELECT action to prevent double processing.")
                    else:
                        state_changed_by_action = self._process_action(app_config.INPUT_ACTION_SELECT) or state_changed_by_action
                
        return state_changed_by_action
        
    def _handle_key_release(self, key, action_name):
        """Handle key release events."""
        state_changed = False
        
        # Handle Pong-specific key releases
        if self.current_state == STATE_PONG_ACTIVE and self.active_pong_game:
            if self.active_pong_game.game_over and key == self.config.KEY_PREV:
                logger.info("Pong (Game Over): Keyboard PREV, quitting to menu")
                state_changed = self._quit_pong_to_menu()
            elif action_name:
                game_result = self.game_manager.handle_pong_input(action_name)
                if game_result == "QUIT_TO_MENU":
                    state_changed = self._quit_pong_to_menu()
                elif game_result:
                    state_changed = True
        
        # Handle general key releases
        elif action_name and self.current_state in [STATE_MENU, STATE_SECRET_GAMES]:
            state_changed = self._process_action(action_name)
        elif action_name == app_config.INPUT_ACTION_BACK:
            if self.current_state not in [STATE_MENU, STATE_PONG_ACTIVE, STATE_SECRET_GAMES]:
                state_changed = self.state_manager.return_to_menu()
                
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
        if (self.previous_state and 
            self.previous_state != STATE_PONG_ACTIVE):
            target_state = self.previous_state
            
        self.game_manager.close_current_game()
        return self.state_manager.transition_to(target_state)

    def update(self):
        """Update application state and check for timed events."""
        state_changed = False
        
        # Check secret combo duration
        if (self.input_manager.check_secret_combo_duration() and
            self.input_manager.check_secret_combo_conditions(
                self.current_state,
                self.menu_manager.get_current_menu_index(self.current_state)
            )):
            logger.info("Secret combo detected! Activating secret games menu")
            state_changed = self.state_manager.transition_to(STATE_SECRET_GAMES)
            self.input_manager.reset_secret_combo()
            
        # Check joystick long press for secret menu
        if self.input_manager.check_joystick_long_press(self.current_state):
            logger.info("Joystick long press detected! Activating secret games menu")
            state_changed = self.state_manager.transition_to(STATE_SECRET_GAMES)
            self.input_manager.reset_joystick_timer()
            
        # Handle continuous Pong input
        if self.current_state == STATE_PONG_ACTIVE:
            self.game_manager.handle_continuous_pong_input(self.keys_held)
            
        # Check long press for back to menu
        if (self.input_manager.check_long_press_duration() and
            self.current_state not in [STATE_PONG_ACTIVE, STATE_MENU, STATE_SECRET_GAMES]):
            logger.info(f"Long press detected in {self.current_state}. Returning to menu")
            state_changed = self.state_manager.return_to_menu()
            self.input_manager.reset_long_press_timer()

        return state_changed

    def _process_action(self, action):
        """Process input actions and route to appropriate handlers."""
        # Handle universal BACK action
        if action == app_config.INPUT_ACTION_BACK:
            if self.current_state == STATE_SECRET_GAMES:
                return self.state_manager.return_to_menu()
            elif self.current_state == STATE_SENSORS_MENU:
                return self._handle_sensors_menu_back()
            elif self.current_state not in [STATE_MENU, STATE_PONG_ACTIVE]:
                return self.state_manager.return_to_menu()
                
        # Route to state-specific handlers
        if self.current_state == STATE_MENU:
            return self._handle_menu_input(action)
        elif self.current_state == STATE_SENSORS_MENU:
            return self._handle_sensors_menu_input(action)
        elif self.current_state == STATE_SECRET_GAMES:
            return self._handle_secret_games_input(action)
        elif self.current_state in [STATE_DASHBOARD, STATE_SENSOR_VIEW, STATE_SYSTEM_INFO]:
            return self._handle_view_input(action)
            
        return False
    
    def _handle_menu_input(self, action):
        """Handle input for the main menu."""
        if action == app_config.INPUT_ACTION_NEXT:
            return self.menu_manager.navigate_next(self.current_state)
        elif action == app_config.INPUT_ACTION_PREV:
            return self.menu_manager.navigate_prev(self.current_state)
        elif action == app_config.INPUT_ACTION_SELECT:
            return self._handle_menu_select()
        elif action == app_config.INPUT_ACTION_BACK and self.menu_manager.menu_stack:
            return self.menu_manager.exit_submenu()
            
        return False
        
    def _handle_menu_select(self):
        """Handle menu item selection."""
        selected_item = self.menu_manager.get_selected_item(self.current_state)
        if not selected_item:
            return False
            
        logger.info(f"Menu SELECT: item='{selected_item.name}'")
        
        if selected_item.target_state == STATE_SENSORS_MENU:
            # Enter sensors submenu
            self.menu_manager.enter_submenu(self.menu_manager.sensors_menu_items)
            return self.state_manager.transition_to(STATE_SENSORS_MENU)
        elif selected_item.target_state:
            # Regular state transition
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
        elif action == app_config.INPUT_ACTION_BACK:
            return self._handle_sensors_menu_back()
            
        return False
        
    def _handle_sensors_menu_select(self):
        """Handle sensors menu item selection."""
        selected_item = self.menu_manager.get_selected_item(self.current_state)
        if (selected_item and 
            selected_item.target_state == STATE_SENSOR_VIEW and 
            selected_item.data):
            self.current_sensor = selected_item.data["sensor_type"]
            self._reset_view_state()
            return self.state_manager.transition_to(STATE_SENSOR_VIEW)
            
        return False

    def _handle_sensors_menu_back(self):
        """Handle back navigation from sensors menu."""
        if self.menu_manager.exit_submenu():
            return self.state_manager.transition_to(STATE_MENU)
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
        if not selected_item:
            return False
            
        logger.info(f"Secret Menu SELECT: {selected_item.name}")
        
        if selected_item.action_name == app_config.ACTION_LAUNCH_PONG:
            if self.game_manager.launch_pong():
                return self.state_manager.transition_to(STATE_PONG_ACTIVE)
        elif selected_item.action_name == app_config.ACTION_LAUNCH_TETRIS:
            if self.game_manager.launch_tetris():
                # Would transition to tetris state when implemented
                pass 
        elif selected_item.action_name == app_config.ACTION_RETURN_TO_MENU:
            return self.state_manager.return_to_menu()
            
        return False
        
    def _handle_view_input(self, action):
        """Handle input for view states (dashboard, sensor view, system info)."""
        if action == app_config.INPUT_ACTION_SELECT:
            self.is_frozen = not self.is_frozen
            if self.current_state == STATE_DASHBOARD:
                self.auto_cycle = not self.auto_cycle
            logger.info(f"View: {'Frozen' if self.is_frozen else 'Unfrozen'}")
            return True
            
        return False 
    
    def _reset_view_state(self):
        """Reset view state when entering a new view."""
        self.is_frozen = False
        self.auto_cycle = True
        logger.info("Reset view state")
    
    def auto_cycle_dashboard(self, current_time):
        """Handle dashboard auto-cycling."""
        if (self.current_state != STATE_DASHBOARD or 
            self.is_frozen or 
            not self.auto_cycle):
            return False
            
        if current_time - self.last_cycle_time >= self.config.AUTO_CYCLE_INTERVAL:
            dashboard_sensors = [ 
                key for key in self.config.SENSOR_MODES 
                if (self.config.SENSOR_DISPLAY_PROPERTIES.get(key, {}).get("graph_type") != "NONE" 
                    and key != app_config.SENSOR_CLOCK)
            ]
            
            if not dashboard_sensors:
                logger.warning("No sensors defined for dashboard cycling")
                return False

            self.cycle_index = (self.cycle_index + 1) % len(dashboard_sensors)
            self.current_sensor = dashboard_sensors[self.cycle_index]
            self.last_cycle_time = current_time
            logger.debug(f"Auto-cycling to {self.current_sensor}")
            return True
            
        return False
        
    # Compatibility methods for existing code
    def get_current_menu_items(self):
        """Get current menu items (compatibility method)."""
        return self.menu_manager.get_current_menu_items(self.current_state)
        
    def get_current_menu_index(self):
        """Get current menu index (compatibility method)."""
        return self.menu_manager.get_current_menu_index(self.current_state) 