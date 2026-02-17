# --- models/input_router.py ---
# Routes input actions to appropriate managers based on current state

import logging
import time
import config as app_config

logger = logging.getLogger(__name__)

# State constants
STATE_MENU = "MENU"
STATE_SENSORS_MENU = "SENSORS_MENU"
STATE_DASHBOARD = "DASHBOARD"
STATE_SENSOR_VIEW = "SENSOR"
STATE_SYSTEM_INFO = "SYSTEM"
STATE_SETTINGS = "SETTINGS"
STATE_SECRET_GAMES = "SECRET_GAMES"
STATE_PONG_ACTIVE = "PONG_ACTIVE"
STATE_BREAKOUT_ACTIVE = "BREAKOUT_ACTIVE"
STATE_SNAKE_ACTIVE = "SNAKE_ACTIVE"
STATE_TETRIS_ACTIVE = "TETRIS_ACTIVE"
STATE_SCHEMATICS = "SCHEMATICS"
STATE_SCHEMATICS_MENU = "SCHEMATICS_MENU"
STATE_SCHEMATICS_CATEGORY = "SCHEMATICS_CATEGORY"
STATE_MEDIA_PLAYER = "MEDIA_PLAYER"
STATE_ST_WIKI = "ST_WIKI"
STATE_SETTINGS_WIFI = "SETTINGS_WIFI"
STATE_SETTINGS_STAPI = "SETTINGS_STAPI"
STATE_SETTINGS_BLUETOOTH = "SETTINGS_BLUETOOTH"
STATE_SETTINGS_DEVICE = "SETTINGS_DEVICE"
STATE_SETTINGS_DISPLAY = "SETTINGS_DISPLAY"
STATE_SETTINGS_CONTROLS = "SETTINGS_CONTROLS"
STATE_SETTINGS_UPDATE = "SETTINGS_UPDATE"
STATE_SETTINGS_SOUND_TEST = "SETTINGS_SOUND_TEST"
STATE_SETTINGS_DEBUG = "SETTINGS_DEBUG"
STATE_SETTINGS_DEBUG_OVERLAY = "SETTINGS_DEBUG_OVERLAY"
STATE_SETTINGS_LOG_VIEWER = "SETTINGS_LOG_VIEWER"
STATE_SELECT_COMBO_DURATION = "SELECT_COMBO_DURATION"
STATE_SETTINGS_VOLUME = "SETTINGS_VOLUME"
STATE_DISPLAY_CYCLE_INTERVAL = "DISPLAY_CYCLE_INTERVAL"
STATE_SETTINGS_WIFI_NETWORKS = "SETTINGS_WIFI_NETWORKS"
STATE_SETTINGS_BLUETOOTH_DEVICES = "SETTINGS_BLUETOOTH_DEVICES"
STATE_WIFI_PASSWORD_ENTRY = "WIFI_PASSWORD_ENTRY"
STATE_CONFIRM_REBOOT = "CONFIRM_REBOOT"
STATE_CONFIRM_SHUTDOWN = "CONFIRM_SHUTDOWN"
STATE_CONFIRM_RESTART_APP = "CONFIRM_RESTART_APP"

