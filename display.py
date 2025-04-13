# --- display.py ---
# Handles drawing the user interface onto the Pygame screen.

import pygame
import config


# Global dictionary to hold loaded fonts
fonts = {}


def init_display():
    """
    Initializes Pygame and the display window. Loads fonts.

    Returns:
        tuple: (screen_surface, clock_object, loaded_fonts_dict) or (None, None, None) on failure.
    """
    global fonts
    try:
        pygame.init()
        if config.FULLSCREEN:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            pygame.mouse.set_visible(False)
        else:
            screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
        pygame.display.set_caption("tricorder")

        # Load fonts
        try:
            fonts['large'] = pygame.font.Font(config.FONT_PRIMARY_PATH, config.FONT_SIZE_LARGE)
            fonts['medium'] = pygame.font.Font(config.FONT_PRIMARY_PATH, config.FONT_SIZE_MEDIUM)
            fonts['small'] = pygame.font.Font(config.FONT_PRIMARY_PATH, config.FONT_SIZE_SMALL)
            print("Fonts loaded successfully.")
        except Exception as e:
            print(f"Warning: Could not load custom font ({config.FONT_PRIMARY_PATH}): {e}. Using default font.")
            fonts['large'] = pygame.font.SysFont(None, config.FONT_SIZE_LARGE)
            fonts['medium'] = pygame.font.SysFont(None, config.FONT_SIZE_MEDIUM)
            fonts['small'] = pygame.font.SysFont(None, config.FONT_SIZE_SMALL)

        clock = pygame.time.Clock()
        print("Display initialized.")
        return screen, clock, fonts

    except Exception as e:
        print(f"Error initializing display: {e}")
        pygame.quit()
        return None, None, None


def draw_ui(screen, current_mode_name, sensor_value, unit, note, is_frozen):  # Added is_frozen parameter
    """
    Draws the entire UI onto the provided screen surface.

    Args:
        screen (pygame.Surface): The display surface to draw on.
        current_mode_name (str): The name of the currently active sensor mode.
        sensor_value (str): The formatted string of the sensor reading.
        unit (str): The unit for the sensor reading.
        note (str): Any additional note for the reading (always "" for now).
        is_frozen (bool): True if the display is currently frozen.
    """
    if not screen or not fonts:
        print("Error: Screen or fonts not initialized for drawing.")
        return

    # 1. Clear screen / Fill background
    screen.fill(config.COLOR_BACKGROUND)

    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # 2. Draw Mode Name (Top Center) - Add Frozen Indicator if needed
    mode_display_text = current_mode_name
    mode_color = config.COLOR_ACCENT
    if is_frozen:
        mode_display_text += " [FROZEN]"
        mode_color = config.COLOR_FROZEN  # Use a different color for frozen mode title

    try:
        mode_text_surface = fonts['medium'].render(mode_display_text, True, mode_color)
        mode_text_rect = mode_text_surface.get_rect(center=(screen_width // 2, config.FONT_SIZE_MEDIUM * 1.5))
        screen.blit(mode_text_surface, mode_text_rect)
    except Exception as e:
        print(f"Error rendering mode text: {e}")

    # 3. Draw Sensor Value (Middle Center)
    try:
        value_text = f"{sensor_value} {unit}"
        # Optionally change value color when frozen? For now, keep it the same.
        value_color = config.COLOR_FOREGROUND
        value_text_surface = fonts['large'].render(value_text, True, value_color)
        value_text_rect = value_text_surface.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.blit(value_text_surface, value_text_rect)
    except Exception as e:
        print(f"Error rendering sensor value: {e}")

    # 4. Draw Note (Below Value, if present) - Logic unchanged, handles empty note
    if note:
        try:
            note_text_surface = fonts['small'].render(note, True, config.COLOR_ACCENT)
            note_text_rect = note_text_surface.get_rect(center=(screen_width // 2, value_text_rect.bottom + config.FONT_SIZE_SMALL * 1.5))
            screen.blit(note_text_surface, note_text_rect)
        except Exception as e:
            print(f"Error rendering note text: {e}")

    # 5. Draw Button Hints (Bottom Center)
    try:
        # Update hint text slightly to reflect Enter = Freeze/Unfreeze
        hint_text = "< PREV | FREEZE | NEXT >"
        hint_color = config.COLOR_FOREGROUND
        if is_frozen:
            hint_text = "< PREV |UNFREEZE| NEXT >"  # Indicate next action for SELECT
            # hint_color = config.COLOR_FROZEN # Optional: Change hint color when frozen

        hint_text_surface = fonts['small'].render(hint_text, True, hint_color)
        hint_text_rect = hint_text_surface.get_rect(center=(screen_width // 2, screen_height - config.FONT_SIZE_SMALL * 1.5))
        screen.blit(hint_text_surface, hint_text_rect)
    except Exception as e:
        print(f"Error rendering hint text: {e}")

    # Note: pygame.display.flip() is called in the main loop after this function returns
