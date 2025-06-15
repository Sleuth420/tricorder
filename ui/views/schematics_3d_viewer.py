# --- ui/views/schematics_3d_viewer.py ---
# 3D Schematics viewer with software-based rendering and SenseHat sensor integration

import pygame
import logging
from ui.components.text_display import render_footer

logger = logging.getLogger(__name__)

def draw_schematics_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the 3D schematics viewer screen.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        ui_scaler (function or None): Scaling function or None
        
    Returns:
        None
    """
    # Schematics model should already be set by input router, but verify it's correct
    if app_state.selected_schematics_data and 'schematics_model' in app_state.selected_schematics_data:
        schematics_model_key = app_state.selected_schematics_data['schematics_model']
        current_schematics_info = app_state.schematics_manager.get_current_schematics_info()
        
        # Double-check that the schematics model is set correctly (should already be done)
        if not current_schematics_info or current_schematics_info['model_key'] != schematics_model_key:
            logger.debug(f"3D Viewer: Schematics model mismatch, correcting to '{schematics_model_key}'")
            app_state.schematics_manager.set_schematics_model(schematics_model_key)
    
    # Check if we're using OpenGL mode
    current_schematics_info = app_state.schematics_manager.get_current_schematics_info()
    is_opengl_mode = (current_schematics_info and 
                     current_schematics_info.get('model_key') in ['worf', 'apollo_1570'])
    
    # Update rotation from sensors only if in auto mode
    if app_state.schematics_manager.auto_rotation_mode:
        sensor_updated = app_state.schematics_manager.update_rotation_from_sensors()
    
    # Render the 3D schematics (includes pause menu for OpenGL mode)
    app_state.schematics_manager.render_schematics(screen, fonts, config_module,
                                      app_state.schematics_pause_menu_active,
                                      app_state.schematics_pause_menu_index)
    
    # Only draw UI elements if not in OpenGL mode (since OpenGL mode handles all UI internally)
    if not is_opengl_mode:
        # Draw pause menu if active
        if app_state.schematics_pause_menu_active:
            _draw_pause_menu(screen, app_state, fonts, config_module)
        else:
            # Draw footer with controls when pause menu is not active
            key_prev_name = pygame.key.name(config_module.KEY_PREV).upper()
            key_next_name = pygame.key.name(config_module.KEY_NEXT).upper()
            key_select_name = pygame.key.name(config_module.KEY_SELECT).upper()
            
            hint_text = ""

            render_footer(
                screen, hint_text, fonts,
                config_module.Theme.FOREGROUND,
                screen.get_width(),
                screen.get_height()
            )

def _draw_pause_menu(screen, app_state, fonts, config_module):
    """Draw the pause menu overlay for the 3D viewer - simplified like confirmation dialog."""
    screen.fill(config_module.Theme.BACKGROUND)
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    font_large = fonts['large']
    font_medium = fonts['medium']

    # Display the menu title
    title_surface = font_large.render("3D VIEWER MENU", True, config_module.Theme.ACCENT)
    title_rect = title_surface.get_rect(center=(screen_width // 2, screen_height // 4))
    screen.blit(title_surface, title_rect)

    # Menu options
    options = ["Toggle Mode", "Back to Schematics", "Resume"]
    current_selection_idx = app_state.schematics_pause_menu_index

    y_offset = title_rect.bottom + 40
    
    for i, option_text in enumerate(options):
        text_color = config_module.Theme.FOREGROUND
        item_width = 160
        item_height = font_medium.get_height() + 20
        
        item_display_rect = pygame.Rect(
            (screen_width // 2) - item_width // 2, 
            y_offset + (i * (item_height + 10)),
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

    # Show current rotation mode
    rotation_mode = "Auto (Sensor)" if app_state.schematics_manager.auto_rotation_mode else "Manual (Keys)"
    mode_text = f"Current Mode: {rotation_mode}"
    mode_font = fonts.get('small', fonts.get('medium'))
    mode_surface = mode_font.render(mode_text, True, config_module.Theme.FOREGROUND)
    mode_rect = mode_surface.get_rect(center=(screen_width // 2, y_offset + len(options) * (item_height + 10) + 20))
    screen.blit(mode_surface, mode_rect)

    # Footer hints
    key_prev_name = pygame.key.name(config_module.KEY_PREV).upper()
    key_next_name = pygame.key.name(config_module.KEY_NEXT).upper()
    key_select_name = pygame.key.name(config_module.KEY_SELECT).upper()
    
    hint = ""

    render_footer(
        screen, hint, fonts,
        config_module.Theme.FOREGROUND,
        screen_width, screen_height
    )