# --- ui/views/settings/update_view.py ---
# Handles rendering of the update settings screen

import pygame
import platform
import logging
import time
import math
from ui.components.menus.list_menu_base import draw_simple_list_menu
from ui.components.text.text_display import render_footer, render_text

logger = logging.getLogger(__name__)

def draw_update_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the update settings screen content using the shared list menu component.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
        ui_scaler (UIScaler): The UI scaler for scaling the screen
    """
    # Get update information
    update_info = app_state.update_manager.get_update_info()
    update_options = update_info['options']
    current_selection_index = update_info['selected_index']
    
    # Extract menu items from update options
    menu_items = [option['name'] for option in update_options]
    
    # For update view, we need to show system info above the menu
    # We'll draw it manually first, then use the list menu component
    screen.fill(config_module.Theme.BACKGROUND)
    if ui_scaler:
        screen_width = ui_scaler.screen_width
        screen_height = ui_scaler.screen_height
        safe_rect = ui_scaler.get_safe_area_rect() if ui_scaler.safe_area_enabled else None
    else:
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        safe_rect = None
    # Use safe area left so text is not cut off by curved bezel
    header_inset = max(ui_scaler.margin("small"), ui_scaler.get_safe_area_margins()["left"]) if (ui_scaler and ui_scaler.safe_area_enabled) else (ui_scaler.margin("small") if ui_scaler else 20)
    if hasattr(app_state, 'update_available') and app_state.update_available:
        header_text = "[UPDATE AVAILABLE]"
        header_surface = fonts['medium'].render(header_text, True, config_module.Theme.ALERT)
        screen.blit(header_surface, (header_inset, header_inset))
        commit_text = f"{app_state.commits_behind} commits behind"
        commit_surface = fonts['small'].render(commit_text, True, config_module.Theme.FOREGROUND)
        small_margin = ui_scaler.margin("small") if ui_scaler else 5
        commit_y = header_inset + (header_surface.get_height() or 0) + small_margin
        screen.blit(commit_surface, (header_inset, commit_y))
        info_y = commit_y + (commit_surface.get_height() or 0) + small_margin
    else:
        info_y = ui_scaler.margin("medium") if ui_scaler else 20
    
    # Display system information at the top
    font_small = fonts['small']
    
    if ui_scaler:
        line_spacing = ui_scaler.margin("small")
        section_spacing = ui_scaler.margin("large")
        if ui_scaler.debug_mode:
            logger.info(f"🎨 UpdateView: screen={screen_width}x{screen_height}, info_y={info_y}px, spacing={line_spacing}px")
    else:
        line_spacing = 3
        section_spacing = 15
    left_inset = max(ui_scaler.margin("small"), ui_scaler.get_safe_area_margins()["left"]) if (ui_scaler and ui_scaler.safe_area_enabled) else (ui_scaler.margin("small") if ui_scaler else 20)
    current_version = update_info['current_version']
    version_text = f"Current: {current_version.get('build_number', 'Unknown')}"
    version_surface = font_small.render(version_text, True, config_module.Theme.FOREGROUND)
    screen.blit(version_surface, (left_inset, info_y))
    info_y += version_surface.get_height() + line_spacing
    
    # Platform info
    platform_text = f"Platform: {update_info['platform']}"
    if update_info['is_raspberry_pi']:
        platform_text += " (Raspberry Pi)"
    platform_surface = font_small.render(platform_text, True, config_module.Theme.FOREGROUND)
    screen.blit(platform_surface, (left_inset, info_y))
    info_y += platform_surface.get_height() + line_spacing
    
    # System config status if on Raspberry Pi
    system_config = update_info.get('system_config_status', {})
    if system_config and update_info['is_raspberry_pi']:
        available_configs = len(system_config.get('available', []))
        total_configs = available_configs + len(system_config.get('missing', []))
        
        if total_configs > 0:
            config_color = config_module.COLOR_ACCENT if available_configs == total_configs else config_module.COLOR_DARK_GREY
            config_text = f"System Configs: {available_configs}/{total_configs} available"
            config_surface = font_small.render(config_text, True, config_color)
            screen.blit(config_surface, (left_inset, info_y))
            info_y += config_surface.get_height() + (line_spacing * 2)
    
    # Last check result
    if update_info['last_check_result']:
        check_color = config_module.COLOR_ACCENT if update_info['update_available'] else config_module.Theme.FOREGROUND
        check_surface = font_small.render(update_info['last_check_result'], True, check_color)
        screen.blit(check_surface, (left_inset, info_y))
        info_y += check_surface.get_height() + section_spacing
    
    # Now draw the menu starting below the info section
    menu_start_y = info_y + (ui_scaler.margin("medium") if ui_scaler else 10)
    
    # Calculate available height for menu items
    bottom_margin = ui_scaler.margin("small") if ui_scaler else 20
    available_height = screen_height - menu_start_y - bottom_margin
    
    # Draw menu items manually without the header since we already have content above (use safe area width/center)
    content_width = safe_rect.width if safe_rect else screen_width
    content_center_x = safe_rect.centerx if safe_rect else (screen_width // 2)
    _draw_update_menu_items(
        screen, menu_items, current_selection_index, fonts, config_module,
        menu_start_y, screen_width, available_height, ui_scaler,
        content_width=content_width, content_center_x=content_center_x
    )


def _draw_update_menu_items(screen, menu_items, selected_index, fonts, config_module, 
                           start_y, screen_width, available_height, ui_scaler=None,
                           content_width=None, content_center_x=None):
    """
    Draw menu items without header for the update view.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        menu_items (list): List of menu item names
        selected_index (int): Currently selected item index
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        start_y (int): Y position to start drawing menu items
        screen_width (int): Width of the screen
        available_height (int): Available height for menu items
        ui_scaler (UIScaler): UI scaler for scaling calculations
        content_width (int, optional): Width to constrain items (safe area width)
        content_center_x (int, optional): Center X for items (safe area center)
    """
    if content_width is None:
        content_width = screen_width
    if content_center_x is None:
        content_center_x = screen_width // 2
    current_time = time.time()
    
    # Calculate item dimensions
    font_medium = fonts['medium']
    item_text_height = font_medium.get_height()
    
    # Use UIScaler for responsive dimensions if available
    if ui_scaler:
        item_height_padding = ui_scaler.padding("medium")
        item_spacing = ui_scaler.margin("small")
    else:
        item_height_padding = 20
        item_spacing = 15
    
    effective_item_height = item_text_height + item_height_padding
    
    # Calculate how many items can fit
    max_visible_items = max(1, available_height // (effective_item_height + item_spacing))
    
    # Handle scrolling if needed
    total_items = len(menu_items)
    if total_items == 0:
        return
    
    # Calculate scroll offset to keep selected item visible
    scroll_offset = 0
    if total_items > max_visible_items:
        ideal_position = max_visible_items // 2
        scroll_offset = max(0, selected_index - ideal_position)
        scroll_offset = min(scroll_offset, total_items - max_visible_items)
    
    visible_start = scroll_offset
    visible_end = min(total_items, visible_start + max_visible_items)
    
    # Draw menu items
    y_offset = start_y + 20  # Add some top margin
    
    for i in range(visible_start, visible_end):
        item_text = menu_items[i]
        is_selected = (i == selected_index)
        
        # Determine colors and styling
        text_color = config_module.Theme.FOREGROUND
        if is_selected:
            text_color = config_module.Theme.MENU_SELECTED_TEXT
        
        # Create item rectangle - center all items within content (safe) area
        item_width = min(400, content_width - 60)
        item_rect = pygame.Rect(
            content_center_x - (item_width // 2), y_offset - (item_height_padding // 2),
            item_width, effective_item_height
        )
        
        # Draw selection arrow for selected item
        if is_selected:
            # Draw animated arrow
            arrow_x = item_rect.right + 10
            arrow_y = item_rect.centery
            arrow_size = 16
            
            # Add animation to the arrow
            color_intensity = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(current_time * 3.0))
            arrow_color = tuple(min(255, int(c * color_intensity)) for c in config_module.Theme.ACCENT)
            
            arrow_points = [
                (arrow_x, arrow_y),  # Left point (tip)
                (arrow_x + arrow_size, arrow_y - arrow_size // 2),  # Top right
                (arrow_x + arrow_size, arrow_y + arrow_size // 2)   # Bottom right
            ]
            pygame.draw.polygon(screen, arrow_color, arrow_points)
        
        # Render item text with breathing effect for selected item
        if is_selected:
            breathing_scale = 1.0 + 0.12 * (0.5 + 0.5 * math.sin(current_time * 2.5))
            text_color = tuple(min(255, int(c * breathing_scale)) for c in text_color)
        
        item_surface = font_medium.render(item_text, True, text_color)
        text_rect = item_surface.get_rect(center=item_rect.center)
        screen.blit(item_surface, text_rect)
        
        y_offset += effective_item_height + item_spacing
    
    # Draw scroll indicators if needed
    if total_items > max_visible_items:
        if visible_start > 0:
            up_indicator = "↑"
            up_surface = font_medium.render(up_indicator, True, config_module.Theme.ACCENT)
            up_rect = up_surface.get_rect(center=(content_center_x, start_y + 5))
            screen.blit(up_surface, up_rect)
        
        if visible_end < total_items:
            down_indicator = "↓"
            down_surface = font_medium.render(down_indicator, True, config_module.Theme.ACCENT)
            down_rect = down_surface.get_rect(center=(content_center_x, y_offset + 10))
            screen.blit(down_surface, down_rect) 