# --- ui/views/tricorder_schematics.py ---
# 3D Ship viewer for the tricorder schematics system

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
    
    # Draw footer with controls
    key_prev_name = pygame.key.name(config_module.KEY_PREV).upper()
    key_next_name = pygame.key.name(config_module.KEY_NEXT).upper()
    key_back_name = "BACK"
    
    current_ship_info = app_state.ship_manager.get_current_ship_info()
    ship_name = current_ship_info['name'] if current_ship_info else "Unknown"
    
    hint_text = f"< {key_prev_name}=Rotate Left | {key_next_name}=Rotate Right | Hold {key_prev_name}=Back >"
    
    render_footer(
        screen,
        hint_text,
        fonts,
        config_module.Theme.FOREGROUND,
        screen.get_width(),
        screen.get_height()
    )