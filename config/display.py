# --- config/display.py ---
# Display and graphics settings for the tricorder application

import platform

# -- Display Settings --
# Use larger window on Windows for development, Pi size for deployment
if platform.system() == "Windows":
    SCREEN_WIDTH = 800      # Larger for development
    SCREEN_HEIGHT = 600     # Larger for development
    FULLSCREEN = False      # Windowed mode for development
else:
    SCREEN_WIDTH = 320      # Pi size
    SCREEN_HEIGHT = 240     # Pi size
    FULLSCREEN = True       # Fullscreen on Pi

FPS = 30                # Frames per second/update rate

# -- Graph Settings (Mainly for Line Graphs) --
GRAPH_HISTORY_SIZE = 30  # Number of data points to keep (= seconds at 1 reading/sec)
GRAPH_LINE_WIDTH = 1     # Width of the graph line in pixels
GRAPH_POINT_SIZE = 2     # Size of the data points in pixels

# -- Splash Screen --
SPLASH_LOGO_PATH = "assets/images/logo.png"
SPLASH_DURATION_MS = 3000  # Original splash duration (not used in loading screen)
LOADING_SCREEN_MIN_DURATION = 5.0  # Minimum loading screen duration in seconds

# -- Media Player (VLC in separate window; UI and navigation in Pygame) --
MEDIA_FOLDER = "assets/media"  # Folder scanned for media files
MEDIA_EXTENSIONS = (".mp3", ".wav", ".ogg", ".mp4", ".avi", ".mov")  # Audio and video (VLC must be installed)

# -- 3D Schematics Zoom Settings --
SCHEMATICS_ZOOM_DEFAULT = 1.0      # Default zoom level (1.0 = normal size)
SCHEMATICS_ZOOM_MIN = 0.2          # Minimum zoom level (0.2 = 20% of normal size)
SCHEMATICS_ZOOM_MAX = 5.0          # Maximum zoom level (5.0 = 500% of normal size)
SCHEMATICS_ZOOM_STEP = 0.1         # Zoom step size for each zoom in/out action
SCHEMATICS_ZOOM_FAST_STEP = 0.3    # Faster zoom step for held actions

# -- Safe Area Settings for Physical Screen Covers --
# These values define the safe area where content should be placed to avoid
# being cut off by curved screen covers or bezels
SAFE_AREA_ENABLED = True           # Enable/disable safe area system
SAFE_AREA_TOP = 15                 # Pixels to avoid at top (for curved top edge)
SAFE_AREA_BOTTOM = 15              # Pixels to avoid at bottom (for curved bottom edge)
SAFE_AREA_LEFT = 20                # Pixels to avoid at left (for curved left edge)
SAFE_AREA_RIGHT = 20               # Pixels to avoid at right (for curved right edge)

# Corner radius for rounded safe area (0 = rectangular safe area)
SAFE_AREA_CORNER_RADIUS = 12       # Pixels - adjust based on your cover's curve

# Alternative: Percentage-based safe areas (overrides pixel values if > 0)
SAFE_AREA_TOP_PERCENT = 0          # 0 = use pixel value, >0 = percentage of screen height
SAFE_AREA_BOTTOM_PERCENT = 0       # 0 = use pixel value, >0 = percentage of screen height
SAFE_AREA_LEFT_PERCENT = 0         # 0 = use pixel value, >0 = percentage of screen width
SAFE_AREA_RIGHT_PERCENT = 0        # 0 = use pixel value, >0 = percentage of screen width 