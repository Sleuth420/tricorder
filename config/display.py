# --- config/display.py ---
# Display and graphics settings for the tricorder application

# -- Display Settings --
SCREEN_WIDTH = 320      # Default width (if not fullscreen)
SCREEN_HEIGHT = 240     # Default height (if not fullscreen)
FULLSCREEN = True      # Run in windowed mode?
FPS = 15                # Frames per second/update rate

# -- Graph Settings (Mainly for Line Graphs) --
GRAPH_HISTORY_SIZE = 30  # Number of data points to keep (= seconds at 1 reading/sec)
GRAPH_LINE_WIDTH = 1     # Width of the graph line in pixels
GRAPH_POINT_SIZE = 2     # Size of the data points in pixels

# -- Splash Screen --
SPLASH_LOGO_PATH = "assets/images/logo.png"
SPLASH_DURATION_MS = 3000 