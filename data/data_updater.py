# --- data/data_updater.py ---
# Handles fetching data from various sources and updating models

import logging

# Import specific data fetching functions
from . import sensors
from . import system_info
# Import config for sensor mode constants and display properties
import config

logger = logging.getLogger(__name__)

def _format_sensor_value(sensor_key, raw_value, display_props):
    """Helper to format a single sensor value and prepare it for sensor_values dict."""
    text_val = "N/A"
    unit = display_props.get("units", "")
    note = ""
    numeric_val = None

    if raw_value is not None:
        try:
            # Handle special formatting for complex types first
            if sensor_key == config.SENSOR_ORIENTATION and isinstance(raw_value, dict):
                text_val = f"P:{raw_value['pitch']:.0f} R:{raw_value['roll']:.0f}"
                # For history/graphing, SENSOR_DISPLAY_PROPERTIES might specify which component, or default (e.g. pitch)
                numeric_val = raw_value.get(display_props.get("component_to_graph", 'pitch')) 

            elif sensor_key == config.SENSOR_ACCELERATION and isinstance(raw_value, dict):
                # Keep X and Y values for display, but use Z for graph/arrow
                text_val = f"X:{raw_value['x']:.2f} Y:{raw_value['y']:.2f}"
                note = ""  # No note needed
                # For history/graphing, use Z component for inertia
                numeric_val = raw_value.get('z')
            
            elif sensor_key == config.SENSOR_CLOCK and hasattr(raw_value, 'strftime'):
                text_val = raw_value.strftime("%H:%M:%S")
                note = raw_value.strftime("%a %d %b %Y")
                numeric_val = None # Clock is not numeric for graphing

            else: # General numeric processing
                numeric_val = float(raw_value) # Convert to float for history
                # Format text value based on precision (can be added to SENSOR_DISPLAY_PROPERTIES)
                precision = display_props.get("precision", 1 if isinstance(numeric_val, float) and not isinstance(numeric_val, int) else 0)
                text_val = f"{numeric_val:.{precision}f}"

        except (ValueError, TypeError, KeyError) as e:
            logger.warning(f"Could not process or format value for {sensor_key}: {raw_value} ({e})")
            text_val = "Error"
            numeric_val = None # Ensure numeric_val is None on error
            note = "Parse Err"
    else: # raw_value is None
        if sensor_key in [config.SENSOR_CPU_USAGE, config.SENSOR_MEMORY_USAGE, config.SENSOR_DISK_USAGE]:
            note = "psutil N/A"
        else:
            note = "Sensor N/A"
        text_val = "N/A" # Keep text_val as N/A for None raw_value
        numeric_val = None

    return {"text": text_val, "unit": unit, "note": note, "value": numeric_val}

