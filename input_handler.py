# --- input_handler.py ---
# Handles user input, currently from keyboard.
# Will be adapted for GPIO buttons later.

import pygame  # Need pygame for key constants
import config  # Need config for key mappings


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
            return "QUIT"

        # Handle keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == config.KEY_EXIT:  # Use configured ESC key
                return "QUIT"
            elif event.key == config.KEY_NEXT:  # Use configured RIGHT ARROW key
                print("DEBUG: 'NEXT' input detected")
                return "NEXT"
            elif event.key == config.KEY_PREV:  # Use configured LEFT ARROW key
                print("DEBUG: 'PREV' input detected")
                return "PREV"
            elif event.key == config.KEY_SELECT:  # Use configured ENTER key
                print("DEBUG: 'SELECT' input detected")
                return "SELECT"

    # No relevant input detected in this batch of events
    return None

# --- Placeholder for GPIO implementation ---
# def init_gpio_buttons():
#     """Initialize GPIO buttons using gpiozero."""
#     pass

# def check_gpio_buttons():
#     """Check the state of GPIO buttons (if not using callbacks)."""
#     pass
