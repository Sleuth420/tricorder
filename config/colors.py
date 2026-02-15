# --- config/colors.py ---
# Color palette and theme definitions for the tricorder application

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
    # Header specific colors
    HARVEST_GOLD = (219, 174, 109)
    ATOMIC_TANGERINE = (255, 156, 99)
    VIKING_BLUE = (93, 192, 211)
    COPPER_ROSE = (156, 107, 110)
    LONDON_HUE = (185, 169, 196)
    EAST_SIDE_PURPLE = (178, 141, 211)
    CALIFORNIA_ORANGE = (254, 143, 1)


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
    HEADER_CORNER_FILL = Palette.ATOMIC_TANGERINE # Color for the filled corner shape
    BORDER_GENERAL = Palette.BLACK          # General border color for UI elements
    BORDER_WIDTH = 1 # General border width for UI elements
    CORNER_CURVE_RADIUS = 24  # Match screen cover's curve (larger radius = gentler); used app-wide

    # Sidebar specific colors (can be a sub-class or dict if it grows more complex)
    SIDEBAR_SYSTEM = Palette.ATOMIC_TANGERINE
    SIDEBAR_TEMP = Palette.HARVEST_GOLD
    SIDEBAR_HUMID = Palette.VIKING_BLUE
    SIDEBAR_PRESS = Palette.COPPER_ROSE
    SIDEBAR_ORIENT = Palette.EAST_SIDE_PURPLE
    SIDEBAR_ACCEL = Palette.LONDON_HUE
    SIDEBAR_ALL = Palette.HARVEST_GOLD # For "All Sensors" view or similar
    SIDEBAR_SETTINGS = Palette.ATOMIC_TANGERINE
    SIDEBAR_SCHEMATICS = Palette.INDIGO # New color for Schematics menu item

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


# -- Legacy Color Variables (for backward compatibility) --
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