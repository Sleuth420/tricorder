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
        if key in self.keys_held:
            self.keys_held.remove(key)
        logger.debug(f"KEYUP: key={key}. keys_held={self.keys_held}")
        
        # Handle KEY_PREV release
        press_duration = None
        if key == self.config.KEY_PREV and self.key_prev_press_start_time is not None:
            press_duration = time.time() - self.key_prev_press_start_time
            self.key_prev_press_start_time = None
            logger.debug("KEY_PREV released, timer reset.")
            
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
            'keys_held': self.keys_held.copy()
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
        
    def reset_long_press_timer(self):
        """Reset the long press timer."""
        self.key_prev_press_start_time = None
        
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