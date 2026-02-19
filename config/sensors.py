# --- config/sensors.py ---
# Sensor configurations and display properties for the tricorder application

# -- Mock Sensor Control --
# Controls whether mock sensors provide dynamic data (drift/noise) or static values
# Set to False for testing when you want stable readings
ENABLE_MOCK_SENSOR_DYNAMICS = False

# -- Sense HAT LED Matrix --
# When True, the 8x8 LED panel shows state-based patterns (menu, sensor bar, media play/pause, etc.)
# Set to False to leave the matrix off after init (saves a small amount of I2C traffic)
SENSE_HAT_LED_ENABLED = True

# Display rotation for the 8x8 matrix (and joystick coordinate mapping). Use when the Pi is mounted
# in a different orientation. Values: 0, 90, 180, 270 (degrees). For horizontal mount, 90 or 270
# flips which way is "up" so the display matches the physical orientation.
SENSE_HAT_DISPLAY_ROTATION = 90

# Lid / matrix on when "open": the Sense HAT has no dedicated ambient light sensor, but on Sense HAT
# *v2* the colour sensor provides RGBC (red, green, blue, clear); the "clear" channel is ambient
# light and can be used as a light sensor. Use the "LED matrix (lid open)" toggle in Settings >
# Display Settings for manual control, or set SENSE_HAT_LID_AUTO_FROM_COLOUR = True for automatic
# lid detection from the colour sensor (v2 only).
# When auto is enabled, clear channel above SENSE_HAT_LID_LIGHT_THRESHOLD = lid open (matrix on).
SENSE_HAT_LID_AUTO_FROM_COLOUR = False   # True = use colour sensor clear channel (Sense HAT v2)
SENSE_HAT_LID_LIGHT_THRESHOLD = 50       # Clear value above this = lid open (tune for your build)

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
SENSOR_VOLTAGE = "VOLTAGE"
SENSOR_BATTERY = "BATTERY"

# Network info keys (used in sensor_values, not strictly cycling sensor modes)
INFO_WIFI_STATUS = "WIFI_STATUS"
INFO_WIFI_SSID = "WIFI_SSID"
INFO_CELL_STATUS = "CELL_STATUS"
INFO_CELL_PROVIDER = "CELL_PROVIDER"
INFO_BLUETOOTH_STATUS = "BLUETOOTH_STATUS"
INFO_BLUETOOTH_DEVICE = "BLUETOOTH_DEVICE"

# -- Sensor Modes --
# Environmental/physical sensors for the sensors menu and sweep (user can cycle through these)
# These are actual sensor readings from the Sense HAT only
SENSOR_MODES = [
    SENSOR_TEMPERATURE, SENSOR_HUMIDITY, SENSOR_PRESSURE, SENSOR_ORIENTATION, SENSOR_ACCELERATION
]

# System sensors for the systems view (displayed as status bars)
SYSTEM_SENSOR_MODES = [
    SENSOR_CPU_USAGE, SENSOR_MEMORY_USAGE, SENSOR_VOLTAGE, SENSOR_BATTERY
]

# All sensor modes (for data collection and history tracking)
ALL_SENSOR_MODES = [
    SENSOR_TEMPERATURE, SENSOR_HUMIDITY, SENSOR_PRESSURE, SENSOR_ORIENTATION, SENSOR_ACCELERATION, 
    SENSOR_CLOCK, SENSOR_CPU_USAGE, SENSOR_MEMORY_USAGE, SENSOR_DISK_USAGE, SENSOR_VOLTAGE, SENSOR_BATTERY
]

# -- Sensor Update Frequencies --
# Default update interval for sensors (seconds)
DEFAULT_SENSOR_UPDATE_INTERVAL = 1.0

# -- Sensor Display Properties (New consolidated structure) --
# Defines display name, units, graph type, specific graph config, and update frequency for each sensor mode
# This will drive data_updater.py formatting and ui/views/sensor_view.py graph choices
SENSOR_DISPLAY_PROPERTIES = {
    SENSOR_TEMPERATURE: {
        "display_name": "Env: Temp",
        "units": "°C",
        "graph_type": "VERTICAL_BAR", # "LINE", "VERTICAL_BAR", "NONE"
        "color_key": "SIDEBAR_HUMID", # For AppState MenuItem color
        "update_interval": 0.5,  # Update every 0.5 seconds for responsive vertical bar
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
        "range_override": (0, 50),
        "precision": 1
    },
    SENSOR_HUMIDITY: {
        "display_name": "Env: Humid",
        "units": "%",
        "graph_type": "VERTICAL_BAR",
        "color_key": "SIDEBAR_TEMP",
        "update_interval": 0.5,  # Update every 0.5 seconds for responsive vertical bar
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
        "update_interval": 0.5,  # Update every 0.5 seconds for responsive vertical bar
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
        "update_interval": 1.0,  # Update every 1 second for line graph data
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
        "update_interval": 1.0,  # Update every 1 second for line graph data
        "range_override": (-2, 2), # For line graph of Z component
        "precision": 2
    },
    SENSOR_CLOCK: {
        "display_name": "Clock", # Not usually graphed
        "units": "",
        "graph_type": "NONE",
        "color_key": "SIDEBAR_ALL", # Example color
        "update_interval": 1.0,  # Update every 1 second for clock display
        "range_override": None,
        "precision": 0
    },
    SENSOR_CPU_USAGE: {
        "display_name": "CPU",
        "units": "%",
        "graph_type": "VERTICAL_BAR", # Changed from LINE to VERTICAL_BAR
        "color_key": "SIDEBAR_SYSTEM", # Example color
        "update_interval": 0.5,  # Update every 0.5 seconds for responsive system monitoring
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
        "update_interval": 0.5,  # Update every 0.5 seconds for responsive system monitoring
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
        "update_interval": 2.0,  # Update every 2 seconds (disk usage changes slowly)
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
    },
    SENSOR_VOLTAGE: {
        "display_name": "Voltage",
        "units": "V",
        "graph_type": "NONE", # Don't graph voltage, just display
        "color_key": "SIDEBAR_SYSTEM",
        "update_interval": 2.0,  # Update every 2 seconds (voltage changes slowly)
        "range_override": None,
        "precision": 2
    },
    SENSOR_BATTERY: {
        "display_name": "Battery",
        "units": "%",
        "graph_type": "NONE", # Don't graph battery, just display
        "color_key": "SIDEBAR_SYSTEM",
        "update_interval": 5.0,  # Update every 5 seconds (battery changes very slowly)
        "range_override": None,
        "precision": 0
    }
} 