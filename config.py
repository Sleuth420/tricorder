import pygame # Add pygame import for key constants

# --- config.py ---
# Stores configuration constants for the tricorder application

# -- Display Settings --
SCREEN_WIDTH = 320      # Default width (if not fullscreen)
SCREEN_HEIGHT = 240     # Default height (if not fullscreen)
FULLSCREEN = True      # Run in windowed mode?
FPS = 30                # Frames per second/update rate

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


# -- Colors --
# Base color palette
class Palette:
    BLACK = (0, 0, 0)
    SICKBAY_GREEN = (0, 255, 70)
    WHITE = (255, 255, 255)
    ENGINEERING_GOLD = (255, 200, 0)
    RED_ALERT = (255, 0, 0)
    FROZEN_BLUE = (100, 150, 255)
    DARK_GREY = (40, 40, 40)
    MEDIUM_GREY = (50, 50, 50)
    LIGHT_GREY = (30, 30, 30) # Renamed from COLOR_GRAPH_GRID for clarity
    PURPLE_MENU_HEADER = (130, 80, 150) # Renamed from COLOR_MENU_HEADER
    PINK = (255, 105, 180)
    ORANGE = (255, 165, 0)
    YELLOW = (255, 255, 0)
    GREEN = (0, 255, 0) # General green, distinct from Sickbay Green if needed
    BLUE = (0, 0, 255)
    INDIGO = (75, 0, 130)
    VIOLET = (238, 130, 238)
    LIGHT_BLUE_INFO = (173, 216, 230) # For info panel text like cellular provider
    DARK_SLATE_BLUE = (72, 61, 139) # Example for secret menu items

# Theme applying palette colors semantically
class Theme:
    BACKGROUND = Palette.BLACK
    FOREGROUND = Palette.SICKBAY_GREEN
    WHITE = Palette.WHITE # Direct use of white
    ACCENT = Palette.ENGINEERING_GOLD
    WARNING = Palette.ENGINEERING_GOLD  # Alias for warning, can be changed later
    ALERT = Palette.RED_ALERT
    FROZEN_INDICATOR = Palette.FROZEN_BLUE

    # Graph specific colors
    GRAPH_BORDER = Palette.MEDIUM_GREY
    GRAPH_GRID = Palette.LIGHT_GREY
    GRAPH_AXIS = Palette.MEDIUM_GREY # New

    # Menu specific colors
    MENU_HEADER_BG = Palette.PURPLE_MENU_HEADER # Background for menu headers
    MENU_SELECTED_BG = Palette.DARK_GREY
    MENU_SELECTED_TEXT = Palette.SICKBAY_GREEN
    # Assuming general menu text might use FOREGROUND or WHITE, define if specific.

    # Header/Corner/Border specific colors
    HEADER_CORNER_FILL = Palette.RED_ALERT # Color for the filled corner shape
    BORDER_GENERAL = Palette.BLACK          # General border color for UI elements
    BORDER_WIDTH = 1 # General border width for UI elements
    CORNER_CURVE_RADIUS = 10 # For rounded corners

    # Sidebar specific colors (can be a sub-class or dict if it grows more complex)
    SIDEBAR_SYSTEM = Palette.RED_ALERT
    SIDEBAR_TEMP = Palette.ORANGE
    SIDEBAR_HUMID = Palette.YELLOW
    SIDEBAR_PRESS = Palette.GREEN
    SIDEBAR_ORIENT = Palette.BLUE
    SIDEBAR_ACCEL = Palette.INDIGO
    SIDEBAR_ALL = Palette.VIOLET # For "All Sensors" view or similar
    SIDEBAR_SETTINGS = Palette.PINK

    # Content-specific colors (e.g., for network info, specific data displays)
    CONTENT_CELLULAR_INFO_BG = Palette.PURPLE_MENU_HEADER # Re-using purple, consider specific name if diverges
    CONTENT_WIFI_INFO_BG = Palette.PURPLE_MENU_HEADER     # Re-using purple
    CONTENT_WIFI_ONLINE_STATUS = Palette.GREEN
    CONTENT_NETWORK_NAME_TEXT = Palette.RED_ALERT # For displaying network names like SSID
    CONTENT_PANEL_TITLE_TEXT = Palette.WHITE # New
    CONTENT_PANEL_HEADER_BG = Palette.DARK_SLATE_BLUE # New, distinct from menu header

    # Secret Menu specific colors
    SECRET_MENU_SIDEBAR_BG = Palette.DARK_SLATE_BLUE # New
    SECRET_MENU_SIDEBAR_TEXT_UNSELECTED = Palette.LIGHT_BLUE_INFO # New


