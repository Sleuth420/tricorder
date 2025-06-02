# --- ui/views/ship_3d_viewer.py ---
# 3D Ship viewer with software-based rendering and SenseHat sensor integration

import pygame
import logging
from ui.components.text_display import render_footer

logger = logging.getLogger(__name__)

def draw_schematics_view(screen, app_state, fonts, config_module):
    """
    Draw the 3D schematics viewer screen.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        
    Returns:
        None
    """
    # Set up the ship model if we have ship selection data
    if app_state.selected_ship_data and 'ship_model' in app_state.selected_ship_data:
        ship_model_key = app_state.selected_ship_data['ship_model']
        current_ship_info = app_state.ship_manager.get_current_ship_info()
        
        # Only change ship if it's different from current
        if not current_ship_info or current_ship_info['model_key'] != ship_model_key:
            success = app_state.ship_manager.set_ship_model(ship_model_key)
            if success:
                logger.info(f"3D Viewer: Loaded ship model '{ship_model_key}'")
            else:
                logger.warning(f"3D Viewer: Failed to load ship model '{ship_model_key}', using default")
    
    # Update rotation from sensors (this happens every frame)
    sensor_updated = app_state.ship_manager.update_rotation_from_sensors()
    
    # Render the 3D ship
    app_state.ship_manager.render_ship(screen, fonts, config_module)
    
    # Draw pause menu if active
    if app_state.schematics_pause_menu_active:
        _draw_pause_menu(screen, app_state, fonts, config_module)
    else:
        # Draw footer with controls when pause menu is not active
        key_prev_name = pygame.key.name(config_module.KEY_PREV).upper()
        key_next_name = pygame.key.name(config_module.KEY_NEXT).upper()
        
        hint_text = f"< {key_prev_name}/{key_next_name}=Rotate | Hold {key_next_name} or Middle Press=Menu >"
        
        render_footer(
            screen,
            hint_text,
            fonts,
            config_module.Theme.FOREGROUND,
            screen.get_width(),
            screen.get_height()
        )

def _draw_pause_menu(screen, app_state, fonts, config_module):
    """Draw the pause menu overlay for the 3D viewer."""
    # Semi-transparent overlay
    overlay = pygame.Surface((screen.get_width(), screen.get_height()))
    overlay.set_alpha(128)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))
    
    # Menu box
    menu_width = 200
    menu_height = 120
    menu_x = (screen.get_width() - menu_width) // 2
    menu_y = (screen.get_height() - menu_height) // 2
    
    menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
    pygame.draw.rect(screen, config_module.Theme.MENU_HEADER_BG, menu_rect)
    pygame.draw.rect(screen, config_module.Theme.ACCENT, menu_rect, 2)
    
    # Menu title
    title_font = fonts.get('medium', fonts.get('small'))
    title_text = "3D VIEWER MENU"
    title_surface = title_font.render(title_text, True, config_module.Theme.FOREGROUND)
    title_rect = title_surface.get_rect(centerx=menu_rect.centerx, y=menu_rect.y + 10)
    screen.blit(title_surface, title_rect)
    
    # Menu options
    option_font = fonts.get('small', fonts.get('medium'))
    options = [
        "Toggle Mode",
        "Back to Ship Menu", 
        "Resume"
    ]
    
    option_y_start = title_rect.bottom + 15
    option_height = 20
    
    for i, option in enumerate(options):
        option_y = option_y_start + (i * option_height)
        
        # Highlight selected option
        if i == app_state.schematics_pause_menu_index:
            highlight_rect = pygame.Rect(menu_x + 5, option_y - 2, menu_width - 10, option_height - 4)
            pygame.draw.rect(screen, config_module.Theme.ACCENT, highlight_rect)
            text_color = config_module.Theme.BACKGROUND
        else:
            text_color = config_module.Theme.FOREGROUND
        
        option_surface = option_font.render(option, True, text_color)
        option_rect = option_surface.get_rect(centerx=menu_rect.centerx, y=option_y)
        screen.blit(option_surface, option_rect)