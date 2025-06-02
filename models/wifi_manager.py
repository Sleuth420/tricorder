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
# New action constants for network browsing
WIFI_ACTION_BROWSE_NETWORKS = "WIFI_BROWSE_NETWORKS"
WIFI_ACTION_BACK_TO_WIFI = "WIFI_BACK_TO_WIFI"
WIFI_ACTION_CONNECT_TO_NETWORK = "WIFI_CONNECT_TO_NETWORK"
WIFI_ACTION_ENTER_PASSWORD = "WIFI_ENTER_PASSWORD"


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
            {"name": "Browse Networks", "action": WIFI_ACTION_BROWSE_NETWORKS},
            {"name": "<- Back to Settings", "action": WIFI_ACTION_BACK_TO_SETTINGS}
        ]
        self.selected_option_index = 0
        
        # Network browsing state
        self.available_networks = []  # List of scanned networks
        self.saved_networks = []      # List of saved network SSIDs
        self.scanning_in_progress = False
        self.network_selected_index = 0  # For network list navigation
        self.last_scan_error = None
        
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

    # --- Network Scanning and Management Methods ---
    
    def scan_networks(self):
        """
        Scan for available WiFi networks.
        Returns:
            bool: True if scan was initiated successfully, False otherwise.
        """
        if self.scanning_in_progress:
            logger.warning("Network scan already in progress")
            return False
            
        if not self.last_known_enabled_state:
            logger.warning("Cannot scan networks: WiFi is disabled")
            self.last_scan_error = "WiFi Disabled"
            return False
            
        self.scanning_in_progress = True
        self.last_scan_error = None
        self.available_networks = []
        
        system = platform.system()
        cmd_list = []
        
        try:
            if system == "Linux":
                # Use nmcli to scan and list networks
                cmd_list = ['nmcli', '-t', '-f', 'SSID,SIGNAL,SECURITY,IN-USE', 'device', 'wifi', 'list']
            elif system == "Windows":
                # Use netsh to scan networks
                cmd_list = ['netsh', 'wlan', 'show', 'profiles']
                # For available networks, we'll need a separate command
                scan_cmd = ['netsh', 'wlan', 'show', 'networks', 'mode=bssid']
            else:
                logger.warning(f"Network scanning not supported on platform: {system}")
                self.last_scan_error = "Unsupported OS"
                self.scanning_in_progress = False
                return False
                
            logger.info(f"Scanning for networks with command: {' '.join(cmd_list)}")
            
            if system == "Linux":
                process = subprocess.run(cmd_list, capture_output=True, text=True, check=True, timeout=15, 
                                       creationflags=subprocess.CREATE_NO_WINDOW if system == "Windows" else 0)
                self._parse_linux_networks(process.stdout)
            elif system == "Windows":
                # First get saved networks
                logger.info(f"Getting saved networks with: {' '.join(cmd_list)}")
                process = subprocess.run(cmd_list, capture_output=True, text=True, check=True, timeout=10,
                                       creationflags=subprocess.CREATE_NO_WINDOW)
                logger.debug(f"Saved networks command output:\n{process.stdout}")
                if process.stderr:
                    logger.warning(f"Saved networks command stderr: {process.stderr}")
                self._parse_windows_saved_networks(process.stdout)
                logger.debug(f"Found {len(self.saved_networks)} saved networks")
                
                # Then scan for available networks
                logger.info(f"Scanning for available networks with: {' '.join(scan_cmd)}")
                try:
                    process = subprocess.run(scan_cmd, capture_output=True, text=True, check=True, timeout=15,
                                           creationflags=subprocess.CREATE_NO_WINDOW)
                    logger.debug(f"Available networks scan output length: {len(process.stdout)} chars")
                    logger.debug(f"Available networks command output:\n{process.stdout}")
                    if process.stderr:
                        logger.warning(f"Available networks scan stderr: {process.stderr}")
                    self._parse_windows_available_networks(process.stdout)
                except subprocess.CalledProcessError as scan_e:
                    logger.error(f"Available networks scan failed: {scan_e}. Stdout: {scan_e.stdout}. Stderr: {scan_e.stderr}")
                    self.last_scan_error = f"Available scan failed: {scan_e.returncode}"
                    # Continue with just saved networks rather than failing completely
                except Exception as scan_e:
                    logger.error(f"Unexpected error during available networks scan: {scan_e}", exc_info=True)
                    self.last_scan_error = "Available scan error"
                
            self.network_selected_index = 0  # Reset selection
            logger.info(f"Network scan completed. Found {len(self.available_networks)} networks")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Network scan command failed: {e}. Stdout: {e.stdout}. Stderr: {e.stderr}")
            self.last_scan_error = f"Scan Failed: {e.returncode}"
        except subprocess.TimeoutExpired:
            logger.error(f"Network scan timed out: {' '.join(cmd_list)}")
            self.last_scan_error = "Scan Timeout"
        except FileNotFoundError:
            logger.error(f"Network scan command not found: {cmd_list[0]}")
            self.last_scan_error = "Command Not Found"
        except Exception as e:
            logger.error(f"Unexpected error during network scan: {e}", exc_info=True)
            self.last_scan_error = "Scan Error"
        finally:
            self.scanning_in_progress = False
            
        return False
    
    def _parse_linux_networks(self, nmcli_output):
        """Parse nmcli network list output for Linux."""
        for line in nmcli_output.strip().split('\n'):
            if not line.strip():
                continue
                
            parts = line.split(':')
            if len(parts) >= 4:
                ssid = parts[0].strip()
                signal = parts[1].strip()
                security = parts[2].strip()
                in_use = parts[3].strip()
                
                if not ssid or ssid == '--':  # Skip hidden or empty SSIDs
                    continue
                    
                try:
                    signal_strength = int(signal) if signal.isdigit() else 0
                except ValueError:
                    signal_strength = 0
                    
                network = {
                    'ssid': ssid,
                    'signal_strength': signal_strength,
                    'security': 'Open' if not security or security == '--' else security,
                    'is_saved': ssid in self.saved_networks,
                    'is_connected': in_use == '*'
                }
                self.available_networks.append(network)
        
        # Sort by signal strength (strongest first)
        self.available_networks.sort(key=lambda x: x['signal_strength'], reverse=True)
    
    def _parse_windows_saved_networks(self, netsh_profiles_output):
        """Parse Windows saved networks from netsh profiles output."""
        self.saved_networks = []
        logger.info(f"PARSING SAVED NETWORKS from {len(netsh_profiles_output)} chars")
        logger.info(f"RAW PROFILES OUTPUT:\n{netsh_profiles_output}")
        
        lines = netsh_profiles_output.split('\n')
        logger.info(f"Split profiles into {len(lines)} lines")
        
        for line_num, line in enumerate(lines):
            logger.debug(f"Profile line {line_num}: '{line.strip()}'")
            if 'All User Profile' in line or 'User Profile' in line:
                # Extract profile name
                parts = line.split(':')
                if len(parts) > 1:
                    profile_name = parts[1].strip()
                    if profile_name:
                        self.saved_networks.append(profile_name)
                        logger.info(f"Found saved network: '{profile_name}'")
        
        logger.info(f"SAVED NETWORKS RESULT: Found {len(self.saved_networks)} saved networks")
        for i, saved in enumerate(self.saved_networks):
            logger.info(f"Saved {i+1}: {saved}")
    
    def _parse_windows_available_networks(self, netsh_networks_output):
        """Parse Windows available networks from netsh show networks output."""
        self.available_networks = []
        current_ssid = None
        current_authentication = 'Open'
        current_signal = 0
        
        logger.info(f"Parsing Windows networks from {len(netsh_networks_output)} chars of output")
        
        lines = netsh_networks_output.split('\n')
        logger.info(f"Found {len(lines)} lines to parse")
        
        for line_num, line in enumerate(lines):
            original_line = line
            line = line.strip()
            
            # Look for SSID lines: "SSID 1 : NetworkName" or "SSID 1 :" (empty)
            if line.startswith('SSID') and ':' in line:
                # Save previous network if we have one
                if current_ssid is not None:  # Allow empty string SSIDs
                    network = {
                        'ssid': current_ssid if current_ssid else f"Hidden_{len(self.available_networks)+1}",
                        'signal_strength': current_signal,
                        'security': current_authentication if current_authentication != 'Open' else 'Open',
                        'is_saved': current_ssid in self.saved_networks if current_ssid else False,
                        'is_connected': False
                    }
                    self.available_networks.append(network)
                    logger.info(f"Added network: '{network['ssid']}' Signal:{network['signal_strength']}% Security:{network['security']} Saved:{network['is_saved']}")
                
                # Extract new SSID
                colon_index = line.find(':')
                if colon_index > 0:
                    ssid_part = line[colon_index + 1:].strip()
                    current_ssid = ssid_part  # Keep empty string if no name
                    current_authentication = 'Open'  # Reset
                    current_signal = 0  # Reset
                    logger.debug(f"Starting new SSID: '{current_ssid}'")
                    
            # Look for Authentication line (not indented)
            elif line.startswith('Authentication') and ':' in line and current_ssid is not None:
                colon_index = line.find(':')
                if colon_index > 0:
                    auth_value = line[colon_index + 1:].strip()
                    current_authentication = auth_value
                    logger.debug(f"Set authentication: {current_authentication}")
                    
            # Look for Signal line (indented, under BSSID)
            elif 'Signal' in line and ':' in line and current_ssid is not None:
                # Signal lines are indented, so check original line has spaces at start
                if original_line.startswith('         Signal') or original_line.startswith('\t'):
                    colon_index = line.find(':')
                    if colon_index > 0:
                        signal_part = line[colon_index + 1:].strip().replace('%', '')
                        try:
                            signal_value = int(signal_part)
                            current_signal = max(current_signal, signal_value)
                            logger.debug(f"Set signal: {current_signal}%")
                        except ValueError:
                            logger.debug(f"Could not parse signal: '{signal_part}'")
        
        # Add the final network
        if current_ssid is not None:
            network = {
                'ssid': current_ssid if current_ssid else f"Hidden_{len(self.available_networks)+1}",
                'signal_strength': current_signal,
                'security': current_authentication if current_authentication != 'Open' else 'Open',
                'is_saved': current_ssid in self.saved_networks if current_ssid else False,
                'is_connected': False
            }
            self.available_networks.append(network)
            logger.info(f"Added final network: '{network['ssid']}' Signal:{network['signal_strength']}% Security:{network['security']} Saved:{network['is_saved']}")
        
        logger.info(f"FINAL RESULT: {len(self.available_networks)} networks found")
        
        # Sort by signal strength (strongest first)
        self.available_networks.sort(key=lambda x: x['signal_strength'], reverse=True)
    
    def connect_to_saved_network(self, ssid):
        """
        Connect to a saved WiFi network.
        Args:
            ssid (str): The SSID of the network to connect to.
        Returns:
            bool: True if connection was attempted successfully, False otherwise.
        """
        if not ssid:
            logger.error("Cannot connect: SSID is empty")
            return False
            
        if ssid not in self.saved_networks:
            logger.warning(f"Cannot connect to '{ssid}': not a saved network")
            return False
            
        system = platform.system()
        cmd_list = []
        
        try:
            if system == "Linux":
                cmd_list = ['nmcli', 'connection', 'up', ssid]
            elif system == "Windows":
                cmd_list = ['netsh', 'wlan', 'connect', f'name="{ssid}"']
            else:
                logger.warning(f"Network connection not supported on platform: {system}")
                return False
                
            logger.info(f"Connecting to network '{ssid}' with command: {' '.join(cmd_list)}")
            
            process = subprocess.run(cmd_list, capture_output=True, text=True, check=True, timeout=30,
                                   creationflags=subprocess.CREATE_NO_WINDOW if system == "Windows" else 0)
            
            logger.info(f"Connection attempt completed for '{ssid}': {process.stdout.strip()}")
            if process.stderr.strip():
                logger.warning(f"Connection stderr for '{ssid}': {process.stderr.strip()}")
                
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to connect to '{ssid}': {e}. Stdout: {e.stdout}. Stderr: {e.stderr}")
        except subprocess.TimeoutExpired:
            logger.error(f"Connection to '{ssid}' timed out")
        except FileNotFoundError:
            logger.error(f"Connection command not found: {cmd_list[0]}")
        except Exception as e:
            logger.error(f"Unexpected error connecting to '{ssid}': {e}", exc_info=True)
            
        return False
    
    def get_available_networks(self):
        """Get the list of available networks from last scan."""
        return self.available_networks
    
    def get_network_selected_index(self):
        """Get the currently selected network index."""
        return self.network_selected_index
    
    def set_network_selected_index(self, index):
        """Set the currently selected network index."""
        if 0 <= index < len(self.available_networks):
            self.network_selected_index = index
        else:
            self.network_selected_index = 0
    
    def navigate_networks_next(self):
        """Navigate to next network in the list."""
        if self.available_networks:
            self.network_selected_index = (self.network_selected_index + 1) % len(self.available_networks)
            return True
        return False
    
    def navigate_networks_prev(self):
        """Navigate to previous network in the list."""
        if self.available_networks:
            self.network_selected_index = (self.network_selected_index - 1 + len(self.available_networks)) % len(self.available_networks)
            return True
        return False
    
    def get_selected_network(self):
        """Get the currently selected network."""
        if 0 <= self.network_selected_index < len(self.available_networks):
            return self.available_networks[self.network_selected_index]
        return None

    def handle_network_browsing_input(self, action_from_app_state):
        """
        Handle input for the WiFi network browsing view.
        Args:
            action_from_app_state (str): The input action (e.g., app_config.INPUT_ACTION_NEXT).
        Returns:
            str or bool: An action string for AppState to process (like WIFI_ACTION_CONNECT_TO_NETWORK),
                         or True/False for simple navigation.
        """
        # Handle rescan if no networks or error
        if action_from_app_state == app_config.INPUT_ACTION_SELECT:
            if not self.available_networks or self.last_scan_error:
                # Trigger rescan
                logger.info("Triggering network rescan from UI")
                self.scan_networks()
                return True
                
            # Handle network selection
            selected_network = self.get_selected_network()
            if selected_network:
                return self.handle_network_selection(selected_network)
            return False
            
        elif action_from_app_state == app_config.INPUT_ACTION_NEXT:
            return self.navigate_networks_next()
        elif action_from_app_state == app_config.INPUT_ACTION_PREV:
            return self.navigate_networks_prev()
        elif action_from_app_state == app_config.INPUT_ACTION_BACK:
            return WIFI_ACTION_BACK_TO_WIFI
        return False
        
    def handle_network_selection(self, network):
        """
        Handle selection of a specific network.
        
        Args:
            network (dict): The selected network data
            
        Returns:
            str: Action string indicating next step
        """
        ssid = network.get('ssid', 'Unknown')
        is_saved = network.get('is_saved', False)
        security = network.get('security', 'Unknown')
        
        logger.info(f"Network selected: {ssid} (saved: {is_saved}, security: {security})")
        
        # Store selected network for connection
        self.selected_network_for_connection = network
        
        # If it's a saved network, try to connect directly
        if is_saved:
            logger.info(f"Attempting to connect to saved network: {ssid}")
            success = self.connect_to_saved_network(ssid)
            if success:
                return WIFI_ACTION_BACK_TO_WIFI  # Return to WiFi settings to show new status
            else:
                logger.error(f"Failed to connect to saved network: {ssid}")
                return False
                
        # If it's an open network (no security), connect directly
        elif security in ['Open', 'None', '']:
            logger.info(f"Attempting to connect to open network: {ssid}")
            success = self.connect_to_network(ssid, "")  # Empty password for open networks
            if success:
                return WIFI_ACTION_BACK_TO_WIFI
            else:
                logger.error(f"Failed to connect to open network: {ssid}")
                return False
                
        # If it's a secured network, need password entry
        else:
            logger.info(f"Network requires password: {ssid}")
            return WIFI_ACTION_ENTER_PASSWORD
            
    def get_selected_network_for_connection(self):
        """Get the network that was selected for connection."""
        return getattr(self, 'selected_network_for_connection', None)
        
    def connect_to_network(self, ssid, password):
        """
        Connect to a WiFi network with the given credentials.
        
        Args:
            ssid (str): The network SSID
            password (str): The network password (empty string for open networks)
            
        Returns:
            bool: True if connection successful
        """
        system = platform.system()
        
        try:
            if system == "Linux":
                # Use nmcli to connect
                cmd = ['nmcli', 'device', 'wifi', 'connect', ssid]
                if password:
                    cmd.extend(['password', password])
                    
                logger.info(f"Connecting to WiFi network: {ssid}")
                result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=15)
                
                if result.returncode == 0:
                    logger.info(f"Successfully connected to {ssid}")
                    self.update_wifi_status()  # Update status after connection
                    return True
                else:
                    logger.error(f"Failed to connect to {ssid}: {result.stderr}")
                    return False
                    
            elif system == "Windows":
                if password:
                    # For Windows, we need to create a profile first, then connect
                    profile_xml = f'''<?xml version="1.0"?>
<WLANProfile xmlns="http://www.microsoft.com/networking/WLAN/profile/v1">
    <name>{ssid}</name>
    <SSIDConfig>
        <SSID>
            <name>{ssid}</name>
        </SSID>
    </SSIDConfig>
    <connectionType>ESS</connectionType>
    <connectionMode>auto</connectionMode>
    <MSM>
        <security>
            <authEncryption>
                <authentication>WPA2PSK</authentication>
                <encryption>AES</encryption>
                <useOneX>false</useOneX>
            </authEncryption>
            <sharedKey>
                <keyType>passPhrase</keyType>
                <protected>false</protected>
                <keyMaterial>{password}</keyMaterial>
            </sharedKey>
        </security>
    </MSM>
</WLANProfile>'''
                    
                    # Write profile to temp file
                    import tempfile
                    import os
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
                        f.write(profile_xml)
                        profile_path = f.name
                    
                    try:
                        # Add profile
                        add_cmd = ['netsh', 'wlan', 'add', 'profile', f'filename="{profile_path}"']
                        subprocess.run(add_cmd, capture_output=True, text=True, check=True, 
                                     creationflags=subprocess.CREATE_NO_WINDOW)
                        
                        # Connect to network
                        connect_cmd = ['netsh', 'wlan', 'connect', f'name="{ssid}"']
                        result = subprocess.run(connect_cmd, capture_output=True, text=True, check=True,
                                              creationflags=subprocess.CREATE_NO_WINDOW)
                        
                        logger.info(f"Successfully connected to {ssid}")
                        self.update_wifi_status()
                        return True
                        
                    finally:
                        # Clean up temp file
                        try:
                            os.unlink(profile_path)
                        except:
                            pass
                else:
                    # Open network - just connect
                    connect_cmd = ['netsh', 'wlan', 'connect', f'name="{ssid}"']
                    result = subprocess.run(connect_cmd, capture_output=True, text=True, check=True,
                                          creationflags=subprocess.CREATE_NO_WINDOW)
                    logger.info(f"Successfully connected to open network {ssid}")
                    self.update_wifi_status()
                    return True
                    
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to connect to {ssid}: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to {ssid}: {e}")
            return False
            
        logger.warning(f"Network connection not supported on platform: {system}")
        return False

    def rescan_networks(self):
        """
        Convenience method to trigger a network rescan.
        Returns:
            bool: True if scan was initiated successfully, False otherwise.
        """
        logger.info("Manual network rescan requested")
        return self.scan_networks()

    # --- Methods for future features (Scan, Connect, View Saved, Forget) will go here ---
    # def get_scan_wifi_command(self): ...
    # def process_scan_wifi_output(self, command_output_dict, app_state_notification_callback): ...
    # etc. 