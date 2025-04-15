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

# -- Fonts --
# (Store font files in a 'fonts' subfolder or use system fonts)
# FONT_PRIMARY_PATH = "fonts/YourRetroFont.ttf" # Example path
FONT_PRIMARY_PATH = None  # Set to None to use Pygame default font
FONT_SIZE_LARGE = 48
FONT_SIZE_MEDIUM = 24
FONT_SIZE_SMALL = 16

# -- Sensor Modes --
# List of sensor modes the user can cycle through
SENSOR_MODES = ["TEMPERATURE", "HUMIDITY", "PRESSURE", "ORIENTATION", "ACCELERATION", "CLOCK", "CPU_USAGE", "MEMORY_USAGE", "DISK_USAGE"]

# -- Sensor Range Configuration --
# Default value ranges for graphing (min, max)
# These help to make graphs more useful by setting consistent scales
# Set to None to auto-scale based on observed values
SENSOR_RANGES = {
    "TEMPERATURE": (10, 40),      # Celsius: typical room temp range
    "HUMIDITY": (0, 100),         # Percent: full range of humidity
    "PRESSURE": (950, 1050),      # hPa/millibars: typical atmospheric pressure
    "ORIENTATION": (None, None),  # Auto-scale for orientation values
    "ACCELERATION": (-2, 2),      # G-force range: typical for handheld movement
    "CPU_USAGE": (0, 100),        # Percentage range
    "MEMORY_USAGE": (0, 100),     # Percentage range
    "DISK_USAGE": (0, 100),       # Percentage range
}

# -- Graph Settings --
GRAPH_HISTORY_SIZE = 60  # Number of data points to keep (= seconds at 1 reading/sec)
GRAPH_LINE_WIDTH = 2     # Width of the graph line in pixels
GRAPH_POINT_SIZE = 3     # Size of the data points in pixels

# -- Input Mapping (Keyboard for now) --
# Using 'A' for Previous/Left and 'D' for Next/Right
# Using Enter/Return for Select
KEY_PREV = 97   # pygame.K_a ('A' key)  # <<< CHANGED HERE
KEY_NEXT = 100  # pygame.K_d ('D' key)  # <<< CHANGED HERE
KEY_SELECT = 13  # pygame.K_RETURN (Enter key)
# KEY_EXIT commented out - use Ctrl+C in terminal

# -- GPIO Pins (Placeholder for later) --
# (BCM Pin number for physical buttons when added)
# PIN_PREV = 2
# PIN_NEXT = 3
# PIN_SELECT = 4
