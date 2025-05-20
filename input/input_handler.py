# --- input/input_handler.py ---
# Handles user input, currently from keyboard.
# Will be adapted for GPIO buttons later.

import pygame
import logging
import config as app_config # For key mappings and action name constants

# Attempt to import sense_hat specific items for joystick
try:
    from sense_hat import ACTION_PRESSED, ACTION_RELEASED, ACTION_HELD
    from data.sensors import sense # Import the global sense object
except ImportError:
    logger.warning("Sense HAT library or sense object not available. Joystick input disabled.")
    sense = None
    ACTION_PRESSED = "pressed" # Define fallbacks if import fails
    ACTION_RELEASED = "released"
    ACTION_HELD = "held"

logger = logging.getLogger(__name__)

# Define a mapping from Pygame keys to action names
# This remains the primary map for keyboard, joystick events are processed separately
KEY_ACTION_MAP = {
    app_config.KEY_PREV: app_config.INPUT_ACTION_PREV,
    app_config.KEY_NEXT: app_config.INPUT_ACTION_NEXT,
    app_config.KEY_SELECT: app_config.INPUT_ACTION_SELECT,
    # Joystick actions are now mapped in config.py as well, but we'll use a more direct approach here for clarity
}

# Mapping from Sense HAT joystick event directions to our "key" constants
SENSE_HAT_DIRECTION_TO_KEY = {
    "up": app_config.JOY_UP,
    "down": app_config.JOY_DOWN,
    "left": app_config.JOY_LEFT,
    "right": app_config.JOY_RIGHT,
    "middle": app_config.JOY_PRESS,
}

def process_input(events, config_module): # config_module is the actual config.py passed in
    """
    Process Pygame events and generate a list of abstract input results.

    Args:
        events (list): List of Pygame events.
        config_module (module): The configuration module (config.py).

    Returns:
        list: A list of dictionaries, each representing an input event or action.
              Example: {'type': 'KEYDOWN', 'key': K_a, 'action': 'PREV'}
                       {'type': 'KEYUP', 'key': K_d, 'action': 'NEXT'}
                       {'type': 'QUIT'}
    """
    results = [] # Store processed input events/actions

    # Process Pygame keyboard events first
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

    # Process Sense HAT joystick events if available
    if sense:
        try:
            joystick_events = sense.stick.get_events()
            for event in joystick_events:
                # We are primarily interested in "pressed" and "released" events
                # "held" might be useful later, but for now, let's keep it simple
                # and consistent with keyboard KEYDOWN/KEYUP.
                
                key = SENSE_HAT_DIRECTION_TO_KEY.get(event.direction)
                if not key: # Unknown direction
                    logger.warning(f"Unknown joystick direction: {event.direction}")
                    continue

                action = config_module.KEY_ACTION_MAP.get(key) # Get mapped action from config.py

                if event.action == ACTION_PRESSED:
                    results.append({
                        'type': 'KEYDOWN', # Treat joystick press like KEYDOWN
                        'key': key,
                        'action': action
                    })
                    logger.debug(f"Joystick KEYDOWN: key={key} (from {event.direction}), action={action}")
                elif event.action == ACTION_RELEASED:
                    results.append({
                        'type': 'KEYUP', # Treat joystick release like KEYUP
                        'key': key,
                        'action': action
                    })
                    logger.debug(f"Joystick KEYUP: key={key} (from {event.direction}), action={action}")
                # Optionally handle ACTION_HELD if needed in the future
                # elif event.action == ACTION_HELD:
                #     logger.debug(f"Joystick HELD: key={key} (from {event.direction}), action={action}")
        except Exception as e:
            logger.error(f"Error reading Sense HAT joystick: {e}", exc_info=True)
            # Potentially set sense to None here if it's a persistent error, or handle more gracefully.

    return results 