# -- Original Color Variables (now mapped to Theme or Palette) --
# Retaining original variable names for now to minimize immediate refactoring impact elsewhere.
# Ideally, other modules would be updated to use Theme.XYZ directly.
COLOR_BACKGROUND = Theme.BACKGROUND
COLOR_FOREGROUND = Theme.FOREGROUND
COLOR_WHITE = Theme.WHITE
COLOR_ACCENT = Theme.ACCENT
COLOR_ALERT = Theme.ALERT
COLOR_FROZEN = Theme.FROZEN_INDICATOR
COLOR_GRAPH_BORDER = Theme.GRAPH_BORDER
COLOR_GRAPH_GRID = Theme.GRAPH_GRID
COLOR_DARK_GREY = Palette.DARK_GREY # Direct palette use if it's just a shade
COLOR_WARNING = Theme.WARNING
COLOR_MENU_HEADER = Theme.MENU_HEADER_BG # Mapped to new theme name
COLOR_SELECTED_BG = Theme.MENU_SELECTED_BG
COLOR_SELECTED_TEXT = Theme.MENU_SELECTED_TEXT

COLOR_HEADER_CORNER = Theme.HEADER_CORNER_FILL # Mapped to new theme name
COLOR_BORDER = Theme.BORDER_GENERAL # Mapped to new theme name
HEADER_HEIGHT = 30 # Height of header/corner section in menu
# CORNER_CURVE_RADIUS defined in Theme

COLOR_SIDEBAR_SYSTEM = Theme.SIDEBAR_SYSTEM
COLOR_SIDEBAR_TEMP = Theme.SIDEBAR_TEMP
COLOR_SIDEBAR_HUMID = Theme.SIDEBAR_HUMID
COLOR_SIDEBAR_PRESS = Theme.SIDEBAR_PRESS
COLOR_SIDEBAR_ORIENT = Theme.SIDEBAR_ORIENT
COLOR_SIDEBAR_ACCEL = Theme.SIDEBAR_ACCEL
COLOR_SIDEBAR_ALL = Theme.SIDEBAR_ALL
COLOR_SIDEBAR_SETTINGS = Theme.SIDEBAR_SETTINGS

COLOR_CELLULAR = Theme.CONTENT_CELLULAR_INFO_BG # Mapped to new theme name
COLOR_WIFI = Theme.CONTENT_WIFI_INFO_BG         # Mapped to new theme name
COLOR_WIFI_ONLINE = Theme.CONTENT_WIFI_ONLINE_STATUS
COLOR_NETWORK = Theme.CONTENT_NETWORK_NAME_TEXT     # Mapped to new theme name

# -- Fonts --
# (Store font files in a 'fonts' subfolder or use system fonts)
# FONT_PRIMARY_PATH = "fonts/YourRetroFont.ttf" # Example path
FONT_PRIMARY_PATH = "fonts/Minecraftia-Regular.ttf" 
FONT_SIZE_LARGE = 30
FONT_SIZE_MEDIUM = 20
FONT_SIZE_SMALL = 16

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


# -- Sensor Range Configuration --
# Default value ranges for graphing (min, max) for LINE graphs.
# VerticalBarGraph uses its own config from SENSOR_DISPLAY_PROPERTIES.
# Set to None to auto-scale based on observed values if SENSOR_DISPLAY_PROPERTIES doesn't provide an override.
# SENSOR_RANGES = { ... } # This is now redundant and removed.

# -- Graph Settings (Mainly for Line Graphs) --
GRAPH_HISTORY_SIZE = 30  # Number of data points to keep (= seconds at 1 reading/sec)
GRAPH_LINE_WIDTH = 1     # Width of the graph line in pixels
GRAPH_POINT_SIZE = 2     # Size of the data points in pixels

