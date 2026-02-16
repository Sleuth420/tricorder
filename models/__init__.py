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
from .schematics_manager import SchematicsManager
from .settings_manager import SettingsManager
from .device_manager import DeviceManager
from .wifi_manager import WifiManager, WIFI_ACTION_TOGGLE, WIFI_ACTION_SCAN, WIFI_ACTION_CONNECT, WIFI_ACTION_VIEW_SAVED, WIFI_ACTION_BACK_TO_SETTINGS, WIFI_ACTION_BROWSE_NETWORKS, WIFI_ACTION_BACK_TO_WIFI, WIFI_ACTION_CONNECT_TO_NETWORK, WIFI_ACTION_ENTER_PASSWORD

# Export other existing models
from .reading_history import ReadingHistory
from .menu_item import MenuItem

# Export state constants for convenience
from .app_state import (
    STATE_MENU, STATE_SENSORS_MENU, STATE_DASHBOARD, STATE_SENSOR_VIEW,
    STATE_SYSTEM_INFO, STATE_SETTINGS, STATE_SECRET_GAMES, STATE_PONG_ACTIVE, STATE_BREAKOUT_ACTIVE, STATE_SNAKE_ACTIVE, STATE_TETRIS_ACTIVE,
    STATE_SCHEMATICS, STATE_SCHEMATICS_MENU, STATE_SCHEMATICS_CATEGORY, STATE_MEDIA_PLAYER,
    STATE_SETTINGS_WIFI,
    STATE_SETTINGS_WIFI_NETWORKS,
    STATE_WIFI_PASSWORD_ENTRY,
    STATE_SETTINGS_BLUETOOTH,
    STATE_SETTINGS_BLUETOOTH_DEVICES,
    STATE_SETTINGS_DEVICE,
    STATE_SETTINGS_DISPLAY,
    STATE_SELECT_COMBO_DURATION,
    STATE_SETTINGS_VOLUME,
    STATE_DISPLAY_CYCLE_INTERVAL,
    # New Confirmation States
    STATE_CONFIRM_REBOOT,
    STATE_CONFIRM_SHUTDOWN,
    STATE_CONFIRM_RESTART_APP
)

# Export public interface
__all__ = [
    'AppState',
    'StateManager',
    'InputManager',
    'MenuManager',
    'GameManager',
    'SchematicsManager',
    'SettingsManager',
    'DeviceManager',
    'WifiManager',
    'STATE_MENU', 'STATE_SENSORS_MENU', 'STATE_DASHBOARD', 'STATE_SENSOR_VIEW',
    'STATE_SYSTEM_INFO', 'STATE_SETTINGS', 'STATE_SECRET_GAMES', 'STATE_PONG_ACTIVE', 'STATE_BREAKOUT_ACTIVE', 'STATE_SNAKE_ACTIVE', 'STATE_TETRIS_ACTIVE',
    'STATE_SCHEMATICS', 'STATE_SCHEMATICS_MENU', 'STATE_SCHEMATICS_CATEGORY', 'STATE_MEDIA_PLAYER',
    'STATE_SETTINGS_WIFI',
    'STATE_SETTINGS_WIFI_NETWORKS',
    'STATE_WIFI_PASSWORD_ENTRY',
    'STATE_SETTINGS_BLUETOOTH',
    'STATE_SETTINGS_BLUETOOTH_DEVICES',
    'STATE_SETTINGS_DEVICE',
    'STATE_SETTINGS_DISPLAY',
    'STATE_SELECT_COMBO_DURATION',
    'STATE_SETTINGS_VOLUME',
    'STATE_DISPLAY_CYCLE_INTERVAL',
    # New Confirmation States
    'STATE_CONFIRM_REBOOT',
    'STATE_CONFIRM_SHUTDOWN',
    'STATE_CONFIRM_RESTART_APP',
    'MenuItem',
    'ReadingHistory',
    # WifiManager actions
    'WIFI_ACTION_TOGGLE',
    'WIFI_ACTION_SCAN',
    'WIFI_ACTION_CONNECT',
    'WIFI_ACTION_VIEW_SAVED',
    'WIFI_ACTION_BACK_TO_SETTINGS',
    'WIFI_ACTION_BROWSE_NETWORKS',
    'WIFI_ACTION_BACK_TO_WIFI',
    'WIFI_ACTION_CONNECT_TO_NETWORK',
    'WIFI_ACTION_ENTER_PASSWORD'
] 