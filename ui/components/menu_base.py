# --- ui/components/menu_base.py ---
# Shared base component for menu rendering (sidebar, header, arrow indicator)

import pygame
import logging
from config import CLASSIFIED_TEXT

logger = logging.getLogger(__name__)

# Module-level flag to prevent repeated layout logging
_layout_logged = False

def draw_menu_base_layout(screen, app_state, fonts, config_module, ui_scaler, base_sidebar_width=None):
    """
    Draw the shared menu base layout (header, sidebar, arrow indicator) with responsive scaling.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        ui_scaler (UIScaler): UI scaling system for responsive design
        base_sidebar_width (int, optional): Override default sidebar width
        
    Returns:
        dict: Layout information for the main content area
    """
    global _layout_logged
    
    screen.fill(config_module.Theme.BACKGROUND)
    
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Layout calculations with arrow indicator area using UIScaler
    if base_sidebar_width is None:
        # Revert to original-style proportional calculations
        if ui_scaler.is_small_screen():
            # For small screens (Pi), use original proportion: ~30% of screen width
            base_sidebar_width = max(90, screen_width // 3)  # ~33% of width, minimum 90px
        else:
            # For larger screens, use original proportion: ~25% of screen width  
            base_sidebar_width = max(120, min(screen_width // 4, 200))  # 25% of width, max 200px

    arrow_indicator_width = ui_scaler.scale(config_module.ARROW_INDICATOR_WIDTH)
    header_height = ui_scaler.header_height()
    
    # Debug logging for layout calculations - only log once
    if ui_scaler.debug_mode and not _layout_logged:
        total_sidebar_width = base_sidebar_width + arrow_indicator_width
        main_content_width = screen_width - total_sidebar_width
        main_content_height = screen_height - header_height
        logger.info(f"🎨 MenuBase Layout: screen={screen_width}x{screen_height}, header={header_height}px, sidebar={base_sidebar_width}px, arrow={arrow_indicator_width}px, main_content={main_content_width}x{main_content_height}px")
        _layout_logged = True

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
                # item.color_key should be a string like "SIDEBAR_SYSTEM" or a Palette color name
                # Try Theme first, then Palette for backwards compatibility
                if hasattr(config_module.Theme, item.color_key):
                    item_bg_color = getattr(config_module.Theme, item.color_key)
                elif hasattr(config_module.Palette, item.color_key):
                    item_bg_color = getattr(config_module.Palette, item.color_key)
                else:
                    item_bg_color = config_module.Theme.ACCENT
            except AttributeError:
                logger.warning(f"Color attribute '{item.color_key}' not found in Theme or Palette for menu item '{item.name}'. Using default accent.")
                item_bg_color = config_module.COLOR_ACCENT # Fallback color
            
            pygame.draw.rect(screen, item_bg_color, item_rect)
            # Draw border outline for item
            pygame.draw.rect(screen, config_module.COLOR_BORDER, item_rect, width=config_module.Theme.BORDER_WIDTH)

            # Draw the category name with responsive text positioning
            font = fonts['medium']
            if item.name == "SECRET GAMES": # Special handling for "SECRET GAMES"
                title_text = CLASSIFIED_TEXT
            else:
                title_text = item.name # Use item.name
            text_surface = font.render(title_text, True, config_module.Palette.BLACK) 
            # Use UIScaler for responsive text padding
            text_padding = ui_scaler.padding("medium")
            text_pos = (item_rect.left + text_padding, item_rect.centery - text_surface.get_height() // 2)
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
        _draw_arrow_indicator(screen, arrow_area_rect, selected_item_rect, selected_item_color, config_module, ui_scaler)

    # --- Part 5: Calculate Main Content Area ---
    total_sidebar_width = base_sidebar_width + arrow_indicator_width
    main_content_rect = pygame.Rect(
        total_sidebar_width,
        header_height,
        screen_width - total_sidebar_width,
        screen_height - header_height
    )
    pygame.draw.rect(screen, config_module.Theme.BACKGROUND, main_content_rect)
    
    # Return layout information for the calling function to use
    return {
        'main_content_rect': main_content_rect,
        'base_sidebar_width': base_sidebar_width,
        'arrow_indicator_width': arrow_indicator_width,
        'total_sidebar_width': total_sidebar_width,
        'header_height': header_height,
        'screen_width': screen_width,
        'screen_height': screen_height
    }

def _draw_arrow_indicator(screen, arrow_area_rect, selected_item_rect, item_color, config_module, ui_scaler):
    """
    Draw a simple arrow indicator pointing left toward the selected menu item with responsive sizing.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        arrow_area_rect (pygame.Rect): Rectangle of the arrow indicator area
        selected_item_rect (pygame.Rect): Rectangle of the selected menu item
        item_color (tuple): RGB color of the selected menu item
        config_module (module): Configuration module for colors
        ui_scaler (UIScaler): UI scaling system for responsive design
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
    
    # Create arrow triangle pointing left with responsive sizing
    arrow_size = ui_scaler.scale(config_module.ARROW_INDICATOR_SIZE)
    arrow_points = [
        (arrow_center_x - arrow_size // 2, arrow_center_y),  # Left point (tip)
        (arrow_center_x + arrow_size // 2, arrow_center_y - arrow_size // 2),  # Top right
        (arrow_center_x + arrow_size // 2, arrow_center_y + arrow_size // 2)   # Bottom right
    ]
    
    # Draw the arrow
    pygame.draw.polygon(screen, arrow_color, arrow_points)
    
    # Optional: Add a subtle border to the arrow
    pygame.draw.polygon(screen, config_module.Palette.BLACK, arrow_points, 1) 