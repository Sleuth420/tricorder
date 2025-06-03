# --- models/input_router.py ---
# Routes input actions to appropriate managers based on current state

import logging
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
STATE_SCHEMATICS = "SCHEMATICS"
STATE_SCHEMATICS_MENU = "SCHEMATICS_MENU"
STATE_SETTINGS_WIFI = "SETTINGS_WIFI"
STATE_SETTINGS_BLUETOOTH = "SETTINGS_BLUETOOTH"
STATE_SETTINGS_DEVICE = "SETTINGS_DEVICE"
STATE_SETTINGS_DISPLAY = "SETTINGS_DISPLAY"
STATE_SELECT_COMBO_DURATION = "SELECT_COMBO_DURATION"
STATE_SETTINGS_WIFI_NETWORKS = "SETTINGS_WIFI_NETWORKS"
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
        elif current_state == STATE_SETTINGS:
            return self._handle_settings_main_menu_input(action)
        elif current_state == STATE_SETTINGS_DISPLAY:
            return self._handle_display_settings_input(action)
        elif current_state == STATE_SETTINGS_DEVICE:
            return self._handle_device_settings_input(action)
        elif current_state == STATE_SELECT_COMBO_DURATION:
            return self._handle_select_combo_duration_input(action)
        elif current_state in [STATE_CONFIRM_REBOOT, STATE_CONFIRM_SHUTDOWN, STATE_CONFIRM_RESTART_APP]:
            return self._handle_confirmation_input(action)
        elif current_state == STATE_SECRET_GAMES:
            return self._handle_secret_games_input(action)
        elif current_state in [STATE_DASHBOARD, STATE_SENSOR_VIEW, STATE_SYSTEM_INFO]:
            return self._handle_view_input(action)
        elif current_state == STATE_SCHEMATICS:
            return self._handle_schematics_input(action)
        elif current_state == STATE_SETTINGS_WIFI:
            return self._handle_wifi_settings_input(action)
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
        elif current_state == STATE_SETTINGS:
            return self._handle_settings_main_menu_back()
        elif current_state in [STATE_SETTINGS_WIFI, STATE_SETTINGS_BLUETOOTH, STATE_SETTINGS_DEVICE, STATE_SETTINGS_DISPLAY, STATE_SELECT_COMBO_DURATION, STATE_SETTINGS_WIFI_NETWORKS, STATE_WIFI_PASSWORD_ENTRY]:
            logger.info(f"BACK from {current_state}, returning to appropriate parent")
            if current_state == STATE_SELECT_COMBO_DURATION:
                return self.app_state.state_manager.transition_to(STATE_SETTINGS_DEVICE)
            elif current_state == STATE_SETTINGS_WIFI_NETWORKS:
                return self.app_state.state_manager.transition_to(STATE_SETTINGS_WIFI)
            elif current_state == STATE_WIFI_PASSWORD_ENTRY:
                return self.app_state.state_manager.transition_to(STATE_SETTINGS_WIFI_NETWORKS)
            else:
                return self.app_state.state_manager.transition_to(STATE_SETTINGS)
        elif current_state not in [STATE_MENU, STATE_PONG_ACTIVE, STATE_BREAKOUT_ACTIVE, STATE_SNAKE_ACTIVE]:
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
        elif selected_item.target_state == STATE_SCHEMATICS_MENU:
            # Schematics menu is also a submenu that needs proper initialization
            schematics_menu_items = self.app_state.menu_manager._generate_schematics_menu_items()
            self.app_state.menu_manager.enter_submenu(
                schematics_menu_items, STATE_MENU, STATE_SCHEMATICS_MENU)
            return self.app_state.state_manager.transition_to(STATE_SCHEMATICS_MENU)
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
        """Handle input for the Display Settings view."""
        result = self.app_state.settings_manager.handle_display_settings_input(action)
        if result == "GO_TO_MAIN_MENU":
            self.app_state.menu_manager.reset_to_main_menu()
            return self.app_state.state_manager.transition_to(STATE_MENU)
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
            elif result == "CONFIRM_REBOOT":
                return self.app_state.state_manager.transition_to(STATE_CONFIRM_REBOOT)
            elif result == "CONFIRM_SHUTDOWN":
                return self.app_state.state_manager.transition_to(STATE_CONFIRM_SHUTDOWN)
            elif result == "CONFIRM_RESTART_APP":
                return self.app_state.state_manager.transition_to(STATE_CONFIRM_RESTART_APP)
        return result

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
        
        if selected_item.action_name == app_config.ACTION_LAUNCH_PONG:
            if self.app_state.game_manager.launch_pong():
                return self.app_state.state_manager.transition_to(STATE_PONG_ACTIVE)
        elif selected_item.action_name == app_config.ACTION_LAUNCH_BREAKOUT:
            if self.app_state.game_manager.launch_breakout():
                return self.app_state.state_manager.transition_to(STATE_BREAKOUT_ACTIVE)
        elif selected_item.action_name == app_config.ACTION_LAUNCH_SNAKE:
            if self.app_state.game_manager.launch_snake():
                return self.app_state.state_manager.transition_to(STATE_SNAKE_ACTIVE)
        elif selected_item.action_name == app_config.ACTION_LAUNCH_TETRIS:
            pass 
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
                # Toggle pause menu (middle press)
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
                # Toggle pause menu (middle press)
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
            self.app_state.schematics_pause_menu_index = (self.app_state.schematics_pause_menu_index - 1) % 3
            return True
        elif action == app_config.INPUT_ACTION_NEXT:
            # Navigate down in pause menu
            self.app_state.schematics_pause_menu_index = (self.app_state.schematics_pause_menu_index + 1) % 3
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
            # Back to schematics menu
            self.app_state.schematics_pause_menu_active = False
            self.app_state.state_manager.transition_to(STATE_SCHEMATICS_MENU)
            logger.debug("Schematics: Returning to schematics menu")
            return True
        elif selected_index == 2:
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
                logger.info("WIFI_ACTION_BROWSE_NETWORKS received. Transitioning to network browsing.")
                self.app_state.wifi_manager.scan_networks()
                return self.app_state.state_manager.transition_to(STATE_SETTINGS_WIFI_NETWORKS)
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