# --- ui/views/settings_view.py ---
# Handles rendering of the settings screen

import pygame
import logging
from ui.components.text_display import render_footer
# import config as app_config # Not strictly needed if config_module is always passed and used

logger = logging.getLogger(__name__)

def draw_settings_view(screen, app_state, fonts, config_module):
    """
    Draw the settings screen content.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state (for frozen status)
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
    """
    screen.fill(config_module.Theme.BACKGROUND)
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    rect = pygame.Rect(0, 0, screen_width, screen_height)

    header_height = config_module.HEADER_HEIGHT # Use config constant
    header_rect = pygame.Rect(rect.left, rect.top, rect.width, header_height)
    pygame.draw.rect(screen, config_module.Theme.BACKGROUND, header_rect) # Use Theme

    font = fonts['small'] # Use 'small' font for header for consistency with other views like system_info
    header_text_str = "Settings"
    if app_state.is_frozen:
        header_text_str += " [FROZEN]"
    header_text_color = config_module.Theme.ACCENT if not app_state.is_frozen else config_module.Theme.FROZEN_INDICATOR # Use Theme
    header_text = font.render(header_text_str, True, header_text_color)
    screen.blit(header_text, (rect.left + 20, header_rect.centery - header_text.get_height() // 2))

    content_y = rect.top + header_height + 20
    footer_height_calc = config_module.FONT_SIZE_SMALL * 3 # For footer space
    content_height = rect.height - header_height - 20 - footer_height_calc # 20 for top padding, 20 for bottom before footer

    settings_panel_rect = pygame.Rect(
        rect.left + 20,
        content_y,
        rect.width - 40,
        content_height
    )

    pygame.draw.rect(screen, config_module.Theme.BACKGROUND, settings_panel_rect) # Use Theme
    pygame.draw.rect(screen, config_module.Theme.ACCENT, settings_panel_rect, config_module.Theme.BORDER_WIDTH)  # Use Theme for border & width

    font_to_use = fonts['medium']
    line_height = font_to_use.get_height() + 20 # Padding between setting lines
    y_offset = settings_panel_rect.top + 20 # Initial y-offset inside the panel
    x_offset = settings_panel_rect.left + 20 # Initial x-offset for text

    # Settings items to display - (attribute_name_in_config, display_label_format)
    # Format string can use {value} placeholder.
    settings_to_display = [
        ("FULLSCREEN", "Fullscreen: {value}"),
        ("AUTO_CYCLE_INTERVAL", "Auto-cycle Interval: {value} seconds"),
        ("FPS", "Framerate: {value} FPS"),
        ("GRAPH_HISTORY_SIZE", "Graph History: {value} seconds"),
        ("INPUT_LONG_PRESS_DURATION", "Long Press: {value}s"),
        ("SECRET_HOLD_DURATION", "Secret Combo: {value}s")
    ]

    for attr_name, label_format in settings_to_display:
        if y_offset + font_to_use.get_height() > settings_panel_rect.bottom - 20: # Check if it fits before drawing
            break # Stop if no more space
        
        value = getattr(config_module, attr_name, "N/A") # Get value from config_module
        
        # Format the value string appropriately (e.g., On/Off for booleans)
        if isinstance(value, bool):
            display_value = "On" if value else "Off"
        else:
            display_value = str(value)
            
        text_to_render = label_format.format(value=display_value)
        setting_surface = font_to_use.render(text_to_render, True, config_module.Theme.FOREGROUND) # Use Theme
        screen.blit(setting_surface, (x_offset, y_offset))
        y_offset += line_height

    key_prev_name = pygame.key.name(config_module.KEY_PREV).upper()
    key_next_name = pygame.key.name(config_module.KEY_NEXT).upper()
    key_select_name = pygame.key.name(config_module.KEY_SELECT).upper()
    action_text = "(Action)" # SELECT still placeholder for settings view
    hint = f"< Hold {key_prev_name}=Menu | {key_select_name}={action_text} | {key_next_name}= - >"

    render_footer(
        screen, hint, fonts,
        config_module.Theme.FOREGROUND, # Use Theme
        screen_width, screen_height
    ) 