# --- models/input_manager.py ---
# Manages input processing and special input combinations

import logging
import time
import config as app_config

logger = logging.getLogger(__name__)

class InputManager:
    """Manages input processing, including secret combos and long press detection."""
    
    def __init__(self, config_module):
        """
        Initialize the input manager.
        
        Args:
            config_module: The configuration module
        """
        self.config = config_module
        
        # Input state tracking
        self.keys_held = set()
        self.secret_combo_start_time = None
        self.key_prev_press_start_time = None
        self.key_next_press_start_time = None  # For 3D viewer pause menu
        self.joystick_middle_press_start_time = None
        # Used to suppress combo key releases after secret menu activation
        self.suppress_keyup_actions = False
        self.suppressed_keys_pending = set()
        
        # Mouse long press tracking
        self.mouse_left_press_start_time = None
        self.mouse_right_press_start_time = None
        self.mouse_middle_press_start_time = None
        # So release can skip PREV when BACK was already handled by long press
        self.key_prev_long_press_consumed = False
        self.mouse_left_long_press_consumed = False
        
        # Zoom combo timing (to prevent accidental menu activation)
        self.last_zoom_combo_time = None
        self.zoom_combo_cooldown = 0.3  # 300ms cooldown after zoom combo ends
        
        # Secret combo configuration
        self.settings_menu_index = -1  # Will be set by menu manager
        
    def set_settings_menu_index(self, index):
        """Set the settings menu index for secret combo detection."""
        self.settings_menu_index = index
        
    def handle_keydown(self, key):
        """
        Handle key down events.
        
        Args:
            key: The key that was pressed
            
        Returns:
            dict: Input event data
        """
        self.keys_held.add(key)
        logger.debug(f"KEYDOWN: key={key}. keys_held={self.keys_held}")
        
        # Start timing for KEY_PREV long press
        if key == self.config.KEY_PREV and self.key_prev_press_start_time is None:
            self.key_prev_press_start_time = time.time()
            logger.debug("KEY_PREV press timer started.")
            
        # Start timing for KEY_NEXT long press (for 3D viewer pause menu)
        if key == self.config.KEY_NEXT and self.key_next_press_start_time is None:
            self.key_next_press_start_time = time.time()
            logger.debug("KEY_NEXT press timer started.")
            
        return {
            'type': 'KEYDOWN',
            'key': key,
            'keys_held': self.keys_held.copy()
        }
        
    def handle_keyup(self, key):
        """
        Handle key up events.
        
        Args:
            key: The key that was released
            
        Returns:
            dict: Input event data
        """
        # Ignore the release once when coming from a secret combo activation
        suppressed_release = False
        if self.suppress_keyup_actions and key in self.suppressed_keys_pending:
            suppressed_release = True
            self.suppressed_keys_pending.discard(key)
            # Clear any timers tied to this key to avoid stray long-press triggers
            if key == self.config.KEY_PREV:
                self.key_prev_press_start_time = None
            if key == self.config.KEY_NEXT:
                self.key_next_press_start_time = None
            if not self.suppressed_keys_pending:
                self.suppress_keyup_actions = False

        if key in self.keys_held:
            self.keys_held.remove(key)
        logger.debug(f"KEYUP: key={key}. keys_held={self.keys_held}")
        
        # Handle KEY_PREV release
        press_duration = None
        if key == self.config.KEY_PREV:
            if self.key_prev_press_start_time is not None:
                press_duration = time.time() - self.key_prev_press_start_time
                self.key_prev_press_start_time = None
                logger.debug("KEY_PREV released, timer reset.")
            elif self.key_prev_long_press_consumed:
                # BACK was already handled in update(); treat as long press so release skips PREV
                press_duration = self.config.INPUT_LONG_PRESS_DURATION
                self.key_prev_long_press_consumed = False
                logger.debug("KEY_PREV release after consumed long press, skipping PREV.")
            
        # Handle KEY_NEXT release (for 3D viewer pause menu)
        next_press_duration = None
        if key == self.config.KEY_NEXT and self.key_next_press_start_time is not None:
            next_press_duration = time.time() - self.key_next_press_start_time
            self.key_next_press_start_time = None
            logger.debug("KEY_NEXT released, timer reset.")
            
        # Reset secret combo if combo keys are released
        if self.secret_combo_start_time and (key == self.config.KEY_PREV or key == self.config.KEY_NEXT):
            logger.info("KEYBOARD SECRET COMBO TIMER RESET (Key Up)")
            self.secret_combo_start_time = None
            
        return {
            'type': 'KEYUP',
            'key': key,
            'press_duration': press_duration,
            'next_press_duration': next_press_duration,
            'keys_held': self.keys_held.copy(),
            'suppressed_release': suppressed_release
        }
        
    def handle_joystick_press(self):
        """Handle joystick middle press."""
        self.joystick_middle_press_start_time = time.time()
        logger.info("Joystick middle PRESS detected. Starting press timer.")
        
        return {
            'type': 'JOYSTICK_MIDDLE_PRESS',
            'timestamp': self.joystick_middle_press_start_time
        }
        
    def handle_joystick_release(self):
        """Handle joystick middle release."""
        if self.joystick_middle_press_start_time is None:
            logger.debug("Joystick middle RELEASE detected without a corresponding press start time.")
            return {'type': 'JOYSTICK_MIDDLE_RELEASE', 'press_duration': 0}
            
        press_duration = time.time() - self.joystick_middle_press_start_time
        logger.debug(f"Joystick middle RELEASE detected. Press duration: {press_duration:.2f}s")
        
        self.joystick_middle_press_start_time = None
        
        return {
            'type': 'JOYSTICK_MIDDLE_RELEASE',
            'press_duration': press_duration
        }
        
    def check_secret_combo_conditions(self, current_state, menu_index):
        """
        Check if conditions are met to START the secret combo timer.
        
        Args:
            current_state (str): Current application state
            menu_index (int): Current menu index
            
        Returns:
            bool: True if secret combo conditions are met
        """
        required_keys = {self.config.KEY_PREV, self.config.KEY_NEXT}
        state_ok = current_state == "MENU"
        index_ok = menu_index == self.settings_menu_index
        keys_ok = required_keys.issubset(self.keys_held)
        
        logger.debug(f"Combo check: state='{current_state}'({state_ok}), "
                    f"index={menu_index}({index_ok}), settings_idx={self.settings_menu_index}, "
                    f"keys={self.keys_held}({keys_ok})")
        
        return state_ok and index_ok and keys_ok
        
    def start_secret_combo_timer(self):
        """Start the secret combo timer."""
        if not self.secret_combo_start_time:
            logger.info("KEYBOARD SECRET COMBO TIMER STARTED")
            self.secret_combo_start_time = time.time()
            return True
        return False
        
    def check_secret_combo_duration(self):
        """
        Check if secret combo has been held long enough.
        
        Returns:
            bool: True if combo duration is met
        """
        if not self.secret_combo_start_time:
            return False
            
        current_time = time.time()
        duration = current_time - self.secret_combo_start_time
        return duration >= self.config.CURRENT_SECRET_COMBO_DURATION
        
    def reset_secret_combo(self):
        """Reset the secret combo timer."""
        self.secret_combo_start_time = None

    def suppress_combo_keyups(self):
        """Suppress the next KEYUPs for combo keys after activating secret menu."""
        self.suppress_keyup_actions = True
        self.suppressed_keys_pending = {self.config.KEY_PREV, self.config.KEY_NEXT}
        # Clear held keys so downstream checks don't see stale state
        self.keys_held.clear()
        
    def check_long_press_duration(self):
        """
        Check if KEY_PREV has been held long enough for back action.
        
        Returns:
            bool: True if long press duration is met
        """
        if not self.key_prev_press_start_time:
            return False
            
        hold_duration = time.time() - self.key_prev_press_start_time
        return hold_duration >= self.config.INPUT_LONG_PRESS_DURATION
        
    def reset_long_press_timer(self, consumed_as_long_press=False):
        """Reset the long press timer. If consumed_as_long_press, next KEY_PREV release will report long duration so PREV is skipped."""
        self.key_prev_press_start_time = None
        if consumed_as_long_press:
            self.key_prev_long_press_consumed = True
        
    def check_next_key_long_press(self):
        """
        Check if KEY_NEXT (D key) has been held long enough for 3D viewer pause menu.
        
        Returns:
            bool: True if long press duration is met
        """
        if not self.key_next_press_start_time:
            return False
            
        hold_duration = time.time() - self.key_next_press_start_time
        return hold_duration >= self.config.INPUT_LONG_PRESS_DURATION
        
    def reset_next_key_timer(self):
        """Reset the next key long press timer."""
        self.key_next_press_start_time = None
        
    def check_joystick_long_press(self, current_state):
        """
        Check if joystick middle button has been held long enough for secret menu.
        
        Args:
            current_state (str): Current application state
            
        Returns:
            bool: True if joystick long press conditions are met
        """
        if (self.joystick_middle_press_start_time is None or 
            current_state != "MENU"):
            return False
            
        current_time = time.time()
        duration = current_time - self.joystick_middle_press_start_time
        return duration >= self.config.CURRENT_SECRET_COMBO_DURATION
        
    def reset_joystick_timer(self):
        """Reset the joystick press timer."""
        self.joystick_middle_press_start_time = None
    
    def check_zoom_in_combo(self):
        """
        Check if Return+D combo is being held for zoom in.
        
        Returns:
            bool: True if zoom in combo is active
        """
        is_active = {self.config.KEY_SELECT, self.config.KEY_NEXT}.issubset(self.keys_held)
        if is_active:
            self.last_zoom_combo_time = time.time()
        return is_active
    
    def check_zoom_out_combo(self):
        """
        Check if Return+A combo is being held for zoom out.
        
        Returns:
            bool: True if zoom out combo is active
        """
        is_active = {self.config.KEY_SELECT, self.config.KEY_PREV}.issubset(self.keys_held)
        if is_active:
            self.last_zoom_combo_time = time.time()
        return is_active
    
    def is_zoom_combo_recently_active(self):
        """
        Check if a zoom combo was recently active (within cooldown period).
        This prevents accidental menu activation when releasing combo keys.
        
        Returns:
            bool: True if zoom combo was recently active
        """
        if not self.last_zoom_combo_time:
            return False
        
        time_since_combo = time.time() - self.last_zoom_combo_time
        return time_since_combo < self.zoom_combo_cooldown
    
    def handle_mousedown(self, button):
        """
        Handle mouse button down events.
        
        Args:
            button: The mouse button that was pressed
            
        Returns:
            dict: Input event data
        """
        logger.debug(f"MOUSEDOWN: button={button}")
        
        # Start timing for mouse long press detection
        if button == self.config.MOUSE_LEFT and self.mouse_left_press_start_time is None:
            self.mouse_left_press_start_time = time.time()
            logger.debug("Mouse left press timer started.")
        elif button == self.config.MOUSE_RIGHT and self.mouse_right_press_start_time is None:
            self.mouse_right_press_start_time = time.time()
            logger.debug("Mouse right press timer started.")
        elif button == self.config.MOUSE_MIDDLE and self.mouse_middle_press_start_time is None:
            self.mouse_middle_press_start_time = time.time()
            logger.debug("Mouse middle press timer started.")
            
        return {
            'type': 'MOUSEDOWN',
            'button': button
        }
        
    def handle_mouseup(self, button):
        """
        Handle mouse button up events.

        Args:
            button: The mouse button that was released

        Returns:
            dict: Input event data including press_duration for long-press detection
        """
        logger.debug(f"MOUSEUP: button={button}")

        press_duration = None
        # Compute duration before resetting so app can suppress release-as-action after long press
        if button == self.config.MOUSE_LEFT:
            if self.mouse_left_press_start_time is not None:
                press_duration = time.time() - self.mouse_left_press_start_time
            elif self.mouse_left_long_press_consumed:
                # BACK was already handled in update(); treat as long press so release skips PREV
                press_duration = self.config.INPUT_LONG_PRESS_DURATION
                self.mouse_left_long_press_consumed = False
                logger.debug("Mouse left release after consumed long press, skipping PREV.")
        elif button == self.config.MOUSE_RIGHT and self.mouse_right_press_start_time is not None:
            press_duration = time.time() - self.mouse_right_press_start_time
        elif button == self.config.MOUSE_MIDDLE and self.mouse_middle_press_start_time is not None:
            press_duration = time.time() - self.mouse_middle_press_start_time

        # Reset timing for mouse long press detection
        if button == self.config.MOUSE_LEFT:
            self.mouse_left_press_start_time = None
            logger.debug("Mouse left press timer reset.")
        elif button == self.config.MOUSE_RIGHT:
            self.mouse_right_press_start_time = None
            logger.debug("Mouse right press timer reset.")
        elif button == self.config.MOUSE_MIDDLE:
            self.mouse_middle_press_start_time = None
            logger.debug("Mouse middle press timer reset.")

        return {
            'type': 'MOUSEUP',
            'button': button,
            'press_duration': press_duration
        }
    
    def check_mouse_left_long_press(self):
        """
        Check if mouse left button has been held long enough for back action.
        
        Returns:
            bool: True if long press duration is met
        """
        if not self.mouse_left_press_start_time:
            return False
            
        hold_duration = time.time() - self.mouse_left_press_start_time
        return hold_duration >= self.config.INPUT_LONG_PRESS_DURATION
        
    def check_mouse_right_long_press(self):
        """
        Check if mouse right button has been held long enough for 3D viewer pause menu.
        
        Returns:
            bool: True if long press duration is met
        """
        if not self.mouse_right_press_start_time:
            return False
            
        hold_duration = time.time() - self.mouse_right_press_start_time
        return hold_duration >= self.config.INPUT_LONG_PRESS_DURATION
        
    def check_mouse_middle_long_press(self, current_state):
        """
        Check if mouse middle button has been held long enough for secret menu.
        
        Args:
            current_state (str): Current application state
            
        Returns:
            bool: True if mouse middle long press conditions are met
        """
        if (self.mouse_middle_press_start_time is None or 
            current_state != "MENU"):
            return False
            
        current_time = time.time()
        duration = current_time - self.mouse_middle_press_start_time
        return duration >= self.config.CURRENT_SECRET_COMBO_DURATION
        
    def reset_mouse_left_timer(self, consumed_as_long_press=False):
        """Reset the mouse left press timer. If consumed_as_long_press, next MOUSE_LEFT release will report long duration so PREV is skipped."""
        self.mouse_left_press_start_time = None
        if consumed_as_long_press:
            self.mouse_left_long_press_consumed = True
        
    def reset_mouse_right_timer(self):
        """Reset the mouse right press timer."""
        self.mouse_right_press_start_time = None
        
    def reset_mouse_middle_timer(self):
        """Reset the mouse middle press timer."""
        self.mouse_middle_press_start_time = None 