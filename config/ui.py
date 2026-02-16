# --- config/ui.py ---
# UI-specific settings for the tricorder application

# -- Fonts --
# (Store font files in a 'fonts' subfolder or use system fonts)
FONT_PRIMARY_PATH = "assets/fonts/Minecraftia-Regular.ttf"
# FONT_PRIMARY_PATH = "assets/fonts/Finalnew.ttf"
FONT_SIZE_LARGE = 30
FONT_SIZE_MEDIUM = 24  # Reduced from 26 for better layout fit
FONT_SIZE_SMALL = 20   # Legible on small screens (was 18); used for commits behind, version, etc.
FONT_SIZE_TINY = 14    # Legible on small screens (was 12); used for hints, debug overlay

# -- UI Layout Constants --
MAX_SIDEBAR_WIDTH = 150
HEADER_HEIGHT = 30 # Height of header/corner section in menu
CLASSIFIED_TEXT = "CLASSIFIED"
GRAPH_NOT_AVAILABLE_TEXT = "Graph N/A"

# -- Arrow Indicator Configuration --
ARROW_INDICATOR_WIDTH = 20        # Width of the arrow indicator area
ARROW_INDICATOR_SIZE = 20         # Size of the arrow triangle (increased from 12)
ARROW_USE_ITEM_COLOR = True       # Whether to use menu item color or red alert color

# -- Dashboard Settings --
AUTO_CYCLE_INTERVAL = 5  # Seconds between auto-cycling in dashboard mode
AUTO_CYCLE_INTERVAL_OPTIONS = [1, 5, 10, 15, 30, 60, "<- Back to Main Menu"] # Seconds, New, updated string option with simpler arrow

# -- Secret Menu Settings -- (New Section)
SECRET_COMBO_DURATION_OPTIONS = [2.0, 3.0, 5.0, 7.0, 10.0] # Seconds

# -- List Menu Settings --
LIST_MENU_MAX_VISIBLE_ITEMS = 4  # Maximum items visible before scrolling

# -- UI Scaling Settings --
# Base resolution for scaling calculations (Pi target resolution)
UI_BASE_WIDTH = 320
UI_BASE_HEIGHT = 240

# Responsive breakpoints
UI_BREAKPOINT_SMALL = 320   # Pi and similar small screens
UI_BREAKPOINT_MEDIUM = 800  # Development screens
UI_BREAKPOINT_LARGE = 1200  # Large development screens

# Debug Configuration
UI_DEBUG_DRAWING = False    # Enable detailed drawing/layout logging (shows dimensions, positions, etc.)

# Admin / battery life testing
# When True, logs elapsed time, scenario (menu/video/sensors etc.), CPU%, RAM%, temp, battery to a
# separate file at regular intervals. Flush+fsync after each write so data survives power loss when
# the Pi dies from battery drain.
ADMIN_TIMER = True
ADMIN_TIMER_LOG_INTERVAL_SEC = 30   # How often to append a row (balance detail vs. write load)
ADMIN_TIMER_LOG_DIR = "logs"
ADMIN_TIMER_LOG_FILENAME = "battery_timer.log"