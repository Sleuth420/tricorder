# --- config/input.py ---
# Input mappings and control settings for the tricorder application

import pygame

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

# Input related timing
INPUT_LONG_PRESS_DURATION = 2.0 # Seconds to qualify as a long press for Back action (Adjusted)
SECRET_HOLD_DURATION = 5.0 # Seconds to hold keys for secret menu (Adjusted to a more common value)

# -- Action Name Constants (for MenuItem.action_name) --
ACTION_LAUNCH_PONG = "LAUNCH_PONG"
ACTION_LAUNCH_TETRIS = "LAUNCH_TETRIS" # Example for future
ACTION_RETURN_TO_MENU = "RETURN_TO_MENU"

# -- GPIO Pins (Placeholder for later) --
# (BCM Pin number for physical buttons when added)
# PIN_PREV = 2
# PIN_NEXT = 3
# PIN_SELECT = 4 