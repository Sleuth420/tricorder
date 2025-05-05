# --- models/app_state.py ---
# Manages application state and navigation

import logging
import time # Import time for last_reading_time initialization
import pygame # Import pygame for key codes
# Import PongGame
from games.pong import PongGame

logger = logging.getLogger(__name__)

# Application states
STATE_MENU = "MENU"           # Main menu
STATE_DASHBOARD = "DASHBOARD" # Dashboard/auto-cycling view
STATE_SENSOR_VIEW = "SENSOR"  # Individual sensor view
STATE_SYSTEM_INFO = "SYSTEM"  # System info view
STATE_SETTINGS = "SETTINGS"   # Settings view
STATE_SECRET_GAMES = "SECRET_GAMES" # New state for secret menu
STATE_PONG_ACTIVE = "PONG_ACTIVE" # New state for Pong game

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
        self.last_reading_time = 0.0 # Initialize last reading time
        
        # Input state for combo detection
        self.keys_held = set()
        self.secret_combo_start_time = None
        self.key_prev_press_start_time = None # Track start time for KEY_PREV long press

        # Menu state
        self.menu_index = 0
        # Add color_key corresponding to config entries for sidebar
        self.menu_items = [
            {"name": "Systems", "state": STATE_SYSTEM_INFO, "sensor": None, "color_key": "COLOR_SIDEBAR_SYSTEM"},
            {"name": "Env: Temp", "state": STATE_SENSOR_VIEW, "sensor": "TEMPERATURE", "color_key": "COLOR_SIDEBAR_TEMP"},
            {"name": "Env: Humid", "state": STATE_SENSOR_VIEW, "sensor": "HUMIDITY", "color_key": "COLOR_SIDEBAR_HUMID"},
            {"name": "Atmos", "state": STATE_SENSOR_VIEW, "sensor": "PRESSURE", "color_key": "COLOR_SIDEBAR_PRESS"},
            {"name": "Attitude", "state": STATE_SENSOR_VIEW, "sensor": "ORIENTATION", "color_key": "COLOR_SIDEBAR_ORIENT"},
            {"name": "Inertia", "state": STATE_SENSOR_VIEW, "sensor": "ACCELERATION", "color_key": "COLOR_SIDEBAR_ACCEL"},
            {"name": "Sweep", "state": STATE_DASHBOARD, "sensor": None, "color_key": "COLOR_SIDEBAR_ALL"},
            {"name": "Settings", "state": STATE_SETTINGS, "sensor": None, "color_key": "COLOR_SIDEBAR_SETTINGS"}
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

        # Secret Games Menu state
        self.secret_menu_index = 0
        self.secret_menu_items = [
            # Use pong action and image
            {"name": "Pong", "image": "images/spork.png", "action": "LAUNCH_PONG"},
            {"name": "Tetris", "image": "images/spork.png", "action": "LAUNCH_TETRIS"},
            {"name": "Quit", "image": None, "action": "RETURN_TO_MENU"}
        ]
        # Active game instance
        self.active_pong_game = None

        # Find the index for the "Settings" menu item for combo check
        self.settings_menu_index = -1
        for i, item in enumerate(self.menu_items):
            if item["name"] == "Settings":
                self.settings_menu_index = i
                break
        if self.settings_menu_index == -1:
            logger.warning("Could not find 'Settings' in menu_items for secret combo.")
        else:
            logger.info(f"Found Settings menu item at index: {self.settings_menu_index}") # Log found index
        
    def _check_secret_combo_conditions(self):
        """Check if conditions are met to START the secret combo timer."""
        required_keys = {self.config.KEY_PREV, self.config.KEY_NEXT}
        state_ok = self.current_state == STATE_MENU
        index_ok = self.menu_index == self.settings_menu_index
        keys_ok = required_keys.issubset(self.keys_held)
        # Detailed log for checking conditions
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
        """
        Handle user input based on current state and detailed input events.

        Args:
            input_results (list): List of input event dictionaries from process_input.

        Returns:
            bool: True if a standard action caused a state change, False otherwise.
                  Does not indicate state changes from secret combo activation.
        """
        state_changed_by_action = False
        combo_potentially_active = bool(self.secret_combo_start_time)

        for result in input_results:
            event_type = result['type']
            key = result.get('key') # Get key if available
            action = result.get('action') # Get action if available

            if event_type == 'QUIT': # Handle QUIT directly if needed
                # Or let main handle it based on the list
                pass

            elif event_type == 'KEYDOWN':
                self.keys_held.add(key)
                logger.debug(f"KEYDOWN: key={key}. keys_held={self.keys_held}") # Log keydown and held set

                # Start KEY_PREV timer if pressed
                if key == self.config.KEY_PREV and self.key_prev_press_start_time is None:
                    self.key_prev_press_start_time = time.time()
                    logger.debug("KEY_PREV press timer started.")

                # Check if we should start the secret combo timer
                if not self.secret_combo_start_time and self._check_secret_combo_conditions():
                    logger.info("SECRET COMBO TIMER STARTED")
                    self.secret_combo_start_time = time.time()
                    combo_potentially_active = True # Prevent standard action processing this cycle

                # --- Direct Pong Input Handling on KeyDown --- #
                if self.current_state == STATE_PONG_ACTIVE and self.active_pong_game:
                    # Only allow paddle movement if game is not paused
                    if not self.active_pong_game.paused and (key == self.config.KEY_PREV or key == self.config.KEY_NEXT):
                        # Pass the key code directly to Pong's input handler (which is now update)
                        # self.active_pong_game.handle_input(key)
                        # Movement is handled by checking keys_held in PongGame.update
                        pass
                    # SELECT key press does nothing on KeyDown in Pong
                    # A/D presses while paused do nothing on KeyDown

            elif event_type == 'KEYUP':
                # Flag to check if combo was active *before* this keyup potentially resets it
                combo_was_active = bool(self.secret_combo_start_time)

                if key in self.keys_held:
                    self.keys_held.remove(key)
                logger.debug(f"KEYUP: key={key}. keys_held={self.keys_held}")

                # Reset combo timer FIRST if a combo key is released
                if self.secret_combo_start_time and (key == self.config.KEY_PREV or key == self.config.KEY_NEXT):
                    logger.info("SECRET COMBO TIMER RESET (Key Up)")
                    self.secret_combo_start_time = None
                    combo_potentially_active = False # Update local flag for this cycle

                # --- Process standard actions only on KeyUp --- #
                # --- and only if the combo wasn't just active --- #
                if not combo_was_active:
                    # Handle KEY_PREV short press release (for MENU/Secret Up action)
                    if key == self.config.KEY_PREV and self.key_prev_press_start_time is not None:
                        press_duration = time.time() - self.key_prev_press_start_time
                        start_time_before_reset = self.key_prev_press_start_time
                        self.key_prev_press_start_time = None # Reset timer regardless
                        logger.debug("KEY_PREV released, timer reset.")
                        # Handle Pong Pause Continue (A)
                        if self.current_state == STATE_PONG_ACTIVE and self.active_pong_game and self.active_pong_game.paused:
                            logger.info("PREV key released in paused Pong. Unpausing.")
                            self.active_pong_game.toggle_pause()
                            state_changed_by_action = True # Indicate potential state interaction
                        # Check duration and state for normal PREV action
                        elif self.current_state in [STATE_MENU, STATE_SECRET_GAMES] and press_duration < self.config.INPUT_LONG_PRESS_DURATION:
                            logger.debug(f"Short press KEY_PREV in {self.current_state} state: processing PREV action on KeyUp.")
                            state_changed_by_action = self._process_action("PREV") or state_changed_by_action
                        # Long press action handled in update()
                        

                    # Handle KEY_NEXT short press release (for MENU/Secret Down action)
                    elif key == self.config.KEY_NEXT:
                         # Handle Pong Pause Quit (D)
                         if self.current_state == STATE_PONG_ACTIVE and self.active_pong_game and self.active_pong_game.paused:
                             logger.info("NEXT key released in paused Pong. Quitting game.")
                             # Quit Pong and return to previous state
                             if self.previous_state:
                                 self.current_state = self.previous_state
                             else:
                                 self.current_state = STATE_MENU # Fallback
                             self.previous_state = STATE_PONG_ACTIVE
                             self.active_pong_game = None # Cleanup game instance
                             state_changed_by_action = True
                             logger.debug(f"State changed via NEXT (Quit) in paused Pong: -> {self.current_state}")
                         # Handle normal NEXT action
                         elif self.current_state in [STATE_MENU, STATE_SECRET_GAMES]:
                             logger.debug(f"Short press KEY_NEXT in {self.current_state} state: processing NEXT action on KeyUp.")
                             state_changed_by_action = self._process_action("NEXT") or state_changed_by_action

                    # Handle KEY_SELECT short press release (for Select/Action)
                    elif key == self.config.KEY_SELECT:
                         # Handle Pong Pause Toggle (Enter)
                         if self.current_state == STATE_PONG_ACTIVE and self.active_pong_game:
                             logger.info("SELECT key released in Pong. Toggling pause.")
                             self.active_pong_game.toggle_pause()
                             state_changed_by_action = True # Indicate potential state interaction
                         # Handle normal SELECT action
                         else: 
                             logger.debug("Short press KEY_SELECT: processing SELECT action on KeyUp.")
                             state_changed_by_action = self._process_action("SELECT") or state_changed_by_action

        return state_changed_by_action

    def update(self):
        """
        Performs time-based updates, like checking the secret combo timer.
        Should be called once per frame.

        Returns:
            bool: True if the state changed (e.g., secret menu activated), False otherwise.
        """
        state_changed = False
        # Check secret combo timer
        if self.secret_combo_start_time:
            current_time = time.time()
            duration = current_time - self.secret_combo_start_time
            required_duration = self.config.SECRET_HOLD_DURATION
            # Log timer check
            logger.debug(f"Checking combo timer: now={current_time:.2f}, start={self.secret_combo_start_time:.2f}, duration={duration:.2f}, required={required_duration}")
            if duration >= required_duration:
                state_changed = self._activate_secret_menu()
                # Return early if secret menu activated to avoid long press back trigger simultaneously
                if state_changed:
                    return state_changed

        # Check KEY_PREV long press timer for Back action
        if self.key_prev_press_start_time is not None:
            hold_duration = time.time() - self.key_prev_press_start_time
            # Only trigger back if NOT in the pong game
            if hold_duration >= self.config.INPUT_LONG_PRESS_DURATION and self.current_state != STATE_PONG_ACTIVE:
                # If in a game state (like Tetris later?), return to secret menu (placeholder logic)
                # if self.current_state in [STATE_TETRIS_ACTIVE]: # Example for future games
                #    # ... return to secret menu ...

                # If in a regular view (not menu), return to main menu
                if self.current_state not in [STATE_MENU, STATE_SECRET_GAMES]: # Avoid going back from menus via long press
                    logger.info(f"Long press KEY_PREV detected in state {self.current_state}. Returning to menu.")
                    state_changed = self._return_to_menu()
                else:
                    # If long pressed in menu/secret menu, just reset timer, don't go back
                    logger.debug(f"Long press KEY_PREV in {self.current_state} state - ignored for back action.")
                # Reset timer ONLY if action was taken or explicitly ignored
                self.key_prev_press_start_time = None
            elif hold_duration >= self.config.INPUT_LONG_PRESS_DURATION and self.current_state == STATE_PONG_ACTIVE:
                # If long pressed during pong, just reset the timer, do nothing else
                logger.debug("Long press KEY_PREV during Pong game - ignored for back action.")
                self.key_prev_press_start_time = None

        # Add other time-based updates here if needed

        return state_changed

    def _process_action(self, action):
        """Processes standard actions based on the current state."""
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
        elif self.current_state == STATE_SETTINGS:
            state_changed = self._handle_settings_input(action)
        elif self.current_state == STATE_SECRET_GAMES:
            state_changed = self._handle_secret_games_input(action)
        elif self.current_state == STATE_PONG_ACTIVE:
            # Pong input is handled on KeyDown directly, not via _process_action
            # state_changed = self._handle_pong_input(action) # Remove this line
            pass # Handled in handle_input

        if state_changed:
            logger.debug(f"State changed via action '{action}': {self.previous_state} -> {self.current_state}")

        return state_changed

    def _return_to_menu(self):
        """Helper method to transition back to the main menu state."""
        self.previous_state = self.current_state
        self.current_state = STATE_MENU
        logger.debug(f"{self.previous_state}: Return to menu")
        return True
    
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
            elif self.current_state == STATE_SETTINGS: # Added handling for settings transition
                logger.debug("Transition to settings view")
                
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

        return False
    
    def _handle_sensor_input(self, action):
        """Handle input in sensor view state."""
        if action == "SELECT":
            # Toggle freeze state
            self.is_frozen = not self.is_frozen
            logger.debug(f"Sensor view: {'Frozen' if self.is_frozen else 'Unfrozen'}")
            return True

        return False
        
    def _handle_system_info_input(self, action):
        """Handle input in system info view state."""
        if action == "SELECT":
            # Toggle freeze state
            self.is_frozen = not self.is_frozen
            logger.debug(f"System info: {'Frozen' if self.is_frozen else 'Unfrozen'}")
            return True

        return False
    
    def _handle_settings_input(self, action):
        """Handle input in settings view state."""
        if action == "SELECT":
            # Toggle setting or apply setting change
            logger.debug(f"Settings: SELECT pressed (currently toggles freeze)")
            self.is_frozen = not self.is_frozen # Keep freeze toggle for now
            return True

        return False
    
    def _handle_secret_games_input(self, action):
        """Handle input in secret games menu state."""
        if action == "SELECT":
            # SELECT does nothing for now
            # Placeholder for launching the selected game
            selected_game = self.secret_menu_items[self.secret_menu_index]
            selected_action = selected_game.get('action')
            logger.info(f"Secret Games: SELECT activated on '{selected_game['name']}'. Action: {selected_action}")

            if selected_action == "RETURN_TO_MENU":
                 return self._return_to_menu()
            elif selected_action == "LAUNCH_PONG":
                logger.info("Launching Pong...")
                self.previous_state = self.current_state
                self.current_state = STATE_PONG_ACTIVE
                # Pass screen dimensions from config
                self.active_pong_game = PongGame(self.config.SCREEN_WIDTH, self.config.SCREEN_HEIGHT, self.config)
                return True # State changed
            elif selected_action == "LAUNCH_TETRIS":
                 logger.warning("Tetris launch not implemented yet.")
                 return False # No state change yet

            return True # Consider action handled, even if placeholder for other games
        elif action == "PREV": # Up
            self.secret_menu_index = (self.secret_menu_index - 1) % len(self.secret_menu_items)
            logger.debug(f"Secret Games Menu navigation: PREV -> {self.secret_menu_items[self.secret_menu_index]['name']}")
            return True
        elif action == "NEXT": # Down
            self.secret_menu_index = (self.secret_menu_index + 1) % len(self.secret_menu_items)
            logger.debug(f"Secret Games Menu navigation: NEXT -> {self.secret_menu_items[self.secret_menu_index]['name']}")
            return True

        # Long press A handled by update() method
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
            # Get sensors suitable for dashboard cycling (exclude system info etc.)
            dashboard_sensors = [item["sensor"] for item in self.menu_items if item["sensor"] and item["state"] == STATE_SENSOR_VIEW]
            if not dashboard_sensors:
                logger.warning("No sensors defined for dashboard cycling.")
                return False

            self.cycle_index = (self.cycle_index + 1) % len(dashboard_sensors)
            self.current_sensor = dashboard_sensors[self.cycle_index]
            self.last_cycle_time = current_time
            logger.debug(f"Auto-cycling to {self.current_sensor}")
            return True
            
        return False 