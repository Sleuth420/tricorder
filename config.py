import pygame # Add pygame import for key constants

# --- config.py ---
# Stores configuration constants for the tricorder application

# -- Display Settings --
SCREEN_WIDTH = 800      # Default width (if not fullscreen)
SCREEN_HEIGHT = 600     # Default height (if not fullscreen)
FULLSCREEN = False      # Run in windowed mode?
FPS = 15                # Frames per second/update rate

# -- Colors (RGB Tuples) --
COLOR_BACKGROUND = (0, 0, 0)        # Black
COLOR_FOREGROUND = (0, 255, 70)     # Sickbay Green
COLOR_ACCENT = (255, 200, 0)      # Engineering Gold/Amber
COLOR_ALERT = (255, 0, 0)         # Red Alert (for errors?)
COLOR_FROZEN = (100, 150, 255)    # Light Blue for Frozen Indicator
COLOR_GRAPH_BORDER = (50, 50, 50)  # Dark gray for graph borders
COLOR_GRAPH_GRID = (30, 30, 30)    # Even darker gray for graph grid lines
COLOR_MENU_HEADER = (130, 80, 150)   # Purple header for menus (from image)
COLOR_SELECTED_BG = (40, 40, 40)   # Dark gray background for selected items
COLOR_SELECTED_TEXT = (0, 255, 70) # Bright green for selected text

# -- Sidebar Colors --
COLOR_SIDEBAR_TEMP = (230, 160, 50)   # Temperature (yellow/gold)
COLOR_SIDEBAR_HUMID = (50, 100, 150)  # Humidity (blue)
COLOR_SIDEBAR_PRESS = (130, 80, 150)  # Pressure (purple)
COLOR_SIDEBAR_ORIENT = (50, 100, 100) # Orientation (teal)
COLOR_SIDEBAR_ACCEL = (50, 100, 100)  # Acceleration (teal)
COLOR_SIDEBAR_ALL = (150, 100, 50)    # All Sensors (orange)
COLOR_SIDEBAR_SYSTEM = (80, 80, 120)  # System Info (slate blue)
COLOR_SIDEBAR_SETTINGS = (100, 100, 100)  # Settings (gray)

# -- Content Colors --
COLOR_CELLULAR = (130, 80, 150)      # Cellular (purple)
COLOR_WIFI = (130, 80, 150)          # WiFi (purple)
COLOR_WIFI_ONLINE = (0, 255, 0)      # WiFi online status (green)
COLOR_NETWORK = (255, 0, 0)          # Network name (red)

# -- Fonts --
# (Store font files in a 'fonts' subfolder or use system fonts)
# FONT_PRIMARY_PATH = "fonts/YourRetroFont.ttf" # Example path
FONT_PRIMARY_PATH = None  # Set to None to use Pygame default font
FONT_SIZE_LARGE = 48
FONT_SIZE_MEDIUM = 24
FONT_SIZE_SMALL = 16

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
GRAPH_HISTORY_SIZE = 60  # Number of data points to keep (= seconds at 1 reading/sec)
GRAPH_LINE_WIDTH = 2     # Width of the graph line in pixels
GRAPH_POINT_SIZE = 3     # Size of the data points in pixels

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
