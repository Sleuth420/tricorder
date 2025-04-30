# --- input/input_handler.py ---
# Handles user input, currently from keyboard.
# Will be adapted for GPIO buttons later.

import pygame
import logging

logger = logging.getLogger(__name__)

def process_input(events, config):
    """
    Processes a list of Pygame events to detect user input, including key holds.

    Args:
        events (list): A list of pygame.event.Event objects.
        config (module): Configuration module with key mappings.

    Returns:
        list: A list of dictionaries, where each dict represents a relevant input event.
              Possible dict types:
              {'type': 'QUIT'}
              {'type': 'KEYDOWN', 'key': pygame_key_code, 'action': mapped_action_or_None}
              {'type': 'KEYUP', 'key': pygame_key_code}
    """
    logger.debug(f"Processing {len(events)} events...")
    results = []
    for event in events:
        logger.debug(f"Processing event: {pygame.event.event_name(event.type)} ({event.type})")
        # Handle window close button
        if event.type == pygame.QUIT:
            logger.info("Input action determined: QUIT (Window Close)")
            results.append({'type': 'QUIT'})
            continue # Process other events too

        # Handle keyboard presses
        if event.type == pygame.KEYDOWN:
            key_code = event.key
            key_name = pygame.key.name(key_code)
            logger.debug(f"KEYDOWN event detected: Code={key_code}, Name='{key_name}'")

            mapped_action = None
            # Standard if/elif check for configured keys
            if key_code == config.KEY_PREV:
                mapped_action = "PREV"
            elif key_code == config.KEY_NEXT:
                mapped_action = "NEXT"
            elif key_code == config.KEY_SELECT:
                mapped_action = "SELECT"
            elif key_code == pygame.K_ESCAPE:
                mapped_action = "QUIT" # Map escape to QUIT action
            # else: (No need for else, mapped_action stays None)

            if mapped_action:
                logger.info(f"Input action mapped for key {key_name}: {mapped_action}")

            results.append({'type': 'KEYDOWN', 'key': key_code, 'action': mapped_action})

        # Handle key releases
        elif event.type == pygame.KEYUP:
            key_code = event.key
            key_name = pygame.key.name(key_code)
            logger.debug(f"KEYUP event detected: Code={key_code}, Name='{key_name}'")
            results.append({'type': 'KEYUP', 'key': key_code})

    # if not results: # Don't log if nothing happened unless debugging verbosely
    #     logger.debug("No relevant input detected in this event batch.")

    return results 