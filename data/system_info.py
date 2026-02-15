# --- data/system_info.py ---
# Handles system monitoring (CPU, memory, disk)

import logging
import os
import platform
import datetime
import subprocess
import socket

# Get a logger for this module
logger = logging.getLogger(__name__)

# Try to import psutil for system monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
    logger.info("psutil library successfully imported for system monitoring.")
except ImportError:
    PSUTIL_AVAILABLE = False
    logger.warning("psutil library not found. System monitoring will be limited.")

def get_current_time():
    """Get the current time."""
    try:
        now = datetime.datetime.now()
        return now
    except Exception as e:
        logger.error(f"Error getting current time: {e}", exc_info=True)
        return None

def get_cpu_usage():
    """Get CPU usage information."""
    if not PSUTIL_AVAILABLE:
        logger.debug("psutil not available for CPU monitoring")
        return None, None  # Usage percent, additional info
        
    try:
        cpu_percent = psutil.cpu_percent()  # Non-blocking call
        
        # Get CPU temperature if available (Raspberry Pi specific)
        additional_info = None
        try:
            if os.path.exists('/sys/class/thermal/thermal_zone0/temp'):
                with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                    temp = float(f.read()) / 1000.0
                additional_info = ("temperature", temp)
                logger.debug(f"CPU temperature: {temp:.1f}°C")
            else:
                cores = psutil.cpu_count()
                additional_info = ("cores", cores)
                logger.debug(f"CPU cores: {cores}")
        except Exception as e:
            logger.warning(f"Could not read CPU temperature: {e}")
            cores = psutil.cpu_count()
            additional_info = ("cores", cores)
            
        logger.debug(f"CPU usage: {cpu_percent:.1f}%")
        return cpu_percent, additional_info
    except Exception as e:
        logger.error(f"Error getting CPU usage: {e}")
        return None, None

def get_memory_usage():
    """Get memory usage information."""
    if not PSUTIL_AVAILABLE:
        logger.debug("psutil not available for memory monitoring")
        return None, None, None  # Percent, used MB, total MB
        
    try:
        memory = psutil.virtual_memory()
        used_mb = memory.used / (1024 * 1024)
        total_mb = memory.total / (1024 * 1024)
        logger.debug(f"Memory usage: {memory.percent:.1f}% ({used_mb:.0f}MB/{total_mb:.0f}MB)")
        return memory.percent, used_mb, total_mb
    except Exception as e:
        logger.error(f"Error getting memory usage: {e}")
        return None, None, None

def get_disk_usage():
    """Get disk usage information."""
    if not PSUTIL_AVAILABLE:
        logger.debug("psutil not available for disk monitoring")
        return None, None, None  # Percent, used GB, total GB
        
    try:
        disk = psutil.disk_usage('/')
        used_gb = disk.used / (1024 * 1024 * 1024)
        total_gb = disk.total / (1024 * 1024 * 1024)
        logger.debug(f"Disk usage: {disk.percent:.1f}% ({used_gb:.1f}GB/{total_gb:.1f}GB)")
        return disk.percent, used_gb, total_gb
    except Exception as e:
        logger.error(f"Error getting disk usage: {e}")
        return None, None, None

