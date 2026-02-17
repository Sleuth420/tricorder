# --- models/app_state.py ---
# Application state management using component managers

import logging
import time
import os # For device actions
from .state_manager import StateManager
from .input_manager import InputManager
from .menu_manager import MenuManager
from .game_manager import GameManager
from .schematics_manager import SchematicsManager
from .settings_manager import SettingsManager
from .device_manager import DeviceManager
from .controls_manager import ControlsManager
from .loading_manager import LoadingManager
from .wifi_manager import WifiManager, WIFI_ACTION_TOGGLE, WIFI_ACTION_BACK_TO_SETTINGS, WIFI_ACTION_BROWSE_NETWORKS, WIFI_ACTION_BACK_TO_WIFI, WIFI_ACTION_CONNECT_TO_NETWORK, WIFI_ACTION_ENTER_PASSWORD # Import WifiManager and relevant actions
from .bluetooth_manager import BluetoothManager
from .password_entry_manager import PasswordEntryManager
from .input_router import InputRouter
from .update_manager import UpdateManager
from .audio_manager import AudioManager
from .network_manager import NetworkManager
from .system_info_manager import SystemInfoManager
from .media_player_manager import MediaPlayerManager
from .st_wiki_manager import StWikiManager
import config as app_config

# Application state constants
STATE_MENU = "MENU"           # Main menu
STATE_SENSORS_MENU = "SENSORS_MENU"  # Sensors submenu
STATE_DASHBOARD = "DASHBOARD" # Dashboard/auto-cycling view
STATE_SENSOR_VIEW = "SENSOR"  # Individual sensor view
STATE_SYSTEM_INFO = "SYSTEM"  # System info view
STATE_SETTINGS = "SETTINGS"   # Main settings category menu
STATE_SECRET_GAMES = "SECRET_GAMES" # Secret menu
STATE_PONG_ACTIVE = "PONG_ACTIVE" # Pong game
STATE_BREAKOUT_ACTIVE = "BREAKOUT_ACTIVE" # Breakout game
STATE_SNAKE_ACTIVE = "SNAKE_ACTIVE" # Snake game
STATE_TETRIS_ACTIVE = "TETRIS_ACTIVE" # Tetris game
STATE_SCHEMATICS = "SCHEMATICS" # Schematics viewer
STATE_SCHEMATICS_MENU = "SCHEMATICS_MENU" # Schematics selection menu
STATE_SCHEMATICS_CATEGORY = "SCHEMATICS_CATEGORY" # Schematics submenu: Schematics | Media Player
STATE_MEDIA_PLAYER = "MEDIA_PLAYER" # Media player view
STATE_ST_WIKI = "ST_WIKI"     # Star Trek wiki (schematics)
STATE_LOADING = "LOADING"     # Loading screen

# New Settings Sub-View States
STATE_SETTINGS_WIFI = "SETTINGS_WIFI"
STATE_SETTINGS_BLUETOOTH = "SETTINGS_BLUETOOTH"
STATE_SETTINGS_BLUETOOTH_DEVICES = "SETTINGS_BLUETOOTH_DEVICES"
STATE_SETTINGS_DEVICE = "SETTINGS_DEVICE"
STATE_SETTINGS_DISPLAY = "SETTINGS_DISPLAY"
STATE_SETTINGS_CONTROLS = "SETTINGS_CONTROLS"
STATE_SETTINGS_UPDATE = "SETTINGS_UPDATE"
STATE_SETTINGS_SOUND_TEST = "SETTINGS_SOUND_TEST"
STATE_SETTINGS_DEBUG = "SETTINGS_DEBUG"
STATE_SETTINGS_DEBUG_OVERLAY = "SETTINGS_DEBUG_OVERLAY"
STATE_SETTINGS_LOG_VIEWER = "SETTINGS_LOG_VIEWER"
STATE_SETTINGS_STAPI = "SETTINGS_STAPI"  # Star Trek Data fetch
STATE_SELECT_COMBO_DURATION = "SELECT_COMBO_DURATION" # New state for selecting combo duration
STATE_SETTINGS_VOLUME = "SETTINGS_VOLUME"  # Device settings: volume control
STATE_DISPLAY_CYCLE_INTERVAL = "DISPLAY_CYCLE_INTERVAL"  # Display settings: dashboard cycle interval picker

# WiFi Sub-States
STATE_SETTINGS_WIFI_NETWORKS = "SETTINGS_WIFI_NETWORKS"  # Browse available networks
STATE_WIFI_PASSWORD_ENTRY = "WIFI_PASSWORD_ENTRY"  # Enter password for WiFi connection

