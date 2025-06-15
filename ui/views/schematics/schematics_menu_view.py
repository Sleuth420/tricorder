# --- ui/views/schematics_menu_view.py ---
# Handles rendering of the schematics selection submenu

import pygame
import logging
from ui.components.text.text_display import render_footer

logger = logging.getLogger(__name__)

def draw_schematics_menu_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the schematics selection submenu view - simplified for small display.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        ui_scaler (UIScaler): The UI scaler
        
    Returns:
        None
    """
    screen.fill(config_module.Theme.BACKGROUND)
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    font_large = fonts['large']
    font_medium = fonts['medium']

    # Use UIScaler for responsive spacing if available
    if ui_scaler:
        title_y_offset = ui_scaler.scale(screen_height // 5)  # Responsive title position
        item_spacing = ui_scaler.margin("medium")  # Responsive item spacing
        item_width = ui_scaler.scale(300)  # Responsive item width
        item_height_padding = ui_scaler.padding("medium")  # Responsive padding
        instruction_spacing = ui_scaler.margin("medium")  # Responsive instruction spacing
        
        # Debug logging for schematics menu layout
        if ui_scaler.debug_mode:
            logger.info(f"🎨 SchematicsMenuView: screen={screen_width}x{screen_height}, item_width={item_width}px, spacing={item_spacing}px")
    else:
        # Fallback to original hardcoded values
        title_y_offset = screen_height // 5
        item_spacing = 15
        item_width = 300
        item_height_padding = 20
        instruction_spacing = 20

    # Display the menu title
    title_surface = font_large.render("Schematics", True, config_module.Theme.ACCENT)
    title_rect = title_surface.get_rect(center=(screen_width // 2, title_y_offset))
    screen.blit(title_surface, title_rect)

    # Get menu items and selection
    menu_items = app_state.get_current_menu_items()
    selected_index = app_state.get_current_menu_index()

    if not menu_items:
        return

    y_offset = title_rect.bottom + 30
    
    for i, item in enumerate(menu_items):
        text_color = config_module.Theme.FOREGROUND
        item_height = font_medium.get_height() + item_height_padding
        
        item_display_rect = pygame.Rect(
            (screen_width // 2) - item_width // 2, 
            y_offset + (i * (item_height + item_spacing)),
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
        selected_schematics = menu_items[selected_index]
        if selected_schematics.name != "Back":
            instruction_text = "Select to view 3D model"
            instruction_font = fonts.get('small', fonts.get('medium'))
            instruction_surface = instruction_font.render(instruction_text, True, config_module.Theme.FOREGROUND)
            instruction_rect = instruction_surface.get_rect(center=(screen_width // 2, y_offset + len(menu_items) * (item_height + item_spacing) + instruction_spacing))
            screen.blit(instruction_surface, instruction_rect)

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