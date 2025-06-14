# --- config/sensors.py ---
# Sensor configurations and display properties for the tricorder application

# -- Sensor Mode Constants --
SENSOR_TEMPERATURE = "TEMPERATURE"
SENSOR_HUMIDITY = "HUMIDITY"
SENSOR_PRESSURE = "PRESSURE"
SENSOR_ORIENTATION = "ORIENTATION"
SENSOR_ACCELERATION = "ACCELERATION"
SENSOR_CLOCK = "CLOCK"
SENSOR_CPU_USAGE = "CPU_USAGE"
SENSOR_MEMORY_USAGE = "MEMORY_USAGE"
SENSOR_DISK_USAGE = "DISK_USAGE"

# Network info keys (used in sensor_values, not strictly cycling sensor modes)
INFO_WIFI_STATUS = "WIFI_STATUS"
INFO_WIFI_SSID = "WIFI_SSID"
INFO_CELL_STATUS = "CELL_STATUS"
INFO_CELL_PROVIDER = "CELL_PROVIDER"

# -- Sensor Modes --
# List of sensor modes the user can cycle through
SENSOR_MODES = [
    SENSOR_TEMPERATURE, SENSOR_HUMIDITY, SENSOR_PRESSURE, SENSOR_ORIENTATION, SENSOR_ACCELERATION, 
    SENSOR_CLOCK, SENSOR_CPU_USAGE, SENSOR_MEMORY_USAGE, SENSOR_DISK_USAGE
]

