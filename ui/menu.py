# --- ui/menu.py ---
# Handles rendering of the menu sidebar and the main menu screen layout

import pygame
import logging
from ui.components.ui_elements import draw_panel # Keep draw_panel if needed elsewhere, or remove
from ui.components.text_display import render_footer
# Import the new view functions
from ui.views.system_info_view import draw_system_info_view

logger = logging.getLogger(__name__)

# REMOVED MENU_CATEGORIES - now driven by app_state.menu_items

def draw_menu_screen(screen, app_state, fonts, config):
    """
    Draw the menu screen with sidebar and main content area (System Info).

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config (module): Configuration module

    Returns:
        None
    """
    # Clear screen with background color
    screen.fill(config.COLOR_BACKGROUND)

    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # Ensure we are in the MENU state to draw this layout
    if app_state.current_state != "MENU":
        logger.warning(f"draw_menu_screen called unexpectedly in state: {app_state.current_state}")
        # Optionally draw an error or return, for now just log.
        return

    # Create sidebar dimensions - make it about 1/4 of the screen width
    sidebar_width = min(screen_width // 4, 150)

    # Get menu items and selected index from app_state
    menu_items = app_state.get_current_menu_items()
    selected_index = app_state.get_current_menu_index()

    # Draw the sidebar
    sidebar_rect = pygame.Rect(0, 0, sidebar_width, screen_height)
    _draw_sidebar(screen, sidebar_rect, menu_items, selected_index, fonts, config)

    # Draw the main content area with System Info
    # NOTE: We need sensor_values here, which isn't typically available
    # when just drawing the menu. For now, pass an empty dict.
    # Ideally, the System Info view might fetch its own needed values
    # or main.py passes relevant parts.
    # We will fetch the data in the new data_updater module later.
    main_content_rect = pygame.Rect(sidebar_width, 0, screen_width - sidebar_width, screen_height)
    # Use the dedicated system info view function, passing the content rect
    # Tell it NOT to draw its own footer, as we will draw the correct MENU footer
    draw_system_info_view(screen, app_state, {}, fonts, config, main_content_rect, draw_footer=False)

    # Draw the correct footer for the MENU state
    key_prev_name = pygame.key.name(config.KEY_PREV).upper()
    key_next_name = pygame.key.name(config.KEY_NEXT).upper()
    key_select_name = pygame.key.name(config.KEY_SELECT).upper()
    hint_text = f"< {key_prev_name}=Up | {key_select_name}=Select | {key_next_name}=Down >"

    render_footer(
        screen,
        hint_text,
        fonts,
        config.COLOR_FOREGROUND,
        screen_width,
        screen_height
    )


def _draw_sidebar(screen, rect, menu_items, selected_index, fonts, config):
    """
    Draw the sidebar with menu categories based on AppState menu_items.
    """
    # Calculate item height
    item_height = rect.height // len(menu_items)

    # Draw each menu category
    for i, item in enumerate(menu_items):
        item_rect = pygame.Rect(
            rect.left,
            rect.top + (i * item_height),
            rect.width,
            item_height
        )

        # Draw the background using the color_key from the item
        try:
            color = getattr(config, item["color_key"])
        except (AttributeError, KeyError):
            logger.warning(f"Color key '{item.get('color_key')}' not found in config for item '{item.get('name')}'. Using default.")
            color = config.COLOR_ACCENT # Fallback color

        pygame.draw.rect(screen, color, item_rect)

        # Draw the category name
        font = fonts['small']
        text_surface = font.render(item["name"], True, (255, 255, 255)) # White text
        text_pos = (item_rect.left + 10, item_rect.centery - text_surface.get_height() // 2)
        screen.blit(text_surface, text_pos)

        # Draw selection indicator if this item is selected
        if i == selected_index:
            # Draw a white border indicator
            border_width = 3
            # Indent the selection rectangle slightly for visibility
            selection_rect = pygame.Rect(
                item_rect.left + border_width // 2,
                item_rect.top + border_width // 2,
                item_rect.width - border_width,
                item_rect.height - border_width
            )
            pygame.draw.rect(screen, (255, 255, 255), selection_rect, border_width)

# REMOVED _draw_system_info function - moved to ui/views/system_info_view.py

# REMOVED _draw_settings function - moved to ui/views/settings_view.py 