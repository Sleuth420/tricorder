# --- input/input_handler.py ---
# Handles user input, currently from keyboard.
# Will be adapted for GPIO buttons later.

import pygame
import logging

logger = logging.getLogger(__name__)

def process_input(events, config):
    """
    Processes a list of Pygame events to detect user input.

    Args:
        events (list): A list of pygame.event.Event objects.
        config (module): Configuration module with key mappings.

    Returns:
        str or None: Returns a string command ("NEXT", "PREV", "SELECT", "QUIT")
                     if a relevant input is detected, otherwise returns None.
    """
    logger.debug(f"Processing {len(events)} events...")
    for event in events:
        logger.debug(f"Processing event: {pygame.event.event_name(event.type)} ({event.type})")
        # Handle window close button
        if event.type == pygame.QUIT:
            logger.info("Input action determined: QUIT (Window Close)")
            return "QUIT"

        # Handle keyboard presses
        if event.type == pygame.KEYDOWN:
            key_code = event.key
            key_name = pygame.key.name(key_code)
            logger.debug(f"KEYDOWN event detected: Code={key_code}, Name='{key_name}'") # Simplified log
            
            action_to_return = None
            
            # Standard if/elif check for configured keys
            if key_code == config.KEY_PREV: # Check for 'a' (pygame.K_a)
                logger.debug(f"Match: KEY_PREV ('{key_name}')")
                action_to_return = "PREV"
            elif key_code == config.KEY_NEXT: # Check for 'd' (pygame.K_d)
                logger.debug(f"Match: KEY_NEXT ('{key_name}')")
                action_to_return = "NEXT"
            elif key_code == config.KEY_SELECT: # Check for Enter (pygame.K_RETURN)
                logger.debug(f"Match: KEY_SELECT ('{key_name}')")
                action_to_return = "SELECT"
            elif key_code == pygame.K_ESCAPE: # Check for Escape
                logger.debug(f"Match: K_ESCAPE ('{key_name}')")
                action_to_return = "QUIT"
            else:
                logger.debug(f"Key {key_code} ('{key_name}') ignored (no action mapped).")
                
            if action_to_return:
                logger.info(f"Input action determined: {action_to_return}")
                return action_to_return

    logger.debug("No relevant action detected in this event batch.")
    # No relevant input detected in this batch of events
    return None 