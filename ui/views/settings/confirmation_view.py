# --- ui/views/settings/confirmation_view.py ---
# Handles rendering of a generic confirmation screen

import pygame
import logging
from ui.components.text.text_display import render_footer, render_text
import config as app_config

logger = logging.getLogger(__name__)

CONFIRMATION_OPTIONS = ["Yes", "No"] # Or "Confirm", "Cancel"

def draw_confirmation_view(screen, app_state, fonts, config_module, message="Are you sure?", ui_scaler=None):
    """
    Draw a generic confirmation screen with consistent styling.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state (for selected option)
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        message (str): The confirmation message to display
        ui_scaler (UIScaler, optional): UI scaling system for responsive design
    """
    screen.fill(config_module.Theme.BACKGROUND)
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    font_large = fonts['large']
    font_medium = fonts['medium']

    # Use UIScaler for responsive dimensions if available
    if ui_scaler:
        message_y = screen_height // 3
        options_spacing = ui_scaler.margin("large")
        item_width = ui_scaler.scale(120)
        item_height = font_medium.get_height() + ui_scaler.padding("medium")
        item_spacing = ui_scaler.margin("medium")
        arrow_size = ui_scaler.scale(16)
        arrow_offset = ui_scaler.scale(10)
        
        # Debug logging for confirmation view layout
        if ui_scaler.debug_mode:
            logger.info(f"🎨 ConfirmationView: screen={screen_width}x{screen_height}, item_size={item_width}x{item_height}px")
    else:
        # Fallback to original calculations
        message_y = screen_height // 3
        options_spacing = 60
        item_width = 120
        item_height = font_medium.get_height() + 15
        item_spacing = 15
        arrow_size = 16
        arrow_offset = 10

    # Display the confirmation message with viking blue header color for consistency
    msg_surface = font_large.render(message, True, config_module.Palette.VIKING_BLUE)
    msg_rect = msg_surface.get_rect(center=(screen_width // 2, message_y))
    screen.blit(msg_surface, msg_rect)

    # Get selected option from app_state
    current_selection_idx = getattr(app_state, 'confirmation_option_index', 0) 

    y_offset = msg_rect.bottom + options_spacing

    for i, option_text in enumerate(CONFIRMATION_OPTIONS):
        text_color = config_module.Theme.FOREGROUND
        is_selected = (i == current_selection_idx)
        
        # Create item rectangle - centered like our list menus
        item_rect = pygame.Rect(
            (screen_width // 2) - (item_width // 2), 
            y_offset + (i * (item_height + item_spacing)),
            item_width,
            item_height
        )

        if is_selected:
            text_color = config_module.Theme.MENU_SELECTED_TEXT
            # Draw left-pointing arrow like our list menus
            arrow_x = item_rect.right + arrow_offset
            arrow_y = item_rect.centery
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