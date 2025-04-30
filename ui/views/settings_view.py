# --- ui/views/settings_view.py ---
# Handles rendering of the settings screen

import pygame
import logging
from ui.components.text_display import render_footer

logger = logging.getLogger(__name__)

def draw_settings_view(screen, app_state, fonts, config):
    """
    Draw the settings screen content.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state (for frozen status)
        fonts (dict): Dictionary of loaded fonts
        config (module): Configuration module
    """
    screen.fill(config.COLOR_BACKGROUND)
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    rect = pygame.Rect(0, 0, screen_width, screen_height)

    # Draw header
    header_height = 30
    header_rect = pygame.Rect(rect.left, rect.top, rect.width, header_height)
    pygame.draw.rect(screen, config.COLOR_BACKGROUND, header_rect)

    # Draw header text
    font = fonts['small']
    header_text_str = "Settings"
    if app_state.is_frozen:
        header_text_str += " [FROZEN]"
    header_text = font.render(header_text_str, True, config.COLOR_ACCENT if not app_state.is_frozen else config.COLOR_FROZEN)
    screen.blit(header_text, (rect.left + 20, header_rect.centery - header_text.get_height() // 2))

    # Calculate content area
    content_y = rect.top + header_height + 20
    content_height = rect.height - header_height - 40 - config.FONT_SIZE_SMALL * 3 # Reserve footer space

    # Settings panel
    settings_rect = pygame.Rect(
        rect.left + 20,
        content_y,
        rect.width - 40,
        content_height
    )

    # Draw settings background
    pygame.draw.rect(screen, config.COLOR_BACKGROUND, settings_rect)
    pygame.draw.rect(screen, config.COLOR_ACCENT, settings_rect, 1)  # Border

    # Determine font size based on available space
    font_to_use = fonts['medium']
    line_height = font_to_use.get_height() + 20

    # Draw settings options (currently read-only display)
    y_offset = settings_rect.top + 20

    # Fullscreen setting
    fullscreen_text = f"Fullscreen: {'On' if config.FULLSCREEN else 'Off'}"
    fullscreen_surface = font_to_use.render(fullscreen_text, True, config.COLOR_FOREGROUND)
    screen.blit(fullscreen_surface, (settings_rect.left + 20, y_offset))
    y_offset += line_height

    # Auto-cycle interval setting
    cycle_text = f"Auto-cycle Interval: {config.AUTO_CYCLE_INTERVAL} seconds"
    cycle_surface = font_to_use.render(cycle_text, True, config.COLOR_FOREGROUND)
    screen.blit(cycle_surface, (settings_rect.left + 20, y_offset))
    y_offset += line_height

    # FPS setting
    fps_text = f"Framerate: {config.FPS} FPS"
    fps_surface = font_to_use.render(fps_text, True, config.COLOR_FOREGROUND)
    screen.blit(fps_surface, (settings_rect.left + 20, y_offset))
    y_offset += line_height

    # Graph history setting
    history_text = f"Graph History: {config.GRAPH_HISTORY_SIZE} seconds"
    history_surface = font_to_use.render(history_text, True, config.COLOR_FOREGROUND)
    screen.blit(history_surface, (settings_rect.left + 20, y_offset))

    # Draw footer
    # Note: SELECT currently just toggles freeze in AppState, no settings are applied yet.
    key_prev_name = pygame.key.name(config.KEY_PREV).upper()
    key_next_name = pygame.key.name(config.KEY_NEXT).upper()
    key_select_name = pygame.key.name(config.KEY_SELECT).upper()

    # SELECT action is placeholder (Freeze/Unfreeze) for now
    action_text = "(Action)"
    hint = f"< Hold {key_prev_name}=Menu | {key_select_name}={action_text} | {key_next_name}= - >"

    render_footer(
        screen,
        hint,
        fonts,
        config.COLOR_FOREGROUND,
        screen_width,
        screen_height
    ) 