# -- Vertical Bar Graph Configurations --
# This is now part of SENSOR_DISPLAY_PROPERTIES. This old structure can be removed.
# VERTICAL_GRAPH_CONFIG = { ... } # REMOVE THIS

# -- Dashboard Settings --
AUTO_CYCLE_INTERVAL = 5  # Seconds between auto-cycling in dashboard mode

# -- Input Mapping (Keyboard for now) --
# Using 'A' for Previous/Left and 'D' for Next/Right
# Using Enter/Return for Select
KEY_PREV = pygame.K_a   # Use Pygame constant
KEY_NEXT = pygame.K_d   # Use Pygame constant
KEY_SELECT = pygame.K_RETURN # Use Pygame constant

# Joystick "key" constants (arbitrary unique values, not Pygame key codes)
# These will be used by the input_handler to represent joystick events
JOY_UP = 1000
JOY_DOWN = 1001
JOY_LEFT = 1002
JOY_RIGHT = 1003
JOY_PRESS = 1004 # Press of the joystick (middle button)

# Abstract Input Action Names (used by AppState and InputHandler)
# These are the actions the application understands, regardless of input source.
INPUT_ACTION_PREV = "PREV"
INPUT_ACTION_NEXT = "NEXT"
INPUT_ACTION_SELECT = "SELECT"
INPUT_ACTION_QUIT = "QUIT"     # For pygame.QUIT events
INPUT_ACTION_BACK = "BACK"     # For returning from sub-states/menus
INPUT_ACTION_FREEZE = "FREEZE" # For freezing/unfreezing sensor views

# -- Key to Action Mapping --
# This map is used by input_handler.py to translate raw key presses
# into meaningful application actions. This needs to be kept in sync
# with the AppState's expectations for actions.
# Note: Complex actions (like long-press or combos) are handled in AppState.
# This map is for direct, single-key-to-action translations.

KEY_ACTION_MAP = {
    KEY_PREV: INPUT_ACTION_PREV,
    KEY_NEXT: INPUT_ACTION_NEXT,
    KEY_SELECT: INPUT_ACTION_SELECT,
    # Joystick mappings - updated for intuitive navigation
    JOY_UP: INPUT_ACTION_PREV,     # UP = Previous (more intuitive)
    JOY_DOWN: INPUT_ACTION_NEXT,   # DOWN = Next (more intuitive)
    JOY_LEFT: INPUT_ACTION_BACK,   # LEFT = Back (unchanged)
    JOY_RIGHT: INPUT_ACTION_NEXT,  # RIGHT = Next (alternative)
    JOY_PRESS: INPUT_ACTION_SELECT # Press = Select (unchanged)
}

# Input related timing
INPUT_LONG_PRESS_DURATION = 2.0 # Seconds to qualify as a long press for Back action (Adjusted)
SECRET_HOLD_DURATION = 5.0 # Seconds to hold keys for secret menu (Adjusted to a more common value)

# -- Splash Screen --
SPLASH_LOGO_PATH = "images/logo.png"
SPLASH_DURATION_MS = 3000

# -- Action Name Constants (for MenuItem.action_name) --
ACTION_LAUNCH_PONG = "LAUNCH_PONG"
ACTION_LAUNCH_TETRIS = "LAUNCH_TETRIS" # Example for future
ACTION_RETURN_TO_MENU = "RETURN_TO_MENU"

# -- Input Action Name Constants (returned by input_handler) --
INPUT_ACTION_PREV = "PREV"
INPUT_ACTION_NEXT = "NEXT"
INPUT_ACTION_SELECT = "SELECT"
INPUT_ACTION_QUIT = "QUIT"

# -- UI Constants --
MAX_SIDEBAR_WIDTH = 150
CLASSIFIED_TEXT = "CLASSIFIED"
GRAPH_NOT_AVAILABLE_TEXT = "Graph N/A"

# -- GPIO Pins (Placeholder for later) --
# (BCM Pin number for physical buttons when added)
# PIN_PREV = 2
# PIN_NEXT = 3
# PIN_SELECT = 4
