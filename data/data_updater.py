# --- data/data_updater.py ---
# Handles fetching data from various sources and updating models

import logging

# Import specific data fetching functions
from . import sensors
from . import system_info

logger = logging.getLogger(__name__)

def update_all_data(sensor_values, reading_history, config):
    """
    Fetches data from all configured sources (sensors, system info) and updates
    the sensor_values dictionary and reading_history object.

    Args:
        sensor_values (dict): Dictionary to store current formatted sensor values.
        reading_history (ReadingHistory): Object to store historical readings.
        config (module): Configuration module.
    """
    logger.debug("Updating all sensor and system data...")

    # --- Sense HAT Sensors --- #

    # Temperature
    temp = sensors.get_temperature()
    if temp is not None:
        sensor_values["TEMPERATURE"] = (f"{temp:.1f}", "°C", "")
        reading_history.add_reading("TEMPERATURE", temp)
    else:
        sensor_values["TEMPERATURE"] = ("Error", "", "Sensor N/A")
        reading_history.add_reading("TEMPERATURE", None)

    # Humidity
    humidity = sensors.get_humidity()
    if humidity is not None:
        sensor_values["HUMIDITY"] = (f"{humidity:.1f}", "%", "")
        reading_history.add_reading("HUMIDITY", humidity)
    else:
        sensor_values["HUMIDITY"] = ("Error", "", "Sensor N/A")
        reading_history.add_reading("HUMIDITY", None)

    # Pressure
    pressure = sensors.get_pressure()
    if pressure is not None:
        sensor_values["PRESSURE"] = (f"{pressure:.1f}", "mbar", "")
        reading_history.add_reading("PRESSURE", pressure)
    else:
        sensor_values["PRESSURE"] = ("Error", "", "Sensor N/A")
        reading_history.add_reading("PRESSURE", None)

    # Orientation
    orientation = sensors.get_orientation()
    if orientation is not None:
        value_str = f"P:{orientation['pitch']:.0f} R:{orientation['roll']:.0f}"
        sensor_values["ORIENTATION"] = (value_str, "deg", "")
        # Just store pitch for graphing
        reading_history.add_reading("ORIENTATION", orientation['pitch'])
    else:
        sensor_values["ORIENTATION"] = ("Error", "", "Sensor N/A")
        reading_history.add_reading("ORIENTATION", None)

    # Acceleration
    acceleration = sensors.get_acceleration()
    if acceleration is not None:
        value_str = f"X:{acceleration['x']:.2f} Y:{acceleration['y']:.2f}"
        note = f"Z:{acceleration['z']:.2f}G"
        sensor_values["ACCELERATION"] = (value_str, "G", note)
        reading_history.add_reading("ACCELERATION", acceleration)
    else:
        sensor_values["ACCELERATION"] = ("Error", "", "Sensor N/A")
        reading_history.add_reading("ACCELERATION", None)

    # --- System Information --- #

    # Clock
    now = system_info.get_current_time()
    if now is not None:
        value_str = now.strftime("%H:%M:%S")
        note = now.strftime("%a %d %b %Y")
        sensor_values["CLOCK"] = (value_str, "", note)
        reading_history.add_reading("CLOCK", None)  # No numeric data to graph
    else:
        sensor_values["CLOCK"] = ("Error", "", "Clock N/A")
        reading_history.add_reading("CLOCK", None)

    # CPU Usage
    cpu_percent, cpu_info = system_info.get_cpu_usage()
    if cpu_percent is not None:
        value_str = f"{cpu_percent:.1f}"
        note = ""
        if cpu_info:
            info_type, info_value = cpu_info
            if info_type == "temperature":
                note = f"Temp: {info_value:.1f}°C"
            elif info_type == "cores":
                note = f"Cores: {info_value}"

        sensor_values["CPU_USAGE"] = (value_str, "%", note)
        reading_history.add_reading("CPU_USAGE", cpu_percent)
    else:
        sensor_values["CPU_USAGE"] = ("N/A", "%", "psutil N/A") # Shorter note
        reading_history.add_reading("CPU_USAGE", None)

    # Memory Usage
    mem_percent, mem_used, mem_total = system_info.get_memory_usage()
    if mem_percent is not None:
        value_str = f"{mem_percent:.1f}"
        note = f"{mem_used:.0f}MB/{mem_total:.0f}MB"
        sensor_values["MEMORY_USAGE"] = (value_str, "%", note)
        reading_history.add_reading("MEMORY_USAGE", mem_percent)
    else:
        sensor_values["MEMORY_USAGE"] = ("N/A", "%", "psutil N/A")
        reading_history.add_reading("MEMORY_USAGE", None)

    # Disk Usage
    disk_percent, disk_used, disk_total = system_info.get_disk_usage()
    if disk_percent is not None:
        value_str = f"{disk_percent:.1f}"
        note = f"{disk_used:.1f}GB/{disk_total:.1f}GB"
        sensor_values["DISK_USAGE"] = (value_str, "%", note)
        reading_history.add_reading("DISK_USAGE", disk_percent)
    else:
        sensor_values["DISK_USAGE"] = ("N/A", "%", "psutil N/A")
        reading_history.add_reading("DISK_USAGE", None)

    logger.debug("Data update complete.") 