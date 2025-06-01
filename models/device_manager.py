# --- models/device_manager.py ---
# Manages device actions and confirmation dialogs

import logging
import os
import platform
import sys
import pygame
import subprocess
import config as app_config

logger = logging.getLogger(__name__)

# Action Constants for Device Settings
ACTION_REBOOT_DEVICE = "REBOOT_DEVICE"
ACTION_SHUTDOWN_DEVICE = "SHUTDOWN_DEVICE"
ACTION_RESTART_APP = "RESTART_APP"

# Confirmation Options
CONFIRMATION_OPTIONS = ["Yes", "No"]

class DeviceManager:
    """Manages device actions and confirmation dialogs."""
    
    def __init__(self, config_module):
        """
        Initialize the device manager.
        
        Args:
            config_module: The configuration module
        """
        self.config = config_module
        
        # Import device action items
        from ui.views.settings.device_settings_view import DEVICE_ACTION_ITEMS
        self.device_action_items = DEVICE_ACTION_ITEMS
        
        # Device settings state
        self.device_settings_option_index = 0
        
        # Confirmation state
        self.confirmation_option_index = 0 
        self.pending_device_action = None

    def handle_device_settings_input(self, action):
        """Handle input for the Device Settings view."""
        state_changed = False
        if action == app_config.INPUT_ACTION_NEXT:
            self.device_settings_option_index = (self.device_settings_option_index + 1) % len(self.device_action_items)
            logger.debug(f"Device Settings NEXT: index={self.device_settings_option_index}, action='{self.device_action_items[self.device_settings_option_index]['name']}'")
            state_changed = True
        elif action == app_config.INPUT_ACTION_PREV:
            self.device_settings_option_index = (self.device_settings_option_index - 1 + len(self.device_action_items)) % len(self.device_action_items)
            logger.debug(f"Device Settings PREV: index={self.device_settings_option_index}, action='{self.device_action_items[self.device_settings_option_index]['name']}'")
            state_changed = True
        elif action == app_config.INPUT_ACTION_SELECT:
            return self.trigger_device_action()
        return state_changed

    def trigger_device_action(self):
        """Transitions to a confirmation state for the selected device action."""
        if not (0 <= self.device_settings_option_index < len(self.device_action_items)):
            logger.error(f"Invalid device_settings_option_index: {self.device_settings_option_index}")
            return False

        selected_action_details = self.device_action_items[self.device_settings_option_index]
        action_type = selected_action_details["action"]
        logger.info(f"Device action selected, transitioning to confirmation: {action_type}")

        if action_type == ACTION_REBOOT_DEVICE:
            self.pending_device_action = ACTION_REBOOT_DEVICE
            return "CONFIRM_REBOOT"
        elif action_type == ACTION_SHUTDOWN_DEVICE:
            self.pending_device_action = ACTION_SHUTDOWN_DEVICE
            return "CONFIRM_SHUTDOWN"
        elif action_type == ACTION_RESTART_APP:
            self.pending_device_action = ACTION_RESTART_APP
            return "CONFIRM_RESTART_APP"
        elif action_type == app_config.ACTION_SELECT_COMBO_DURATION:
            logger.info("Device Settings: Action Select Combo Duration selected.")
            return "SELECT_COMBO_DURATION"
        elif action_type == app_config.ACTION_GO_TO_MAIN_MENU:
            logger.info("Device Settings: Action Go To Main Menu selected.")
            return "GO_TO_MAIN_MENU"
        else:
            logger.warning(f"Unknown device action type for confirmation: {action_type}")
        return False

    def handle_confirmation_input(self, action):
        """Handle input for confirmation dialogs."""
        state_changed = False
        if action == app_config.INPUT_ACTION_NEXT or action == app_config.INPUT_ACTION_PREV:
            # Toggle between 0 (Yes) and 1 (No)
            self.confirmation_option_index = 1 - self.confirmation_option_index 
            logger.debug(f"Confirmation option toggled to: {CONFIRMATION_OPTIONS[self.confirmation_option_index]}")
            state_changed = True
        elif action == app_config.INPUT_ACTION_SELECT:
            if self.confirmation_option_index == 0:  # "Yes"
                if self.pending_device_action:
                    self.execute_pending_device_action()
                    return True
                else:
                    logger.warning("Confirmation selected (Yes), but no pending_device_action found.")
                    return "BACK_TO_DEVICE_SETTINGS"
            else:  # "No"
                logger.info("Device action cancelled (No selected).")
                self.pending_device_action = None
                return "BACK_TO_DEVICE_SETTINGS"
        elif action == app_config.INPUT_ACTION_BACK:
            logger.info("Device action cancelled (Back action).")
            self.pending_device_action = None
            return "BACK_TO_DEVICE_SETTINGS"
        return state_changed

    def execute_pending_device_action(self):
        """Execute the confirmed device action."""
        action_to_execute = self.pending_device_action
        if not action_to_execute:
            logger.error("Attempted to execute pending device action, but none was set.")
            return False

        logger.info(f"Executing confirmed device action: {action_to_execute}")
        self.pending_device_action = None

        if action_to_execute == ACTION_REBOOT_DEVICE:
            if platform.system() == "Linux":
                logger.warning("Device reboot initiated (Linux).")
                os.system("sudo reboot")
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif platform.system() == "Windows":
                logger.warning("Reboot action is disabled on Windows for safety in this application.")
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                return True
            return True

        elif action_to_execute == ACTION_SHUTDOWN_DEVICE:
            if platform.system() == "Linux":
                logger.warning("Device shutdown initiated (Linux).")
                os.system("sudo shutdown now")
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            elif platform.system() == "Windows":
                logger.warning("Shutdown action is disabled on Windows for safety in this application.")
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                return True
            return True

        elif action_to_execute == ACTION_RESTART_APP:
            logger.warning("Application restart initiated.")
            try:
                pygame.quit()
                
                if platform.system() == "Windows":
                    cmd = [sys.executable] + sys.argv
                    logger.info(f"Restarting (Windows) with: {cmd}")
                    subprocess.Popen(cmd, creationflags=subprocess.DETACHED_PROCESS)
                    sys.exit(0)
                else:
                    args = [sys.executable] + sys.argv 
                    logger.info(f"Restarting (Linux/Unix) with: os.execv({sys.executable}, {args})")
                    os.execv(sys.executable, args)
            except Exception as e:
                logger.error(f"Failed to restart application: {e}", exc_info=True)
                sys.exit(1)
            return True

        else:
            logger.warning(f"Unknown pending device action to execute: {action_to_execute}")
            return False

    def get_device_settings_info(self):
        """Get current device settings information for UI."""
        return {
            'options': self.device_action_items,
            'selected_index': self.device_settings_option_index,
            'selected_option': self.device_action_items[self.device_settings_option_index] if self.device_action_items else None
        }

    def get_confirmation_info(self):
        """Get current confirmation information for UI."""
        return {
            'options': CONFIRMATION_OPTIONS,
            'selected_index': self.confirmation_option_index,
            'selected_option': CONFIRMATION_OPTIONS[self.confirmation_option_index],
            'pending_action': self.pending_device_action
        } 