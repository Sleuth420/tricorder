# --- models/settings_manager.py ---
# Manages settings-related state and input handling

import logging
import config as app_config

logger = logging.getLogger(__name__)

class SettingsManager:
    """Manages settings-related state and input handling."""
    
    def __init__(self, config_module):
        """
        Initialize the settings manager.
        
        Args:
            config_module: The configuration module
        """
        self.config = config_module
        
        # Import settings options
        from config import AUTO_CYCLE_INTERVAL_OPTIONS, SECRET_COMBO_DURATION_OPTIONS
        
        # Display settings state (main menu: Dashboard auto-cycle, Safe area, Debug layout, Back)
        self.display_settings_option_index = 0
        # Cycle interval picker sub-screen state
        self.display_cycle_interval_index = 0
        self._init_display_cycle_interval_index()
        
        # Combo duration selection state
        self.combo_duration_selection_index = 0
        self._init_combo_duration_index()
        
    def _init_display_cycle_interval_index(self):
        """Initialize cycle interval picker index from current config."""
        try:
            interval_options = [x for x in getattr(self.config, 'AUTO_CYCLE_INTERVAL_OPTIONS', [1, 5, 10, 15, 30, 60]) if isinstance(x, int)]
            if not interval_options:
                interval_options = [1, 5, 10, 15, 30, 60]
            current = getattr(self.config, 'AUTO_CYCLE_INTERVAL', 5)
            if current in interval_options:
                self.display_cycle_interval_index = interval_options.index(current)
            else:
                self.display_cycle_interval_index = 0
        except (ValueError, AttributeError):
            self.display_cycle_interval_index = 0

    def _init_combo_duration_index(self):
        """Initialize combo duration index with current config value."""
        try:
            current_duration = self.config.CURRENT_SECRET_COMBO_DURATION
            if current_duration in self.config.SECRET_COMBO_DURATION_OPTIONS:
                self.combo_duration_selection_index = self.config.SECRET_COMBO_DURATION_OPTIONS.index(current_duration)
        except (ValueError, AttributeError):
            logger.warning(f"Could not find current CURRENT_SECRET_COMBO_DURATION {self.config.CURRENT_SECRET_COMBO_DURATION} in options, defaulting index to 0.")
            self.combo_duration_selection_index = 0

    # Display settings main menu: 0=Dashboard auto-cycle, 1=LED matrix (lid open), 2=Back
    DISPLAY_MENU_ACTION_CYCLE = "DISPLAY_CYCLE_INTERVAL"
    DISPLAY_MENU_ACTION_LED_MATRIX = "TOGGLE_LED_MATRIX"
    DISPLAY_MENU_ACTION_BACK = "GO_BACK"
    DISPLAY_SETTINGS_MENU_LEN = 3

    def handle_display_settings_input(self, action):
        """Handle input for the Display Settings main menu (3 items)."""
        state_changed = False
        if action == app_config.INPUT_ACTION_NEXT:
            self.display_settings_option_index = (self.display_settings_option_index + 1) % self.DISPLAY_SETTINGS_MENU_LEN
            state_changed = True
        elif action == app_config.INPUT_ACTION_PREV:
            self.display_settings_option_index = (self.display_settings_option_index - 1 + self.DISPLAY_SETTINGS_MENU_LEN) % self.DISPLAY_SETTINGS_MENU_LEN
            state_changed = True
        elif action == app_config.INPUT_ACTION_SELECT:
            result = self._dispatch_display_settings_action()
            if isinstance(result, str):
                return result
            state_changed = result
        return state_changed

    def _dispatch_display_settings_action(self):
        """Dispatch Select action for current Display Settings menu item. Returns action string or bool."""
        idx = self.display_settings_option_index
        if idx == 0:
            return self.DISPLAY_MENU_ACTION_CYCLE
        if idx == 1:
            return self.DISPLAY_MENU_ACTION_LED_MATRIX
        if idx == 2:
            return self.DISPLAY_MENU_ACTION_BACK
        return False

    def handle_display_cycle_interval_input(self, action):
        """Handle input for the Dashboard auto-cycle interval picker sub-screen."""
        from config import AUTO_CYCLE_INTERVAL_OPTIONS
        # Build options: numeric intervals + Back (same as config but Back label different in view)
        interval_values = [x for x in AUTO_CYCLE_INTERVAL_OPTIONS if isinstance(x, int)]
        if not interval_values:
            interval_values = [1, 5, 10, 15, 30, 60]
        options_count = len(interval_values) + 1  # +1 for Back
        state_changed = False
        if action == app_config.INPUT_ACTION_NEXT:
            self.display_cycle_interval_index = (self.display_cycle_interval_index + 1) % options_count
            state_changed = True
        elif action == app_config.INPUT_ACTION_PREV:
            self.display_cycle_interval_index = (self.display_cycle_interval_index - 1 + options_count) % options_count
            state_changed = True
        elif action == app_config.INPUT_ACTION_SELECT:
            if self.display_cycle_interval_index < len(interval_values):
                self.config.AUTO_CYCLE_INTERVAL = interval_values[self.display_cycle_interval_index]
                logger.info(f"Applied Dashboard auto-cycle interval: {interval_values[self.display_cycle_interval_index]}s")
                state_changed = True
            else:
                return "BACK_TO_DISPLAY_SETTINGS"
        return state_changed

    def apply_display_settings(self):
        """Legacy: no longer used; kept for compatibility. Use _dispatch_display_settings_action."""
        return False

    def handle_combo_duration_input(self, action):
        """Handle input for the Select Combo Duration view."""
        options = self.config.SECRET_COMBO_DURATION_OPTIONS
        state_changed = False
        
        if action == app_config.INPUT_ACTION_NEXT:
            self.combo_duration_selection_index = (self.combo_duration_selection_index + 1) % len(options)
            logger.debug(f"Combo Duration Select NEXT: index={self.combo_duration_selection_index}, value={options[self.combo_duration_selection_index]}s")
            state_changed = True
        elif action == app_config.INPUT_ACTION_PREV:
            self.combo_duration_selection_index = (self.combo_duration_selection_index - 1 + len(options)) % len(options)
            logger.debug(f"Combo Duration Select PREV: index={self.combo_duration_selection_index}, value={options[self.combo_duration_selection_index]}s")
            state_changed = True
        elif action == app_config.INPUT_ACTION_SELECT:
            state_changed = self.apply_combo_duration_setting()
        return state_changed

    def apply_combo_duration_setting(self):
        """Apply the selected secret combo duration."""
        selected_duration = self.config.SECRET_COMBO_DURATION_OPTIONS[self.combo_duration_selection_index]
        try:
            self.config.CURRENT_SECRET_COMBO_DURATION = selected_duration
            logger.info(f"Applied new Secret Combo Duration: {selected_duration}s")
            return True
        except Exception as e:
            logger.error(f"Error applying combo duration setting: {e}")
            return False

    def get_display_settings_info(self):
        """Get current display settings main menu selection for UI."""
        return {
            'selected_index': self.display_settings_option_index,
        }

    def get_display_cycle_interval_info(self):
        """Get current cycle interval picker state for UI."""
        from config import AUTO_CYCLE_INTERVAL_OPTIONS
        interval_values = [x for x in AUTO_CYCLE_INTERVAL_OPTIONS if isinstance(x, int)]
        if not interval_values:
            interval_values = [1, 5, 10, 15, 30, 60]
        return {
            'options': interval_values,
            'selected_index': self.display_cycle_interval_index,
            'current_interval': getattr(self.config, 'AUTO_CYCLE_INTERVAL', 5),
        }

    def get_combo_duration_info(self):
        """Get current combo duration information for UI."""
        return {
            'options': self.config.SECRET_COMBO_DURATION_OPTIONS,
            'selected_index': self.combo_duration_selection_index,
            'selected_value': self.config.SECRET_COMBO_DURATION_OPTIONS[self.combo_duration_selection_index]
        } 