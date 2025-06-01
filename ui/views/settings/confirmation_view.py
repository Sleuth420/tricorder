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
    Draw a generic confirmation screen.

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
    rect = pygame.Rect(0, 0, screen_width, screen_height)

    font_large = fonts['large']
    font_medium = fonts['medium']

    # Display the confirmation message
    msg_surface = font_large.render(message, True, config_module.Theme.ACCENT)
    msg_rect = msg_surface.get_rect(center=(screen_width // 2, screen_height // 3))
    screen.blit(msg_surface, msg_rect)

    # Determine selected option (Yes/No). AppState needs to manage this index.
    # For simplicity, assuming a new attribute like app_state.confirmation_option_index (0 for Yes, 1 for No)
    current_selection_idx = getattr(app_state, 'confirmation_option_index', 0) 
    # This attribute would be navigated by INPUT_ACTION_PREV/NEXT in AppState._handle_confirmation_input
    # and selected by INPUT_ACTION_SELECT.

    y_offset = msg_rect.bottom + 50
    option_spacing = 60

    for i, option_text in enumerate(CONFIRMATION_OPTIONS):
        text_color = config_module.Theme.FOREGROUND
        item_width = 150
        item_height = font_medium.get_height() + 20
        
        item_display_rect = pygame.Rect(
            (screen_width // 2) - item_width // 2, 
            y_offset + (i * (item_height + 15)),
            item_width,
            item_height
        )

        if i == current_selection_idx:
            text_color = config_module.Theme.MENU_SELECTED_TEXT
            bg_color_selected = config_module.Theme.MENU_SELECTED_BG
            pygame.draw.rect(screen, bg_color_selected, item_display_rect, border_radius=5)
        else:
            # Draw a border for unselected items to make them look like buttons
            pygame.draw.rect(screen, config_module.Theme.GRAPH_BORDER, item_display_rect, 2, border_radius=5)

        option_surface = font_medium.render(option_text, True, text_color)
        option_rect = option_surface.get_rect(center=item_display_rect.center)
        screen.blit(option_surface, option_rect)

    # Footer hints
    # For confirmation, SELECT maps to current_selection_idx (Yes/No)
    # BACK maps to No/Cancel
    key_prev_name = pygame.key.name(config_module.KEY_PREV).upper() # Or Up/Down for Yes/No toggle
    key_next_name = pygame.key.name(config_module.KEY_NEXT).upper()
    key_select_name = pygame.key.name(config_module.KEY_SELECT).upper()
    key_back_name = "BACK" # Or map to config_module.KEY_BACK if defined
    
    hint = f"< {key_prev_name}/{key_next_name}=Toggle | {key_select_name}=Confirm | Hold {key_prev_name}=Cancel >"
    if current_selection_idx == 0: # "Yes" is selected
        hint = f"< {key_prev_name}/{key_next_name}=Toggle | {key_select_name}=YES | Hold {key_prev_name}=Cancel >"
    else: # "No" is selected
        hint = f"< {key_prev_name}/{key_next_name}=Toggle | {key_select_name}=NO | Hold {key_prev_name}=Cancel >"

    render_footer(
        screen, hint, fonts,
        config_module.Theme.FOREGROUND,
        screen_width, screen_height
    ) 