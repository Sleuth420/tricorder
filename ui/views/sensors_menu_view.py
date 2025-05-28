# --- ui/views/sensors_menu_view.py ---
# Handles rendering of the sensors submenu

import pygame
import logging
from ui.components.text_display import render_footer

logger = logging.getLogger(__name__)

def draw_sensors_menu_view(screen, app_state, sensor_values, sensor_history, fonts, config_module):
    """
    Draw the sensors submenu view.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        sensor_values (dict): Dictionary of current sensor values
        sensor_history (ReadingHistory): Sensor reading history
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        
    Returns:
        None
    """
    screen.fill(config_module.Theme.BACKGROUND) 

    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # Layout calculations with arrow indicator area
    base_sidebar_width = min(screen_width // 4, 150)
    arrow_indicator_width = config_module.ARROW_INDICATOR_WIDTH
    
    header_height = config_module.HEADER_HEIGHT
    header_color = config_module.Theme.HEADER_CORNER_FILL 
    corner_color = config_module.Theme.HEADER_CORNER_FILL
    curve_radius = config_module.Theme.CORNER_CURVE_RADIUS

    menu_items = app_state.get_current_menu_items()
    selected_index = app_state.get_current_menu_index()

    # --- Part 1: Draw Corner Rectangle (Distinct block, Orange) ---
    corner_rect = pygame.Rect(0, 0, base_sidebar_width, header_height)
    # Apply rounding only to the top-left corner
    pygame.draw.rect(screen, corner_color, corner_rect, border_top_left_radius=curve_radius)
    # Draw border outline (should respect rounding)
    pygame.draw.rect(screen, config_module.COLOR_BORDER, corner_rect, width=config_module.Theme.BORDER_WIDTH, border_top_left_radius=curve_radius)

    # --- Part 2: Draw Header Bar (Starts AFTER base sidebar width, Orange) ---
    # Header should span from base_sidebar_width to screen_width (no gap for arrow area)
    header_rect = pygame.Rect(base_sidebar_width, 0, screen_width - base_sidebar_width, header_height)
    pygame.draw.rect(screen, header_color, header_rect)
    # Draw border outline
    pygame.draw.rect(screen, config_module.COLOR_BORDER, header_rect, width=config_module.Theme.BORDER_WIDTH)

    # --- Part 3: Draw Sidebar Items (Starts BELOW header height) ---
    sidebar_content_y_start = header_height # Items start below the header/corner
    sidebar_content_height = screen_height - header_height
    sidebar_items_area = pygame.Rect(0, sidebar_content_y_start, base_sidebar_width, sidebar_content_height)

    selected_item_rect = None
    selected_item_color = config_module.Theme.ACCENT

    if menu_items:
        item_height = sidebar_content_height // len(menu_items)
        for i, item in enumerate(menu_items): # item is now a MenuItem object
            item_rect = pygame.Rect(
                sidebar_items_area.left,
                sidebar_content_y_start + (i * item_height),
                sidebar_items_area.width,
                item_height
            )

            try:
                # item.color_key should be a string like "SIDEBAR_SYSTEM"
                # Get the color directly from config_module.Theme using getattr
                item_bg_color = getattr(config_module.Theme, item.color_key) if item.color_key else config_module.Theme.ACCENT
            except AttributeError:
                logger.warning(f"Theme color attribute '{item.color_key}' not found for menu item '{item.name}'. Using default accent.")
                item_bg_color = config_module.COLOR_ACCENT # Fallback color
            
            pygame.draw.rect(screen, item_bg_color, item_rect)
            # Draw border outline for item
            pygame.draw.rect(screen, config_module.COLOR_BORDER, item_rect, width=config_module.Theme.BORDER_WIDTH)

            # Draw the category name
            font = fonts['medium']
            title_text = item.name # Use item.name
            text_surface = font.render(title_text, True, config_module.Palette.BLACK) 
            text_pos = (item_rect.left + 10, item_rect.centery - text_surface.get_height() // 2)
            screen.blit(text_surface, text_pos)

            # Store selected item info for arrow indicator
            if i == selected_index:
                selected_item_rect = item_rect
                selected_item_color = item_bg_color

    # --- Part 4: Draw Arrow Indicator Area (ONLY below header) ---
    arrow_area_rect = pygame.Rect(
        base_sidebar_width, 
        sidebar_content_y_start,  # Start below header, same as sidebar items
        arrow_indicator_width, 
        sidebar_content_height    # Same height as sidebar content
    )
    
    # Draw arrow indicator if we have a selected item
    if selected_item_rect:
        _draw_arrow_indicator(screen, arrow_area_rect, selected_item_rect, selected_item_color, config_module)

    # --- Part 5: Draw Main Content Area ---
    total_sidebar_width = base_sidebar_width + arrow_indicator_width
    main_content_rect = pygame.Rect(
        total_sidebar_width,
        header_height,
        screen_width - total_sidebar_width,
        screen_height - header_height
    )
    pygame.draw.rect(screen, config_module.Theme.BACKGROUND, main_content_rect)

    # Display sensors submenu content
    title_font = fonts['large']
    title_text = "Sensors"
    title_surface = title_font.render(title_text, True, config_module.Theme.ACCENT)
    title_rect = title_surface.get_rect(centerx=main_content_rect.centerx, y=main_content_rect.top + 30)
    screen.blit(title_surface, title_rect)
    
    # Display instruction text
    instruction_font = fonts['medium']
    instruction_text = "Select a sensor to view"
    instruction_surface = instruction_font.render(instruction_text, True, config_module.Theme.FOREGROUND)
    instruction_rect = instruction_surface.get_rect(centerx=main_content_rect.centerx, y=title_rect.bottom + 20)
    screen.blit(instruction_surface, instruction_rect)
    
    # Show back instruction
    back_text = "Press BACK to return to main menu"
    back_surface = instruction_font.render(back_text, True, config_module.Theme.FOREGROUND)
    back_rect = back_surface.get_rect(centerx=main_content_rect.centerx, y=instruction_rect.bottom + 40)
    screen.blit(back_surface, back_rect)

    # --- Part 6: Draw Footer (centered on main content area only) ---
    key_prev_name = pygame.key.name(config_module.KEY_PREV).upper()
    key_next_name = pygame.key.name(config_module.KEY_NEXT).upper()
    key_select_name = pygame.key.name(config_module.KEY_SELECT).upper()
    key_back_name = "BACK"  # Generic back key name
    hint_text = f"< {key_prev_name}=Up | {key_select_name}=Select | {key_next_name}=Down | {key_back_name}=Back >"

    # Create a custom footer rendering that centers on main content area
    footer_font = fonts.get('small', fonts.get('medium'))
    footer_surface = footer_font.render(hint_text, True, config_module.Theme.FOREGROUND)
    footer_y = screen_height - footer_surface.get_height() - 5
    footer_x = main_content_rect.centerx - footer_surface.get_width() // 2
    screen.blit(footer_surface, (footer_x, footer_y))


def _draw_arrow_indicator(screen, arrow_area_rect, selected_item_rect, item_color, config_module):
    """
    Draw a simple arrow indicator pointing left toward the selected menu item.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        arrow_area_rect (pygame.Rect): Rectangle of the arrow indicator area
        selected_item_rect (pygame.Rect): Rectangle of the selected menu item
        item_color (tuple): RGB color of the selected menu item
        config_module (module): Configuration module for colors
    """
    # Clear the arrow area
    pygame.draw.rect(screen, config_module.Theme.BACKGROUND, arrow_area_rect)
    
    # Calculate arrow position (centered vertically with selected item)
    arrow_center_y = selected_item_rect.centery
    arrow_center_x = arrow_area_rect.centerx
    
    # Choose arrow color
    if config_module.ARROW_USE_ITEM_COLOR:
        arrow_color = item_color
    else:
        arrow_color = config_module.Palette.RED_ALERT  # Red as requested
    
    # Create arrow triangle pointing left
    arrow_size = config_module.ARROW_INDICATOR_SIZE
    arrow_points = [
        (arrow_center_x - arrow_size // 2, arrow_center_y),  # Left point (tip)
        (arrow_center_x + arrow_size // 2, arrow_center_y - arrow_size // 2),  # Top right
        (arrow_center_x + arrow_size // 2, arrow_center_y + arrow_size // 2)   # Bottom right
    ]
    
    # Draw the arrow
    pygame.draw.polygon(screen, arrow_color, arrow_points)
    
    # Optional: Add a subtle border to the arrow
    pygame.draw.polygon(screen, config_module.Palette.BLACK, arrow_points, 1) 