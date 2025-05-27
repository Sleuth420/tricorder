# --- ui/views/ship_menu_view.py ---
# Handles the display and logic for the ship selection menu

import pygame
import logging
from models.app_state import STATE_SHIP_MENU

logger = logging.getLogger(__name__)

def draw_ship_menu_view(screen, app_state, fonts, config_module):
    """
    Draw the ship selection menu screen.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config.py)
    """
    screen.fill(config_module.Theme.BACKGROUND)
    
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Draw title
    title_font = fonts['large']
    title_text = "Ship Schematics"
    title_surface = title_font.render(title_text, True, config_module.Theme.ACCENT)
    title_rect = title_surface.get_rect(center=(screen_width // 2, 30))
    screen.blit(title_surface, title_rect)
    
    # Draw menu items
    menu_font = fonts['medium']
    menu_y = title_rect.bottom + 40
    menu_spacing = 40
    
    for i, item in enumerate(app_state.menu_items):
        # Calculate item position
        item_y = menu_y + (i * menu_spacing)
        
        # Draw selection indicator
        if i == app_state.menu_index:
            # Draw selected item background
            selected_bg_rect = pygame.Rect(
                screen_width // 4,
                item_y - 5,
                screen_width // 2,
                menu_font.get_height() + 10
            )
            pygame.draw.rect(screen, config_module.Theme.MENU_SELECTED_BG, selected_bg_rect)
            
            # Draw item text in selected color
            text_color = config_module.Theme.MENU_SELECTED_TEXT
        else:
            # Draw item text in normal color
            text_color = config_module.Theme.FOREGROUND
        
        # Draw item text
        item_surface = menu_font.render(item.name, True, text_color)
        item_rect = item_surface.get_rect(center=(screen_width // 2, item_y))
        screen.blit(item_surface, item_rect)
    
    # Draw footer with controls
    footer_font = fonts['small']
    footer_text = "Use UP/DOWN to select, ENTER to view, ESC to return"
    footer_surface = footer_font.render(footer_text, True, config_module.Theme.FOREGROUND)
    footer_rect = footer_surface.get_rect(center=(screen_width // 2, screen_height - 20))
    screen.blit(footer_surface, footer_rect) 