def get_voltage_info():
    """Get system voltage information for both Windows and Linux."""
    try:
        if platform.system() == "Linux":
            # Try vcgencmd for Raspberry Pi
            try:
                result = subprocess.run(['vcgencmd', 'measure_volts', 'core'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    # Output format: "volt=1.2000V"
                    voltage_str = result.stdout.strip()
                    if 'volt=' in voltage_str:
                        voltage_val = float(voltage_str.split('=')[1].replace('V', ''))
                        logger.debug(f"Core voltage: {voltage_val:.2f}V")
                        return voltage_val
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, ValueError) as e:
                logger.debug(f"vcgencmd not available or failed: {e}")
            
            # Try reading from power supply info
            power_supply_dirs = ['/sys/class/power_supply/BAT0', '/sys/class/power_supply/BAT1', '/sys/class/power_supply/ADP1']
            for psu_dir in power_supply_dirs:
                voltage_file = os.path.join(psu_dir, 'voltage_now')
                if os.path.exists(voltage_file):
                    try:
                        with open(voltage_file, 'r') as f:
                            # Voltage is typically in microvolts
                            voltage_uv = int(f.read().strip())
                            voltage_v = voltage_uv / 1000000.0
                            logger.debug(f"Power supply voltage: {voltage_v:.2f}V")
                            return voltage_v
                    except (ValueError, IOError) as e:
                        logger.debug(f"Could not read voltage from {voltage_file}: {e}")
        
        elif platform.system() == "Windows":
            # Try to get voltage info from Windows power management
            if PSUTIL_AVAILABLE:
                try:
                    battery = psutil.sensors_battery()
                    if battery and hasattr(battery, 'voltage') and battery.voltage:
                        logger.debug(f"Windows battery voltage: {battery.voltage:.2f}V")
                        return battery.voltage
                except AttributeError:
                    pass
            
            # Windows - no voltage data available
            logger.debug("Windows: No voltage information available")
        
        logger.debug("No voltage information available")
        return None
    except Exception as e:
        logger.error(f"Error getting voltage info: {e}", exc_info=True)
        return None

def get_battery_info():
    """Get battery information for both Windows and Linux."""
    try:
        # Try psutil battery info first (works on Windows and some Linux)
        if PSUTIL_AVAILABLE:
            try:
                battery = psutil.sensors_battery()
                if battery:
                    percent = battery.percent
                    plugged = battery.power_plugged
                    status = "Charging" if plugged else "Discharging"
                    logger.debug(f"Battery: {percent:.0f}% ({status})")
                    return percent, status
            except AttributeError:
                # sensors_battery not available on this platform
                pass
        
        # Try Linux-specific battery info
        if platform.system() == "Linux":
            battery_dirs = ['/sys/class/power_supply/BAT0', '/sys/class/power_supply/BAT1']
            for bat_dir in battery_dirs:
                if os.path.exists(bat_dir):
                    try:
                        # Read capacity
                        capacity_file = os.path.join(bat_dir, 'capacity')
                        status_file = os.path.join(bat_dir, 'status')
                        
                        capacity = None
                        status = "Unknown"
                        
                        if os.path.exists(capacity_file):
                            with open(capacity_file, 'r') as f:
                                capacity = int(f.read().strip())
                        
                        if os.path.exists(status_file):
                            with open(status_file, 'r') as f:
                                status = f.read().strip()
                        
                        if capacity is not None:
                            logger.debug(f"Linux battery: {capacity}% ({status})")
                            return capacity, status
                            
                    except (ValueError, IOError) as e:
                        logger.debug(f"Could not read battery info from {bat_dir}: {e}")
            
            # Linux - no battery detected
            logger.debug("Linux: No battery detected")
            return None, None
        
        elif platform.system() == "Windows":
            # Windows - no battery detected
            logger.debug("Windows: No battery detected")
            return None, None
        
        logger.debug("No battery information available")
        return None, None
    except Exception as e:
        logger.error(f"Error getting battery info: {e}", exc_info=True)
        return None, None

def get_bluetooth_info():
    """Get Bluetooth status and connected device name (Linux: bluetoothctl; Windows: placeholder)."""
    try:
        if platform.system() == "Linux":
            return _get_bluetooth_info_linux()
        elif platform.system() == "Windows":
            return "N/A", "Windows"
        else:
            return "N/A", "Unsupported"
    except Exception as e:
        logger.error(f"Error getting Bluetooth info: {e}", exc_info=True)
        return "Error", "Error"


def _get_bluetooth_info_linux():
    """Linux: use bluetoothctl to get powered state and connected device. Fallback to hciconfig for on/off."""
    # 1) Check powered state and connected devices via bluetoothctl
    try:
        show_result = subprocess.run(
            ["bluetoothctl", "show"],
            capture_output=True, text=True, timeout=3
        )
        if show_result.returncode != 0:
            raise FileNotFoundError("bluetoothctl show failed")
        out = show_result.stdout
        out_lower = out.lower()
        if "powered: no" in out_lower or "powered: off" in out_lower:
            return "Off", "Disabled"

        # 2) Get connected device(s): BlueZ 5.65+ supports "bluetoothctl devices Connected"
        conn_result = subprocess.run(
            ["bluetoothctl", "devices", "Connected"],
            capture_output=True, text=True, timeout=3
        )
        if conn_result.returncode == 0 and conn_result.stdout.strip():
            # Parse first line: "Device AA:BB:CC:DD:EE:FF Device Name"
            line = conn_result.stdout.strip().split("\n")[0]
            parts = line.split(None, 2)  # max 3 parts: Device, MAC, Name
            if len(parts) >= 3:
                return "Connected", parts[2].strip()
            if len(parts) >= 2:
                return "Connected", parts[1]
            return "Connected", "Device"

        # 3) Older BlueZ: list all devices then check info for each until we find connected
        dev_result = subprocess.run(
            ["bluetoothctl", "devices"],
            capture_output=True, text=True, timeout=3
        )
        if dev_result.returncode != 0 or not dev_result.stdout.strip():
            return "On", "No Devices"

        for line in dev_result.stdout.strip().split("\n"):
            parts = line.split(None, 2)
            if len(parts) < 2 or parts[0].lower() != "device":
                continue
            mac = parts[1]
            info_result = subprocess.run(
                ["bluetoothctl", "info", mac],
                capture_output=True, text=True, timeout=2
            )
            if info_result.returncode != 0:
                continue
            info_lower = info_result.stdout.lower()
            if "connected: yes" not in info_lower:
                continue
            # Get device name from "Name: ..."
            for info_line in info_result.stdout.split("\n"):
                if info_line.strip().lower().startswith("name:"):
                    name = info_line.split(":", 1)[1].strip()
                    return "Connected", name or mac
            return "Connected", mac

        return "On", "No Devices"

    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.debug(f"bluetoothctl failed: {e}, trying hciconfig")
    except Exception as e:
        logger.debug(f"Bluetooth bluetoothctl path failed: {e}")

    # Fallback: hciconfig for adapter on/off only (no device name)
    try:
        result = subprocess.run(["hciconfig"], capture_output=True, text=True, timeout=3)
        if result.returncode == 0 and "up running" in result.stdout.lower():
            return "On", "Available"
        if result.returncode == 0:
            return "Off", "Disabled"
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        pass
    return "N/A", "Not Available"

def get_wifi_info():
    """Get WiFi status and SSID."""
    if not PSUTIL_AVAILABLE:
        logger.debug("psutil not available for WiFi monitoring")
        return "N/A", "N/A"

    try:
        # Try to get more detailed WiFi info using system commands
        if platform.system() == "Linux":
            try:
                # Try iwconfig first for SSID
                result = subprocess.run(['iwconfig'], capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'ESSID:' in line and 'off/any' not in line.lower():
                            # Extract SSID
                            essid_part = line.split('ESSID:')[1].strip()
                            if essid_part.startswith('"') and essid_part.endswith('"'):
                                ssid = essid_part[1:-1]  # Remove quotes
                                return "Connected", ssid
                            elif essid_part and essid_part != '""':
                                return "Connected", essid_part
                
                # Try nmcli as fallback
                result = subprocess.run(['nmcli', '-t', '-f', 'ACTIVE,SSID', 'dev', 'wifi'], 
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if line.startswith('yes:'):
                            ssid = line.split(':', 1)[1]
                            if ssid:
                                return "Connected", ssid
                            
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
                logger.debug(f"WiFi command failed, falling back to psutil: {e}")
        
        # Fallback to psutil method
        stats = psutil.net_if_stats()
        addrs = psutil.net_if_addrs()
        for interface, stat in stats.items():
            # Look for a wireless interface that is up and likely has an IP
            # This is heuristic, might need adjustment based on OS/hardware
            if stat.isup and interface in addrs:
                # Rough check for wireless keywords, might need refinement
                if any(keyword in interface.lower() for keyword in ['wlan', 'wi-fi', 'wireless']):
                    # Try to get SSID - platform specific, might need external commands
                    # For now, return 'Connected' if interface is up
                    # A more robust solution would use platform-specific tools
                    ssid = "Connected" # Placeholder until SSID fetching is added
                    status = "Online" if stat.isup else "Offline"
                    logger.debug(f"WiFi found: {interface}, Status: {status}, SSID: {ssid}")
                    return status, ssid

        logger.debug("No active WiFi interface found.")
        return "Offline", "N/A"
    except Exception as e:
        logger.error(f"Error getting WiFi info: {e}", exc_info=True)
        return "Error", "N/A"


def get_local_ip():
    """Get the primary local IPv4 address (e.g. for WiFi interface). Returns None if not connected."""
    if not PSUTIL_AVAILABLE:
        return None
    try:
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()
        # Prefer wlan*, then eth*, then first up interface with IPv4
        for name in sorted(addrs.keys()):
            if not stats.get(name, None) or not stats[name].isup:
                continue
            for addr in addrs[name]:
                if addr.family == socket.AF_INET:
                    ip = addr.address
                    if ip and not ip.startswith('127.'):
                        if 'wlan' in name.lower() or 'wi' in name.lower():
                            return ip
                        if 'eth' in name.lower():
                            return ip
        for name in sorted(addrs.keys()):
            if not stats.get(name, None) or not stats[name].isup:
                continue
            for addr in addrs[name]:
                if addr.family == socket.AF_INET:
                    ip = addr.address
                    if ip and not ip.startswith('127.'):
                        return ip
        return None
    except Exception as e:
        logger.debug(f"Error getting local IP: {e}")
        return None


def get_location_and_public_ip(timeout_sec=3.0):
    """
    Fetch approximate location and public IP (e.g. when on WiFi). Uses ip-api.com (no key).
    Returns (location_str, public_ip) e.g. ("London, United Kingdom", "1.2.3.4") or (None, None) on failure.
    """
    try:
        import urllib.request
        import json
        req = urllib.request.Request(
            "http://ip-api.com/json/?fields=city,country,query",
            headers={"User-Agent": "Tricorder/1.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
            data = json.loads(resp.read().decode())
        city = data.get("city") or ""
        country = data.get("country") or ""
        location = f"{city}, {country}" if (city and country) else (country or city or None)
        public_ip = data.get("query") or None
        return (location, public_ip)
    except Exception as e:
        logger.debug(f"Location/public-IP fetch failed: {e}")
        return (None, None)


def get_cellular_info():
    """Get Cellular status and provider (Basic Check)."""
    if not PSUTIL_AVAILABLE:
        logger.debug("psutil not available for Cellular monitoring")
        return "N/A", "N/A"

    try:
        # This is a very basic check. Real cellular info often needs specific modem libs/AT commands.
        stats = psutil.net_if_stats()
        for interface, stat in stats.items():
            # Look for common cellular interface names
            if stat.isup and any(keyword in interface.lower() for keyword in ['ppp', 'wwan', 'mobile', 'lte']):
                status = "Online" # Assuming up means online
                provider = "Unknown" # psutil doesn't provide provider info
                logger.debug(f"Cellular interface found: {interface}, Status: {status}")
                return status, provider

        logger.debug("No active Cellular interface found.")
        return "Offline", "N/A"
    except Exception as e:
        logger.error(f"Error getting Cellular info: {e}", exc_info=True)
        return "Error", "N/A" 