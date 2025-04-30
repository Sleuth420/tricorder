import pygame # Add pygame import for key constants

# --- config.py ---
# Stores configuration constants for the tricorder application

# -- Display Settings --
SCREEN_WIDTH = 320      # Default width (if not fullscreen)
SCREEN_HEIGHT = 240     # Default height (if not fullscreen)
FULLSCREEN = False      # Run in windowed mode?
FPS = 15                # Frames per second/update rate

# -- Colors (RGB Tuples) --
COLOR_BACKGROUND = (0, 0, 0)        # Black
COLOR_FOREGROUND = (0, 255, 70)     # Sickbay Green
COLOR_ACCENT = (255, 200, 0)      # Engineering Gold/Amber (Used elsewhere?)
COLOR_ALERT = (255, 0, 0)         # Red Alert (for errors?)
COLOR_FROZEN = (100, 150, 255)    # Light Blue for Frozen Indicator
COLOR_GRAPH_BORDER = (50, 50, 50)  # Dark gray for graph borders
COLOR_GRAPH_GRID = (30, 30, 30)    # Even darker gray for graph grid lines
COLOR_MENU_HEADER = (130, 80, 150)   # Purple header for menus (Used in draw_panel?)
COLOR_SELECTED_BG = (40, 40, 40)   # Dark gray background for selected items
COLOR_SELECTED_TEXT = (0, 255, 70) # Bright green for selected text

# -- Header/Corner/Sidebar Layout --
HEADER_HEIGHT = 30
CORNER_CURVE_RADIUS = 25
BORDER_WIDTH = 1

# -- Header/Corner Color --
COLOR_HEADER_CORNER = (255, 165, 0)   # Orange

# -- Border Color --
COLOR_BORDER = (0, 0, 0) # Black

# -- Sidebar Colors --
COLOR_SIDEBAR_SYSTEM = (255, 165, 0)    # Orange (Matches Header)
COLOR_SIDEBAR_TEMP = (220, 160, 80)     # Greeny-orange
COLOR_SIDEBAR_HUMID = (100, 180, 200)   # Aqua blue / light blueish
COLOR_SIDEBAR_PRESS = (100, 70, 80)     # Purpleish brown
COLOR_SIDEBAR_ORIENT = (180, 150, 200)  # Light purple
COLOR_SIDEBAR_ACCEL = (255, 180, 100)   # Light orange
COLOR_SIDEBAR_ALL = (255, 220, 0)       # Yellow
COLOR_SIDEBAR_SETTINGS = (255, 165, 0)  # Orange (Matches Header)

# -- Content Colors --
COLOR_CELLULAR = (130, 80, 150)      # Cellular (purple)
COLOR_WIFI = (130, 80, 150)          # WiFi (purple)
COLOR_WIFI_ONLINE = (0, 255, 0)      # WiFi online status (green)
COLOR_NETWORK = (255, 0, 0)          # Network name (red)

# -- Fonts --
# (Store font files in a 'fonts' subfolder or use system fonts)
# FONT_PRIMARY_PATH = "fonts/YourRetroFont.ttf" # Example path
FONT_PRIMARY_PATH = None  # Set to None to use Pygame default font
FONT_SIZE_LARGE = 24
FONT_SIZE_MEDIUM = 14
FONT_SIZE_SMALL = 10

# -- Sensor Modes --
# List of sensor modes the user can cycle through
SENSOR_MODES = [
    "TEMPERATURE", "HUMIDITY", "PRESSURE", "ORIENTATION", "ACCELERATION", 
    "CLOCK", "CPU_USAGE", "MEMORY_USAGE", "DISK_USAGE"
]

# -- Sensor Range Configuration --
# Default value ranges for graphing (min, max)
# These help to make graphs more useful by setting consistent scales
# Set to None to auto-scale based on observed values
SENSOR_RANGES = {
    "TEMPERATURE": (0, 100),      # Celsius: typical room temp range
    "HUMIDITY": (0, 100),         # Percent: full range of humidity
    "PRESSURE": (950, 1050),      # hPa/millibars: typical atmospheric pressure
    "ORIENTATION": (None, None),  # Auto-scale for orientation values
    "ACCELERATION": (-4, 4),      # G-force range: typical for handheld movement
    "CPU_USAGE": (0, 100),        # Percentage range
    "MEMORY_USAGE": (0, 100),     # Percentage range
    "DISK_USAGE": (0, 100),       # Percentage range
}

# -- Graph Settings --
GRAPH_HISTORY_SIZE = 30  # Number of data points to keep (= seconds at 1 reading/sec)
GRAPH_LINE_WIDTH = 1     # Width of the graph line in pixels
GRAPH_POINT_SIZE = 2     # Size of the data points in pixels

# -- Dashboard Settings --
AUTO_CYCLE_INTERVAL = 5  # Seconds between auto-cycling in dashboard mode

# -- Input Mapping (Keyboard for now) --
# Using 'A' for Previous/Left and 'D' for Next/Right
# Using Enter/Return for Select
KEY_PREV = pygame.K_a   # Use Pygame constant
KEY_NEXT = pygame.K_d   # Use Pygame constant
KEY_SELECT = pygame.K_RETURN # Use Pygame constant

# -- GPIO Pins (Placeholder for later) --
# (BCM Pin number for physical buttons when added)
# PIN_PREV = 2
# PIN_NEXT = 3
# PIN_SELECT = 4

# -- Secret Menu --
SECRET_HOLD_DURATION = 5.0 # Seconds to hold keys for secret menu

# -- Input --
INPUT_LONG_PRESS_DURATION = 0.75 # Seconds to qualify as a long press for Back action
