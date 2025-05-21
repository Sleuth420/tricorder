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
    
    def __init__(self, config_module, screen_width, screen_height): # config_module is the actual config.py module
        """
        Initialize the application state.
        
        Args:
            config_module: The configuration module (config.py)
            screen_width (int): The actual width of the screen.
            screen_height (int): The actual height of the screen.
        """
        self.config = config_module # Store the passed config module
        self.actual_screen_width = screen_width
        self.actual_screen_height = screen_height
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
        self.joystick_middle_press_start_time = None # For joystick long press detection

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
        items.append(MenuItem(name="Schematics", target_state=STATE_SETTINGS, color_key="SIDEBAR_SCHEMATICS"))
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
            action_name = result.get('action')

            if event_type == self.config.INPUT_ACTION_QUIT: # Pygame quit
                # This is usually handled by main loop checking `running`
                # but if input_handler sends it, we can acknowledge.
                logger.info(f"'{self.config.INPUT_ACTION_QUIT}' action type received by app_state.")
                # Potentially set a flag or directly influence main loop if needed.
                pass

            elif event_type == 'KEYDOWN':
                self.keys_held.add(key)
                logger.debug(f"KEYDOWN: key={key}. keys_held={self.keys_held}")

                if key == self.config.KEY_PREV and self.key_prev_press_start_time is None:
                    self.key_prev_press_start_time = time.time()
                    logger.debug("KEY_PREV press timer started.")

                if not self.secret_combo_start_time and self._check_secret_combo_conditions():
                    logger.info("KEYBOARD SECRET COMBO TIMER STARTED")
                    self.secret_combo_start_time = time.time()
                    combo_potentially_active = True
            
            elif event_type == 'JOYSTICK':
                if action_name:
                    logger.debug(f"JOYSTICK event: action_name='{action_name}' in state {self.current_state}")
                    if self.current_state == STATE_PONG_ACTIVE and self.active_pong_game:
                        # Handle input for PONG game state
                        if not self.active_pong_game.paused:  # Game is active and not paused
                            if action_name == app_config.INPUT_ACTION_PREV:  # Joystick Up Press for paddle
                                logger.debug("Pong (Active): Joystick UP PRESS, moving paddle.")
                                self.active_pong_game.move_paddle_up()
                            elif action_name == app_config.INPUT_ACTION_NEXT:  # Joystick Down Press for paddle
                                logger.debug("Pong (Active): Joystick DOWN PRESS, moving paddle.")
                                self.active_pong_game.move_paddle_down()
                            elif action_name == app_config.INPUT_ACTION_SELECT: # Joystick Middle to PAUSE game
                                logger.info("Joystick SELECT in active Pong. Pausing game.")
                                self.active_pong_game.toggle_pause()
                                state_changed_by_action = True

                        elif self.active_pong_game.paused: # Game is PAUSED, handle pause menu
                            if action_name == app_config.INPUT_ACTION_PREV: # Joystick Up for pause menu navigation
                                logger.debug("Pong (Paused): Joystick UP, navigating pause menu.")
                                self.active_pong_game.navigate_pause_menu_up()
                            elif action_name == app_config.INPUT_ACTION_NEXT: # Joystick Down for pause menu navigation
                                logger.debug("Pong (Paused): Joystick DOWN, navigating pause menu.")
                                self.active_pong_game.navigate_pause_menu_down()
                            elif action_name == app_config.INPUT_ACTION_SELECT: # Joystick Middle to select pause menu option
                                logger.debug("Pong (Paused): Joystick SELECT, selecting pause menu option.")
                                menu_action_result = self.active_pong_game.select_pause_menu_option()
                                if menu_action_result == "RESUME_GAME":
                                    logger.info("Pong: Resuming game from pause menu (joystick).")
                                    state_changed_by_action = True 
                                elif menu_action_result == "QUIT_TO_MENU":
                                    logger.info("Pong: Quitting to menu from pause menu (joystick).")
                                    # First store the target state
                                    target_state = STATE_MENU
                                    if self.previous_state and self.previous_state != STATE_PONG_ACTIVE:
                                        target_state = self.previous_state
                                    # Update previous state
                                    self.previous_state = STATE_PONG_ACTIVE
                                    # Change state first
                                    self.current_state = target_state
                                    # Clear game instance last
                                    self.active_pong_game = None
                                    state_changed_by_action = True
                        elif self.active_pong_game.game_over: # Game is OVER, handle back action
                            if action_name == app_config.INPUT_ACTION_BACK: # Joystick Left to quit from GAME OVER screen
                                logger.info("Pong (Game Over): Joystick BACK, quitting to menu.")
                                if self.previous_state and self.previous_state != STATE_PONG_ACTIVE:
                                    self.current_state = self.previous_state
                                else:
                                    self.current_state = STATE_MENU
                                self.previous_state = STATE_PONG_ACTIVE
                                self.active_pong_game = None
                                state_changed_by_action = True
                        
                        # General SELECT for pause (if not paused, not game over, and not already handled by menu selection)
                        if action_name == app_config.INPUT_ACTION_SELECT and not self.active_pong_game.paused and not self.active_pong_game.game_over and not state_changed_by_action:
                            logger.debug(f"Joystick action '{action_name}' being routed to _process_action for state {self.current_state}")
                            state_changed_by_action = self._process_action(action_name) or state_changed_by_action
                    else: # Not in Pong game state, or pong game not active - process general joystick actions
                        logger.debug(f"Joystick action '{action_name}' being routed to _process_action for state {self.current_state}")
                        state_changed_by_action = self._process_action(action_name) or state_changed_by_action

            elif event_type == 'JOYSTICK_UP_HELD':
                if self.current_state == STATE_PONG_ACTIVE and self.active_pong_game and not self.active_pong_game.paused:
                    logger.debug("Pong: Joystick UP_HELD detected, moving paddle.")
                    self.active_pong_game.move_paddle_up()
            
            elif event_type == 'JOYSTICK_DOWN_HELD':
                if self.current_state == STATE_PONG_ACTIVE and self.active_pong_game and not self.active_pong_game.paused:
                    logger.debug("Pong: Joystick DOWN_HELD detected, moving paddle.")
                    self.active_pong_game.move_paddle_down()

            elif event_type == 'JOYSTICK_MIDDLE_PRESS':
                logger.debug(f"Joystick middle PRESS detected in state {self.current_state}. Starting press timer.")
                self.joystick_middle_press_start_time = time.time()
            
            elif event_type == 'JOYSTICK_MIDDLE_RELEASE':
                if self.joystick_middle_press_start_time is not None:
                    press_duration = time.time() - self.joystick_middle_press_start_time
                    logger.debug(f"Joystick middle RELEASE detected. Press duration: {press_duration:.2f}s")
                    
                    current_state_before_select = self.current_state
                    timer_was_running = self.joystick_middle_press_start_time 
                    self.joystick_middle_press_start_time = None 

                    if current_state_before_select == STATE_MENU and timer_was_running and press_duration >= self.config.SECRET_HOLD_DURATION:
                        logger.debug("Joystick middle long press for secret menu handled by update(). No SELECT action from release here.")
                    elif current_state_before_select != STATE_SECRET_GAMES: 
                        logger.debug("Joystick middle short press detected. Processing as INPUT_ACTION_SELECT.")
                        state_changed_by_action = self._process_action(app_config.INPUT_ACTION_SELECT) or state_changed_by_action
                    else:
                        logger.debug("Joystick middle released, but state is SECRET_GAMES or was not a short press. No SELECT action.")
                else:
                    logger.debug("Joystick middle RELEASE detected without a corresponding press start time.")

            elif event_type == 'KEYUP':
                combo_was_active = bool(self.secret_combo_start_time)
                if key in self.keys_held:
                    self.keys_held.remove(key)
                logger.debug(f"KEYUP: key={key}. keys_held={self.keys_held}")

                if self.secret_combo_start_time and (key == self.config.KEY_PREV or key == self.config.KEY_NEXT):
                    logger.info("KEYBOARD SECRET COMBO TIMER RESET (Key Up)")
                    self.secret_combo_start_time = None
                    combo_potentially_active = False
                
                if not combo_was_active:
                    if key == self.config.KEY_PREV and self.key_prev_press_start_time is not None:
                        press_duration = time.time() - self.key_prev_press_start_time
                        self.key_prev_press_start_time = None 
                        logger.debug("KEY_PREV released, timer reset.")
                        # keyboard PREV in paused Pong: navigate pause menu UP
                        if self.current_state == STATE_PONG_ACTIVE and self.active_pong_game and self.active_pong_game.paused and action_name == app_config.INPUT_ACTION_PREV:
                            logger.info("Keyboard PREV in paused Pong. Navigating pause menu up.")
                            self.active_pong_game.navigate_pause_menu_up()
                            # state_changed_by_action = True # UI update handled by Pong's draw method
                        # Long press was handled in update(), no specific action here on KEYUP for that.
                        # However, for GAME OVER in PONG, a simple KEY_PREV press should go back.
                        elif self.current_state == STATE_PONG_ACTIVE and self.active_pong_game and self.active_pong_game.game_over and key == self.config.KEY_PREV:
                            logger.info("Pong (Game Over): Keyboard PREV (release), quitting to menu.")
                            if self.previous_state and self.previous_state != STATE_PONG_ACTIVE:
                                self.current_state = self.previous_state
                            else:
                                self.current_state = STATE_MENU
                            self.previous_state = STATE_PONG_ACTIVE
                            self.active_pong_game = None
                            state_changed_by_action = True
                        # General short press KEY_PREV for menu nav, if not a long press that was reset
                        elif self.current_state in [STATE_MENU, STATE_SECRET_GAMES] and (self.key_prev_press_start_time is None or (time.time() - self.key_prev_press_start_time < self.config.INPUT_LONG_PRESS_DURATION)):
                            logger.debug(f"Short press PREV in {self.current_state}: processing PREV action on KeyUp.")
                            state_changed_by_action = self._process_action(app_config.INPUT_ACTION_PREV) or state_changed_by_action
                        
                    elif key == self.config.KEY_NEXT and action_name == app_config.INPUT_ACTION_NEXT:
                         # keyboard NEXT in paused Pong: navigate pause menu DOWN
                         if self.current_state == STATE_PONG_ACTIVE and self.active_pong_game and self.active_pong_game.paused and action_name == app_config.INPUT_ACTION_NEXT:
                             logger.info("Keyboard NEXT in paused Pong. Navigating pause menu down.")
                             self.active_pong_game.navigate_pause_menu_down()
                             # state_changed_by_action = True
                         elif self.current_state in [STATE_MENU, STATE_SECRET_GAMES]:
                             logger.debug(f"Short press NEXT in {self.current_state} state: processing NEXT action on KeyUp.")
                             state_changed_by_action = self._process_action(app_config.INPUT_ACTION_NEXT) or state_changed_by_action

                    elif key == self.config.KEY_SELECT and action_name == app_config.INPUT_ACTION_SELECT:
                         # keyboard SELECT in paused Pong: select pause menu item
                         if self.current_state == STATE_PONG_ACTIVE and self.active_pong_game and self.active_pong_game.paused:
                             logger.info("Keyboard SELECT in paused Pong. Selecting pause menu option.")
                             menu_action = self.active_pong_game.select_pause_menu_option()
                             if menu_action == "RESUME_GAME":
                                 logger.info("Pong: Resuming game from pause menu (keyboard).")
                                 state_changed_by_action = True
                             elif menu_action == "QUIT_TO_MENU":
                                 logger.info("Pong: Quitting to menu from pause menu (keyboard).")
                                 # First store the target state
                                 target_state = STATE_MENU
                                 if self.previous_state and self.previous_state != STATE_PONG_ACTIVE:
                                     target_state = self.previous_state
                                 # Update previous state
                                 self.previous_state = STATE_PONG_ACTIVE
                                 # Change state first
                                 self.current_state = target_state
                                 # Clear game instance last
                                 self.active_pong_game = None
                                 state_changed_by_action = True
                         # keyboard SELECT in active (unpaused) Pong: PAUSE the game
                         elif self.current_state == STATE_PONG_ACTIVE and self.active_pong_game and not self.active_pong_game.paused:
                             logger.info("SELECT key released in active Pong. Pausing game.")
                             self.active_pong_game.toggle_pause()
                             state_changed_by_action = True 
                         else: 
                             logger.debug("Short press SELECT (keyboard): processing SELECT action on KeyUp for non-Pong state.")
                             state_changed_by_action = self._process_action(app_config.INPUT_ACTION_SELECT) or state_changed_by_action
                    
                    elif action_name == app_config.INPUT_ACTION_BACK: 
                        if self.current_state not in [STATE_MENU, STATE_PONG_ACTIVE, STATE_SECRET_GAMES] or \
                           (self.current_state == STATE_SECRET_GAMES): # Allow back from secret games menu
                            logger.info(f"BACK action triggered by key {key} in state {self.current_state}. Returning to menu.")
                            state_changed_by_action = self._return_to_menu() or state_changed_by_action
                        else:
                            logger.debug(f"BACK action by key {key} in state {self.current_state} not processed by generic rule.")


        return state_changed_by_action

    def update(self):
        state_changed = False
        # Keyboard secret combo check
        if self.secret_combo_start_time:
            current_time = time.time()
            duration = current_time - self.secret_combo_start_time
            required_duration = self.config.SECRET_HOLD_DURATION
            if duration >= required_duration:
                if self._check_secret_combo_conditions(): 
                    logger.info("Keyboard secret combo detected! Activating secret games menu.")
                    state_changed = self._activate_secret_menu()
                    if state_changed:
                        self.secret_combo_start_time = None 
                        return state_changed 
                else:
                    self.secret_combo_start_time = None 
        
        # Joystick middle long press check for secret menu
        if self.joystick_middle_press_start_time is not None and self.current_state == STATE_MENU:
            current_time = time.time()
            duration = current_time - self.joystick_middle_press_start_time
            required_duration = self.config.SECRET_HOLD_DURATION 
            if duration >= required_duration:
                logger.info("Joystick middle long press detected in MENU! Activating secret games menu.")
                state_changed = self._activate_secret_menu()
                if state_changed:
                    self.joystick_middle_press_start_time = None 
                    return state_changed
        
        # Handle continuous paddle movement for Pong from keyboard keys_held
        if self.current_state == STATE_PONG_ACTIVE and self.active_pong_game and not self.active_pong_game.paused:
            if self.config.KEY_PREV in self.keys_held:
                self.active_pong_game.move_paddle_up()
            if self.config.KEY_NEXT in self.keys_held:
                self.active_pong_game.move_paddle_down()

        # Long press KEY_PREV for back to menu (non-Pong states)
        if self.key_prev_press_start_time is not None:
            hold_duration = time.time() - self.key_prev_press_start_time
            if hold_duration >= self.config.INPUT_LONG_PRESS_DURATION:
                if self.current_state not in [STATE_PONG_ACTIVE, STATE_MENU, STATE_SECRET_GAMES]: 
                    logger.info(f"Long press KEY_PREV detected in state {self.current_state}. Returning to menu.")
                    state_changed = self._return_to_menu()
                # Reset timer regardless of action to prevent re-triggering or interference
                self.key_prev_press_start_time = None 
                if state_changed: return state_changed # Return if this action changed state

        # Auto cycle dashboard (if applicable)
        # Note: This was originally in main loop, but makes more sense here if app_state manages time-based transitions.
        # However, keeping it in main.py is also fine if it simplifies things there.
        # For now, assuming main.py handles auto_cycle_dashboard.
        # If you want app_state to handle it:
        # current_time = time.time()
        # if self.auto_cycle_dashboard(current_time): # auto_cycle_dashboard would return True if cycled
        #    state_changed = True # Or a more specific flag if needed for display updates

        return state_changed

    def _process_action(self, action):
        state_changed = False
        
        # Handle BACK action universally if applicable
        if action == app_config.INPUT_ACTION_BACK:
            # Conditions under which BACK should take to the main menu:
            # Not already in MENU, and not in PONG_ACTIVE (unless paused, but back from pong is handled by NEXT when paused)
            # SECRET_GAMES menu should also allow back to MENU.
            if self.current_state not in [STATE_MENU, STATE_PONG_ACTIVE]:
                logger.info(f"BACK action processed in state {self.current_state}. Returning to menu.")
                return self._return_to_menu() # state_changed is handled by _return_to_menu
            elif self.current_state == STATE_SECRET_GAMES: # Explicitly handle back from secret games to main menu
                logger.info(f"BACK action processed in SECRET_GAMES. Returning to main menu.")
                return self._return_to_menu()
            else:
                logger.debug(f"BACK action received in state {self.current_state}, but no generic back action defined here (e.g., already in menu or unpaused game).")
                return False # No state change from this generic handler

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
            return True # Indicate UI update needed
        elif action == app_config.INPUT_ACTION_PREV:
            self.menu_index = (self.menu_index - 1 + num_items) % num_items
            logger.debug(f"Menu PREV: index={self.menu_index}, item='{self.menu_items[self.menu_index].name}'")
            return True # Indicate UI update needed
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
            return True # Indicate UI update needed
        elif action == app_config.INPUT_ACTION_PREV:
            self.secret_menu_index = (self.secret_menu_index - 1 + num_items) % num_items
            logger.debug(f"Secret Menu PREV: index={self.secret_menu_index}, item='{self.secret_menu_items[self.secret_menu_index].name}'")
            return True # Indicate UI update needed
        elif action == app_config.INPUT_ACTION_SELECT:
            selected_item = self.secret_menu_items[self.secret_menu_index]
            logger.info(f"Secret Menu SELECT: item='{selected_item.name}' with action='{selected_item.action_name}'")
            
            if selected_item.action_name == app_config.ACTION_LAUNCH_PONG:
                logger.info("Launching Pong...")
                self.previous_state = self.current_state
                self.current_state = STATE_PONG_ACTIVE
                # Use actual screen dimensions for PongGame
                self.active_pong_game = PongGame(self.actual_screen_width, self.actual_screen_height, self.config)
                return True
            elif selected_item.action_name == app_config.ACTION_LAUNCH_TETRIS:
                logger.warning("Tetris launch selected, but not yet implemented.")
                pass 
            elif selected_item.action_name == app_config.ACTION_RETURN_TO_MENU:
                logger.info("Returning to main menu from secret menu.")
                # If the recorded previous_state was PONG_ACTIVE, that means we just exited Pong
                # and are now exiting the secret games menu. We should go to the main menu,
                # not back into the (now non-existent) Pong game.
                if self.previous_state and self.previous_state != STATE_SECRET_GAMES and self.previous_state != STATE_PONG_ACTIVE:
                    self.current_state = self.previous_state
                else:
                    # Default to STATE_MENU if previous_state was SECRET_GAMES or PONG_ACTIVE
                    self.current_state = STATE_MENU
                self.previous_state = STATE_SECRET_GAMES # Original previous state for this transition
                self.secret_combo_start_time = None # Reset combo timer if any
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