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
        
        # Display settings state
        self.display_settings_option_index = 0
        self._init_display_settings_index()
        
        # Combo duration selection state
        self.combo_duration_selection_index = 0
        self._init_combo_duration_index()
        
    def _init_display_settings_index(self):
        """Initialize display settings index with current config value."""
        try:
            from config import AUTO_CYCLE_INTERVAL_OPTIONS
            current_interval = self.config.AUTO_CYCLE_INTERVAL
            if current_interval in AUTO_CYCLE_INTERVAL_OPTIONS:
                self.display_settings_option_index = AUTO_CYCLE_INTERVAL_OPTIONS.index(current_interval)
        except (ValueError, AttributeError):
            logger.warning(f"Could not find current AUTO_CYCLE_INTERVAL {self.config.AUTO_CYCLE_INTERVAL} in options, defaulting index to 0.")
            self.display_settings_option_index = 0
    
    def _init_combo_duration_index(self):
        """Initialize combo duration index with current config value."""
        try:
            current_duration = self.config.CURRENT_SECRET_COMBO_DURATION
            if current_duration in self.config.SECRET_COMBO_DURATION_OPTIONS:
                self.combo_duration_selection_index = self.config.SECRET_COMBO_DURATION_OPTIONS.index(current_duration)
        except (ValueError, AttributeError):
            logger.warning(f"Could not find current CURRENT_SECRET_COMBO_DURATION {self.config.CURRENT_SECRET_COMBO_DURATION} in options, defaulting index to 0.")
            self.combo_duration_selection_index = 0

    def handle_display_settings_input(self, action):
        """Handle input for the Display Settings view."""
        from config import AUTO_CYCLE_INTERVAL_OPTIONS
        
        state_changed = False
        if action == app_config.INPUT_ACTION_NEXT:
            self.display_settings_option_index = (self.display_settings_option_index + 1) % len(AUTO_CYCLE_INTERVAL_OPTIONS)
            logger.debug(f"Display Settings NEXT: index={self.display_settings_option_index}, value={AUTO_CYCLE_INTERVAL_OPTIONS[self.display_settings_option_index]}")
            state_changed = True
        elif action == app_config.INPUT_ACTION_PREV:
            self.display_settings_option_index = (self.display_settings_option_index - 1 + len(AUTO_CYCLE_INTERVAL_OPTIONS)) % len(AUTO_CYCLE_INTERVAL_OPTIONS)
            logger.debug(f"Display Settings PREV: index={self.display_settings_option_index}, value={AUTO_CYCLE_INTERVAL_OPTIONS[self.display_settings_option_index]}")
            state_changed = True
        elif action == app_config.INPUT_ACTION_SELECT:
            state_changed = self.apply_display_settings()
        return state_changed

    def apply_display_settings(self):
        """Apply the selected display settings."""
        from config import AUTO_CYCLE_INTERVAL_OPTIONS
        
        selected_option = AUTO_CYCLE_INTERVAL_OPTIONS[self.display_settings_option_index]
        
        if isinstance(selected_option, str) and selected_option == "<- Back to Main Menu":
            logger.info("Display Settings: Action Go To Main Menu selected.")
            return "GO_TO_MAIN_MENU"  # Return action for AppState to handle
        elif isinstance(selected_option, int):
            try:
                self.config.AUTO_CYCLE_INTERVAL = selected_option
                logger.info(f"Applied new Auto-Cycle Interval: {selected_option}s")
                return True
            except Exception as e:
                logger.error(f"Error applying display setting: {e}")
                return False
        else:
            logger.warning(f"Unknown option type in display settings: {selected_option}")
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
        """Get current display settings information for UI."""
        from config import AUTO_CYCLE_INTERVAL_OPTIONS
        return {
            'options': AUTO_CYCLE_INTERVAL_OPTIONS,
            'selected_index': self.display_settings_option_index,
            'selected_value': AUTO_CYCLE_INTERVAL_OPTIONS[self.display_settings_option_index]
        }

    def get_combo_duration_info(self):
        """Get current combo duration information for UI."""
        return {
            'options': self.config.SECRET_COMBO_DURATION_OPTIONS,
            'selected_index': self.combo_duration_selection_index,
            'selected_value': self.config.SECRET_COMBO_DURATION_OPTIONS[self.combo_duration_selection_index]
        } 