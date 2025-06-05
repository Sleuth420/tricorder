# --- ui/views/settings/update_view.py ---
# Handles rendering of the update settings screen

import pygame
import platform
import logging
from ui.components.text_display import render_footer, render_text

logger = logging.getLogger(__name__)

def draw_update_view(screen, app_state, fonts, config_module):
    """
    Draw the update settings screen content.

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

    # Header
    font_small = fonts['small']
    header_text_str = "System Updates"
    if app_state.is_frozen:
        header_text_str += " [FROZEN]"
    header_text_color = config_module.Theme.ACCENT
    header_text = font_small.render(header_text_str, True, header_text_color)
    screen.blit(header_text, (rect.left + 20, header_rect.centery - header_text.get_height() // 2))

    content_y = rect.top + header_height + 20
    font_medium = fonts['medium']
    
    # Get update information
    update_info = app_state.update_manager.get_update_info()
    
    # Display current version info
    current_version = update_info['current_version']
    version_text = f"Current: {current_version.get('build_number', 'Unknown')}"
    version_surface = font_small.render(version_text, True, config_module.Theme.FOREGROUND)
    screen.blit(version_surface, (rect.left + 20, content_y))
    content_y += version_surface.get_height() + 5
    
    # Display platform info
    platform_text = f"Platform: {update_info['platform']}"
    if update_info['is_raspberry_pi']:
        platform_text += " (Raspberry Pi)"
    platform_surface = font_small.render(platform_text, True, config_module.Theme.FOREGROUND)
    screen.blit(platform_surface, (rect.left + 20, content_y))
    content_y += platform_surface.get_height() + 5
    
    # Display system config status if on Raspberry Pi
    system_config = update_info.get('system_config_status', {})
    if system_config and update_info['is_raspberry_pi']:
        available_configs = len(system_config.get('available', []))
        total_configs = available_configs + len(system_config.get('missing', []))
        
        if total_configs > 0:
            config_color = config_module.COLOR_ACCENT if available_configs == total_configs else config_module.COLOR_DARK_GREY
            config_text = f"System Configs: {available_configs}/{total_configs} available"
            config_surface = font_small.render(config_text, True, config_color)
            screen.blit(config_surface, (rect.left + 20, content_y))
            content_y += config_surface.get_height() + 10
        else:
            content_y += 10
    else:
        content_y += 10
    
    # Display last check result if available
    if update_info['last_check_result']:
        check_color = config_module.COLOR_ACCENT if update_info['update_available'] else config_module.Theme.FOREGROUND
        check_surface = font_small.render(update_info['last_check_result'], True, check_color)
        screen.blit(check_surface, (rect.left + 20, content_y))
        content_y += check_surface.get_height() + 15
    else:
        content_y += 15

    # Menu items rendering
    item_height_padding = 20
    item_text_height = font_medium.get_height()
    effective_item_height = item_text_height + item_height_padding
    
    update_options = update_info['options']
    current_selection_index = update_info['selected_index']

    y_offset = content_y + 10

    for i, option in enumerate(update_options):
        option_name = option['name']
        
        text_color = config_module.Theme.FOREGROUND
        
        if i == current_selection_index:
            text_color = config_module.Theme.MENU_SELECTED_TEXT
            bg_color_selected = config_module.Theme.MENU_SELECTED_BG
            
            selection_bg_rect = pygame.Rect(
                rect.left + 30, 
                y_offset - (item_height_padding // 2),   
                rect.width - 60,
                effective_item_height 
            )
            pygame.draw.rect(screen, bg_color_selected, selection_bg_rect, border_radius=5)

        option_text_surface = font_medium.render(option_name, True, text_color)
        option_text_rect = option_text_surface.get_rect(
            centery=y_offset + (item_text_height // 2),
            left=rect.left + 40 
        )
        screen.blit(option_text_surface, option_text_rect)
        
        # Show description for selected item
        if i == current_selection_index and 'description' in option:
            desc_text = option['description']
            desc_surface = font_small.render(desc_text, True, config_module.COLOR_DARK_GREY)
            desc_rect = desc_surface.get_rect(
                left=rect.left + 50,
                top=option_text_rect.bottom + 3
            )
            screen.blit(desc_surface, desc_rect)
        
        y_offset += effective_item_height + 10

    # Key hints
    key_prev_name = pygame.key.name(config_module.KEY_PREV).upper()
    key_next_name = pygame.key.name(config_module.KEY_NEXT).upper()
    key_select_name = pygame.key.name(config_module.KEY_SELECT).upper()
    
    hint = f"{key_prev_name}/{key_next_name}: Navigate  {key_select_name}: Select"

    render_footer(
        screen, hint, fonts,
        config_module.Theme.FOREGROUND,
        screen_width, screen_height
    ) 