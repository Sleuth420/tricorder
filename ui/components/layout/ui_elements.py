# --- ui/components/ui_elements.py ---
# Provides reusable UI drawing functions

import pygame
import logging

logger = logging.getLogger(__name__)

def draw_panel(screen, rect, title, fonts, colors, ui_scaler=None):
    """
    Draws a bordered panel with a title bar.
    Callers should pass rects derived from ui_scaler content areas when using scaling.

    Args:
        screen (pygame.Surface): The surface to draw on.
        rect (pygame.Rect): The rectangle defining the panel's bounds.
        title (str): The title text for the panel.
        fonts (dict): Dictionary of loaded Pygame fonts (expects 'small' or 'medium').
        colors (dict): Dictionary of color information for the panel.
                       Expected keys: 'background', 'border', 'title', 'title_text'
        ui_scaler (UIScaler, optional): If provided, title bar padding and border use scaled values.

    Returns:
        pygame.Rect: The rectangle representing the content area of the panel (below the title bar).
    """
    panel_bg_color = colors.get('background', (30, 30, 30))
    border_color = colors.get('border', (100, 100, 100))
    title_bar_color = colors.get('title', (50, 50, 50))
    title_text_color = colors.get('title_text', (255, 255, 255))
    font_to_use = fonts.get('small', fonts.get('medium'))
    title_padding = ui_scaler.padding("small") if ui_scaler else 8
    border_width = max(1, ui_scaler.scale(2)) if ui_scaler else 2

    pygame.draw.rect(screen, panel_bg_color, rect)
    pygame.draw.rect(screen, border_color, rect, border_width)

    title_bar_height = font_to_use.get_height() + title_padding
    title_bar_rect = pygame.Rect(rect.left, rect.top, rect.width, title_bar_height)

    # Draw title bar background
    pygame.draw.rect(screen, title_bar_color, title_bar_rect)
    pygame.draw.rect(screen, border_color, title_bar_rect, border_width)

    # Draw title text
    title_surface = font_to_use.render(title.upper(), True, title_text_color)
    title_pos = (
        title_bar_rect.left + (title_bar_rect.width - title_surface.get_width()) // 2, # Centered Horizontally
        title_bar_rect.top + (title_bar_height - title_surface.get_height()) // 2  # Centered Vertically
    )
    screen.blit(title_surface, title_pos)

    # Define content area (below title bar)
    content_rect = pygame.Rect(
        rect.left, 
        rect.top + title_bar_height, 
        rect.width, 
        rect.height - title_bar_height
    )
    return content_rect

# -- Removed draw_menu_item and draw_menu functions --
# These were likely part of an older menu system and are no longer used.
# The current menu is drawn by ui/menu.py::draw_menu_screen
# and ui/views/secret_games_view.py::_draw_secret_sidebar

# def draw_menu_item(screen, item_text, rect, is_selected, fonts, colors):
#     ...

# def draw_menu(screen, menu_items, selected_index, rect, fonts, colors):
#     ... 