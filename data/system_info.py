# --- data/system_info.py ---
# Handles system monitoring (CPU, memory, disk)

import logging
import os
import platform
import datetime
import subprocess

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
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
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
    """Get Bluetooth status information."""
    try:
        if platform.system() == "Linux":
            # Try using bluetoothctl or hciconfig
            try:
                # Try hciconfig first (more reliable)
                result = subprocess.run(['hciconfig'], capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    output = result.stdout.lower()
                    if 'up running' in output:
                        # Check if any devices are connected
                        try:
                            bt_result = subprocess.run(['bluetoothctl', 'info'], 
                                                     capture_output=True, text=True, timeout=2)
                            if bt_result.returncode == 0 and 'connected: yes' in bt_result.stdout.lower():
                                return "Connected", "Device Connected"
                            else:
                                return "On", "No Devices"
                        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
                            return "On", "Available"
                    else:
                        return "Off", "Disabled"
                else:
                    return "N/A", "Not Available"
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
                logger.debug(f"Bluetooth check failed: {e}")
                return "N/A", "Not Available"
        
        elif platform.system() == "Windows":
            # Windows Bluetooth check is more complex, return placeholder
            return "N/A", "Windows"
        
        else:
            return "N/A", "Unsupported"
            
    except Exception as e:
        logger.error(f"Error getting Bluetooth info: {e}", exc_info=True)
        return "Error", "Error"

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