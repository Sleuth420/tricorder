# --- ui/views/ship_menu_view.py ---
# Handles rendering of the ship selection submenu

import pygame
import logging
from ui.components.text_display import render_footer

logger = logging.getLogger(__name__)

def draw_ship_menu_view(screen, app_state, fonts, config_module):
    """
    Draw the ship selection submenu view - simplified for small display.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        
    Returns:
        None
    """
    screen.fill(config_module.Theme.BACKGROUND)
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    font_large = fonts['large']
    font_medium = fonts['medium']

    # Display the menu title
    title_surface = font_large.render("Ship Schematics", True, config_module.Theme.ACCENT)
    title_rect = title_surface.get_rect(center=(screen_width // 2, screen_height // 5))
    screen.blit(title_surface, title_rect)

    # Get menu items and selection
    menu_items = app_state.get_current_menu_items()
    selected_index = app_state.get_current_menu_index()

    if not menu_items:
        return

    y_offset = title_rect.bottom + 30
    
    for i, item in enumerate(menu_items):
        text_color = config_module.Theme.FOREGROUND
        item_width = 200
        item_height = font_medium.get_height() + 20
        
        item_display_rect = pygame.Rect(
            (screen_width // 2) - item_width // 2, 
            y_offset + (i * (item_height + 15)),
            item_width,
            item_height
        )

        if i == selected_index:
            text_color = config_module.Theme.MENU_SELECTED_TEXT
            bg_color_selected = config_module.Theme.MENU_SELECTED_BG
            pygame.draw.rect(screen, bg_color_selected, item_display_rect, border_radius=5)
        else:
            # Draw a border for unselected items to make them look like buttons
            pygame.draw.rect(screen, config_module.Theme.GRAPH_BORDER, item_display_rect, 2, border_radius=5)

        item_surface = font_medium.render(item.name, True, text_color)
        item_rect = item_surface.get_rect(center=item_display_rect.center)
        screen.blit(item_surface, item_rect)

    # Show instruction
    if menu_items and 0 <= selected_index < len(menu_items):
        selected_ship = menu_items[selected_index]
        if selected_ship.name != "Back":
            instruction_text = "Select to view 3D model"
            instruction_font = fonts.get('small', fonts.get('medium'))
            instruction_surface = instruction_font.render(instruction_text, True, config_module.Theme.FOREGROUND)
            instruction_rect = instruction_surface.get_rect(center=(screen_width // 2, y_offset + len(menu_items) * (item_height + 15) + 20))
            screen.blit(instruction_surface, instruction_rect)

    # Footer hints
    key_prev_name = pygame.key.name(config_module.KEY_PREV).upper()
    key_next_name = pygame.key.name(config_module.KEY_NEXT).upper()
    key_select_name = pygame.key.name(config_module.KEY_SELECT).upper()
    
    selected_name = menu_items[selected_index].name if menu_items and 0 <= selected_index < len(menu_items) else "Item"
    hint_text = f"< {key_prev_name}/{key_next_name}=Navigate | {key_select_name}={selected_name} | Hold {key_prev_name}=Back >"

    render_footer(
        screen, hint_text, fonts,
        config_module.Theme.FOREGROUND,
        screen_width, screen_height
    ) 