class InputRouter:
    """Routes input actions to appropriate managers based on current state."""
    
    def __init__(self, app_state):
        """Initialize the input router with reference to app state."""
        self.app_state = app_state
        
    def route_action(self, action, current_state):
        """
        Route an action to the appropriate handler based on current state.
        
        Args:
            action (str): The input action to process
            current_state (str): The current application state
            
        Returns:
            bool or str: Result from the handler
        """
        logger.debug(f"Routing action '{action}' for state '{current_state}'")
        
        # Handle back action universally first
        if action == app_config.INPUT_ACTION_BACK:
            return self._handle_back_action(current_state)
            
        # Route to state-specific handlers
        if current_state == STATE_MENU:
            return self._handle_menu_input(action)
        elif current_state == STATE_SENSORS_MENU:
            return self._handle_sensors_menu_input(action)
        elif current_state == STATE_SCHEMATICS_MENU:
            return self._handle_schematics_menu_input(action)
        elif current_state == STATE_SCHEMATICS_CATEGORY:
            return self._handle_schematics_category_input(action)
        elif current_state == STATE_MEDIA_PLAYER:
            return self._handle_media_player_input(action)
        elif current_state == STATE_ST_WIKI:
            return self._handle_st_wiki_input(action)
        elif current_state == STATE_SETTINGS:
            return self._handle_settings_main_menu_input(action)
        elif current_state == STATE_SETTINGS_DISPLAY:
            return self._handle_display_settings_input(action)
        elif current_state == STATE_SETTINGS_DEVICE:
            return self._handle_device_settings_input(action)
        elif current_state == STATE_SETTINGS_CONTROLS:
            return self._handle_controls_settings_input(action)
        elif current_state == STATE_SETTINGS_UPDATE:
            return self._handle_update_settings_input(action)
        elif current_state == STATE_SETTINGS_STAPI:
            return self._handle_stapi_settings_input(action)
        elif current_state == STATE_SETTINGS_SOUND_TEST:
            return self._handle_sound_test_input(action)
        elif current_state == STATE_SETTINGS_DEBUG:
            return self._handle_debug_settings_input(action)
        elif current_state == STATE_SETTINGS_DEBUG_OVERLAY:
            return self._handle_debug_overlay_input(action)
        elif current_state == STATE_SETTINGS_LOG_VIEWER:
            return self._handle_log_viewer_input(action)
        elif current_state == STATE_SELECT_COMBO_DURATION:
            return self._handle_select_combo_duration_input(action)
        elif current_state == STATE_SETTINGS_VOLUME:
            return self._handle_volume_settings_input(action)
        elif current_state == STATE_DISPLAY_CYCLE_INTERVAL:
            return self._handle_display_cycle_interval_input(action)
        elif current_state in [STATE_CONFIRM_REBOOT, STATE_CONFIRM_SHUTDOWN, STATE_CONFIRM_RESTART_APP]:
            return self._handle_confirmation_input(action)
        elif current_state == STATE_SECRET_GAMES:
            return self._handle_secret_games_input(action)
        elif current_state == STATE_PONG_ACTIVE:
            return self._handle_pong_input(action)
        elif current_state == STATE_BREAKOUT_ACTIVE:
            return self._handle_breakout_input(action)
        elif current_state == STATE_SNAKE_ACTIVE:
            return self._handle_snake_input(action)
        elif current_state == STATE_TETRIS_ACTIVE:
            return self._handle_tetris_input(action)
        elif current_state in [STATE_DASHBOARD, STATE_SENSOR_VIEW, STATE_SYSTEM_INFO]:
            return self._handle_view_input(action)
        elif current_state == STATE_SCHEMATICS:
            return self._handle_schematics_input(action)
        elif current_state == STATE_SETTINGS_WIFI:
            return self._handle_wifi_settings_input(action)
        elif current_state == STATE_SETTINGS_BLUETOOTH:
            return self._handle_bluetooth_settings_input(action)
        elif current_state == STATE_SETTINGS_BLUETOOTH_DEVICES:
            return self._handle_bluetooth_devices_input(action)
        elif current_state == STATE_SETTINGS_WIFI_NETWORKS:
            return self._handle_wifi_networks_input(action)
        elif current_state == STATE_WIFI_PASSWORD_ENTRY:
            return self._handle_wifi_password_entry_input(action)
            
        logger.warning(f"No handler found for state '{current_state}' with action '{action}'")
        return False
        
    def _handle_back_action(self, current_state):
        """Handle back action based on current state."""
        if current_state == STATE_SECRET_GAMES:
            return self.app_state.state_manager.return_to_menu()
        elif current_state == STATE_SENSORS_MENU:
            return self._handle_sensors_menu_back()
        elif current_state == STATE_SCHEMATICS_MENU:
            return self._handle_schematics_menu_back()
        elif current_state == STATE_SCHEMATICS_CATEGORY:
            return self._handle_schematics_category_back()
        elif current_state == STATE_MEDIA_PLAYER:
            mgr = getattr(self.app_state, 'media_player_manager', None)
            if mgr and (mgr.is_playing() or mgr.is_paused()):
                # Stop playback so track list is visible; next Back goes to season list or exit
                mgr.stop()
                return True
            if mgr and not mgr.is_browsing_seasons():
                # In episode list: back goes to season list
                mgr.clear_season()
                return True
            if mgr:
                mgr.on_exit_view()
            return (self.app_state.state_manager.return_to_previous() or
                    self.app_state.state_manager.return_to_menu())
        elif current_state == STATE_ST_WIKI:
            from models.st_wiki_manager import VIEW_MODE_CATEGORY, VIEW_MODE_LIST, VIEW_MODE_DETAIL
            mgr = getattr(self.app_state, 'st_wiki_manager', None)
            if not mgr:
                return self.app_state.state_manager.transition_to(STATE_SCHEMATICS_CATEGORY)
            mode = mgr.get_view_mode()
            if mode == VIEW_MODE_DETAIL:
                mgr.back_from_detail()
                return True
            if mode == VIEW_MODE_LIST:
                mgr.back_from_list()
                return True
            return self.app_state.state_manager.transition_to(STATE_SCHEMATICS_CATEGORY)
        elif current_state == STATE_SETTINGS:
            return self._handle_settings_main_menu_back()
        elif current_state in [STATE_SETTINGS_WIFI, STATE_SETTINGS_BLUETOOTH, STATE_SETTINGS_DEVICE, STATE_SETTINGS_DISPLAY, STATE_SETTINGS_CONTROLS, STATE_SETTINGS_UPDATE, STATE_SETTINGS_STAPI, STATE_SETTINGS_SOUND_TEST, STATE_SETTINGS_DEBUG, STATE_SETTINGS_DEBUG_OVERLAY, STATE_SETTINGS_LOG_VIEWER, STATE_SELECT_COMBO_DURATION, STATE_SETTINGS_VOLUME, STATE_DISPLAY_CYCLE_INTERVAL, STATE_SETTINGS_WIFI_NETWORKS, STATE_SETTINGS_BLUETOOTH_DEVICES, STATE_WIFI_PASSWORD_ENTRY]:
            logger.info(f"BACK from {current_state}, returning to appropriate parent")
            if current_state == STATE_SELECT_COMBO_DURATION or current_state == STATE_SETTINGS_VOLUME:
                return self.app_state.state_manager.transition_to(STATE_SETTINGS_DEVICE)
            elif current_state == STATE_DISPLAY_CYCLE_INTERVAL:
                return self.app_state.state_manager.transition_to(STATE_SETTINGS_DISPLAY)
            elif current_state == STATE_SETTINGS_WIFI_NETWORKS:
                return self.app_state.state_manager.transition_to(STATE_SETTINGS_WIFI)
            elif current_state == STATE_SETTINGS_BLUETOOTH_DEVICES:
                return self.app_state.state_manager.transition_to(STATE_SETTINGS_BLUETOOTH)
            elif current_state == STATE_WIFI_PASSWORD_ENTRY:
                return self.app_state.state_manager.transition_to(STATE_SETTINGS_WIFI_NETWORKS)
            elif current_state == STATE_SETTINGS_DEBUG:
                return self.app_state.state_manager.transition_to(STATE_SETTINGS)
            else:
                return self.app_state.state_manager.transition_to(STATE_SETTINGS)
        elif current_state not in [STATE_MENU, STATE_PONG_ACTIVE, STATE_BREAKOUT_ACTIVE, STATE_SNAKE_ACTIVE, STATE_TETRIS_ACTIVE]:
            logger.info(f"BACK from {current_state} (general view), returning to previous or menu")
            return (self.app_state.state_manager.return_to_previous() or 
                   self.app_state.state_manager.return_to_menu())
        return False

    def _handle_menu_input(self, action):
        """Handle input for the main menu."""
        if action == app_config.INPUT_ACTION_NEXT:
            return self.app_state.menu_manager.navigate_next(STATE_MENU)
        elif action == app_config.INPUT_ACTION_PREV:
            return self.app_state.menu_manager.navigate_prev(STATE_MENU)
        elif action == app_config.INPUT_ACTION_SELECT:
            return self._handle_menu_select()
        return False

    def _handle_menu_select(self):
        """Handle main menu item selection."""
        selected_item = self.app_state.menu_manager.get_selected_item(STATE_MENU)
        if not selected_item:
            return False
            
        logger.info(f"Menu SELECT: item='{selected_item.name}', target='{selected_item.target_state}'")
        
        if selected_item.target_state == STATE_SENSORS_MENU:
            self.app_state.menu_manager.enter_submenu(
                self.app_state.menu_manager.sensors_menu_items, STATE_MENU, STATE_SENSORS_MENU)
            return self.app_state.state_manager.transition_to(STATE_SENSORS_MENU)
        elif selected_item.target_state == STATE_SETTINGS:
            self.app_state.menu_manager.enter_submenu(
                self.app_state.menu_manager.settings_menu_items, STATE_MENU, STATE_SETTINGS)
            return self.app_state.state_manager.transition_to(STATE_SETTINGS)
        elif selected_item.target_state == STATE_SCHEMATICS_CATEGORY:
            # Schematics category: Schematics (3D) | Media Player
            self.app_state.menu_manager.enter_submenu(
                self.app_state.menu_manager.schematics_category_menu_items, STATE_MENU, STATE_SCHEMATICS_CATEGORY)
            return self.app_state.state_manager.transition_to(STATE_SCHEMATICS_CATEGORY)
        elif selected_item.target_state:
            if selected_item.target_state == STATE_SENSOR_VIEW and selected_item.data:
                self.app_state.current_sensor = selected_item.data["sensor_type"]
                self.app_state._reset_view_state()
            elif selected_item.target_state == STATE_DASHBOARD:
                self.app_state._reset_view_state()
            return self.app_state.state_manager.transition_to(selected_item.target_state)
        return False

    def _handle_sensors_menu_input(self, action):
        """Handle input for the sensors submenu."""
        if action == app_config.INPUT_ACTION_NEXT:
            return self.app_state.menu_manager.navigate_next(STATE_SENSORS_MENU)
        elif action == app_config.INPUT_ACTION_PREV:
            return self.app_state.menu_manager.navigate_prev(STATE_SENSORS_MENU)
        elif action == app_config.INPUT_ACTION_SELECT:
            return self._handle_sensors_menu_select()
        return False

    def _handle_sensors_menu_select(self):
        """Handle sensors menu item selection."""
        selected_item = self.app_state.menu_manager.get_selected_item(STATE_SENSORS_MENU)
        if (selected_item and selected_item.target_state == STATE_SENSOR_VIEW and selected_item.data):
            self.app_state.current_sensor = selected_item.data["sensor_type"]
            self.app_state._reset_view_state()
            return self.app_state.state_manager.transition_to(STATE_SENSOR_VIEW)
        return False

    def _handle_sensors_menu_back(self):
        """Handle back navigation from sensors menu."""
        previous_menu_state_name = self.app_state.menu_manager.exit_submenu()
        if previous_menu_state_name:
            return self.app_state.state_manager.transition_to(previous_menu_state_name)
        return self.app_state.state_manager.return_to_menu()

    def _handle_schematics_menu_input(self, action):
        """Handle input for the schematics selection menu."""
        if action in [app_config.INPUT_ACTION_NEXT, app_config.INPUT_ACTION_PREV]:
            # Navigate the schematics menu
            if action == app_config.INPUT_ACTION_NEXT:
                self.app_state.menu_manager.navigate_next(STATE_SCHEMATICS_MENU)
            else:
                self.app_state.menu_manager.navigate_prev(STATE_SCHEMATICS_MENU)
            return True
        elif action == app_config.INPUT_ACTION_SELECT:
            return self._handle_schematics_menu_select()
        elif action == app_config.INPUT_ACTION_BACK:
            return self._handle_schematics_menu_back()
        return False

    def _handle_schematics_menu_select(self):
        """Handle selection in the schematics menu."""
        selected_item = self.app_state.menu_manager.get_selected_item(STATE_SCHEMATICS_MENU)
        if selected_item:
            if selected_item.target_state == STATE_MENU:
                # Back option selected - use submenu system
                logger.debug(f"Schematics menu: Back option selected, exiting submenu")
                previous_menu_state_name = self.app_state.menu_manager.exit_submenu()
                if previous_menu_state_name:
                    self.app_state.state_manager.transition_to(previous_menu_state_name)
                else:
                    self.app_state.state_manager.return_to_menu()
            elif selected_item.target_state == STATE_SCHEMATICS:
                # Schematics selected, store the selected schematics data and go to 3D viewer
                logger.debug(f"Schematics menu: Selected schematics '{selected_item.name}' with data {selected_item.data}")
                # Store selected schematics info in app state for the 3D viewer
                self.app_state.selected_schematics_data = selected_item.data
                
                # Check if this requires model loading
                if selected_item.data and 'schematics_model' in selected_item.data:
                    schematics_model_key = selected_item.data['schematics_model']
                    schematics_model = self.app_state.schematics_manager.schematics_models.get(schematics_model_key)
                    
                    # For complex models (OBJ files), use loading screen
                    if schematics_model and schematics_model.get('type') == 'opengl_model':
                        # Start loading operation
                        loading_op = self.app_state.start_loading_operation(
                            STATE_SCHEMATICS, 
                            f"Loading {selected_item.name}", 
                            3
                        )
                        
                        # Schedule the actual model loading for next frame
                        # This allows the loading screen to be displayed first
                        self.app_state.loading_manager.set_pending_model_load(schematics_model_key, loading_op)
                    else:
                        # For simple models, load directly
                        success = self.app_state.schematics_manager.set_schematics_model(schematics_model_key)
                        if success:
                            logger.info(f"Schematics model pre-set to '{schematics_model_key}' for smooth transition")
                        else:
                            logger.warning(f"Failed to pre-set schematics model '{schematics_model_key}'")
                        self.app_state.state_manager.transition_to(STATE_SCHEMATICS)
                else:
                    # No model specified, go directly to schematics
                    self.app_state.state_manager.transition_to(STATE_SCHEMATICS)
            return True
        return False

    def _handle_schematics_menu_back(self):
        """Handle back action in schematics menu."""
        logger.debug(f"Schematics menu: BACK action, exiting submenu")
        previous_menu_state_name = self.app_state.menu_manager.exit_submenu()
        if previous_menu_state_name:
            return self.app_state.state_manager.transition_to(previous_menu_state_name)
        return self.app_state.state_manager.return_to_menu()

    def _handle_schematics_category_input(self, action):
        """Handle input for the schematics category menu (Schematics | Media Player)."""
        if action == app_config.INPUT_ACTION_NEXT:
            return self.app_state.menu_manager.navigate_next(STATE_SCHEMATICS_CATEGORY)
        elif action == app_config.INPUT_ACTION_PREV:
            return self.app_state.menu_manager.navigate_prev(STATE_SCHEMATICS_CATEGORY)
        elif action == app_config.INPUT_ACTION_SELECT:
            return self._handle_schematics_category_select()
        return False

    def _handle_schematics_category_select(self):
        """Handle selection in the schematics category menu."""
        selected_item = self.app_state.menu_manager.get_selected_item(STATE_SCHEMATICS_CATEGORY)
        if not selected_item:
            return False
        if selected_item.target_state == STATE_MENU:
            previous_menu_state_name = self.app_state.menu_manager.exit_submenu()
            if previous_menu_state_name:
                return self.app_state.state_manager.transition_to(previous_menu_state_name)
            return self.app_state.state_manager.return_to_menu()
        elif selected_item.target_state == STATE_SCHEMATICS_MENU:
            schematics_menu_items = self.app_state.menu_manager._generate_schematics_menu_items()
            self.app_state.menu_manager.enter_submenu(
                schematics_menu_items, STATE_SCHEMATICS_CATEGORY, STATE_SCHEMATICS_MENU)
            return self.app_state.state_manager.transition_to(STATE_SCHEMATICS_MENU)
        elif selected_item.target_state == STATE_MEDIA_PLAYER:
            if hasattr(self.app_state, 'media_player_manager') and self.app_state.media_player_manager:
                self.app_state.media_player_manager.on_enter_view()
            return self.app_state.state_manager.transition_to(STATE_MEDIA_PLAYER)
        elif selected_item.target_state == STATE_ST_WIKI:
            return self.app_state.state_manager.transition_to(STATE_ST_WIKI)
        return False

    def _handle_schematics_category_back(self):
        """Handle back from schematics category menu."""
        previous_menu_state_name = self.app_state.menu_manager.exit_submenu()
        if previous_menu_state_name:
            return self.app_state.state_manager.transition_to(previous_menu_state_name)
        return self.app_state.state_manager.return_to_menu()

    def _handle_media_player_input(self, action):
        """Handle input: list = navigate; playing/paused = PREV/NEXT volume, SELECT = toggle play/pause; BACK handled in _handle_back_action."""
        mgr = getattr(self.app_state, 'media_player_manager', None)
        if not mgr:
            return False
        if action == app_config.INPUT_ACTION_BACK:
            return False

        # When playing or paused: PREV/NEXT = volume, SELECT = toggle play/pause (VLC + marquee only)
        if mgr.is_playing() or mgr.is_paused():
            if action == app_config.INPUT_ACTION_PREV:
                mgr.volume_down()
                return True
            if action == app_config.INPUT_ACTION_NEXT:
                mgr.volume_up()
                return True
            if action == app_config.INPUT_ACTION_SELECT:
                mgr.toggle_play_pause()
                return True
            return False

        # Track list (not playing): PREV/NEXT = list, SELECT = play or open season
        if action == app_config.INPUT_ACTION_PREV:
            return mgr.navigate_prev()
        if action == app_config.INPUT_ACTION_NEXT:
            return mgr.navigate_next()
        if action == app_config.INPUT_ACTION_SELECT:
            if mgr.is_browsing_seasons():
                folder = mgr.get_selected_season_folder()
                if folder:
                    mgr.set_season(folder)
                return True
            mgr.select_track(mgr.get_current_index())
            mgr.play()
            return True
        return False

    def _handle_st_wiki_input(self, action):
        """Handle input for Star Trek wiki: category list -> item list -> detail view. BACK handled in _handle_back_action."""
        from models.st_wiki_manager import VIEW_MODE_CATEGORY, VIEW_MODE_LIST, VIEW_MODE_DETAIL
        mgr = getattr(self.app_state, 'st_wiki_manager', None)
        if not mgr or not mgr.has_data():
            return False
        mode = mgr.get_view_mode()
        if action == app_config.INPUT_ACTION_PREV:
            if mode == VIEW_MODE_CATEGORY:
                mgr.navigate_prev_category()
            elif mode == VIEW_MODE_LIST:
                mgr.navigate_prev_item()
            else:
                mgr.navigate_detail_prev()
            return True
        if action == app_config.INPUT_ACTION_NEXT:
            if mode == VIEW_MODE_CATEGORY:
                mgr.navigate_next_category()
            elif mode == VIEW_MODE_LIST:
                mgr.navigate_next_item()
            else:
                mgr.navigate_detail_next()
            return True
        if action == app_config.INPUT_ACTION_SELECT:
            if mode == VIEW_MODE_CATEGORY:
                mgr.enter_list()
            elif mode == VIEW_MODE_LIST:
                mgr.enter_detail()
            return True
        return False

    def _handle_settings_main_menu_input(self, action):
        """Handle input for the main settings category menu."""
        if action == app_config.INPUT_ACTION_NEXT:
            return self.app_state.menu_manager.navigate_next(STATE_SETTINGS)
        elif action == app_config.INPUT_ACTION_PREV:
            return self.app_state.menu_manager.navigate_prev(STATE_SETTINGS)
        elif action == app_config.INPUT_ACTION_SELECT:
            return self._handle_settings_main_menu_select()
        return False

    def _handle_settings_main_menu_select(self):
        """Handle selection from the main settings category menu."""
        selected_item = self.app_state.menu_manager.get_selected_item(STATE_SETTINGS)
        if not selected_item or not selected_item.target_state:
            return False
        
        logger.info(f"Settings Menu SELECT: item='{selected_item.name}', target_state='{selected_item.target_state}'")
        
        if selected_item.target_state == STATE_MENU:
            self.app_state.menu_manager.reset_to_main_menu()
            
        return self.app_state.state_manager.transition_to(selected_item.target_state)

    def _handle_settings_main_menu_back(self):
        """Handle back navigation from the main settings category menu."""
        previous_menu_state_name = self.app_state.menu_manager.exit_submenu()
        if previous_menu_state_name:
            return self.app_state.state_manager.transition_to(previous_menu_state_name)
        return self.app_state.state_manager.return_to_menu()

    def _handle_display_settings_input(self, action):
        """Handle input for the Display Settings main menu."""
        result = self.app_state.settings_manager.handle_display_settings_input(action)
        if isinstance(result, str):
            if result == "DISPLAY_CYCLE_INTERVAL":
                return self.app_state.state_manager.transition_to(STATE_DISPLAY_CYCLE_INTERVAL)
            if result == "TOGGLE_LED_MATRIX":
                self.app_state.led_matrix_enabled = not self.app_state.led_matrix_enabled
                logger.info("LED matrix (lid open) %s", "on" if self.app_state.led_matrix_enabled else "off")
                return True
            if result == "GO_BACK":
                return self.app_state.state_manager.transition_to(STATE_SETTINGS)
        return result

    def _handle_device_settings_input(self, action):
        """Handle input for the Device Settings view."""
        result = self.app_state.device_manager.handle_device_settings_input(action)
        if isinstance(result, str):
            if result == "GO_TO_MAIN_MENU":
                self.app_state.menu_manager.reset_to_main_menu()
                return self.app_state.state_manager.transition_to(STATE_MENU)
            elif result == "SELECT_COMBO_DURATION":
                return self.app_state.state_manager.transition_to(STATE_SELECT_COMBO_DURATION)
            elif result == "VOLUME":
                return self.app_state.state_manager.transition_to(STATE_SETTINGS_VOLUME)
            elif result == "CONFIRM_REBOOT":
                return self.app_state.state_manager.transition_to(STATE_CONFIRM_REBOOT)
            elif result == "CONFIRM_SHUTDOWN":
                return self.app_state.state_manager.transition_to(STATE_CONFIRM_SHUTDOWN)
            elif result == "CONFIRM_RESTART_APP":
                return self.app_state.state_manager.transition_to(STATE_CONFIRM_RESTART_APP)
        return result

    def _handle_bluetooth_settings_input(self, action):
        """Handle input for the Bluetooth Settings view (toggle, devices, back)."""
        if not self.app_state.bluetooth_manager:
            return self.app_state.state_manager.transition_to(STATE_SETTINGS)

        result = self.app_state.bluetooth_manager.handle_input(action)
        if isinstance(result, str):
            from .bluetooth_manager import (
                BLUETOOTH_ACTION_TOGGLE,
                BLUETOOTH_ACTION_DEVICES,
                BLUETOOTH_ACTION_BACK_TO_SETTINGS,
            )
            if result == BLUETOOTH_ACTION_TOGGLE:
                self.app_state.bluetooth_manager.toggle_bluetooth()
                return True
            if result == BLUETOOTH_ACTION_DEVICES:
                return self.app_state.state_manager.transition_to(STATE_SETTINGS_BLUETOOTH_DEVICES)
            if result == BLUETOOTH_ACTION_BACK_TO_SETTINGS:
                return self.app_state.state_manager.transition_to(STATE_SETTINGS)
        return result

    def _handle_bluetooth_devices_input(self, action):
        """Handle input for the Bluetooth device list (scan, connect/disconnect, back)."""
        if not self.app_state.bluetooth_manager:
            return self.app_state.state_manager.transition_to(STATE_SETTINGS_BLUETOOTH)

        result = self.app_state.bluetooth_manager.handle_device_list_input(action)
        if isinstance(result, str):
            from .bluetooth_manager import (
                BLUETOOTH_ACTION_BACK_TO_BLUETOOTH,
                BLUETOOTH_ACTION_CONNECT_OR_DISCONNECT,
                BLUETOOTH_ACTION_SCAN_DEVICES,
            )
            if result == BLUETOOTH_ACTION_BACK_TO_BLUETOOTH:
                return self.app_state.state_manager.transition_to(STATE_SETTINGS_BLUETOOTH)
            if result == BLUETOOTH_ACTION_SCAN_DEVICES:
                loading_operation = self.app_state.start_loading_operation(
                    target_state=STATE_SETTINGS_BLUETOOTH_DEVICES,
                    operation_name="Scanning for devices",
                    total_steps=3,
                )
                def on_done():
                    target = self.app_state.complete_loading_operation()
                    if target:
                        self.app_state.state_manager.transition_to(target)
                self.app_state.bluetooth_manager.start_scan(on_done)
                return True
            if result == BLUETOOTH_ACTION_CONNECT_OR_DISCONNECT:
                dev = self.app_state.bluetooth_manager.get_selected_device()
                if dev:
                    mac = dev.get("mac")
                    if dev.get("connected"):
                        self.app_state.bluetooth_manager.disconnect_device(mac)
                    else:
                        self.app_state.bluetooth_manager.connect_device(mac)
                return True
        return result

    def _handle_controls_settings_input(self, action):
        """Handle input for the Controls Settings view."""
        if action == app_config.INPUT_ACTION_NEXT:
            return self.app_state.controls_manager.navigate_next()
        elif action == app_config.INPUT_ACTION_PREV:
            return self.app_state.controls_manager.navigate_prev()
        # Back action is handled by the universal back handler
        return False

    def _handle_update_settings_input(self, action):
        """Handle input for the Update Settings view."""
        result = self.app_state.update_manager.handle_update_input(action)
        if isinstance(result, str):
            if result == "GO_BACK":
                return self.app_state.state_manager.transition_to(STATE_SETTINGS)
            elif result == "START_APP_UPDATE":
                return self._start_app_update()
            elif result == "START_SYSTEM_UPDATE":
                return self._start_system_update()
        return result
    
    def _handle_sound_test_input(self, action):
        """Handle input for the Sound Test view."""
        # Check if we're in the dedicated audio test screen
        if hasattr(self.app_state, 'show_audio_test_screen') and self.app_state.show_audio_test_screen:
            return self._handle_audio_test_screen_input(action)
        
        # Check if we're in the audio diagnostics screen
        if hasattr(self.app_state, 'show_audio_diagnostics_screen') and self.app_state.show_audio_diagnostics_screen:
            return self._handle_audio_diagnostics_screen_input(action)
        
        # Handle the main sound test menu
        if action == app_config.INPUT_ACTION_NEXT:
            # Navigate down in sound test menu
            if not hasattr(self.app_state, 'sound_test_option_index'):
                self.app_state.sound_test_option_index = 0
            self.app_state.sound_test_option_index = (self.app_state.sound_test_option_index + 1) % 5
            return True
        elif action == app_config.INPUT_ACTION_PREV:
            # Navigate up in sound test menu
            if not hasattr(self.app_state, 'sound_test_option_index'):
                self.app_state.sound_test_option_index = 0
            self.app_state.sound_test_option_index = (self.app_state.sound_test_option_index - 1) % 5
            return True
        elif action == app_config.INPUT_ACTION_SELECT:
            # Handle sound test selection
            if not hasattr(self.app_state, 'sound_test_option_index'):
                self.app_state.sound_test_option_index = 0
            
            if self.app_state.sound_test_option_index == 0:  # Advanced Audio Test
                self.app_state.show_audio_test_screen = True
                logger.info("Entering advanced audio test screen")
                return True
            elif self.app_state.sound_test_option_index == 1:  # Quick Test Sound
                if self.app_state.audio_manager:
                    self.app_state.audio_manager.play_sound('test_sound')
                    logger.info("Playing quick test sound")
                return True
            elif self.app_state.sound_test_option_index == 2:  # Audio Status Info
                self.app_state.show_audio_diagnostics_screen = True
                logger.info("Entering audio diagnostics screen")
                return True
            elif self.app_state.sound_test_option_index == 3:  # Stop Music
                if self.app_state.audio_manager:
                    self.app_state.audio_manager.stop_music()
                    logger.info("Stopped music")
                return True
            elif self.app_state.sound_test_option_index == 4:  # Back to Settings
                return self.app_state.state_manager.transition_to(STATE_SETTINGS)
        return False
    
    def _handle_audio_diagnostics_screen_input(self, action):
        """Handle input for the audio diagnostics screen."""
        if action == app_config.INPUT_ACTION_BACK:
            # Return to sound test menu
            self.app_state.show_audio_diagnostics_screen = False
            logger.info("Returning to sound test menu from diagnostics")
            return True
        elif action == app_config.INPUT_ACTION_SELECT:
            # Also handle SELECT as back for consistency
            self.app_state.show_audio_diagnostics_screen = False
            logger.info("Returning to sound test menu from diagnostics (SELECT)")
            return True
        return False
    
    def _handle_audio_test_screen_input(self, action):
        """Handle input for the dedicated audio test screen."""
        if not hasattr(self.app_state, 'audio_test_screen'):
            return False
            
        audio_test = self.app_state.audio_test_screen
        
        if action == app_config.INPUT_ACTION_BACK:
            # Return to sound test menu
            audio_test.stop_test()
            self.app_state.show_audio_test_screen = False
            logger.info("Returned to sound test menu (BACK)")
            return True
        elif action == app_config.INPUT_ACTION_NEXT:
            # Navigate down in audio test screen
            audio_test.selected_option = (audio_test.selected_option + 1) % 4
            return True
        elif action == app_config.INPUT_ACTION_PREV:
            # Navigate up in audio test screen
            audio_test.selected_option = (audio_test.selected_option - 1) % 4
            return True
        elif action == app_config.INPUT_ACTION_SELECT:
            # Handle audio test screen selection
            if audio_test.selected_option == 0:  # Play/Stop Test
                if audio_test.is_playing:
                    audio_test.stop_test()
                    if self.app_state.audio_manager:
                        self.app_state.audio_manager.stop_music()
                    logger.info("Stopped audio test")
                else:
                    audio_test.start_test()
                    if self.app_state.audio_manager:
                        self.app_state.audio_manager.play_sound('test_sound')
                        self.app_state.audio_manager.set_volume(audio_test.volume)
                    logger.info("Started audio test")
                return True
            elif audio_test.selected_option == 1:  # Volume Up
                audio_test.volume = min(1.0, audio_test.volume + 0.1)
                if self.app_state.audio_manager:
                    self.app_state.audio_manager.set_volume(audio_test.volume)
                logger.info(f"Volume increased to {int(audio_test.volume * 100)}%")
                return True
            elif audio_test.selected_option == 2:  # Volume Down
                audio_test.volume = max(0.0, audio_test.volume - 0.1)
                if self.app_state.audio_manager:
                    self.app_state.audio_manager.set_volume(audio_test.volume)
                logger.info(f"Volume decreased to {int(audio_test.volume * 100)}%")
                return True
            elif audio_test.selected_option == 3:  # Back to Sound Test Menu
                audio_test.stop_test()
                self.app_state.show_audio_test_screen = False
                logger.info("Returned to sound test menu (SELECT)")
                return True
        return False
    
    def _handle_stapi_settings_input(self, action):
        """Handle input for Star Trek Data settings: Fetch data (runs script in background) or Back."""
        if not hasattr(self.app_state, "stapi_settings_index"):
            self.app_state.stapi_settings_index = 0
        idx = self.app_state.stapi_settings_index
        menu_len = 2  # "Fetch Star Trek Data", "<- Back"
        if action == app_config.INPUT_ACTION_NEXT:
            self.app_state.stapi_settings_index = (idx + 1) % menu_len
            return True
        if action == app_config.INPUT_ACTION_PREV:
            self.app_state.stapi_settings_index = (idx - 1 + menu_len) % menu_len
            return True
        if action == app_config.INPUT_ACTION_SELECT:
            if idx == 0:
                return self._start_stapi_fetch()
            if idx == 1:
                return self.app_state.state_manager.transition_to(STATE_SETTINGS)
        return False

    def _start_stapi_fetch(self):
        """Run scripts/fetch_stapi_data.py in a background thread with loading screen."""
        loading_operation = self.app_state.start_loading_operation(
            STATE_SETTINGS_STAPI,
            "Fetching Star Trek Data",
            total_steps=5
        )

        def perform_fetch():
            try:
                import subprocess
                import sys
                from pathlib import Path
                project_root = Path(__file__).resolve().parent.parent
                script = project_root / "scripts" / "fetch_stapi_data.py"
                if not script.exists():
                    logger.error("STAPI fetch script not found: %s", script)
                    self.app_state.complete_loading_operation()
                    self.app_state.state_manager.transition_to(STATE_SETTINGS_STAPI)
                    return
                subprocess.run(
                    [sys.executable, str(script)],
                    cwd=str(project_root),
                    timeout=300,
                    capture_output=True,
                )
                if hasattr(self.app_state, "st_wiki_manager") and self.app_state.st_wiki_manager:
                    self.app_state.st_wiki_manager.reload()
            except subprocess.TimeoutExpired:
                logger.error("STAPI fetch timed out")
            except Exception as e:
                logger.exception("STAPI fetch failed: %s", e)
            finally:
                self.app_state.complete_loading_operation()
                self.app_state.state_manager.transition_to(STATE_SETTINGS_STAPI)

        import threading
        t = threading.Thread(target=perform_fetch)
        t.daemon = True
        t.start()
        return True

    def _handle_debug_settings_input(self, action):
        """Handle input for the Debug Settings menu (View Logs, Debug Overlay, Admin Timer, Back)."""
        if action == app_config.INPUT_ACTION_NEXT:
            if not hasattr(self.app_state, "debug_settings_option_index"):
                self.app_state.debug_settings_option_index = 0
            self.app_state.debug_settings_option_index = (self.app_state.debug_settings_option_index + 1) % 4
            return True
        elif action == app_config.INPUT_ACTION_PREV:
            if not hasattr(self.app_state, "debug_settings_option_index"):
                self.app_state.debug_settings_option_index = 0
            self.app_state.debug_settings_option_index = (self.app_state.debug_settings_option_index - 1 + 4) % 4
            return True
        elif action == app_config.INPUT_ACTION_SELECT:
            if not hasattr(self.app_state, "debug_settings_option_index"):
                self.app_state.debug_settings_option_index = 0
            idx = self.app_state.debug_settings_option_index
            if idx == 0:
                return self.app_state.state_manager.transition_to(STATE_SETTINGS_LOG_VIEWER)
            if idx == 1:
                return self.app_state.state_manager.transition_to(STATE_SETTINGS_DEBUG_OVERLAY)
            if idx == 2:
                # Toggle Admin Timer
                self.app_state.admin_timer_enabled = not self.app_state.admin_timer_enabled
                if self.app_state.admin_timer:
                    if self.app_state.admin_timer_enabled:
                        self.app_state.admin_timer.start()
                    else:
                        self.app_state.admin_timer.stop()
                logger.info("Admin timer %s", "ON" if self.app_state.admin_timer_enabled else "OFF")
                return True
            if idx == 3:
                return self.app_state.state_manager.transition_to(STATE_SETTINGS)
        return False

    def _handle_debug_overlay_input(self, action):
        """Handle input for the Debug Overlay settings view."""
        if action == app_config.INPUT_ACTION_NEXT:
            # Navigate down in debug overlay menu
            if not hasattr(self.app_state, 'debug_overlay_option_index'):
                self.app_state.debug_overlay_option_index = 0
            self.app_state.debug_overlay_option_index = (self.app_state.debug_overlay_option_index + 1) % 3
            return True
        elif action == app_config.INPUT_ACTION_PREV:
            # Navigate up in debug overlay menu
            if not hasattr(self.app_state, 'debug_overlay_option_index'):
                self.app_state.debug_overlay_option_index = 0
            self.app_state.debug_overlay_option_index = (self.app_state.debug_overlay_option_index - 1) % 3
            return True
        elif action == app_config.INPUT_ACTION_SELECT:
            # Handle debug overlay selection
            if not hasattr(self.app_state, 'debug_overlay_option_index'):
                self.app_state.debug_overlay_option_index = 0
            
            if self.app_state.debug_overlay_option_index == 0:  # Toggle Debug Overlay
                # Toggle debug overlay state
                self.app_state.debug_overlay.set_enabled(not self.app_state.debug_overlay.enabled)
                logger.info(f"Debug overlay {'enabled' if self.app_state.debug_overlay.enabled else 'disabled'}")
                return True
            elif self.app_state.debug_overlay_option_index == 1:  # Back to Settings
                return self.app_state.state_manager.transition_to(STATE_SETTINGS)
        return False
    
    def _handle_log_viewer_input(self, action):
        """Handle input for the Log Viewer."""
        if action == app_config.INPUT_ACTION_NEXT:
            # Scroll down in log viewer
            if not hasattr(self.app_state, 'log_viewer_scroll_index'):
                self.app_state.log_viewer_scroll_index = 0
            self.app_state.log_viewer_scroll_index += 1
            return True
        elif action == app_config.INPUT_ACTION_PREV:
            # Scroll up in log viewer
            if not hasattr(self.app_state, 'log_viewer_scroll_index'):
                self.app_state.log_viewer_scroll_index = 0
            self.app_state.log_viewer_scroll_index = max(0, self.app_state.log_viewer_scroll_index - 1)
            return True
        elif action == app_config.INPUT_ACTION_BACK:
            # Go back to settings
            return self.app_state.state_manager.transition_to(STATE_SETTINGS)
        return False
    
    def _start_app_update(self):
        """Start the application update process with loading screen."""
        # Start loading operation
        loading_operation = self.app_state.start_loading_operation(
            STATE_SETTINGS_UPDATE, 
            "Updating Application",
            total_steps=7
        )
        
        # Run the update in the background
        def perform_update():
            success = self.app_state.update_manager.perform_app_update(loading_operation)
            
            # Complete loading operation
            self.app_state.complete_loading_operation()
            
            if success:
                # Restart application after successful update
                self.app_state.update_manager.restart_application()
            else:
                # Stay in update menu to show results
                return self.app_state.state_manager.transition_to(STATE_SETTINGS_UPDATE)
        
        # Start update process
        import threading
        update_thread = threading.Thread(target=perform_update)
        update_thread.daemon = True
        update_thread.start()
        
        return True
    
    def _start_system_update(self):
        """Start the system update process with loading screen."""
        # Start loading operation
        loading_operation = self.app_state.start_loading_operation(
            STATE_SETTINGS_UPDATE, 
            "Updating System",
            total_steps=6
        )
        
        # Run the update in the background
        def perform_update():
            success = self.app_state.update_manager.perform_system_update(loading_operation)
            
            # Complete loading operation
            self.app_state.complete_loading_operation()
            
            if success:
                # Restart application after successful update
                self.app_state.update_manager.restart_application()
            else:
                # Stay in update menu to show results
                return self.app_state.state_manager.transition_to(STATE_SETTINGS_UPDATE)
        
        # Start update process
        import threading
        update_thread = threading.Thread(target=perform_update)
        update_thread.daemon = True
        update_thread.start()
        
        return True

    def _handle_confirmation_input(self, action):
        """Handle confirmation input."""
        result = self.app_state.device_manager.handle_confirmation_input(action)
        if result == "BACK_TO_DEVICE_SETTINGS":
            return self.app_state.state_manager.transition_to(STATE_SETTINGS_DEVICE)
        return result

    def _handle_secret_games_input(self, action):
        """Handle input for the secret games menu."""
        if action == app_config.INPUT_ACTION_NEXT:
            return self.app_state.menu_manager.navigate_next(STATE_SECRET_GAMES)
        elif action == app_config.INPUT_ACTION_PREV:
            return self.app_state.menu_manager.navigate_prev(STATE_SECRET_GAMES)
        elif action == app_config.INPUT_ACTION_SELECT:
            return self._handle_secret_games_select()
        return False

    def _handle_secret_games_select(self):
        """Handle secret games menu selection."""
        selected_item = self.app_state.menu_manager.get_selected_item(STATE_SECRET_GAMES)
        if not selected_item:
            return False
            
        logger.info(f"Secret Menu SELECT: {selected_item.name}")
        
        ui_scaler = getattr(self.app_state, 'ui_scaler', None)
        if selected_item.action_name == app_config.ACTION_LAUNCH_PONG:
            if self.app_state.game_manager.launch_pong(ui_scaler):
                return self.app_state.state_manager.transition_to(STATE_PONG_ACTIVE)
        elif selected_item.action_name == app_config.ACTION_LAUNCH_BREAKOUT:
            if self.app_state.game_manager.launch_breakout(ui_scaler):
                return self.app_state.state_manager.transition_to(STATE_BREAKOUT_ACTIVE)
        elif selected_item.action_name == app_config.ACTION_LAUNCH_SNAKE:
            if self.app_state.game_manager.launch_snake(ui_scaler):
                return self.app_state.state_manager.transition_to(STATE_SNAKE_ACTIVE)
        elif selected_item.action_name == app_config.ACTION_LAUNCH_TETRIS:
            if self.app_state.game_manager.launch_tetris(ui_scaler):
                return self.app_state.state_manager.transition_to(STATE_TETRIS_ACTIVE)
        elif selected_item.action_name == app_config.ACTION_RETURN_TO_MENU:
            return self.app_state.state_manager.return_to_menu()
        return False

    def _handle_view_input(self, action):
        """Handle SELECT action for view states to freeze/unfreeze."""
        if action == app_config.INPUT_ACTION_SELECT:
            self.app_state.is_frozen = not self.app_state.is_frozen
            if self.app_state.current_state == STATE_DASHBOARD:
                self.app_state.auto_cycle = not self.app_state.auto_cycle
            logger.info(f"View State '{self.app_state.current_state}': {'Frozen' if self.app_state.is_frozen else 'Unfrozen'}. Auto-cycle: {self.app_state.auto_cycle if self.app_state.current_state == STATE_DASHBOARD else 'N/A'}")
            return True
        return False

    def _handle_schematics_input(self, action):
        """Handle input for the 3D schematics viewer."""
        logger.debug(f"Schematics input received: action='{action}'")
        
        # Check if pause menu is active
        if self.app_state.schematics_pause_menu_active:
            logger.debug("Pause menu is active, delegating to pause menu handler")
            return self._handle_schematics_pause_menu_input(action)
        
        # Check if we're in manual or auto rotation mode
        is_manual_mode = not self.app_state.schematics_manager.auto_rotation_mode
        logger.debug(f"Rotation mode: {'Manual' if is_manual_mode else 'Auto'}")
        
        if is_manual_mode:
            # Manual mode: A/D control rotation, long press A/D control up/down rotation
            if action == app_config.INPUT_ACTION_PREV:
                # Left rotation (A key)
                logger.debug("Manual mode: A key - applying LEFT rotation")
                self.app_state.schematics_manager.apply_manual_rotation('LEFT')
                return True
            elif action == app_config.INPUT_ACTION_NEXT:
                # Right rotation (D key)
                logger.debug("Manual mode: D key - applying RIGHT rotation")
                self.app_state.schematics_manager.apply_manual_rotation('RIGHT')
                return True
            elif action == app_config.INPUT_ACTION_SELECT:
                # Toggle pause menu (middle press) - but check for recent zoom combo activity
                if self.app_state.input_manager.is_zoom_combo_recently_active():
                    logger.debug("Manual mode: SELECT ignored due to recent zoom combo activity")
                    return True
                logger.info("Manual mode: SELECT (Enter) key - activating pause menu")
                self.app_state.schematics_pause_menu_active = True
                self.app_state.schematics_pause_menu_index = 0
                logger.debug("Schematics: Pause menu activated")
                return True
            elif action == app_config.INPUT_ACTION_BACK:
                # In manual mode, BACK only works as emergency fallback
                # Normal back should go through pause menu
                logger.debug("Schematics: Emergency BACK action in manual mode")
                self.app_state.state_manager.transition_to(STATE_SCHEMATICS_MENU)
                return True
        else:
            # Auto mode: Normal navigation behavior, manual rotation disabled
            if action == app_config.INPUT_ACTION_PREV:
                # In auto mode, A key does normal navigation (could be used for other purposes)
                # For now, we'll ignore it or handle it differently
                logger.debug("Schematics: PREV action in auto mode (ignored)")
                return True
            elif action == app_config.INPUT_ACTION_NEXT:
                # In auto mode, D key does normal navigation  
                logger.debug("Schematics: NEXT action in auto mode (ignored)")
                return True
            elif action == app_config.INPUT_ACTION_SELECT:
                # Toggle pause menu (middle press) - but check for recent zoom combo activity
                if self.app_state.input_manager.is_zoom_combo_recently_active():
                    logger.debug("Auto mode: SELECT ignored due to recent zoom combo activity")
                    return True
                self.app_state.schematics_pause_menu_active = True
                self.app_state.schematics_pause_menu_index = 0
                logger.debug("Schematics: Pause menu activated")
                return True
            elif action == app_config.INPUT_ACTION_BACK:
                # In auto mode, BACK works normally (long press A)
                logger.debug("Schematics: BACK action in auto mode, returning to schematics menu")
                self.app_state.state_manager.transition_to(STATE_SCHEMATICS_MENU)
                return True
        
        return False
    
    def _handle_schematics_pause_menu_input(self, action):
        """Handle input when the schematics pause menu is active."""
        if action == app_config.INPUT_ACTION_PREV:
            # Navigate up in pause menu
            self.app_state.schematics_pause_menu_index = (self.app_state.schematics_pause_menu_index - 1) % 6
            return True
        elif action == app_config.INPUT_ACTION_NEXT:
            # Navigate down in pause menu
            self.app_state.schematics_pause_menu_index = (self.app_state.schematics_pause_menu_index + 1) % 6
            return True
        elif action == app_config.INPUT_ACTION_SELECT:
            # Select pause menu option
            return self._handle_schematics_pause_menu_select()
        elif action == app_config.INPUT_ACTION_BACK:
            # Close pause menu
            self.app_state.schematics_pause_menu_active = False
            logger.debug("Schematics: Pause menu closed")
            return True
        return False
    
    def _handle_schematics_pause_menu_select(self):
        """Handle selection in the schematics pause menu."""
        selected_index = self.app_state.schematics_pause_menu_index
        
        if selected_index == 0:
            # Toggle rotation mode
            self.app_state.schematics_manager.toggle_rotation_mode()
            self.app_state.schematics_pause_menu_active = False
            logger.debug("Schematics: Rotation mode toggled, pause menu closed")
            return True
        elif selected_index == 1:
            # Zoom In
            self.app_state.schematics_manager.zoom_in()
            logger.debug("Schematics: Zoom in from pause menu")
            return True
        elif selected_index == 2:
            # Zoom Out
            self.app_state.schematics_manager.zoom_out()
            logger.debug("Schematics: Zoom out from pause menu")
            return True
        elif selected_index == 3:
            # Reset Zoom
            self.app_state.schematics_manager.reset_zoom()
            logger.debug("Schematics: Zoom reset from pause menu")
            return True
        elif selected_index == 4:
            # Back to schematics menu
            self.app_state.schematics_pause_menu_active = False
            self.app_state.state_manager.transition_to(STATE_SCHEMATICS_MENU)
            logger.debug("Schematics: Returning to schematics menu")
            return True
        elif selected_index == 5:
            # Resume/Close menu
            self.app_state.schematics_pause_menu_active = False
            logger.debug("Schematics: Pause menu closed, resuming")
            return True
        return False

    def _handle_select_combo_duration_input(self, action):
        """Handle combo duration input."""
        result = self.app_state.settings_manager.handle_combo_duration_input(action)
        if result and action == app_config.INPUT_ACTION_SELECT:
            return self.app_state.state_manager.transition_to(STATE_SETTINGS_DEVICE)
        return result

    def _handle_display_cycle_interval_input(self, action):
        """Handle Dashboard auto-cycle interval picker sub-screen."""
        result = self.app_state.settings_manager.handle_display_cycle_interval_input(action)
        if result == "BACK_TO_DISPLAY_SETTINGS":
            return self.app_state.state_manager.transition_to(STATE_SETTINGS_DISPLAY)
        return result

    def _handle_volume_settings_input(self, action):
        """Handle volume settings: Next = volume up, Prev = volume down."""
        if action != app_config.INPUT_ACTION_NEXT and action != app_config.INPUT_ACTION_PREV:
            return False
        am = getattr(self.app_state, "audio_manager", None)
        if not am or not am.enabled:
            return False
        vol = am.get_volume()
        step = 0.05
        if action == app_config.INPUT_ACTION_NEXT:
            vol = min(1.0, vol + step)
        else:
            vol = max(0.0, vol - step)
        am.set_volume(vol)
        logger.debug(f"Volume set to {int(vol * 100)}%")
        return True

    def _handle_wifi_settings_input(self, action):
        """Handle input for the WiFi Settings view."""
        if not self.app_state.wifi_manager:
            logger.error("WifiManager not initialized, cannot handle WiFi settings input.")
            return self.app_state.state_manager.transition_to(STATE_SETTINGS)

        wifi_manager_action_result = self.app_state.wifi_manager.handle_input(action)

        if isinstance(wifi_manager_action_result, str):
            from .wifi_manager import WIFI_ACTION_TOGGLE, WIFI_ACTION_BROWSE_NETWORKS, WIFI_ACTION_BACK_TO_SETTINGS
            
            if wifi_manager_action_result == WIFI_ACTION_TOGGLE:
                logger.info("WIFI_ACTION_TOGGLE received. Calling wifi_manager.toggle_wifi()")
                self.app_state.wifi_manager.toggle_wifi()
                return True
            elif wifi_manager_action_result == WIFI_ACTION_BROWSE_NETWORKS:
                logger.info("WIFI_ACTION_BROWSE_NETWORKS received. Starting loading screen.")
                # Start loading operation for network scanning
                loading_operation = self.app_state.start_loading_operation(
                    target_state=STATE_SETTINGS_WIFI_NETWORKS,
                    operation_name="Finding available networks",
                    total_steps=3
                )
                
                # Start network scan in background
                def scan_completion_callback():
                    # Complete the loading and transition to networks view
                    target = self.app_state.complete_loading_operation()
                    if target:
                        self.app_state.state_manager.transition_to(target)
                
                self.app_state.wifi_manager.start_background_scan(scan_completion_callback, loading_operation)
                return True
            elif wifi_manager_action_result == WIFI_ACTION_BACK_TO_SETTINGS:
                return self.app_state.state_manager.transition_to(STATE_SETTINGS)
            else:
                logger.warning(f"Unknown action string from WifiManager: {wifi_manager_action_result}")
                return False
        
        return wifi_manager_action_result

    def _handle_wifi_networks_input(self, action):
        """Handle input for the WiFi network browsing view."""
        if not self.app_state.wifi_manager:
            logger.error("WifiManager not initialized, cannot handle WiFi network browsing input.")
            return self.app_state.state_manager.transition_to(STATE_SETTINGS)

        wifi_manager_action_result = self.app_state.wifi_manager.handle_network_browsing_input(action)

        if isinstance(wifi_manager_action_result, str):
            from .wifi_manager import WIFI_ACTION_BACK_TO_WIFI, WIFI_ACTION_ENTER_PASSWORD
            
            if wifi_manager_action_result == WIFI_ACTION_BACK_TO_WIFI:
                return self.app_state.state_manager.transition_to(STATE_SETTINGS_WIFI)
            elif wifi_manager_action_result == WIFI_ACTION_ENTER_PASSWORD:
                selected_network = self.app_state.wifi_manager.get_selected_network_for_connection()
                if selected_network:
                    self.app_state.password_entry_manager.set_target_network(selected_network)
                    return self.app_state.state_manager.transition_to(STATE_WIFI_PASSWORD_ENTRY)
                else:
                    logger.error("No selected network for password entry")
                    return False
            else:
                logger.warning(f"Unknown action string from WifiManager: {wifi_manager_action_result}")
                return False
        
        return wifi_manager_action_result

    def _handle_wifi_password_entry_input(self, action):
        """Handle input for the WiFi password entry view."""
        if not self.app_state.password_entry_manager:
            logger.error("PasswordEntryManager not initialized, cannot handle password entry input.")
            return self.app_state.state_manager.transition_to(STATE_SETTINGS_WIFI)

        password_manager_result = self.app_state.password_entry_manager.handle_input(action)

        if isinstance(password_manager_result, str):
            if password_manager_result == 'ATTEMPT_CONNECTION':
                password = self.app_state.password_entry_manager.get_current_password()
                target_network = self.app_state.password_entry_manager.get_target_network()
                
                if target_network:
                    ssid = target_network.get('ssid', 'Unknown')
                    logger.info(f"Attempting WiFi connection to {ssid} with password")
                    success = self.app_state.wifi_manager.connect_to_network(ssid, password)
                    if success:
                        logger.info(f"Successfully connected to {ssid}")
                        return self.app_state.state_manager.transition_to(STATE_SETTINGS_WIFI)
                    else:
                        logger.error(f"Failed to connect to {ssid}")
                        return False
                else:
                    logger.error("No target network set for password entry")
                    return self.app_state.state_manager.transition_to(STATE_SETTINGS_WIFI_NETWORKS)
                    
            elif password_manager_result == 'CANCEL_PASSWORD_ENTRY':
                logger.info("Password entry cancelled")
                return self.app_state.state_manager.transition_to(STATE_SETTINGS_WIFI_NETWORKS)
            else:
                logger.warning(f"Unknown action string from PasswordEntryManager: {password_manager_result}")
                return False
        
        return password_manager_result 

    def _handle_pong_input(self, action):
        """Handle input for the Pong game."""
        if not self.app_state.active_pong_game:
            return False
            
        game_result = self.app_state.game_manager.handle_pong_input(action)
        if game_result == "QUIT_TO_MENU":
            return self.app_state.state_manager.return_to_menu()
        elif game_result:
            return True
        return False

    def _handle_breakout_input(self, action):
        """Handle input for the Breakout game."""
        if not self.app_state.active_breakout_game:
            return False
            
        game_result = self.app_state.game_manager.handle_breakout_input(action)
        if game_result == "QUIT_TO_MENU":
            return self.app_state.state_manager.return_to_menu()
        elif game_result:
            return True
        return False

    def _handle_snake_input(self, action):
        """Handle input for the Snake game."""
        if not self.app_state.active_snake_game:
            return False
            
        game_result = self.app_state.game_manager.handle_snake_input(action)
        if game_result == "QUIT_TO_MENU":
            return self.app_state.state_manager.return_to_menu()
        elif game_result:
            return True
        return False

    def _handle_tetris_input(self, action):
        """Handle input for the Tetris game."""
        if not self.app_state.active_tetris_game:
            return False
        game_result = self.app_state.game_manager.handle_tetris_input(action)
        if game_result == "QUIT_TO_MENU":
            return self.app_state.state_manager.return_to_menu()
        elif game_result:
            return True
        return False