# Confirmation States (New)
STATE_CONFIRM_REBOOT = "CONFIRM_REBOOT"
STATE_CONFIRM_SHUTDOWN = "CONFIRM_SHUTDOWN"
STATE_CONFIRM_RESTART_APP = "CONFIRM_RESTART_APP"



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
        self.ui_scaler = None  # Set after display init (main.py) so games/UI can use safe area

        # Initialize component managers
        self.state_manager = StateManager(config_module)
        self.input_manager = InputManager(config_module)
        
        # Update status tracking
        self.update_available = False
        self.commits_behind = 0
        # Location and public IP (fetched once on boot when WiFi connected)
        self.location_from_ip = None
        self.public_ip = None
        
        # Schematics selection data for 3D viewer
        self.selected_schematics_data = None  # Data from schematics menu selection
        
        # 3D viewer pause menu state
        self.schematics_pause_menu_active = False
        self.schematics_pause_menu_index = 0
        self.menu_manager = MenuManager(config_module)
        self.game_manager = GameManager(config_module, screen_width, screen_height)
        self.schematics_manager = SchematicsManager(config_module, screen_width, screen_height)
        self.settings_manager = SettingsManager(config_module)
        self.device_manager = DeviceManager(config_module)
        self.controls_manager = ControlsManager(config_module)
        self.loading_manager = LoadingManager(config_module, screen_width, screen_height)
        self.wifi_manager = WifiManager(config_module) # Instantiate WifiManager (no command func needed)
        self.bluetooth_manager = BluetoothManager(config_module)
        self.update_manager = UpdateManager(config_module) # Instantiate UpdateManager
        self.audio_manager = AudioManager(config_module) # Instantiate AudioManager
        self.network_manager = NetworkManager() # Instantiate NetworkManager
        self.system_info_manager = SystemInfoManager() # Instantiate SystemInfoManager
        self.media_player_manager = MediaPlayerManager(config_module) # Instantiate MediaPlayerManager
        self.st_wiki_manager = StWikiManager(config_module)  # Star Trek wiki (STAPI cache)

        # Debug overlay - initialized with screen dimensions
        from ui.components.debug import DebugOverlay
        self.debug_overlay = DebugOverlay(screen_width, screen_height)
        # Admin timer: runtime toggle (main.py sets .admin_timer reference after creating it)
        self.admin_timer_enabled = getattr(config_module, "ADMIN_TIMER", False)
        self.admin_timer = None
        
        # Password entry manager - initialized with screen dimensions
        import pygame
        screen_rect = pygame.Rect(0, 0, screen_width, screen_height)
        self.password_entry_manager = PasswordEntryManager(config_module, screen_rect, None)  # Fonts will be set later
        
        # Initialize input router
        self.input_router = InputRouter(self)
        
        # Set up cross-component dependencies
        self.input_manager.set_settings_menu_index(
            self.menu_manager.get_settings_main_menu_idx()
        )
        
        # Core sensor and view state
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
        
    @property
    def active_breakout_game(self):
        """Get the active Breakout game instance."""
        return self.game_manager.get_breakout_game()
        
    @property
    def active_snake_game(self):
        """Get the active Snake game instance."""
        return self.game_manager.get_snake_game()

    @property
    def active_tetris_game(self):
        """Get the active Tetris game instance."""
        return self.game_manager.get_tetris_game()

    @property
    def secret_menu_items(self):
        """Get secret menu items (compatibility property)."""
        return self.menu_manager.secret_menu_items
        
    @property
    def secret_menu_index(self):
        """Get secret menu index (compatibility property)."""
        return self.menu_manager.secret_menu_index

    # Settings Manager Properties for UI compatibility
    @property
    def display_settings_option_index(self):
        """Get display settings option index."""
        return self.settings_manager.display_settings_option_index
    
    @property
    def combo_duration_selection_index(self):
        """Get combo duration selection index."""
        return self.settings_manager.combo_duration_selection_index

    # Device Manager Properties for UI compatibility
    @property
    def device_settings_option_index(self):
        """Get device settings option index."""
        return self.device_manager.device_settings_option_index
    
    @property
    def confirmation_option_index(self):
        """Get confirmation option index."""
        return self.device_manager.confirmation_option_index
    
    @property
    def pending_device_action(self):
        """Get pending device action."""
        return self.device_manager.pending_device_action
    
    # Controls Manager Properties for UI compatibility
    @property
    def controls_index(self):
        """Get controls view index."""
        return self.controls_manager.get_current_index()
    
    # Update Manager Properties for UI compatibility
    @property
    def update_menu_index(self):
        """Get update menu index."""
        return self.update_manager.update_menu_index

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
        # When entering WiFi settings, trigger a status check
        if new_state == STATE_SETTINGS_WIFI and self.current_state != STATE_SETTINGS_WIFI:
            if self.wifi_manager:
                self.wifi_manager.update_wifi_status() # WifiManager handles its own status update
        if new_state == STATE_SETTINGS_BLUETOOTH and self.current_state != STATE_SETTINGS_BLUETOOTH:
            if self.bluetooth_manager:
                self.bluetooth_manager.update_bluetooth_status()
        if new_state == STATE_SETTINGS_BLUETOOTH_DEVICES and self.current_state != STATE_SETTINGS_BLUETOOTH_DEVICES:
            if self.bluetooth_manager:
                self.bluetooth_manager.refresh_devices()
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
                
                # Track input for debug overlay
                if hasattr(self, 'debug_overlay'):
                    self.debug_overlay.add_input_event('KEYDOWN', key)
                
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
                if key_event.get('suppressed_release'):
                    logger.debug("Key release suppressed after secret combo activation.")
                    continue
                
                # Track input for debug overlay
                if hasattr(self, 'debug_overlay'):
                    self.debug_overlay.add_input_event('KEYUP', key)
                
                if not self.input_manager.secret_combo_start_time:
                    state_changed_by_action = self._handle_key_release(key, action_name, key_event) or state_changed_by_action
            
            elif event_type == 'JOYSTICK':
                # Track input for debug overlay
                if hasattr(self, 'debug_overlay'):
                    self.debug_overlay.add_input_event('JOYSTICK', action_name)
                
                if action_name:
                    if self.current_state == STATE_PONG_ACTIVE:
                        state_changed_by_action = self._handle_pong_joystick_input(action_name) or state_changed_by_action
                    elif self.current_state == STATE_BREAKOUT_ACTIVE:
                        state_changed_by_action = self._handle_breakout_joystick_input(action_name) or state_changed_by_action
                    elif self.current_state == STATE_SNAKE_ACTIVE:
                        state_changed_by_action = self._handle_snake_joystick_input(action_name) or state_changed_by_action
                    elif self.current_state == STATE_TETRIS_ACTIVE:
                        state_changed_by_action = self._handle_tetris_joystick_input(action_name) or state_changed_by_action
                    elif self.current_state == STATE_WIFI_PASSWORD_ENTRY:
                        # Handle joystick navigation for password entry
                        direction = result.get('direction')
                        if direction in ['up', 'down', 'left', 'right']:
                            direction_map = {'up': 'UP', 'down': 'DOWN', 'left': 'LEFT', 'right': 'RIGHT'}
                            if self.password_entry_manager:
                                self.password_entry_manager.handle_joystick_input(direction_map[direction])
                        else:
                            state_changed_by_action = self._route_action(action_name) or state_changed_by_action
                    elif self.current_state == STATE_SCHEMATICS and not self.schematics_pause_menu_active:
                        # Special handling for joystick in schematics view
                        state_changed_by_action = self._handle_schematics_joystick_input(result) or state_changed_by_action
                    else:
                        state_changed_by_action = self._route_action(action_name) or state_changed_by_action

            elif event_type == 'JOYSTICK_UP_HELD':
                if self.current_state == STATE_PONG_ACTIVE:
                    self.game_manager.handle_pong_input(app_config.INPUT_ACTION_PREV)
                elif self.current_state == STATE_BREAKOUT_ACTIVE:
                    self.game_manager.handle_breakout_input(app_config.INPUT_ACTION_PREV)
                elif self.current_state == STATE_SNAKE_ACTIVE:
                    self.game_manager.handle_snake_input(app_config.INPUT_ACTION_PREV)
                elif self.current_state == STATE_SCHEMATICS and not self.schematics_pause_menu_active:
                    # Joystick UP held = Zoom In
                    self.schematics_manager.zoom_in(fast=True)
                    state_changed_by_action = True
            
            elif event_type == 'JOYSTICK_DOWN_HELD':
                if self.current_state == STATE_PONG_ACTIVE:
                    self.game_manager.handle_pong_input(app_config.INPUT_ACTION_NEXT)
                elif self.current_state == STATE_BREAKOUT_ACTIVE:
                    self.game_manager.handle_breakout_input(app_config.INPUT_ACTION_NEXT)
                elif self.current_state == STATE_SNAKE_ACTIVE:
                    self.game_manager.handle_snake_input(app_config.INPUT_ACTION_NEXT)
                elif self.current_state == STATE_SCHEMATICS and not self.schematics_pause_menu_active:
                    # Joystick DOWN held = Zoom Out
                    self.schematics_manager.zoom_out(fast=True)
                    state_changed_by_action = True

            elif event_type == 'JOYSTICK_MIDDLE_PRESS':
                self.input_manager.handle_joystick_press()
            
            elif event_type == 'JOYSTICK_MIDDLE_RELEASE':
                release_event = self.input_manager.handle_joystick_release()
                press_duration = release_event.get('press_duration', 0)
                
                current_state_before_select = self.current_state

                if (current_state_before_select == STATE_MENU and 
                    self.menu_manager.get_current_menu_index(STATE_MENU) == self.menu_manager.get_settings_main_menu_idx() and
                    press_duration >= self.config.CURRENT_SECRET_COMBO_DURATION):
                    logger.debug("Joystick long press for secret menu (on Settings item) handled by update()")
                elif current_state_before_select != STATE_SECRET_GAMES: 
                    logger.info(f"Joystick short press: Processing SELECT in {current_state_before_select}")
                    
                    if state_changed_by_action:
                        logger.info("State already changed in this input cycle. Skipping SELECT action.")
                    else:
                        state_changed_by_action = self._route_action(app_config.INPUT_ACTION_SELECT) or state_changed_by_action

            elif event_type == 'MOUSEDOWN':
                button = result.get('button')
                self.input_manager.handle_mousedown(button)
                # Check for secret combo start (on main menu settings item) - same as keyboard
                if (self.current_state == STATE_MENU and
                    not self.input_manager.secret_combo_start_time and
                    self.input_manager.check_secret_combo_conditions(
                        self.current_state, 
                        self.menu_manager.get_current_menu_index(STATE_MENU)
                    )):
                    self.input_manager.start_secret_combo_timer()
                    
            elif event_type == 'MOUSEUP':
                button = result.get('button')
                mouseup_event = self.input_manager.handle_mouseup(button)

                if not self.input_manager.secret_combo_start_time:
                    action_name = result.get('action')
                    if action_name:
                        press_dur = mouseup_event.get('press_duration')
                        # Mouse left release: if this was a long press, BACK was already handled in update().
                        if (action_name == app_config.INPUT_ACTION_PREV and
                                button == self.config.MOUSE_LEFT):
                            if (press_dur is not None and
                                    press_dur >= getattr(self.config, 'INPUT_LONG_PRESS_DURATION', 2.0)):
                                pass  # skip routing PREV on release after long press
                            else:
                                state_changed_by_action = self._route_action(action_name) or state_changed_by_action
                        else:
                            state_changed_by_action = self._route_action(action_name) or state_changed_by_action
                
        return state_changed_by_action
        
    def _handle_key_release(self, key, action_name, key_event=None):
        """Handle key release events. key_event may contain press_duration, next_press_duration."""
        state_changed = False
        key_event = key_event or {}

        if self.current_state == STATE_PONG_ACTIVE and self.active_pong_game:
            if self.active_pong_game.game_over and action_name == app_config.INPUT_ACTION_PREV:
                state_changed = self._quit_pong_to_menu()
            elif action_name:
                game_result = self.game_manager.handle_pong_input(action_name)
                if game_result == "QUIT_TO_MENU":
                    state_changed = self._quit_pong_to_menu()
                elif game_result:
                    state_changed = True
        
        elif self.current_state == STATE_BREAKOUT_ACTIVE and self.active_breakout_game:
            if self.active_breakout_game.game_over and action_name == app_config.INPUT_ACTION_PREV:
                state_changed = self._quit_breakout_to_menu()
            elif action_name:
                game_result = self.game_manager.handle_breakout_input(action_name)
                if game_result == "QUIT_TO_MENU":
                    state_changed = self._quit_breakout_to_menu()
                elif game_result:
                    state_changed = True
        
        elif self.current_state == STATE_SNAKE_ACTIVE and self.active_snake_game:
            if self.active_snake_game.game_over and action_name == app_config.INPUT_ACTION_PREV:
                state_changed = self._quit_snake_to_menu()
            elif action_name:
                game_result = self.game_manager.handle_snake_input(action_name)
                if game_result == "QUIT_TO_MENU":
                    state_changed = self._quit_snake_to_menu()
                elif game_result:
                    state_changed = True

        elif self.current_state == STATE_TETRIS_ACTIVE and self.active_tetris_game:
            if self.active_tetris_game.game_over and action_name == app_config.INPUT_ACTION_PREV:
                state_changed = self._quit_tetris_to_menu()
            elif action_name:
                game_result = self.game_manager.handle_tetris_input(action_name)
                if game_result == "QUIT_TO_MENU":
                    state_changed = self._quit_tetris_to_menu()
                elif game_result:
                    state_changed = True
        
        # Special handling for schematics view - check rotation mode
        elif self.current_state == STATE_SCHEMATICS and not self.schematics_pause_menu_active:
            state_changed = self._handle_schematics_key_release(key, action_name)
        
        # General key releases for menu navigation or back action
        elif action_name == app_config.INPUT_ACTION_BACK:
            if self.current_state not in [STATE_MENU, STATE_PONG_ACTIVE, STATE_BREAKOUT_ACTIVE, STATE_SNAKE_ACTIVE, STATE_TETRIS_ACTIVE, STATE_SECRET_GAMES, STATE_SENSORS_MENU, STATE_SETTINGS, STATE_SCHEMATICS_CATEGORY, STATE_MEDIA_PLAYER, STATE_ST_WIKI]:
                state_changed = self.state_manager.return_to_previous()
                if not state_changed or not self.state_manager.previous_state:
                    state_changed = self.state_manager.return_to_menu()
        elif action_name:
            # PREV release: if this was a long press, BACK was already handled in update();
            # do not also route PREV on release (would cause extra "up one menu item" action).
            if action_name == app_config.INPUT_ACTION_PREV:
                press_dur = key_event.get("press_duration")
                if press_dur is not None and press_dur >= getattr(self.config, "INPUT_LONG_PRESS_DURATION", 2.0):
                    return state_changed
            state_changed = self._route_action(action_name)
                
        return state_changed
        
    def _handle_pong_joystick_input(self, action_name):
        """Handle joystick input specifically for Pong game."""
        game_result = self.game_manager.handle_pong_input(action_name)
        
        if game_result == "QUIT_TO_MENU":
            return self._quit_pong_to_menu()
        elif game_result:
            return True
        return False
        
    def _handle_breakout_joystick_input(self, action_name):
        """Handle joystick input specifically for Breakout game."""
        game_result = self.game_manager.handle_breakout_input(action_name)
        
        if game_result == "QUIT_TO_MENU":
            return self._quit_breakout_to_menu()
        elif game_result:
            return True
        return False
        
    def _handle_snake_joystick_input(self, action_name):
        """Handle joystick input specifically for Snake game."""
        game_result = self.game_manager.handle_snake_input(action_name)
        
        if game_result == "QUIT_TO_MENU":
            return self._quit_snake_to_menu()
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
        
    def _quit_breakout_to_menu(self):
        """Quit Breakout game and return to menu."""
        target_state = STATE_MENU
        if self.previous_state and self.previous_state != STATE_BREAKOUT_ACTIVE:
            target_state = self.previous_state
        self.game_manager.close_current_game()
        return self.state_manager.transition_to(target_state)
        
    def _quit_snake_to_menu(self):
        """Quit Snake game and return to menu."""
        target_state = STATE_MENU
        if self.previous_state and self.previous_state != STATE_SNAKE_ACTIVE:
            target_state = self.previous_state
        self.game_manager.close_current_game()
        return self.state_manager.transition_to(target_state)

    def _quit_tetris_to_menu(self):
        """Quit Tetris game and return to menu."""
        target_state = STATE_MENU
        if self.previous_state and self.previous_state != STATE_TETRIS_ACTIVE:
            target_state = self.previous_state
        self.game_manager.close_current_game()
        return self.state_manager.transition_to(target_state)

    def _handle_tetris_joystick_input(self, action_name):
        """Handle joystick input specifically for Tetris game."""
        game_result = self.game_manager.handle_tetris_input(action_name)
        if game_result == "QUIT_TO_MENU":
            return self._quit_tetris_to_menu()
        elif game_result:
            return True
        return False

    def _route_action(self, action):
        """Route an action to the appropriate handler using the input router."""
        return self.input_router.route_action(action, self.current_state)

    def update(self):
        """Update application state and check for timed events."""
        state_changed = False
        
        # Handle pending model loads (after loading screen is displayed)
        if self.loading_manager.has_pending_model_load() and self.current_state == STATE_LOADING:
            # Ensure loading screen is visible for at least a short time
            if not hasattr(self, '_loading_start_time'):
                self._loading_start_time = time.time()
                return True  # Keep showing loading screen
            
            # Wait at least 0.5 seconds before starting model load
            if time.time() - self._loading_start_time < 0.5:
                return True  # Keep showing loading screen
            
            pending_load = self.loading_manager.get_pending_model_load()
            schematics_model_key = pending_load['schematics_model_key']
            loading_operation = pending_load['loading_operation']
            
            try:
                # Perform the actual model loading with progress tracking
                # Don't use context manager to avoid blocking - manually manage progress
                loading_operation.current_step = 0
                loading_operation.loading_screen.update_progress(0.0, loading_operation.operation_name)
                
                success = self.schematics_manager.set_schematics_model(schematics_model_key, loading_operation)
                
                # Manually complete the loading operation
                loading_operation.loading_screen.update_progress(1.0, "Complete!")
                
                if success:
                    logger.info(f"Model '{schematics_model_key}' loaded successfully")
                else:
                    logger.warning(f"Failed to load model '{schematics_model_key}'")
                
                # Clear the pending load and transition to target state
                target_state = self.loading_manager.complete_loading_operation()
                if target_state:
                    # Clean up loading timing
                    if hasattr(self, '_loading_start_time'):
                        delattr(self, '_loading_start_time')
                    self.state_manager.transition_to(target_state)
                    state_changed = True
                
            except Exception as e:
                logger.error(f"Error during model loading: {e}")
                # On error, still complete the loading but log the issue
                target_state = self.loading_manager.complete_loading_operation()
                if target_state:
                    if hasattr(self, '_loading_start_time'):
                        delattr(self, '_loading_start_time')
                    self.state_manager.transition_to(target_state)
            
            return True  # State will change when loading completes
        
        # Check secret combo duration (only from main menu on settings item)
        if (self.current_state == STATE_MENU and
            self.input_manager.check_secret_combo_duration() and
            self.input_manager.check_secret_combo_conditions(
                self.current_state,
                self.menu_manager.get_current_menu_index(STATE_MENU)
            )):
            logger.info("Secret combo detected! Activating secret games menu")
            state_changed = self.state_manager.transition_to(STATE_SECRET_GAMES)
            # Ignore the follow-up key releases from the combo
            self.input_manager.suppress_combo_keyups()
            self.input_manager.reset_secret_combo()
            # Reset long press timer to prevent immediate exit
            self.input_manager.reset_long_press_timer()
            
        # Check joystick long press for secret menu (only from main menu on settings item)
        if (self.current_state == STATE_MENU and 
            self.menu_manager.get_current_menu_index(STATE_MENU) == self.menu_manager.get_settings_main_menu_idx() and
            self.input_manager.check_joystick_long_press(self.current_state)):
            logger.info("Joystick long press on Settings item detected! Activating secret games menu")
            state_changed = self.state_manager.transition_to(STATE_SECRET_GAMES)
            self.input_manager.reset_joystick_timer()
            # Reset long press timer to prevent immediate exit
            self.input_manager.reset_long_press_timer()
            
        if self.current_state == STATE_PONG_ACTIVE:
            self.game_manager.handle_continuous_pong_input(self.keys_held)
        elif self.current_state == STATE_BREAKOUT_ACTIVE:
            self.game_manager.handle_continuous_breakout_input(self.keys_held)
        # Snake doesn't need continuous input - it uses discrete turns
        elif self.current_state == STATE_TETRIS_ACTIVE:
            self.game_manager.update_tetris(self.keys_held)

        # Check KEY_PREV long press for back to menu / previous state
        if self.input_manager.check_long_press_duration():
            # If a secret combo is currently being timed (i.e., secret_combo_start_time is not None),
            # prioritize that and don't trigger the independent 'Back' action from KEY_PREV.
            if self.input_manager.secret_combo_start_time is None:
                # Special handling for schematics view based on rotation mode
                if self.current_state == STATE_SCHEMATICS and not self.schematics_pause_menu_active:
                    handled = self._handle_schematics_long_press('PREV')
                    if handled:
                        state_changed = True
                    self.input_manager.reset_long_press_timer(consumed_as_long_press=handled)
                else:
                    logger.info(f"KEY_PREV Long press detected in {self.current_state}.")
                    handled_by_back_action = self._route_action(app_config.INPUT_ACTION_BACK)
                    if not handled_by_back_action:
                        if self.current_state not in [STATE_MENU, STATE_PONG_ACTIVE, STATE_BREAKOUT_ACTIVE, STATE_SNAKE_ACTIVE, STATE_TETRIS_ACTIVE, STATE_SECRET_GAMES]:
                            logger.info(f"Long press in view state {self.current_state}, returning to previous or menu.")
                            state_changed = self.state_manager.return_to_previous()
                            if not state_changed or not self.state_manager.previous_state:
                                state_changed = self.state_manager.return_to_menu()
                    else:
                        state_changed = True
                    # Consumed so KEYUP does not route PREV (would move selection up one)
                    self.input_manager.reset_long_press_timer(consumed_as_long_press=True)
                
        # Check D key long press: 3D viewer = pause menu (media player uses A/D for volume, pause menu for rest)
        if self.input_manager.check_next_key_long_press():
            if (self.current_state == STATE_SCHEMATICS and 
                not self.schematics_pause_menu_active):
                handled = self._handle_schematics_long_press('NEXT')
                if handled:
                    state_changed = True
                self.input_manager.reset_next_key_timer()
        
        # Check zoom combos for schematics view (Return+A/D)
        if (self.current_state == STATE_SCHEMATICS and 
            not self.schematics_pause_menu_active):
            if self.input_manager.check_zoom_in_combo():
                # Return+D = Zoom In
                self.schematics_manager.zoom_in(fast=True)
                state_changed = True
            elif self.input_manager.check_zoom_out_combo():
                # Return+A = Zoom Out
                self.schematics_manager.zoom_out(fast=True)
                state_changed = True

        # Check mouse left button long press for back action
        if self.input_manager.check_mouse_left_long_press():
            if self.input_manager.secret_combo_start_time is None:
                # Special handling for schematics view based on rotation mode
                if self.current_state == STATE_SCHEMATICS and not self.schematics_pause_menu_active:
                    handled = self._handle_schematics_long_press('PREV')
                    if handled:
                        state_changed = True
                    self.input_manager.reset_mouse_left_timer(consumed_as_long_press=handled)
                else:
                    logger.info(f"Mouse left long press detected in {self.current_state}.")
                    handled_by_back_action = self._route_action(app_config.INPUT_ACTION_BACK)
                    if not handled_by_back_action:
                        if self.current_state not in [STATE_MENU, STATE_PONG_ACTIVE, STATE_BREAKOUT_ACTIVE, STATE_SNAKE_ACTIVE, STATE_TETRIS_ACTIVE, STATE_SECRET_GAMES]:
                            logger.info(f"Mouse left long press in view state {self.current_state}, returning to previous or menu.")
                            state_changed = self.state_manager.return_to_previous()
                            if not state_changed or not self.state_manager.previous_state:
                                state_changed = self.state_manager.return_to_menu()
                    else:
                        state_changed = True
                    # Consumed so MOUSEUP does not route PREV (would move selection up one)
                    self.input_manager.reset_mouse_left_timer(consumed_as_long_press=True)
                    
        # Check mouse right button long press for 3D viewer pause menu
        if (self.current_state == STATE_SCHEMATICS and 
            not self.schematics_pause_menu_active and 
            self.input_manager.check_mouse_right_long_press()):
            logger.info("Mouse right long press detected in schematics view - activating pause menu")
            self.schematics_pause_menu_active = True
            self.schematics_pause_menu_index = 0
            self.input_manager.reset_mouse_right_timer()
            state_changed = True
            
        # Check mouse middle button long press for secret menu (only from main menu on settings item)
        if (self.current_state == STATE_MENU and 
            self.menu_manager.get_current_menu_index(STATE_MENU) == self.menu_manager.get_settings_main_menu_idx() and
            self.input_manager.check_mouse_middle_long_press(self.current_state)):
            logger.info("Mouse middle long press on Settings item detected! Activating secret games menu")
            state_changed = self.state_manager.transition_to(STATE_SECRET_GAMES)
            self.input_manager.reset_mouse_middle_timer()
            # Reset long press timer to prevent immediate exit
            self.input_manager.reset_long_press_timer()

        return state_changed
    
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
        """Get current menu index for the current state."""
        return self.menu_manager.get_current_menu_index(self.current_state)
    
    def start_loading_operation(self, target_state, operation_name="Loading", total_steps=3):
        """
        Start a loading operation with progress tracking.
        
        Args:
            target_state (str): State to transition to after loading
            operation_name (str): Name of the operation
            total_steps (int): Total number of loading steps
        """
        loading_operation = self.loading_manager.start_loading_operation(target_state, operation_name, total_steps)
        # Transition to loading state
        self.state_manager.transition_to(STATE_LOADING)
        return loading_operation
    
    def complete_loading_operation(self):
        """Complete the current loading operation and transition to target state."""
        return self.loading_manager.complete_loading_operation()
    
    def get_loading_screen(self):
        """Get the current loading screen instance."""
        return self.loading_manager.get_loading_screen()
    
    def is_loading(self):
        """Check if currently in loading state."""
        return self.current_state == STATE_LOADING

    def _handle_schematics_joystick_input(self, joystick_result):
        """Handle joystick input for schematics view based on rotation mode."""
        direction = joystick_result.get('direction')
        action_name = joystick_result.get('action')
        
        # Check if we're in manual mode
        is_manual_mode = not self.schematics_manager.auto_rotation_mode
        
        if is_manual_mode:
            # In manual mode, joystick directions control rotation
            if direction == 'left':
                self.schematics_manager.apply_manual_rotation('LEFT')
                logger.debug("Joystick LEFT: Manual rotation left")
                return True
            elif direction == 'right':
                self.schematics_manager.apply_manual_rotation('RIGHT')
                logger.debug("Joystick RIGHT: Manual rotation right")
                return True
            elif direction == 'up':
                self.schematics_manager.apply_manual_rotation('UP')
                logger.debug("Joystick UP: Manual rotation up")
                return True
            elif direction == 'down':
                self.schematics_manager.apply_manual_rotation('DOWN')
                logger.debug("Joystick DOWN: Manual rotation down")
                return True
            # For middle press, fall through to normal SELECT handling
            elif direction == 'middle':
                return self._route_action(app_config.INPUT_ACTION_SELECT)
        else:
            # In auto mode, use normal joystick behavior
            # But don't allow BACK from joystick left in auto mode either
            if action_name == app_config.INPUT_ACTION_BACK:
                # In auto mode, joystick left could go back
                logger.debug("Joystick LEFT: Back action in auto mode")
                return self._route_action(action_name)
            elif action_name:
                return self._route_action(action_name)
        
        return False
    
    def _handle_schematics_key_release(self, key, action_name):
        """Handle key release events specifically for schematics view."""
        # Check rotation mode
        is_manual_mode = not self.schematics_manager.auto_rotation_mode
        
        if is_manual_mode:
            # In manual mode, PREV/NEXT control rotation (keyboard, joystick, or mouse)
            if action_name == app_config.INPUT_ACTION_PREV:
                self.schematics_manager.apply_manual_rotation('LEFT')
                logger.debug("PREV released: Manual rotation LEFT")
                return True
            elif action_name == app_config.INPUT_ACTION_NEXT:
                self.schematics_manager.apply_manual_rotation('RIGHT')
                logger.debug("NEXT released: Manual rotation RIGHT")
                return True
            elif action_name == app_config.INPUT_ACTION_SELECT:
                # Enter key in manual mode - pass through to input router to activate pause menu
                logger.debug("Enter key released in manual mode - routing to input router")
                return self._route_action(action_name)
            elif action_name == app_config.INPUT_ACTION_BACK:
                # Emergency back only (shouldn't happen in normal manual operation)
                logger.debug("Emergency back action in manual mode")
                return self._route_action(action_name)
        else:
            # In auto mode, use normal key behavior
            if action_name:
                return self._route_action(action_name)
        
        return False
    
    def _handle_schematics_long_press(self, key_type):
        """Handle long press events for schematics view based on rotation mode."""
        is_manual_mode = not self.schematics_manager.auto_rotation_mode
        
        if is_manual_mode:
            # In manual mode, long press A/D should rotate up/down
            if key_type == 'PREV':  # Long press A
                self.schematics_manager.apply_manual_rotation('UP')
                logger.debug("Long press A: Manual rotation UP")
                return True
            elif key_type == 'NEXT':  # Long press D
                self.schematics_manager.apply_manual_rotation('DOWN')
                logger.debug("Long press D: Manual rotation DOWN")
                return True
        else:
            # In auto mode, long press A should go back
            if key_type == 'PREV':  # Long press A
                logger.info("Long press A in auto mode: Going back")
                return self._route_action(app_config.INPUT_ACTION_BACK)
            elif key_type == 'NEXT':  # Long press D
                # In auto mode, could activate pause menu or ignore
                logger.info("Long press D in auto mode: Activating pause menu")
                self.schematics_pause_menu_active = True
                self.schematics_pause_menu_index = 0
                return True
        
        return False