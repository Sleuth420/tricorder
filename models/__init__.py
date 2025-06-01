# --- models package initialization ---
"""
The models package contains modules for state management and data storage.
"""

# Export the main AppState
from .app_state import AppState

# Export the component managers for direct access if needed
from .state_manager import StateManager
from .input_manager import InputManager
from .menu_manager import MenuManager
from .game_manager import GameManager

# Export other existing models
from .reading_history import ReadingHistory
from .menu_item import MenuItem

# Export state constants for convenience
from .app_state import (
    STATE_MENU, STATE_SENSORS_MENU, STATE_DASHBOARD, STATE_SENSOR_VIEW,
    STATE_SYSTEM_INFO, STATE_SETTINGS, STATE_SECRET_GAMES, STATE_PONG_ACTIVE,
    STATE_SCHEMATICS,
    STATE_SETTINGS_WIFI,
    STATE_SETTINGS_BLUETOOTH,
    STATE_SETTINGS_DEVICE,
    STATE_SETTINGS_DISPLAY,
    STATE_SELECT_COMBO_DURATION,
    # New Confirmation States
    STATE_CONFIRM_REBOOT,
    STATE_CONFIRM_SHUTDOWN,
    STATE_CONFIRM_RESTART_APP
)

# Export public interface
__all__ = [
    'AppState',
    'STATE_MENU', 'STATE_SENSORS_MENU', 'STATE_DASHBOARD', 'STATE_SENSOR_VIEW',
    'STATE_SYSTEM_INFO', 'STATE_SETTINGS', 'STATE_SECRET_GAMES', 'STATE_PONG_ACTIVE',
    'STATE_SCHEMATICS',
    'STATE_SETTINGS_WIFI',
    'STATE_SETTINGS_BLUETOOTH',
    'STATE_SETTINGS_DEVICE',
    'STATE_SETTINGS_DISPLAY',
    'STATE_SELECT_COMBO_DURATION',
    # New Confirmation States
    'STATE_CONFIRM_REBOOT',
    'STATE_CONFIRM_SHUTDOWN',
    'STATE_CONFIRM_RESTART_APP',
    'MenuItem',
    'ReadingHistory'
] 