def update_all_data(sensor_values, reading_history, app_config):
    """
    Fetches data from all configured sources and updates
    the sensor_values dictionary and reading_history object.

    Args:
        sensor_values (dict): Dictionary to store current formatted sensor values.
        reading_history (ReadingHistory): Object to store historical readings.
        app_config (module): Configuration module (passed as `config` from main).
    """
    logger.debug("Updating all sensor and system data...")

    # Data fetching functions map (Sensor Key -> Function to call)
    # These are general system/sensor reading functions
    data_fetch_map = {
        app_config.SENSOR_TEMPERATURE: sensors.get_temperature,
        app_config.SENSOR_HUMIDITY: sensors.get_humidity,
        app_config.SENSOR_PRESSURE: sensors.get_pressure,
        app_config.SENSOR_ORIENTATION: sensors.get_orientation,
        app_config.SENSOR_ACCELERATION: sensors.get_acceleration,
        app_config.SENSOR_CLOCK: system_info.get_current_time,
        app_config.SENSOR_CPU_USAGE: lambda: system_info.get_cpu_usage()[0], # Only need percent for now
        app_config.SENSOR_MEMORY_USAGE: lambda: system_info.get_memory_usage()[0], # Only need percent
        app_config.SENSOR_DISK_USAGE: lambda: system_info.get_disk_usage()[0], # Only need percent
        app_config.SENSOR_VOLTAGE: system_info.get_voltage_info,
        app_config.SENSOR_BATTERY: lambda: system_info.get_battery_info()[0], # Only need percent
    }

    # Iterate through SENSOR_MODES defined in config
    for sensor_key in app_config.SENSOR_MODES:
        raw_value = None
        display_props = app_config.SENSOR_DISPLAY_PROPERTIES.get(sensor_key, {})
        
        fetch_func = data_fetch_map.get(sensor_key)
        if fetch_func:
            try:
                raw_value = fetch_func()
            except Exception as e:
                logger.error(f"Error fetching data for {sensor_key}: {e}", exc_info=True)
                raw_value = None # Ensure it's None on error
        else:
            logger.warning(f"No data fetch function defined for sensor mode: {sensor_key}")

        # Format the value and update sensor_values dict
        formatted_data = _format_sensor_value(sensor_key, raw_value, display_props)
        sensor_values[sensor_key] = formatted_data
        
        # Add to reading history (use the processed numeric_val)
        # ReadingHistory.add_reading will handle specific logic for ACCELERATION (e.g. if it expects dict or a component)
        # For now, we pass the numeric_val which _format_sensor_value extracts/calculates.
        # If ACCELERATION needs the whole dict for history, this needs adjustment in ReadingHistory or here.
        history_val_to_add = formatted_data['value']
        if sensor_key == app_config.SENSOR_ACCELERATION and isinstance(raw_value, dict):
            # ReadingHistory for ACCELERATION might expect the full dict or a specific component.
            # If SENSOR_DISPLAY_PROPERTIES specifies a component_to_graph, use that. Otherwise, pass raw if it's a dict.
            # For now, add_reading in ReadingHistory handles ACCELERATION dict specifically to get 'x'.
            # We can make this more consistent later.
            history_val_to_add = raw_value # Pass the raw dict if it's ACCELERATION
        
        reading_history.add_reading(sensor_key, history_val_to_add)

    # --- Network Information (Not part of SENSOR_MODES cycle, direct update) --- #
    # These are informational and don't typically go into reading_history for graphing.
    
    # WiFi Info
    wifi_status_val, wifi_ssid_val = system_info.get_wifi_info()
    sensor_values[app_config.INFO_WIFI_STATUS] = {"text": wifi_status_val, "unit": "", "note": "", "value": None}
    sensor_values[app_config.INFO_WIFI_SSID] = {"text": wifi_ssid_val, "unit": "", "note": "", "value": None}

    # Bluetooth Info (replacing cellular)
    bluetooth_status_val, bluetooth_device_val = system_info.get_bluetooth_info()
    sensor_values[app_config.INFO_BLUETOOTH_STATUS] = {"text": bluetooth_status_val, "unit": "", "note": "", "value": None}
    sensor_values[app_config.INFO_BLUETOOTH_DEVICE] = {"text": bluetooth_device_val, "unit": "", "note": "", "value": None}

    # --- Special case for CPU to include temperature as note if available ---
    if app_config.SENSOR_CPU_USAGE in sensor_values:
        _ , cpu_info_details = system_info.get_cpu_usage() # Call again to get the tuple
        if cpu_info_details:
            info_type, info_value = cpu_info_details
            current_note = sensor_values[app_config.SENSOR_CPU_USAGE]["note"]
            new_note = current_note
            if info_type == "temperature":
                new_note = f"Temp: {info_value:.1f}°C"
            elif info_type == "cores":
                new_note = f"Cores: {info_value}"
            if new_note:
                 sensor_values[app_config.SENSOR_CPU_USAGE]["note"] = new_note.strip()

    # --- Special case for Memory and Disk to include Used/Total as note ---
    if app_config.SENSOR_MEMORY_USAGE in sensor_values:
        _p, mem_used, mem_total = system_info.get_memory_usage()
        if mem_used is not None and mem_total is not None:
            sensor_values[app_config.SENSOR_MEMORY_USAGE]["note"] = f"{mem_used:.0f}MB/{mem_total:.0f}MB"
    
    if app_config.SENSOR_DISK_USAGE in sensor_values:
        _p, disk_used, disk_total = system_info.get_disk_usage()
        if disk_used is not None and disk_total is not None:
             sensor_values[app_config.SENSOR_DISK_USAGE]["note"] = f"{disk_used:.1f}GB/{disk_total:.1f}GB"

    # --- Special case for Battery to include status as note ---
    if app_config.SENSOR_BATTERY in sensor_values:
        _percent, battery_status = system_info.get_battery_info()
        if battery_status:
            sensor_values[app_config.SENSOR_BATTERY]["note"] = battery_status

    logger.debug("Data update complete.") 