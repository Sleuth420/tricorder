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

# -- Fonts --
# (Store font files in a 'fonts' subfolder or use system fonts)
# FONT_PRIMARY_PATH = "fonts/YourRetroFont.ttf" # Example path
FONT_PRIMARY_PATH = None  # Set to None to use Pygame default font
FONT_SIZE_LARGE = 48
FONT_SIZE_MEDIUM = 24
FONT_SIZE_SMALL = 16

# -- Sensor Modes --
# List of sensor modes the user can cycle through
SENSOR_MODES = ["TEMPERATURE", "HUMIDITY", "PRESSURE", "ORIENTATION"]

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
