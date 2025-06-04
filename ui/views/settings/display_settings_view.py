# --- ui/views/settings/display_settings_view.py ---
# Handles rendering of the display settings screen

import pygame
import logging
from ui.components.text_display import render_footer, render_text
# import config as app_config # For accessing current interval and action names
# We will use config_module passed in, but need options for iteration
from config import AUTO_CYCLE_INTERVAL_OPTIONS # Import directly for iterating options

logger = logging.getLogger(__name__)

# Define available auto-cycle intervals - REMOVED, will import from config
# AUTO_CYCLE_INTERVAL_OPTIONS = [1, 5, 10, 15] # Seconds

def draw_display_settings_view(screen, app_state, fonts, config_module):
    """
    Draw the display settings screen content.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
    """
    screen.fill(config_module.Theme.BACKGROUND)
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    rect = pygame.Rect(0, 0, screen_width, screen_height)

    header_height = config_module.HEADER_HEIGHT
    header_rect = pygame.Rect(rect.left, rect.top, rect.width, header_height)
    pygame.draw.rect(screen, config_module.Theme.BACKGROUND, header_rect)

    font_small = fonts['small']
    header_text_str = "Display Settings"
    header_text_color = config_module.Theme.ACCENT
    header_text = font_small.render(header_text_str, True, header_text_color)
    screen.blit(header_text, (rect.left + 20, header_rect.centery - header_text.get_height() // 2))

    content_y = rect.top + header_height + 20
    
    font_medium = fonts['medium']
    line_height = font_medium.get_height() + 15
    y_offset = content_y + 20

    # Display current setting
    current_interval = config_module.AUTO_CYCLE_INTERVAL # Get current value
    current_text_surface = font_medium.render(f"Current Auto-Cycle: {current_interval}s", True, config_module.Theme.FOREGROUND)
    screen.blit(current_text_surface, (rect.left + 30, y_offset))
    y_offset += line_height + 10

    # Display options
    option_title_surface = font_small.render("Select New Interval:", True, config_module.Theme.FOREGROUND)
    screen.blit(option_title_surface, (rect.left + 30, y_offset))
    y_offset += font_small.get_height() + 10

    # This index should come from app_state, e.g., app_state.display_settings_option_index
    # For now, using a placeholder or assuming it's managed if we add input handling later.
    # current_selection_idx = app_state.display_settings_option_index 
    # (To be added to AppState)
    current_selection_idx = getattr(app_state, 'display_settings_option_index', 0)


    for i, option_value in enumerate(AUTO_CYCLE_INTERVAL_OPTIONS):
        # Handle text formatting for integer vs. string options
        if isinstance(option_value, int):
            option_text = f"{option_value}s"
        else: # It's a string, like "Back to Main Menu"
            option_text = option_value

        text_color = config_module.Theme.FOREGROUND
        
        item_display_rect = pygame.Rect(
            rect.left + 40,
            y_offset,
            rect.width - 80,
            line_height
        )

        if i == current_selection_idx:
            text_color = config_module.Theme.MENU_SELECTED_TEXT
            bg_color_selected = config_module.Theme.MENU_SELECTED_BG
            pygame.draw.rect(screen, bg_color_selected, item_display_rect, border_radius=5)
        
        option_surface = font_medium.render(option_text, True, text_color)
        option_rect = option_surface.get_rect(left=item_display_rect.left + 10, centery=item_display_rect.centery)
        screen.blit(option_surface, option_rect)
        y_offset += line_height

    # Footer hints
    key_prev_name = pygame.key.name(config_module.KEY_PREV).upper()
    key_next_name = pygame.key.name(config_module.KEY_NEXT).upper()
    key_select_name = pygame.key.name(config_module.KEY_SELECT).upper()
    
    hint = ""

    render_footer(
        screen, hint, fonts,
        config_module.Theme.FOREGROUND,
        screen_width, screen_height
    ) 