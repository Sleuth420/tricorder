# --- input_handler.py ---
# Handles user input, currently from keyboard.
# Will be adapted for GPIO buttons later.

import pygame  # Need pygame for key constants
import config  # Need config for key mappings
import logging # Add logging import

# Get a logger for this module
logger = logging.getLogger(__name__)

def process_input(events):
    """
    Processes a list of Pygame events to detect user input.

    Args:
        events (list): A list of pygame.event.Event objects.

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
                logger.debug("Input detected: NEXT") # Changed from print
                return "NEXT"
            elif event.key == config.KEY_PREV:
                logger.debug("Input detected: PREV") # Changed from print
                return "PREV"
            elif event.key == config.KEY_SELECT:
                logger.debug("Input detected: SELECT") # Changed from print
                return "SELECT"
            # Check for fallback/alternative keys (e.g., arrows if A/D aren't preferred)
            # Remove the explicit check for KEY_EXIT unless you re-add it to config
            # elif event.key == pygame.K_ESCAPE: # Example: Check for ESC key
            #     logger.debug("Input detected: QUIT (Escape Key)")
            #     return "QUIT"

    # No relevant input detected in this batch of events
    return None

# --- Placeholder for GPIO implementation ---
# def init_gpio_buttons():
#     """Initialize GPIO buttons using gpiozero."""
#     try:
#         # ... GPIO setup ...
#         logger.info("GPIO buttons initialized.")
#     except Exception as e:
#         logger.error(f"Error initializing GPIO buttons: {e}", exc_info=True)

# def check_gpio_buttons():
#     """Check the state of GPIO buttons (if not using callbacks)."""
#     # ... check buttons ...
#     if button_pressed:
#         logger.debug(f"GPIO Input detected: {button_name}")
#         return action
#     return None
