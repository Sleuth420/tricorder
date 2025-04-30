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
    Structured into distinct rectangular parts: Corner (TEMP RED), Header, Sidebar Items.
    """
    # Clear screen with background color
    screen.fill(config.COLOR_BACKGROUND)

    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # Ensure we are in the MENU state to draw this layout
    if app_state.current_state != "MENU":
        logger.warning(f"draw_menu_screen called unexpectedly in state: {app_state.current_state}")
        return

    # Define dimensions and colors using config
    sidebar_width = min(screen_width // 4, 150)
    header_height = config.HEADER_HEIGHT # Use constant from config
    header_color = config.COLOR_HEADER_CORNER # Use new Orange constant
    corner_color = config.COLOR_HEADER_CORNER # Corner uses same Orange constant
    curve_radius = config.CORNER_CURVE_RADIUS # Use constant from config

    # Get menu items and selected index
    menu_items = app_state.get_current_menu_items()
    selected_index = app_state.get_current_menu_index()

    # --- Part 1: Draw Corner Rectangle (Distinct block, Orange) ---
    corner_rect = pygame.Rect(0, 0, sidebar_width, header_height)
    # Apply rounding only to the top-left corner
    pygame.draw.rect(screen, corner_color, corner_rect, border_top_left_radius=curve_radius)
    # Draw border outline (should respect rounding)
    pygame.draw.rect(screen, config.COLOR_BORDER, corner_rect, width=config.BORDER_WIDTH, border_top_left_radius=curve_radius)

    # --- Part 2: Draw Header Bar (Starts AFTER sidebar width, Orange) ---
    header_rect = pygame.Rect(sidebar_width, 0, screen_width - sidebar_width, header_height)
    pygame.draw.rect(screen, header_color, header_rect)
    # Draw border outline
    pygame.draw.rect(screen, config.COLOR_BORDER, header_rect, width=config.BORDER_WIDTH)

    # --- Part 3: Draw Sidebar Items (Starts BELOW header height) ---
    sidebar_content_y_start = header_height # Items start below the header/corner
    sidebar_content_height = screen_height - header_height
    sidebar_items_area = pygame.Rect(0, sidebar_content_y_start, sidebar_width, sidebar_content_height)

    if menu_items: # Avoid division by zero
        item_height = sidebar_content_height // len(menu_items)
        for i, item in enumerate(menu_items):
            item_rect = pygame.Rect(
                sidebar_items_area.left,
                sidebar_content_y_start + (i * item_height),
                sidebar_items_area.width,
                item_height
            )

            # Draw the background using the color_key from the item
            try:
                item_bg_color = getattr(config, item["color_key"])
            except (AttributeError, KeyError):
                logger.warning(f"Color key '{item.get('color_key')}' not found for '{item.get('name')}'. Using default.")
                item_bg_color = config.COLOR_ACCENT # Fallback color
            pygame.draw.rect(screen, item_bg_color, item_rect)
            # Draw border outline for item
            pygame.draw.rect(screen, config.COLOR_BORDER, item_rect, width=config.BORDER_WIDTH)

            # Draw the category name
            font = fonts['medium']
            text_surface = font.render(item["name"], True, (255, 255, 255)) # White text
            text_pos = (item_rect.left + 10, item_rect.centery - text_surface.get_height() // 2)
            screen.blit(text_surface, text_pos)

            # Draw selection indicator if this item is selected
            if i == selected_index:
                # Draw a white border indicator
                border_width = 3
                selection_rect = pygame.Rect(
                    item_rect.left + border_width // 2,
                    item_rect.top + border_width // 2,
                    item_rect.width - border_width,
                    item_rect.height - border_width
                )
                pygame.draw.rect(screen, (255, 255, 255), selection_rect, border_width)

    # --- Part 4: Draw Main Content Area --- (Below header, right of sidebar)
    main_content_rect = pygame.Rect(
        sidebar_width,
        header_height, # Start below the header
        screen_width - sidebar_width,
        screen_height - header_height # Adjust height
    )
    # Use the dedicated system info view function, passing the adjusted content rect
    # Tell it NOT to draw its own footer, as we will draw the correct MENU footer
    draw_system_info_view(screen, app_state, {}, fonts, config, main_content_rect, draw_footer=False)

    # --- Part 5: Draw Footer --- (For the overall menu screen)
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

# REMOVED _draw_sidebar function - logic integrated above
# def _draw_sidebar(screen, rect, menu_items, selected_index, fonts, config, header_height):
#    ...

# REMOVED _draw_system_info function - moved to ui/views/system_info_view.py

# REMOVED _draw_settings function - moved to ui/views/settings_view.py 