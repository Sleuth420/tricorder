# --- input/input_handler.py ---
# Handles user input, currently from keyboard.
# Will be adapted for GPIO buttons later.

import pygame
import logging
import config as app_config # For key mappings and action name constants

# Initialize logger first
logger = logging.getLogger(__name__)

# Import sense_hat constants first
try:
    from sense_hat import ACTION_PRESSED, ACTION_RELEASED, ACTION_HELD
    logger.info("Sense HAT constants imported successfully")
except ImportError:
    logger.warning("Sense HAT library not available. Joystick input disabled.")
    ACTION_PRESSED = "pressed" # Define fallbacks if import fails
    ACTION_RELEASED = "released"
    ACTION_HELD = "held"

# Define a mapping from Pygame keys to action names
# This remains the primary map for keyboard, joystick events are processed separately
KEY_ACTION_MAP = {
    app_config.KEY_PREV: app_config.INPUT_ACTION_PREV,
    app_config.KEY_NEXT: app_config.INPUT_ACTION_NEXT,
    app_config.KEY_SELECT: app_config.INPUT_ACTION_SELECT,
    # Joystick actions are now mapped in config/input.py as well, but we'll use a more direct approach here for clarity
}

# Mouse button to action mapping (imported from config)
MOUSE_ACTION_MAP = app_config.MOUSE_ACTION_MAP

# Mapping from Sense HAT joystick event directions to our "key" constants
SENSE_HAT_DIRECTION_TO_KEY = {
    # Board is mounted vertically; remap physical directions to logical ones
    "up": app_config.JOY_LEFT,    # physical up is logical left
    "down": app_config.JOY_RIGHT, # physical down is logical right
    "left": app_config.JOY_DOWN,  # physical left is logical down
    "right": app_config.JOY_UP,   # physical right is logical up
    "middle": app_config.JOY_PRESS,
}

# Physical-to-logical direction mapping for the vertical orientation
PHYSICAL_TO_LOGICAL_DIRECTION = {
    "up": "left",     # board physically up now reads as logical left
    "down": "right",  # board physically down now reads as logical right
    "left": "down",   # board physically left now reads as logical down
    "right": "up",    # board physically right now reads as logical up
    "middle": "middle",
}


def _map_physical_to_logical(direction):
    """Translate raw Sense HAT direction to logical direction given board rotation."""
    return PHYSICAL_TO_LOGICAL_DIRECTION.get(direction, direction)

# Initialize sense as None by default at module level
sense = None

def init_joystick():
    """Initialize the Sense HAT joystick if available by using the already initialized sensor object."""
    global sense # This is input_handler.sense
    try:
        # Import the sense object that should have been initialized by main.py
        from data.sensors import sense as system_sense_hat_object
        if system_sense_hat_object is not None:
            sense = system_sense_hat_object # Use the already initialized object
            # The joystick events are cleared in data.sensors.init_sensors(),
            # so no need to clear them again here usually.
            logger.info("Sense HAT joystick support successfully referenced.")
            return True
        else:
            logger.warning("Sense HAT object from data.sensors is None. Joystick not available.")
            sense = None
            return False
    except ImportError:
        logger.error("Could not import sense object from data.sensors. Joystick cannot be initialized.", exc_info=True)
        sense = None
        return False
    except Exception as e:
        logger.error(f"Error during joystick initialization by reference: {e}", exc_info=True)
        sense = None
        return False