# -- Sensor Display Properties (New consolidated structure) --
# Defines display name, units, graph type, and specific graph config for each sensor mode
# This will drive data_updater.py formatting and ui/views/sensor_view.py graph choices
SENSOR_DISPLAY_PROPERTIES = {
    SENSOR_TEMPERATURE: {
        "display_name": "Env: Temp",
        "units": "°C", # Changed from C
        "graph_type": "VERTICAL_BAR", # "LINE", "VERTICAL_BAR", "NONE"
        "color_key": "SIDEBAR_HUMID", # For AppState MenuItem color
        "vertical_graph_config": {
            "min_val": 0,
            "max_val": 50,
            "normal_range": (18, 28),
            "critical_low": 10,
            "critical_high": 35,
            "num_ticks": 5,
            "precision": 1,
            "dynamic_range": True
        },
        "range_override": (0, 50), # For line graph if ever used, or general reference
        "precision": 1
    },
    SENSOR_HUMIDITY: {
        "display_name": "Env: Humid",
        "units": "%",
        "graph_type": "VERTICAL_BAR",
        "color_key": "SIDEBAR_TEMP",
        "vertical_graph_config": {
            "min_val": 0,
        "max_val": 100,
            "normal_range": (30, 70), # Normal humidity range (GREEN zone)
            "critical_low": 20,  # Below this = RED (too dry)
            "critical_high": 80, # Above this = RED (too humid)
            "num_ticks": 5, # Reduced from 11 for better readability
            "precision": 1,
            "dynamic_range": True,  # Enable smart zoom
            "zoom_factor": 0.4,     # Show 40% of full range (40% window)
            "min_zoom_range": 25,   # Never zoom closer than 25% range
            "stability_threshold": 5.0  # Scale only changes when humidity changes by 5%
        },
        "range_override": (0, 100),
        "precision": 1
    },
    SENSOR_PRESSURE: {
        "display_name": "Atmos",
        "units": "mbar", # Changed from hPa for consistency if preferred
        "graph_type": "VERTICAL_BAR",
        "color_key": "SIDEBAR_PRESS",
        "vertical_graph_config": {
        "min_val": 950,
        "max_val": 1050,
        "normal_range": (980, 1030), # Normal atmospheric pressure (GREEN zone)
        "critical_low": 960,   # Below this = RED (very low pressure)
        "critical_high": 1040, # Above this = RED (very high pressure)
            "num_ticks": 5, # Reduced from 11 for better readability
            "precision": 1,
            "dynamic_range": True,  # Enable smart zoom
            "zoom_factor": 0.6,     # Show 60% of full range (60mbar window)
            "min_zoom_range": 40,   # Never zoom closer than 40 mbar range
            "stability_threshold": 8.0  # Scale only changes when pressure changes by 8mbar
        },
        "range_override": (950, 1050),
        "precision": 1
    },
    SENSOR_ORIENTATION: {
        "display_name": "Attitude",
        "units": "deg", # Pitch/Roll/Yaw in degrees
        "graph_type": "LINE", # Use line graph for orientation (e.g., pitch)
        "color_key": "SIDEBAR_ORIENT",
        # No vertical_graph_config needed if graph_type is LINE
        "range_override": (-180, 180), # Example range for pitch/roll for line graph
        "component_to_graph": "pitch",
        "precision": 0
    },
    SENSOR_ACCELERATION: {
        "display_name": "Inertia",
        "units": "G",
        "graph_type": "LINE", # Using line graph for Z component over time
        "component_to_graph": "z", # Using Z component for inertia
        "color_key": "SIDEBAR_ACCEL",
        "range_override": (-2, 2), # For line graph of Z component
        "precision": 2
    },
    SENSOR_CLOCK: {
        "display_name": "Clock", # Not usually graphed
        "units": "",
        "graph_type": "NONE",
        "color_key": "SIDEBAR_ALL", # Example color
        "range_override": None,
        "precision": 0
    },
    SENSOR_CPU_USAGE: {
        "display_name": "CPU",
        "units": "%",
        "graph_type": "VERTICAL_BAR", # Changed from LINE to VERTICAL_BAR
        "color_key": "SIDEBAR_SYSTEM", # Example color
        "vertical_graph_config": {
             "min_val": 0, "max_val": 100, 
             "normal_range": (0, 75),      # Normal CPU usage (GREEN zone)
             "critical_low": 0, "critical_high": 90, # Above 90% = RED (overloaded)
             "num_ticks": 5,
             "precision": 1,
             "dynamic_range": True,  # Enable smart zoom
             "zoom_factor": 0.6,     # Show 60% of full range
             "min_zoom_range": 30,   # Never zoom closer than 30% range
             "stability_threshold": 10.0  # Scale only changes when CPU usage changes by 10%
        },
        "range_override": (0, 100),
        "precision": 1
    },
    SENSOR_MEMORY_USAGE: {
        "display_name": "Memory",
        "units": "%",
        "graph_type": "VERTICAL_BAR", # Changed from LINE to VERTICAL_BAR
        "color_key": "SIDEBAR_SYSTEM", # Example color
         "vertical_graph_config": {
             "min_val": 0, "max_val": 100, 
             "normal_range": (0, 75),      # Normal memory usage (GREEN zone)
             "critical_low": 0, "critical_high": 90, # Above 90% = RED (low memory)
             "num_ticks": 5,
             "precision": 1,
             "dynamic_range": True,  # Enable smart zoom
             "zoom_factor": 0.6,     # Show 60% of full range
             "min_zoom_range": 30,   # Never zoom closer than 30% range
             "stability_threshold": 10.0  # Scale only changes when memory usage changes by 10%
        },
        "range_override": (0, 100),
        "precision": 1
    },
    SENSOR_DISK_USAGE: {
        "display_name": "Disk",
        "units": "%",
        "graph_type": "VERTICAL_BAR", # Changed from LINE to VERTICAL_BAR
        "color_key": "SIDEBAR_SYSTEM", # Example color
         "vertical_graph_config": {
             "min_val": 0, "max_val": 100, 
             "normal_range": (0, 80),      # Normal disk usage (GREEN zone)
             "critical_low": 0, "critical_high": 95, # Above 95% = RED (disk full)
             "num_ticks": 5,
             "precision": 1,
             "dynamic_range": True,  # Enable smart zoom
             "zoom_factor": 0.5,     # Show 50% of full range
             "min_zoom_range": 25,   # Never zoom closer than 25% range
             "stability_threshold": 8.0  # Scale only changes when disk usage changes by 8%
        },
        "range_override": (0, 100),
        "precision": 1
    }
} 