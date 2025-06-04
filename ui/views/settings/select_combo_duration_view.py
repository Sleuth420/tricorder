# --- ui/views/settings/select_combo_duration_view.py ---
# View for selecting the secret combo hold duration

import pygame
import logging
import config as app_config # For SECRET_COMBO_DURATION_OPTIONS and Theme
from ui.components.text_display import render_footer, render_title # render_text_with_selection_indicator is not standard

logger = logging.getLogger(__name__)

def draw_select_combo_duration_view(screen, app_state, fonts, config_module):
    """
    Draws the screen for selecting the secret combo hold duration.
    """
    screen.fill(config_module.Theme.BACKGROUND)
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # Title
    title_rect = render_title(
        screen,
        "Secret Combo Duration",
        fonts,
        config_module.Theme.ACCENT,
        30, # Y position
        screen_width
    )

    # Display options
    current_y = title_rect.bottom + 40
    item_height = fonts['medium'].get_height() + 20 # Increased padding
    options_list = app_config.SECRET_COMBO_DURATION_OPTIONS
    # Append a "<- Back to Device Settings" option manually for this view
    # Or rely on standard back button handling. For now, let's use standard back.

    for index, option_value in enumerate(options_list):
        is_selected = (index == app_state.combo_duration_selection_index)
        option_text = f"{option_value:.1f}s"

        # Manual rendering similar to display_settings_view
        text_color = config_module.Theme.ACCENT if is_selected else config_module.Theme.FOREGROUND
        indicator_color = config_module.Theme.ACCENT # Color for the selection indicator

        text_surface = fonts['medium'].render(option_text, True, text_color)
        text_rect = text_surface.get_rect(center=(screen_width // 2, current_y))
        
        if is_selected:
            # Draw selection indicator (e.g., brackets or highlight)
            indicator_l_text = ">"
            indicator_r_text = "<"
            indicator_offset = 10 # Distance from text

            # Left indicator
            l_surf = fonts['medium'].render(indicator_l_text, True, indicator_color)
            l_rect = l_surf.get_rect(centery=text_rect.centery, right=text_rect.left - indicator_offset)
            screen.blit(l_surf, l_rect)

            # Right indicator
            r_surf = fonts['medium'].render(indicator_r_text, True, indicator_color)
            r_rect = r_surf.get_rect(centery=text_rect.centery, left=text_rect.right + indicator_offset)
            screen.blit(r_surf, r_rect)
            
        screen.blit(text_surface, text_rect)
        current_y += item_height

    # Footer hints
    key_prev_name = pygame.key.name(config_module.KEY_PREV).upper()
    key_next_name = pygame.key.name(config_module.KEY_NEXT).upper()
    key_select_name = pygame.key.name(config_module.KEY_SELECT).upper()
    
    hint_text = ""

    render_footer(
        screen, hint_text, fonts,
        config_module.Theme.FOREGROUND,
        screen_width, screen_height
    ) 