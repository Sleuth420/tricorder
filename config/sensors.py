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
        "color_key": "SIDEBAR_TEMP", # For AppState MenuItem color
        "vertical_graph_config": { # Specific to VerticalBarGraph
            "min_val": 0, # Changed from 32
            "max_val": 50, # Changed from 100 (typical SenseHAT range for ambient)
            "normal_range": (18, 28), # Typical room temp
            "critical_low": 10,
            "critical_high": 35,
            "num_ticks": 9, # Adjusted for 0-50 range
            "precision": 1
        },
        "range_override": (0, 50), # For line graph if ever used, or general reference
        "precision": 1
    },
    SENSOR_HUMIDITY: {
        "display_name": "Env: Humid",
        "units": "%",
        "graph_type": "VERTICAL_BAR",
        "color_key": "SIDEBAR_HUMID",
        "vertical_graph_config": {
            "min_val": 0,
        "max_val": 100,
            "normal_range": (30, 70), # Adjusted normal range
            "critical_low": 20,
            "critical_high": 80,
            "num_ticks": 11,
            "precision": 1
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
        "normal_range": (980, 1030),
        "critical_low": 960,
        "critical_high": 1040,
            "num_ticks": 11,
            "precision": 1
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
        "graph_type": "VERTICAL_BAR", # Or LINE if preferred for one axis
        "component_to_graph": "y", # Specify which component for VerticalBarGraph, e.g., 'y' or 'x' or 'z'
        "color_key": "SIDEBAR_ACCEL",
        "vertical_graph_config": { # Example for Y-axis G-force
            "min_val": -2, # Adjusted range for typical motion
            "max_val": 2,
        "normal_range": (-0.5, 0.5),
        "critical_low": -1.5,
        "critical_high": 1.5,
            "num_ticks": 9,
            "precision": 2
        },
        "range_override": (-2, 2), # For line graph of a single component
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
        "graph_type": "LINE", # Or VERTICAL_BAR
        "color_key": "SIDEBAR_SYSTEM", # Example color
        "vertical_graph_config": {
             "min_val": 0, "max_val": 100, "normal_range": (0, 75),
             "critical_low": 0, "critical_high": 90, "num_ticks": 11,
             "precision": 1
        },
        "range_override": (0, 100),
        "precision": 1
    },
    SENSOR_MEMORY_USAGE: {
        "display_name": "Memory",
        "units": "%",
        "graph_type": "LINE", # Or VERTICAL_BAR
        "color_key": "SIDEBAR_SYSTEM", # Example color
         "vertical_graph_config": {
             "min_val": 0, "max_val": 100, "normal_range": (0, 75),
             "critical_low": 0, "critical_high": 90, "num_ticks": 11,
             "precision": 1
        },
        "range_override": (0, 100),
        "precision": 1
    },
    SENSOR_DISK_USAGE: {
        "display_name": "Disk",
        "units": "%",
        "graph_type": "LINE", # Or VERTICAL_BAR
        "color_key": "SIDEBAR_SYSTEM", # Example color
         "vertical_graph_config": {
             "min_val": 0, "max_val": 100, "normal_range": (0, 80),
             "critical_low": 0, "critical_high": 95, "num_ticks": 11,
             "precision": 1
        },
        "range_override": (0, 100),
        "precision": 1
    }
} 