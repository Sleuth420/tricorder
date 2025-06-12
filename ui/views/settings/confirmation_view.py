# --- ui/views/settings/confirmation_view.py ---
# Handles rendering of a generic confirmation screen

import pygame
import logging
from ui.components.text_display import render_footer, render_text
import config as app_config

logger = logging.getLogger(__name__)

CONFIRMATION_OPTIONS = ["Yes", "No"] # Or "Confirm", "Cancel"

def draw_confirmation_view(screen, app_state, fonts, config_module, message="Are you sure?"):
    """
    Draw a generic confirmation screen with consistent styling.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state (for selected option)
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        message (str): The confirmation message to display
    """
    screen.fill(config_module.Theme.BACKGROUND)
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    font_large = fonts['large']
    font_medium = fonts['medium']

    # Display the confirmation message with viking blue header color for consistency
    msg_surface = font_large.render(message, True, config_module.Palette.VIKING_BLUE)
    msg_rect = msg_surface.get_rect(center=(screen_width // 2, screen_height // 3))
    screen.blit(msg_surface, msg_rect)

    # Get selected option from app_state
    current_selection_idx = getattr(app_state, 'confirmation_option_index', 0) 

    y_offset = msg_rect.bottom + 60
    item_spacing = 15  # Tighter spacing like our other menus

    for i, option_text in enumerate(CONFIRMATION_OPTIONS):
        text_color = config_module.Theme.FOREGROUND
        is_selected = (i == current_selection_idx)
        
        # Create item rectangle - centered like our list menus
        item_width = 120
        item_height = font_medium.get_height() + 15
        item_rect = pygame.Rect(
            (screen_width // 2) - (item_width // 2), 
            y_offset + (i * (item_height + item_spacing)),
            item_width,
            item_height
        )

        if is_selected:
            text_color = config_module.Theme.MENU_SELECTED_TEXT
            # Draw left-pointing arrow like our list menus
            arrow_x = item_rect.right + 10
            arrow_y = item_rect.centery
            arrow_size = 16
            arrow_points = [
                (arrow_x, arrow_y),  # Left point (tip)
                (arrow_x + arrow_size, arrow_y - arrow_size // 2),  # Top right
                (arrow_x + arrow_size, arrow_y + arrow_size // 2)   # Bottom right
            ]
            pygame.draw.polygon(screen, config_module.Theme.ACCENT, arrow_points)
        else:
            # Draw subtle border for unselected items
            pygame.draw.rect(screen, config_module.Theme.GRAPH_BORDER, item_rect, 1, border_radius=5)

        # Render option text - centered like our list menus
        option_surface = font_medium.render(option_text, True, text_color)
        option_rect = option_surface.get_rect(center=item_rect.center)
        screen.blit(option_surface, option_rect)

    # No footer for simple confirmation view - keeps it clean 