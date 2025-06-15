# --- ui/components/list_menu_base.py ---
# Shared base component for scrollable list menu rendering (settings, schematics, etc.)

import pygame
import logging
from ui.components.text.text_display import render_footer

logger = logging.getLogger(__name__)

def draw_scrollable_list_menu(screen, title, menu_items, selected_index, fonts, config_module, 
                             footer_hint="", item_style="simple", ui_scaler=None):
    """
    Draw a scrollable list menu with consistent header/footer layout.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        title (str): Menu title for the header
        menu_items (list): List of menu items (strings or dicts with 'name' key)
        selected_index (int): Currently selected item index
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        footer_hint (str): Custom footer hint text (optional)
        item_style (str): "simple", "button", or "detailed"
        ui_scaler (UIScaler): UI scaler for scaling calculations
        
    Returns:
        dict: Layout information including visible item range
    """
    screen.fill(config_module.Theme.BACKGROUND)
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Use UIScaler for responsive dimensions if available
    if ui_scaler:
        header_top_margin = ui_scaler.header_top_margin()
        header_height = ui_scaler.header_height() + ui_scaler.scale(20)  # Taller header
        content_spacing = ui_scaler.margin("large")
        item_height_padding = ui_scaler.padding("medium")
        
        # Debug logging for list menu layout
        if ui_scaler.debug_mode:
            logger.info(f"🎨 ListMenuBase: screen={screen_width}x{screen_height}, header={header_height}px, spacing={content_spacing}px")
    else:
        # Fallback to original calculations
        header_top_margin = screen_height // 20  # Reduced top spacing
        header_height = config_module.HEADER_HEIGHT + 20  # Taller header for better spacing
        content_spacing = screen_height // 10  # Increased spacing
        item_height_padding = 20
    
    # === HEADER SECTION ===
    header_rect = pygame.Rect(0, header_top_margin, screen_width, header_height)
    pygame.draw.rect(screen, config_module.Theme.BACKGROUND, header_rect)
    
    # Use larger font for header and center it
    font_large = fonts['large']
    header_text = font_large.render(title, True, config_module.Palette.VIKING_BLUE)
    header_text_rect = header_text.get_rect(center=(screen_width // 2, header_rect.centery))
    screen.blit(header_text, header_text_rect)
    
    # === CONTENT SECTION ===
    content_y = header_rect.bottom + content_spacing
    footer_height = config_module.FONT_SIZE_SMALL * 3  # Approximate footer space
    available_height = screen_height - content_y - footer_height - 20
    
    # Calculate item dimensions
    font_medium = fonts['medium']
    item_text_height = font_medium.get_height()
    effective_item_height = item_text_height + item_height_padding
    
    # Use config value for max visible items - exactly 4 items
    max_visible_items = getattr(config_module, 'LIST_MENU_MAX_VISIBLE_ITEMS', 4)
    
    # Handle scrolling
    total_items = len(menu_items)
    if total_items == 0:
        return {"visible_start": 0, "visible_end": 0}
    
    # Calculate scroll offset to keep selected item visible
    scroll_offset = 0
    if total_items > max_visible_items:
        # Keep selected item in the middle of visible area when possible
        ideal_position = max_visible_items // 2
        scroll_offset = max(0, selected_index - ideal_position)
        scroll_offset = min(scroll_offset, total_items - max_visible_items)
    
    visible_start = scroll_offset
    visible_end = min(total_items, visible_start + max_visible_items)
    
    # === RENDER ITEMS ===
    y_offset = content_y + 20
    
    for i in range(visible_start, visible_end):
        item = menu_items[i]
        
        # Extract item text (handle MenuItem objects, dicts, and strings)
        if hasattr(item, 'name'):
            # MenuItem object with .name attribute
            item_text = item.name
        elif isinstance(item, dict):
            # Dictionary with 'name' key
            item_text = item.get('name', str(item))
        else:
            # String or other object
            item_text = str(item)
        
        # Determine colors and styling
        text_color = config_module.Theme.FOREGROUND
        is_selected = (i == selected_index)
        
        # Create item rectangle - center all items
        if item_style == "button":
            # Button style with borders
            item_rect = pygame.Rect(
                (screen_width // 2) - 150, y_offset - 10,
                300, effective_item_height
            )
        else:
            # Simple list style - centered
            item_width = min(400, screen_width - 60)  # Limit width but center it
            item_rect = pygame.Rect(
                (screen_width // 2) - (item_width // 2), y_offset - (item_height_padding // 2),
                item_width, effective_item_height
            )
        
        # Draw selection border
        if is_selected:
            text_color = config_module.Theme.MENU_SELECTED_TEXT
            # Draw left-pointing arrow to the right of the menu item
            arrow_x = item_rect.right + 10
            arrow_y = item_rect.centery
            arrow_size = 16
            arrow_points = [
                (arrow_x, arrow_y),  # Left point (tip)
                (arrow_x + arrow_size, arrow_y - arrow_size // 2),  # Top right
                (arrow_x + arrow_size, arrow_y + arrow_size // 2)   # Bottom right
            ]
            pygame.draw.polygon(screen, config_module.Theme.ACCENT, arrow_points)
        elif item_style == "button":
            # Draw border for unselected button items
            pygame.draw.rect(screen, config_module.Theme.GRAPH_BORDER, item_rect, 2, border_radius=5)
        
        # Render item text
        item_surface = font_medium.render(item_text, True, text_color)
        
        if item_style == "button":
            # Center text for button style
            text_rect = item_surface.get_rect(center=item_rect.center)
        else:
            # Center text for simple style too
            text_rect = item_surface.get_rect(center=item_rect.center)
        
        screen.blit(item_surface, text_rect)
        y_offset += effective_item_height + 15  # Reduced spacing between items
    
    # === SCROLL INDICATORS ===
    if total_items > max_visible_items:
        font_medium = fonts['medium']
        
        if visible_start > 0:
            up_indicator = "↑"
            up_surface = font_medium.render(up_indicator, True, config_module.Theme.ACCENT)
            up_rect = up_surface.get_rect(center=(screen_width // 2, content_y - 15))
            screen.blit(up_surface, up_rect)
        
        if visible_end < total_items:
            down_indicator = "↓"
            down_surface = font_medium.render(down_indicator, True, config_module.Theme.ACCENT)
            down_rect = down_surface.get_rect(center=(screen_width // 2, y_offset + 10))
            screen.blit(down_surface, down_rect)
    
    # === FOOTER === (Optional footer - only show if footer_hint is provided)
    if footer_hint is not None:
        if not footer_hint:
            # Generate default footer hint
            key_prev = pygame.key.name(config_module.KEY_PREV).upper()
            key_next = pygame.key.name(config_module.KEY_NEXT).upper()
            key_select = pygame.key.name(config_module.KEY_SELECT).upper()
            footer_hint = f"< {key_prev}=Up | {key_next}=Down | {key_select}=Select >"
        
        render_footer(
            screen, footer_hint, fonts,
            config_module.Theme.FOREGROUND,
            screen_width, screen_height
        )
    
    return {
        "visible_start": visible_start,
        "visible_end": visible_end,
        "total_items": total_items,
        "scroll_offset": scroll_offset
    }

def draw_simple_list_menu(screen, title, menu_items, selected_index, fonts, config_module, footer_hint="", show_footer=False, ui_scaler=None):
    """
    Convenience function for simple list menus without scrolling complexity.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        title (str): Menu title for the header
        menu_items (list): List of menu items (strings or dicts with 'name' key)
        selected_index (int): Currently selected item index
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        footer_hint (str): Custom footer hint text (optional)
        show_footer (bool): Whether to show footer (default False for settings-style menus)
        ui_scaler (UIScaler, optional): UI scaling system for responsive design
        
    Returns:
        dict: Layout information
    """
    return draw_scrollable_list_menu(
        screen, title, menu_items, selected_index, fonts, config_module,
        footer_hint=footer_hint if show_footer else None, item_style="simple", ui_scaler=ui_scaler
    )

def draw_button_list_menu(screen, title, menu_items, selected_index, fonts, config_module, footer_hint="", ui_scaler=None):
    """
    Convenience function for button-style list menus.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        title (str): Menu title for the header
        menu_items (list): List of menu items (strings or dicts with 'name' key)
        selected_index (int): Currently selected item index
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        footer_hint (str): Custom footer hint text (optional)
        ui_scaler (UIScaler, optional): UI scaling system for responsive design
        
    Returns:
        dict: Layout information
    """
    return draw_scrollable_list_menu(
        screen, title, menu_items, selected_index, fonts, config_module,
        footer_hint=footer_hint, item_style="button", ui_scaler=ui_scaler
    ) 