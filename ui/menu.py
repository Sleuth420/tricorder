# --- ui/menu.py ---
# Handles rendering of the menu system

import pygame
import logging
from ui.components.ui_elements import draw_menu
from ui.components.text_display import render_footer

logger = logging.getLogger(__name__)

def draw_menu_screen(screen, app_state, fonts, config):
    """
    Draw the menu screen.
    
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
    
    # Get current menu items and index
    menu_items = app_state.get_current_menu_items()
    selected_index = app_state.get_current_menu_index()
    
    # Just get the displayable item names
    item_names = [item["name"] for item in menu_items]
    
    # Draw main menu title
    title = "TRICORDER"
    if app_state.menu_stack:
        # We're in a submenu
        title = menu_items[0].get("submenu_title", item_names[0])
    
    # Create menu rectangle (centered on screen, with padding)
    menu_width = min(screen_width - 40, 500)  # Max width of 500px or screen width - 40px
    menu_height = min(screen_height - 80, len(item_names) * 50 + 50)  # Height based on items + header
    
    menu_rect = pygame.Rect(
        (screen_width - menu_width) // 2,
        (screen_height - menu_height) // 2,
        menu_width,
        menu_height
    )
    
    # Set up colors dictionary for menu drawing
    colors = {
        'background': config.COLOR_BACKGROUND,
        'foreground': config.COLOR_FOREGROUND,
        'accent': config.COLOR_ACCENT,
        'menu_header': (80, 0, 100),  # Purple header for retro feel
        'selected_bg': (40, 40, 40),  # Dark gray background for selected item
        'selected_text': config.COLOR_FOREGROUND,  # Bright green for selected text
        'border': (50, 50, 50)  # Gray for borders
    }
    
    # Draw the menu
    draw_menu(screen, menu_rect, item_names, selected_index, fonts, colors, title)
    
    # Draw navigation help at the bottom
    render_footer(
        screen,
        "< PREV | SELECT | NEXT >",
        fonts,
        config.COLOR_FOREGROUND,
        screen_width,
        screen_height
    ) 