# --- models/bluetooth_manager.py ---
# Manages Bluetooth operations: toggle power, list devices, connect/disconnect.

import logging
import platform
import queue
import subprocess
import threading
import time
import config as app_config
from data import system_info

logger = logging.getLogger(__name__)

# Bluetooth action constants
BLUETOOTH_ACTION_TOGGLE = "BLUETOOTH_TOGGLE"
BLUETOOTH_ACTION_DEVICES = "BLUETOOTH_DEVICES"
BLUETOOTH_ACTION_BACK_TO_SETTINGS = "BLUETOOTH_BACK_TO_SETTINGS"
BLUETOOTH_ACTION_BACK_TO_BLUETOOTH = "BLUETOOTH_BACK_TO_BLUETOOTH"
BLUETOOTH_ACTION_CONNECT_OR_DISCONNECT = "BLUETOOTH_CONNECT_OR_DISCONNECT"
BLUETOOTH_ACTION_SCAN_DEVICES = "BLUETOOTH_SCAN_DEVICES"


class BluetoothManager:
    """Manages Bluetooth power, device list, and connect/disconnect (Linux: bluetoothctl)."""

    def __init__(self, config_module):
        self.config = config_module
        self.status_str = "Unknown"
        self.device_str = ""
        self._options = []
        self._build_options()
        self.selected_option_index = 0

        # Device list state
        self.devices = []  # list of {"mac": str, "name": str, "connected": bool}
        self.device_selected_index = 0
        self.scanning = False
        self.last_scan_error = None
        self._scan_result_queue = queue.Queue()
        self._scan_completion_callback = None

        self.update_bluetooth_status()

    def _build_options(self):
        self._options = [
            {"name": f"Bluetooth: {self.status_str} (Toggle)", "action": BLUETOOTH_ACTION_TOGGLE, "status_key": "bluetooth_status"},
            {"name": "Devices...", "action": BLUETOOTH_ACTION_DEVICES},
            {"name": "<- Back to Settings", "action": BLUETOOTH_ACTION_BACK_TO_SETTINGS},
        ]

    def _update_options_display(self):
        for opt in self._options:
            if opt.get("action") == BLUETOOTH_ACTION_TOGGLE:
                opt["name"] = f"Bluetooth: {self.status_str} (Toggle)"
                break

    def update_bluetooth_status(self):
        """Refresh status and device name from system_info."""
        try:
            self.status_str, self.device_str = system_info.get_bluetooth_info()
            if not self.status_str or self.status_str == "N/A":
                self.status_str = "Unknown"
        except Exception as e:
            logger.debug("Bluetooth status failed: %s", e)
            self.status_str = "Error"
            self.device_str = ""
        self._update_options_display()

    def toggle_bluetooth(self):
        """Toggle Bluetooth power on/off. Linux only (bluetoothctl)."""
        if platform.system() != "Linux":
            logger.warning("Bluetooth toggle not supported on %s", platform.system())
            self.status_str = "N/A"
            self._update_options_display()
            return False

        try:
            # Determine current state to decide toggle direction
            status_lower = (self.status_str or "").lower()
            turn_on = status_lower in ("off", "disabled", "n/a", "error", "unknown")
            cmd = ["bluetoothctl", "power", "on" if turn_on else "off"]
            logger.info("Bluetooth toggle: %s", " ".join(cmd))
            self.status_str = "Toggling..."
            self._update_options_display()

            subprocess.run(cmd, capture_output=True, text=True, timeout=5, check=True)
            time.sleep(0.5)
            self.update_bluetooth_status()
            return True
        except subprocess.CalledProcessError as e:
            logger.error("Bluetooth toggle failed: %s", e)
            self.status_str = "Error"
            self._update_options_display()
            return False
        except FileNotFoundError:
            logger.error("bluetoothctl not found")
            self.status_str = "No bluetoothctl"
            self._update_options_display()
            return False
        except Exception as e:
            logger.exception("Bluetooth toggle error: %s", e)
            self.status_str = "Error"
            self._update_options_display()
            return False

    def handle_input(self, action):
        """Handle input for the main Bluetooth settings menu."""
        if action == app_config.INPUT_ACTION_NEXT:
            self.selected_option_index = (self.selected_option_index + 1) % len(self._options)
            return True
        if action == app_config.INPUT_ACTION_PREV:
            self.selected_option_index = (self.selected_option_index - 1 + len(self._options)) % len(self._options)
            return True
        if action == app_config.INPUT_ACTION_SELECT:
            return self._options[self.selected_option_index]["action"]
        return False

    def get_current_display_options(self):
        self._update_options_display()
        return self._options

    def get_selected_index(self):
        return self.selected_option_index

    # --- Device list (for Devices... sub-view) ---

    def refresh_devices(self):
        """Populate self.devices from bluetoothctl (Linux). On other OS, clear list."""
        self.devices = []
        self.last_scan_error = None
        if platform.system() != "Linux":
            return

        try:
            # List all known devices
            result = subprocess.run(
                ["bluetoothctl", "devices"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode != 0 or not result.stdout.strip():
                return

            for line in result.stdout.strip().split("\n"):
                parts = line.split(None, 2)
                if len(parts) < 2 or parts[0].lower() != "device":
                    continue
                mac = parts[1]
                name = parts[2].strip() if len(parts) >= 3 else mac
                connected = self._is_device_connected(mac)
                self.devices.append({"mac": mac, "name": name or mac, "connected": connected})
        except Exception as e:
            logger.debug("Refresh Bluetooth devices failed: %s", e)
            self.last_scan_error = str(e)

    def _is_device_connected(self, mac):
        try:
            r = subprocess.run(
                ["bluetoothctl", "info", mac],
                capture_output=True, text=True, timeout=2
            )
            if r.returncode == 0 and "connected: yes" in r.stdout.lower():
                return True
        except Exception:
            pass
        return False

    def start_scan(self, completion_callback=None):
        """Start a short scan in a background thread. Main thread should call check_scan_completion()."""
        if platform.system() != "Linux" or self.scanning:
            if completion_callback:
                completion_callback()
            return False
        self.scanning = True
        self.last_scan_error = None
        self._scan_completion_callback = completion_callback

        def do_scan():
            try:
                subprocess.run(["bluetoothctl", "scan", "on"], capture_output=True, text=True, timeout=1)
                time.sleep(5)
                subprocess.run(["bluetoothctl", "scan", "off"], capture_output=True, text=True, timeout=2)
            except Exception as e:
                logger.debug("Bluetooth scan error: %s", e)
            finally:
                self.scanning = False
                self.refresh_devices()
                self._scan_result_queue.put({"status": "complete"})

        t = threading.Thread(target=do_scan, daemon=True)
        t.start()
        return True

    def check_scan_completion(self):
        """Call from main thread to process scan completion and run callback."""
        try:
            result = self._scan_result_queue.get_nowait()
            if result.get("status") == "complete" and self._scan_completion_callback:
                cb = self._scan_completion_callback
                self._scan_completion_callback = None
                cb()
            return True
        except queue.Empty:
            pass
        return False

    def get_device_list(self):
        """Return list of devices (call refresh_devices first if needed)."""
        return self.devices

    def get_device_display_list(self):
        """Return list for UI: first row is 'Scan for new devices', then devices."""
        scan_row = [{"name": "Scan for new devices", "mac": None, "connected": False}]
        return scan_row + self.devices

    def get_device_selected_index(self):
        return self.device_selected_index

    def set_device_selected_index(self, index):
        total = len(self.devices) + 1  # +1 for Scan row
        if total and 0 <= index < total:
            self.device_selected_index = index

    def handle_device_list_input(self, action):
        """Handle input when showing device list. Returns action string or bool."""
        total = len(self.devices) + 1
        if total == 0:
            if action == app_config.INPUT_ACTION_BACK:
                return BLUETOOTH_ACTION_BACK_TO_BLUETOOTH
            return False

        if action == app_config.INPUT_ACTION_NEXT:
            self.device_selected_index = (self.device_selected_index + 1) % total
            return True
        if action == app_config.INPUT_ACTION_PREV:
            self.device_selected_index = (self.device_selected_index - 1 + total) % total
            return True
        if action == app_config.INPUT_ACTION_SELECT:
            if self.device_selected_index == 0:
                return BLUETOOTH_ACTION_SCAN_DEVICES
            return BLUETOOTH_ACTION_CONNECT_OR_DISCONNECT
        if action == app_config.INPUT_ACTION_BACK:
            return BLUETOOTH_ACTION_BACK_TO_BLUETOOTH
        return False

    def get_selected_device(self):
        """Return the currently selected device dict or None (index 0 = Scan row)."""
        if self.device_selected_index <= 0 or self.device_selected_index > len(self.devices):
            return None
        return self.devices[self.device_selected_index - 1]

    def connect_device(self, mac):
        """Connect to device by MAC. Returns True on success."""
        if platform.system() != "Linux":
            return False
        try:
            r = subprocess.run(
                ["bluetoothctl", "connect", mac],
                capture_output=True, text=True, timeout=15
            )
            if r.returncode == 0:
                self.update_bluetooth_status()
                self.refresh_devices()
                return True
            logger.warning("bluetoothctl connect %s failed: %s", mac, r.stderr or r.stdout)
            return False
        except Exception as e:
            logger.exception("Connect failed: %s", e)
            return False

    def disconnect_device(self, mac):
        """Disconnect device by MAC. Returns True on success."""
        if platform.system() != "Linux":
            return False
        try:
            r = subprocess.run(
                ["bluetoothctl", "disconnect", mac],
                capture_output=True, text=True, timeout=10
            )
            if r.returncode == 0:
                self.update_bluetooth_status()
                self.refresh_devices()
                return True
            logger.warning("bluetoothctl disconnect %s failed: %s", mac, r.stderr or r.stdout)
            return False
        except Exception as e:
            logger.exception("Disconnect failed: %s", e)
            return False
