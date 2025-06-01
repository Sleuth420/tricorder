# --- models/wifi_manager.py ---
# Manages WiFi operations like toggling on/off, scanning, and connecting.

import logging
import platform
import subprocess
import re
import config as app_config

logger = logging.getLogger(__name__)

# WiFi action constants
WIFI_ACTION_TOGGLE = "WIFI_TOGGLE"
WIFI_ACTION_SCAN = "WIFI_SCAN"
WIFI_ACTION_CONNECT = "WIFI_CONNECT"
WIFI_ACTION_VIEW_SAVED = "WIFI_VIEW_SAVED"
WIFI_ACTION_BACK_TO_SETTINGS = "WIFI_BACK_TO_SETTINGS"


class WifiManager:
    """Manages WiFi operations directly using subprocess."""

    def __init__(self, config_module):
        """
        Initialize the WifiManager.

        Args:
            config_module: The application configuration module.
        """
        self.config = config_module
        self.wifi_status_str = "Unknown"  # e.g., "Enabled", "Disabled", "Unknown", "Error"
        self.last_known_enabled_state = None # True, False, or None
        self.wifi_interface_name = self._determine_wifi_interface_name()
        self.wifi_options = [
            {"name": f"Wi-Fi Status: {self.wifi_status_str} (Toggle)", "action": WIFI_ACTION_TOGGLE, "status_key": "wifi_status"},
            # {"name": "Scan for Networks", "action": WIFI_ACTION_SCAN}, # Future
            {"name": "<- Back to Settings", "action": WIFI_ACTION_BACK_TO_SETTINGS}
        ]
        self.selected_option_index = 0
        self.update_wifi_status() # Get initial status

    def _determine_wifi_interface_name(self):
        """Determines the Wi-Fi interface name based on the OS using subprocess."""
        system = platform.system()
        if system == "Windows":
            # For Windows, 'netsh interface show interface' can list interfaces.
            # We'll try a common default "Wi-Fi". A more robust method could parse this.
            # Example: Find line with "Wireless LAN adapter Wi-Fi:"
            try:
                result = subprocess.run(['netsh', 'interface', 'show', 'interface'], capture_output=True, text=True, check=True, creationflags=subprocess.CREATE_NO_WINDOW if system == "Windows" else 0)
                for line in result.stdout.splitlines():
                    if "wi-fi" in line.lower() and "wireless" in line.lower(): # Heuristic
                        match = re.search(r"Connect name:\s*(.*)", line, re.IGNORECASE)
                        if match and match.group(1).strip():
                            name = match.group(1).strip()
                            logger.info(f"Determined Windows Wi-Fi interface: '{name}'")
                            return name
                logger.warning("Could not determine exact Wi-Fi interface on Windows, defaulting to 'Wi-Fi'")
                return "Wi-Fi" # Common default
            except FileNotFoundError:
                logger.error("'netsh' command not found. Cannot determine Wi-Fi interface on Windows.")
                return "Wi-Fi" # Fallback
            except subprocess.CalledProcessError as e:
                logger.error(f"Error running 'netsh interface show interface': {e.stderr}")
                return "Wi-Fi" # Fallback
            except Exception as e:
                logger.error(f"Unexpected error determining Wi-Fi interface on Windows: {e}")
                return "Wi-Fi" # Fallback

        elif system == "Linux":
            try:
                # Use 'ip link' or 'nmcli dev status'
                result = subprocess.run(['nmcli', '-t', '-f', 'DEVICE,TYPE', 'device'], capture_output=True, text=True, check=True)
                for line in result.stdout.splitlines():
                    if "wifi" in line.lower():
                        parts = line.split(':')
                        if len(parts) > 0:
                            name = parts[0].strip()
                            logger.info(f"Automatically detected Wi-Fi interface (via nmcli): {name}")
                            return name
                # Fallback to ip link if nmcli fails or doesn't show wifi
                result = subprocess.run(['ip', '-o', 'link', 'show'], capture_output=True, text=True, check=True)
                for line in result.stdout.splitlines():
                    if 'wlan' in line or 'wlx' in line:
                        parts = line.split(':')
                        if len(parts) > 1:
                            name = parts[1].strip().split(' ')[0] # Get the name before any other info
                            logger.info(f"Automatically detected Wi-Fi interface (via ip link): {name}")
                            return name
                logger.warning("Could not auto-detect Wi-Fi interface name on Linux. Falling back to 'wlan0'.")
                return "wlan0"
            except FileNotFoundError:
                logger.error("'nmcli' or 'ip' command not found. Cannot determine Wi-Fi interface on Linux.")
                return "wlan0" # Fallback
            except subprocess.CalledProcessError as e:
                logger.error(f"Error determining Wi-Fi interface name on Linux: {e.stderr}")
                return "wlan0" # Fallback
            except Exception as e:
                logger.error(f"Unexpected error determining Wi-Fi interface on Linux: {e}")
                return "wlan0"

        logger.warning(f"Unsupported platform for Wi-Fi interface detection: {system}. Using 'default_wifi'.")
        return "default_wifi"

    def update_wifi_status(self):
        """
        Gets and updates the current WiFi status (Enabled/Disabled/Error/Unknown)
        and the internal boolean state `self.last_known_enabled_state`.
        This method directly calls subprocess.
        """
        system = platform.system()
        cmd_list = []
        self.wifi_status_str = "Checking..."

        if system == "Linux":
            if not self.wifi_interface_name: # Should have been determined by init
                logger.error("WiFi interface name not determined for Linux.")
                self.wifi_status_str = "Error: No Interface"
                self.last_known_enabled_state = None
                return
            # Check general radio status first
            cmd_list = ['nmcli', 'radio', 'wifi']
        elif system == "Windows":
            if not self.wifi_interface_name:
                logger.error("WiFi interface name not determined for Windows.")
                self.wifi_status_str = "Error: No Interface"
                self.last_known_enabled_state = None
                return
            cmd_list = ['netsh', 'interface', 'show', 'interface', f'name="{self.wifi_interface_name}"']
        else:
            logger.warning(f"WiFi status check not supported on platform: {system}")
            self.wifi_status_str = "Unsupported OS"
            self.last_known_enabled_state = None
            return

        try:
            logger.info(f"Executing for WiFi status: {' '.join(cmd_list)}")
            process = subprocess.run(cmd_list, capture_output=True, text=True, check=True, timeout=5, creationflags=subprocess.CREATE_NO_WINDOW if system == "Windows" else 0)
            stdout = process.stdout.strip()
            stderr = process.stderr.strip()

            if stderr: # Prioritize stderr for error indication
                logger.error(f"Error getting WiFi status. Command: {' '.join(cmd_list)}. Stderr: {stderr}")
                self.wifi_status_str = "Error (stderr)"
                self.last_known_enabled_state = None
            elif system == "Linux":
                if "enabled" in stdout.lower():
                    self.wifi_status_str = "Enabled"
                    self.last_known_enabled_state = True
                elif "disabled" in stdout.lower():
                    self.wifi_status_str = "Disabled"
                    self.last_known_enabled_state = False
                else:
                    self.wifi_status_str = "Unknown (nmcli)"
                    self.last_known_enabled_state = None
                    logger.warning(f"Unexpected nmcli output for wifi status: {stdout}")
            elif system == "Windows":
                # More robust regex to catch variations in spacing and capitalization for "Admin State"
                admin_state_enabled_match = re.search(r"Administrative state\s*:\s*Enabled", stdout, re.IGNORECASE)
                admin_state_disabled_match = re.search(r"Administrative state\s*:\s*Disabled", stdout, re.IGNORECASE)
                connect_state_connected_match = re.search(r"Connect state\s*:\s*Connected", stdout, re.IGNORECASE)

                if admin_state_enabled_match:
                    self.wifi_status_str = "Enabled"
                    self.last_known_enabled_state = True
                    # If admin state is enabled, but connect state is disconnected, it's still administratively enabled.
                    # We primarily care about the admin state for toggling.
                    if not connect_state_connected_match:
                        logger.info(f"Wi-Fi interface '{self.wifi_interface_name}' is Enabled but Disconnected.")
                elif admin_state_disabled_match:
                    self.wifi_status_str = "Disabled"
                    self.last_known_enabled_state = False
                else:
                    # Fallback or if admin state is not clearly enabled/disabled but other info exists
                    self.wifi_status_str = "Unknown (netsh)"
                    self.last_known_enabled_state = None
                    logger.warning(f"Could not determine admin state from netsh output for interface '{self.wifi_interface_name}'. Full output: {stdout}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed for WiFi status. Command: {' '.join(cmd_list)}. Error: {e}. Stdout: {e.stdout}. Stderr: {e.stderr}")
            self.wifi_status_str = "Error (Exec)"
            self.last_known_enabled_state = None
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out for WiFi status: {' '.join(cmd_list)}")
            self.wifi_status_str = "Error (Timeout)"
            self.last_known_enabled_state = None
        except FileNotFoundError:
            logger.error(f"Command not found for WiFi status: {cmd_list[0]}")
            self.wifi_status_str = "Error (No Cmd)"
            self.last_known_enabled_state = None
        except Exception as e:
            logger.critical(f"Unexpected error getting WiFi status. Command: {' '.join(cmd_list)}. Error: {e}", exc_info=True)
            self.wifi_status_str = "Error (Critical)"
            self.last_known_enabled_state = None
        finally:
            self._update_wifi_options_display()


    def toggle_wifi(self):
        """
        Toggles WiFi on or off using subprocess.
        Returns:
            bool: True if the command was attempted successfully (regardless of state change), False otherwise.
                  The actual state change should be confirmed by a subsequent call to update_wifi_status().
        """
        if self.last_known_enabled_state is None:
            logger.warning("Cannot toggle WiFi: current state is unknown. Please refresh status.")
            self.wifi_status_str = "Unknown (Toggle)"
            self._update_wifi_options_display()
            return False # Indicate that toggle wasn't truly attempted due to unknown state

        system = platform.system()
        cmd_list = []
        action_str = "on" if not self.last_known_enabled_state else "off"
        admin_action_str = "enable" if not self.last_known_enabled_state else "disable" # For netsh

        if system == "Linux":
            cmd_list = ['nmcli', 'radio', 'wifi', action_str]
        elif system == "Windows":
            if not self.wifi_interface_name:
                 logger.error("Cannot toggle WiFi on Windows: interface name not determined.")
                 return False
            cmd_list = ['netsh', 'interface', 'set', 'interface', f'name="{self.wifi_interface_name}"', f'admin={admin_action_str}']
        else:
            logger.warning(f"WiFi toggle not supported on platform: {system}")
            self.wifi_status_str = "Unsupported OS"
            self._update_wifi_options_display()
            return False

        try:
            logger.info(f"Executing WiFi toggle: {' '.join(cmd_list)}")
            # Indicate attempt to toggle
            self.wifi_status_str = "Toggling..."
            self._update_wifi_options_display() # Show "Toggling..." in UI

            process = subprocess.run(cmd_list, capture_output=True, text=True, check=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW if system == "Windows" else 0)
            logger.info(f"WiFi toggle command output: {process.stdout.strip()}")
            if process.stderr.strip():
                logger.warning(f"WiFi toggle command stderr: {process.stderr.strip()}")
            # After successful command, immediately update status to confirm
            self.update_wifi_status()
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Command failed for WiFi toggle. Command: {' '.join(cmd_list)}. Error: {e}. Stdout: {e.stdout}. Stderr: {e.stderr}")
            self.wifi_status_str = f"Error (Toggle Failed: {e.returncode})"
            self.last_known_enabled_state = None # State is uncertain
        except subprocess.TimeoutExpired:
            logger.error(f"Command timed out for WiFi toggle: {' '.join(cmd_list)}")
            self.wifi_status_str = "Error (Toggle Timeout)"
            self.last_known_enabled_state = None
        except FileNotFoundError:
            logger.error(f"Command not found for WiFi toggle: {cmd_list[0]}")
            self.wifi_status_str = "Error (No Cmd)"
            self.last_known_enabled_state = None
        except Exception as e:
            logger.critical(f"Unexpected error toggling WiFi. Command: {' '.join(cmd_list)}. Error: {e}", exc_info=True)
            self.wifi_status_str = "Error (Critical Toggle)"
            self.last_known_enabled_state = None
        finally:
            self._update_wifi_options_display() # Update display based on outcome
        return False


    def _update_wifi_options_display(self):
        """Updates the name of the toggle option based on current status string."""
        for option in self.wifi_options:
            if option["action"] == WIFI_ACTION_TOGGLE:
                option["name"] = f"Wi-Fi: {self.wifi_status_str} (Toggle)"
                break
        logger.debug(f"Updated WiFi display option to: {self.wifi_options[0]['name']}")


    def handle_input(self, action_from_app_state):
        """
        Handle input for the WiFi settings view.
        Args:
            action_from_app_state (str): The input action (e.g., app_config.INPUT_ACTION_NEXT).
        Returns:
            str or bool: An action string for AppState to process (like WIFI_ACTION_TOGGLE),
                         or True/False for simple navigation.
        """
        if action_from_app_state == app_config.INPUT_ACTION_NEXT:
            self.selected_option_index = (self.selected_option_index + 1) % len(self.wifi_options)
            return True
        elif action_from_app_state == app_config.INPUT_ACTION_PREV:
            self.selected_option_index = (self.selected_option_index - 1 + len(self.wifi_options)) % len(self.wifi_options)
            return True
        elif action_from_app_state == app_config.INPUT_ACTION_SELECT:
            selected_item_action = self.wifi_options[self.selected_option_index]["action"]
            logger.info(f"WiFi Settings: Selected option with action: {selected_item_action}")
            return selected_item_action # This action string (e.g., WIFI_ACTION_TOGGLE) will be returned to AppState
        return False

    def get_current_wifi_display_options(self):
        """Returns the options to be displayed in the UI."""
        # Ensure the status string in the options is up-to-date
        self._update_wifi_options_display()
        return self.wifi_options

    def get_selected_index(self):
        """Returns the currently selected option index."""
        return self.selected_option_index

    # --- Methods for future features (Scan, Connect, View Saved, Forget) will go here ---
    # def get_scan_wifi_command(self): ...
    # def process_scan_wifi_output(self, command_output_dict, app_state_notification_callback): ...
    # etc. 