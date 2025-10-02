# --- ui/views/settings/update_view.py ---
# Handles rendering of the update settings screen

import pygame
import platform
import logging
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
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Add update available header if needed
    if hasattr(app_state, 'update_available') and app_state.update_available:
        header_text = "[UPDATE AVAILABLE]"
        header_surface = fonts['medium'].render(header_text, True, config_module.Theme.ALERT)
        screen.blit(header_surface, (20, 20))
        
        # Show commit count
        commit_text = f"{app_state.commits_behind} commits behind"
        commit_surface = fonts['small'].render(commit_text, True, config_module.Theme.FOREGROUND)
        screen.blit(commit_surface, (20, 45))
        
        # Adjust other content down
        info_y = 70
    else:
        info_y = 20
    
    # Display system information at the top
    font_small = fonts['small']
    
    # Use UIScaler for responsive spacing if available
    if ui_scaler:
        if not (hasattr(app_state, 'update_available') and app_state.update_available):
            info_y = ui_scaler.margin("medium")
        line_spacing = ui_scaler.margin("small")
        section_spacing = ui_scaler.margin("large")
        
        # Debug logging for update view layout
        if ui_scaler.debug_mode:
            logger.info(f"🎨 UpdateView: screen={screen_width}x{screen_height}, info_y={info_y}px, spacing={line_spacing}px")
    else:
        # Fallback to original calculations
        if not (hasattr(app_state, 'update_available') and app_state.update_available):
            info_y = 20
        line_spacing = 3
        section_spacing = 15
    
    # Current version
    current_version = update_info['current_version']
    version_text = f"Current: {current_version.get('build_number', 'Unknown')}"
    version_surface = font_small.render(version_text, True, config_module.Theme.FOREGROUND)
    screen.blit(version_surface, (20, info_y))
    info_y += version_surface.get_height() + line_spacing
    
    # Platform info
    platform_text = f"Platform: {update_info['platform']}"
    if update_info['is_raspberry_pi']:
        platform_text += " (Raspberry Pi)"
    platform_surface = font_small.render(platform_text, True, config_module.Theme.FOREGROUND)
    screen.blit(platform_surface, (20, info_y))
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
            screen.blit(config_surface, (20, info_y))
            info_y += config_surface.get_height() + (line_spacing * 2)
    
    # Last check result
    if update_info['last_check_result']:
        check_color = config_module.COLOR_ACCENT if update_info['update_available'] else config_module.Theme.FOREGROUND
        check_surface = font_small.render(update_info['last_check_result'], True, check_color)
        screen.blit(check_surface, (20, info_y))
        info_y += check_surface.get_height() + section_spacing
    
    # Now draw the menu starting below the info section
    menu_start_y = info_y + ui_scaler.margin("medium") if ui_scaler else info_y + 10
    
    # Temporarily adjust screen for the menu component
    menu_screen = screen.subsurface(pygame.Rect(0, menu_start_y, screen_width, screen_height - menu_start_y))
    
    # Use the shared list menu component for the options
    draw_simple_list_menu(
        screen=menu_screen,
        title="System Updates",
        menu_items=menu_items,
        selected_index=current_selection_index,
        fonts=fonts,
        config_module=config_module,
        footer_hint=None,  # No footer for this view
        ui_scaler=ui_scaler
    ) 