def process_input(events, config_module): # config_module is the actual config package passed in
    """
    Process Pygame events and generate a list of abstract input results.

    Args:
        events (list): List of Pygame events.
        config_module (module): The configuration module (config package).

    Returns:
        list: A list of dictionaries, each representing an input event or action.
              Example: {'type': 'KEYDOWN', 'key': K_a, 'action': 'PREV'}
                       {'type': 'KEYUP', 'key': K_d, 'action': 'NEXT'}
                       {'type': 'QUIT'}
    """
    global sense  # Declare global at start of function
    results = [] # Store processed input events/actions

    # Process Pygame keyboard and mouse events first
    for event in events:
        if event.type == pygame.QUIT:
            logger.info("pygame.QUIT event detected by input_handler.")
            results.append({'type': app_config.INPUT_ACTION_QUIT})
        elif event.type == pygame.KEYDOWN:
            action = KEY_ACTION_MAP.get(event.key) # Get action if key is mapped
            results.append({
                'type': 'KEYDOWN',
                'key': event.key,
                'action': action
            })
            logger.debug(f"KEYDOWN event: key={event.key}, mapped_action={action}")
        elif event.type == pygame.KEYUP:
            action = KEY_ACTION_MAP.get(event.key) # Get action if key is mapped
            results.append({
                'type': 'KEYUP',
                'key': event.key,
                'action': action
            })
            logger.debug(f"KEYUP event: key={event.key}, mapped_action={action}")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            action = MOUSE_ACTION_MAP.get(event.button) # Get action if mouse button is mapped
            results.append({
                'type': 'MOUSEDOWN',
                'button': event.button,
                'action': action,
                'pos': event.pos
            })
            logger.debug(f"MOUSEDOWN event: button={event.button}, mapped_action={action}, pos={event.pos}")
        elif event.type == pygame.MOUSEBUTTONUP:
            action = MOUSE_ACTION_MAP.get(event.button) # Get action if mouse button is mapped
            results.append({
                'type': 'MOUSEUP',
                'button': event.button,
                'action': action,
                'pos': event.pos
            })
            logger.debug(f"MOUSEUP event: button={event.button}, mapped_action={action}, pos={event.pos}")

    # Process Sense HAT joystick events if available
    if sense:
        try:
            joystick_events = sense.stick.get_events()
            if joystick_events:
                logger.info(f"Found {len(joystick_events)} joystick events")
                for event in joystick_events:
                    logical_direction = _map_physical_to_logical(event.direction)
                    logger.info(
                        f"Joystick event: physical='{event.direction}', logical='{logical_direction}', action='{event.action}', timestamp={event.timestamp}"
                    )
                    
                    # Process joystick events directly
                    if event.action == ACTION_PRESSED:
                        if logical_direction == "up":
                            results.append({
                                'type': 'JOYSTICK',
                                'direction': 'up',
                                'action': config_module.INPUT_ACTION_PREV
                            })
                        elif logical_direction == "down":
                            results.append({
                                'type': 'JOYSTICK',
                                'direction': 'down',
                                'action': config_module.INPUT_ACTION_NEXT
                            })
                        elif logical_direction == "middle":
                            # For middle press, we send a specific event type that app_state can use
                            # to start a timer for long-press detection.
                            results.append({
                                'type': 'JOYSTICK_MIDDLE_PRESS', # Distinct type
                                'direction': 'middle',
                                # No immediate action here, app_state will decide based on duration
                            })
                        elif logical_direction == "left":
                            results.append({
                                'type': 'JOYSTICK',
                                'direction': 'left',
                                'action': config_module.INPUT_ACTION_BACK
                            })
                        elif logical_direction == "right":
                            results.append({
                                'type': 'JOYSTICK',
                                'direction': 'right',
                                'action': config_module.INPUT_ACTION_NEXT
                            })
                    elif event.action == ACTION_RELEASED:
                        if logical_direction == "up":
                            results.append({
                                'type': 'JOYSTICK_RELEASE',
                                'direction': 'up',
                                'action': config_module.INPUT_ACTION_PREV
                            })
                        elif logical_direction == "down":
                            results.append({
                                'type': 'JOYSTICK_RELEASE',
                                'direction': 'down',
                                'action': config_module.INPUT_ACTION_NEXT
                            })
                        elif logical_direction == "middle":
                            # Signal middle button release
                            results.append({
                                'type': 'JOYSTICK_MIDDLE_RELEASE',
                                'direction': 'middle'
                                # Action determined by app_state based on press duration
                            })
                        elif logical_direction == "left":
                            results.append({
                                'type': 'JOYSTICK_RELEASE',
                                'direction': 'left',
                                'action': config_module.INPUT_ACTION_BACK
                            })
                        elif logical_direction == "right":
                            results.append({
                                'type': 'JOYSTICK_RELEASE',
                                'direction': 'right',
                                'action': config_module.INPUT_ACTION_NEXT
                            })
                    elif event.action == ACTION_HELD: # Handle joystick held state for continuous movement
                        if logical_direction == "up":
                            results.append({
                                'type': 'JOYSTICK_UP_HELD',
                                'direction': 'up' # Action is implied by type
                            })
                        elif logical_direction == "down":
                            results.append({
                                'type': 'JOYSTICK_DOWN_HELD',
                                'direction': 'down' # Action is implied by type
                            })
                        # Add other directions for HELD if needed later (e.g. for other games)
            else:
                logger.debug("No joystick events found")
        except Exception as e:
            logger.error(f"Error reading Sense HAT joystick: {e}", exc_info=True)
            sense = None
            logger.warning("Sense HAT joystick disabled due to error")

    return results 