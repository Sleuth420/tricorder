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