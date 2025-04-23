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
    for event in events:
        # Handle window close button
        if event.type == pygame.QUIT:
            logger.debug("Input detected: QUIT (Window Close)")
            return "QUIT"

        # Handle keyboard presses
        if event.type == pygame.KEYDOWN:
            # Check for configured keys FIRST
            if event.key == config.KEY_NEXT:
                logger.debug("Input detected: NEXT")
                return "NEXT"
            elif event.key == config.KEY_PREV:
                logger.debug("Input detected: PREV")
                return "PREV"
            elif event.key == config.KEY_SELECT:
                logger.debug("Input detected: SELECT")
                return "SELECT"
            # Check for Escape key for Quit
            elif event.key == pygame.K_ESCAPE:
                logger.debug("Input detected: QUIT (Escape Key)")
                return "QUIT"

    # No relevant input detected in this batch of events
    return None 