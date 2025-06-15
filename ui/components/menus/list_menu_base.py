# --- ui/components/list_menu_base.py ---
# Shared base component for scrollable list menu rendering (settings, schematics, etc.)

import pygame
import logging
import time
import math
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
    current_time = time.time()
    
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
    
    # === ANIMATED HEADER SECTION ===
    header_rect = pygame.Rect(0, header_top_margin, screen_width, header_height)
    pygame.draw.rect(screen, config_module.Theme.BACKGROUND, header_rect)
    
    # Draw animated header with glow effect
    font_large = fonts['large']
    _draw_animated_header(screen, title, font_large, header_rect, current_time, config_module)
    
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
    
    # === RENDER ANIMATED ITEMS ===
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
        
        # Draw selection arrow (original working version with subtle animation)
        if is_selected:
            text_color = config_module.Theme.MENU_SELECTED_TEXT
            
            # Draw simple animated arrow (using original font-based approach)
            arrow_x = item_rect.right + 10
            arrow_y = item_rect.centery
            arrow_size = 16
            
            # Add more prominent animation to the original arrow
            color_intensity = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(current_time * 3.0))
            arrow_color = tuple(min(255, int(c * color_intensity)) for c in config_module.Theme.ACCENT)
            
            arrow_points = [
                (arrow_x, arrow_y),  # Left point (tip)
                (arrow_x + arrow_size, arrow_y - arrow_size // 2),  # Top right
                (arrow_x + arrow_size, arrow_y + arrow_size // 2)   # Bottom right
            ]
            pygame.draw.polygon(screen, arrow_color, arrow_points)
        elif item_style == "button":
            # Draw border for unselected button items with subtle animation
            border_alpha = 0.6 + 0.2 * (0.5 + 0.5 * math.sin(current_time * 0.8 + i * 0.3))
            border_color = tuple(min(255, int(c * border_alpha)) for c in config_module.Theme.GRAPH_BORDER)
            pygame.draw.rect(screen, border_color, item_rect, 2, border_radius=5)
        
        # Render item text with strong breathing effect for selected item
        if is_selected:
            breathing_scale = 1.0 + 0.12 * (0.5 + 0.5 * math.sin(current_time * 2.5))
            text_color = tuple(min(255, int(c * breathing_scale)) for c in text_color)
        
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
    
    # Draw ambient tricorder effects
    _draw_list_ambient_effects(screen, screen_width, screen_height, header_rect, content_y, current_time, config_module)
    
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

def _draw_animated_header(screen, title, font, header_rect, current_time, config_module):
    """Draw animated header with more prominent pulsing effects."""
    # More prominent breathing effect
    breathing_scale = 1.0 + 0.1 * (0.5 + 0.5 * math.sin(current_time * 1.5))
    header_color = tuple(min(255, int(c * breathing_scale)) for c in config_module.Palette.VIKING_BLUE)
    header_text = font.render(title, True, header_color)
    header_text_rect = header_text.get_rect(center=(header_rect.centerx, header_rect.centery))
    screen.blit(header_text, header_text_rect)




def _draw_list_ambient_effects(screen, screen_width, screen_height, header_rect, content_y, current_time, config_module):
    """Draw ambient tricorder effects around the list menu."""
    # Only draw if we have enough space
    if screen_width < 300 or screen_height < 200:
        return
    
    # Corner status indicators
    _draw_corner_status_dots(screen, screen_width, screen_height, current_time, config_module)
    
    # Side data streams
    if screen_width > 400:
        _draw_side_data_streams(screen, screen_width, screen_height, header_rect, content_y, current_time, config_module)
    
    # Bottom status bar
    _draw_bottom_status_line(screen, screen_width, screen_height, current_time, config_module)

def _draw_corner_status_dots(screen, screen_width, screen_height, current_time, config_module):
    """Draw pulsing status dots in corners."""
    dot_positions = [
        (15, 15),  # Top left
        (screen_width - 15, 15),  # Top right
        (15, screen_height - 15),  # Bottom left
        (screen_width - 15, screen_height - 15)  # Bottom right
    ]
    
    colors = [
        config_module.Palette.GREEN,
        config_module.Palette.ENGINEERING_GOLD,
        config_module.Theme.ACCENT,
        config_module.Palette.VIKING_BLUE
    ]
    
    for i, (pos, color) in enumerate(zip(dot_positions, colors)):
        pulse_offset = i * 0.8
        pulse_alpha = 0.4 + 0.6 * (0.5 + 0.5 * math.sin(current_time * 2.5 + pulse_offset))
        dot_color = tuple(min(255, int(c * pulse_alpha)) for c in color)
        pygame.draw.circle(screen, dot_color, pos, 6)

def _draw_side_data_streams(screen, screen_width, screen_height, header_rect, content_y, current_time, config_module):
    """Draw flowing data streams on the sides."""
    # Left side stream
    left_area = pygame.Rect(5, content_y, 20, screen_height - content_y - 50)
    _draw_vertical_data_stream(screen, left_area, current_time, config_module, "left")
    
    # Right side stream
    right_area = pygame.Rect(screen_width - 25, content_y, 20, screen_height - content_y - 50)
    _draw_vertical_data_stream(screen, right_area, current_time, config_module, "right")

def _draw_vertical_data_stream(screen, area, current_time, config_module, side):
    """Draw vertical flowing data stream."""
    stream_speed = 2.0
    dot_spacing = 20
    
    # Calculate number of dots that fit
    num_dots = max(1, area.height // dot_spacing)
    
    for i in range(num_dots):
        dot_offset = i * 0.4
        dot_progress = (current_time * stream_speed + dot_offset) % 2.0
        
        if dot_progress < 1.5:
            dot_y = area.top + int((dot_progress / 1.5) * area.height)
            dot_x = area.centerx
            
            # Calculate dot alpha and size
            if dot_progress < 0.75:
                alpha = dot_progress / 0.75
                size = int(3 * (dot_progress / 0.75))
            else:
                alpha = (1.5 - dot_progress) / 0.75
                size = int(3 * ((1.5 - dot_progress) / 0.75))
            
            if size > 0 and alpha > 0.1:
                dot_color = (0, int(150 * alpha), int(50 * alpha))
                pygame.draw.circle(screen, dot_color, (dot_x, dot_y), max(1, size))

def _draw_bottom_status_line(screen, screen_width, screen_height, current_time, config_module):
    """Draw animated status line at bottom."""
    line_y = screen_height - 30
    line_width = screen_width - 40
    line_x = 20
    
    # Draw base status line
    base_alpha = 0.3 + 0.2 * (0.5 + 0.5 * math.sin(current_time * 1.0))
    base_color = (0, int(60 * base_alpha), int(20 * base_alpha))
    pygame.draw.line(screen, base_color, (line_x, line_y), (line_x + line_width, line_y), 1)
    
    # Animated scanning line
    scan_progress = (current_time * 1.2) % 2.0
    if scan_progress < 1.0:
        scan_x = line_x + int(scan_progress * line_width)
        scan_alpha = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(current_time * 4.0))
        scan_color = (0, int(150 * scan_alpha), int(60 * scan_alpha))
        pygame.draw.line(screen, scan_color, (scan_x - 10, line_y), (scan_x + 10, line_y), 2)

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