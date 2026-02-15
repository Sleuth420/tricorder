# --- config/input.py ---
# Input mappings and control settings for the tricorder application
#
# How controls are used:
# 1. Raw events (key, mouse, joystick) are mapped to abstract actions here and in
#    input/input_handler.py: KEY_ACTION_MAP, MOUSE_ACTION_MAP, joystick direction → action.
# 2. Actions are INPUT_ACTION_PREV, INPUT_ACTION_NEXT, INPUT_ACTION_SELECT, INPUT_ACTION_BACK.
# 3. input_manager tracks key/button for long-press and combos (KEY_PREV hold = BACK, etc.).
# 4. app_state and input_router use action names only for routing and game-over (e.g. PREV on
#    game over = quit to menu). Use get_control_labels() for any user-visible key/button text.

import platform
import pygame

# -- Control display style for footers --
# "auto" = use button labels (Left/Middle/Right) on Raspberry Pi, key names (A/D/Enter) elsewhere
# "buttons" = always show Left, Right, Middle, Back (for Pi / joystick when keys not available)
# "keys" = always show key names
CONTROL_DISPLAY_STYLE = "auto"

def _is_raspberry_pi():
    """True if running on Raspberry Pi (physical buttons / joystick, no keyboard labels)."""
    if platform.system() != "Linux":
        return False
    try:
        with open("/proc/cpuinfo", "r") as f:
            return "Raspberry Pi" in f.read()
    except Exception:
        return False

def get_control_labels(use_buttons=None):
    """
    Return display labels for footer hints, adapted to OS/input.
    On Pi: Left, Right, Middle, Back (hold Left). On Windows/dev: A, D, Enter, Back.

    Args:
        use_buttons: If True, use button labels; if False, use key names; if None, use CONTROL_DISPLAY_STYLE / auto.

    Returns:
        dict with keys "prev", "next", "select", "back"
    """
    if use_buttons is None:
        use_buttons = (
            CONTROL_DISPLAY_STYLE == "buttons"
            or (CONTROL_DISPLAY_STYLE == "auto" and _is_raspberry_pi())
        )
    if use_buttons:
        return {
            "prev": "Left",
            "next": "Right",
            "select": "Middle",
            "back": "Back (hold Left)",
        }
    return {
        "prev": pygame.key.name(KEY_PREV).upper(),
        "next": pygame.key.name(KEY_NEXT).upper(),
        "select": pygame.key.name(KEY_SELECT).upper(),
        "back": "Back (hold " + pygame.key.name(KEY_PREV).upper() + ")",
    }

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

# Mouse button constants (using Pygame mouse button constants)
MOUSE_LEFT = 1    # Left mouse button
MOUSE_RIGHT = 3   # Right mouse button  
MOUSE_MIDDLE = 2  # Middle mouse button (scroll wheel click)

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

# Mouse button to action mapping
# Mouse controls replicate keyboard controls exactly
MOUSE_ACTION_MAP = {
    MOUSE_LEFT: INPUT_ACTION_PREV,    # Left click = Previous (like A key)
    MOUSE_RIGHT: INPUT_ACTION_NEXT,   # Right click = Next (like D key)
    MOUSE_MIDDLE: INPUT_ACTION_SELECT # Middle click = Select (like Enter key)
}

# Input related timing
INPUT_LONG_PRESS_DURATION = 2.0 # Seconds to qualify as a long press for Back action (Adjusted)
DEFAULT_SECRET_HOLD_DURATION = 5.0 # Default seconds to hold keys for secret menu
CURRENT_SECRET_COMBO_DURATION = DEFAULT_SECRET_HOLD_DURATION # Current configurable duration
# SECRET_HOLD_DURATION = 5.0 # Original line, commented out or removed

# -- Action Name Constants (for MenuItem.action_name) --
ACTION_LAUNCH_PONG = "LAUNCH_PONG"
ACTION_LAUNCH_TETRIS = "LAUNCH_TETRIS" # Example for future
ACTION_LAUNCH_BREAKOUT = "LAUNCH_BREAKOUT"
ACTION_LAUNCH_SNAKE = "LAUNCH_SNAKE"
ACTION_RETURN_TO_MENU = "RETURN_TO_MENU"
ACTION_GO_TO_MAIN_MENU = "GO_TO_MAIN_MENU" # New action for direct to main menu
ACTION_SELECT_COMBO_DURATION = "SELECT_COMBO_DURATION" # New action
ACTION_TEST_SOUND = "TEST_SOUND" # New action for sound testing

# -- Audio Configuration --
AUDIO_ENABLED = True
AUDIO_FREQUENCY = 22050
AUDIO_BUFFER_SIZE = 512
SOUND_EFFECTS_PATH = "assets/sounds/"

# -- GPIO Pins (Placeholder for later) --
# (BCM Pin number for physical buttons when added)
# PIN_PREV = 2
# PIN_NEXT = 3
# PIN_SELECT = 4 