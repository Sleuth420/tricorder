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
    # Use UIScaler dimensions when available (best practice: no raw screen.get_* for layout)
    if ui_scaler:
        screen_width = ui_scaler.screen_width
        screen_height = ui_scaler.screen_height
        header_top_margin = ui_scaler.header_top_margin()
        header_height = ui_scaler.header_height() + ui_scaler.scale(20)
        content_spacing = ui_scaler.margin("large")
        item_height_padding = ui_scaler.padding("medium")
        if ui_scaler.debug_mode:
            logger.info(f"🎨 ListMenuBase: screen={screen_width}x{screen_height}, header={header_height}px, spacing={content_spacing}px")
    else:
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        header_top_margin = screen_height // 20
        header_height = config_module.HEADER_HEIGHT + 20
        content_spacing = screen_height // 10
        item_height_padding = 20
    current_time = time.time()
    
    # === ANIMATED HEADER SECTION ===
    header_rect = pygame.Rect(0, header_top_margin, screen_width, header_height)
    pygame.draw.rect(screen, config_module.Theme.BACKGROUND, header_rect)
    
    # Draw animated header with glow effect
    font_large = fonts['large']
    _draw_animated_header(screen, title, font_large, header_rect, current_time, config_module)
    
    # === CONTENT SECTION ===
    content_y = header_rect.bottom + content_spacing
    footer_margin = ui_scaler.scale(20) if ui_scaler else 20
    footer_height = (config_module.FONT_SIZE_SMALL * 3) if not ui_scaler else ui_scaler.scale(config_module.FONT_SIZE_SMALL * 3)
    available_height = screen_height - content_y - footer_height - footer_margin
    
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
    content_top_offset = ui_scaler.scale(20) if ui_scaler else 20
    item_spacing = ui_scaler.scale(15) if ui_scaler else 15
    y_offset = content_y + content_top_offset
    
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
        
        # Create item rectangle - center all items (use UIScaler for sizes when available)
        if item_style == "button":
            btn_half_w = ui_scaler.scale(150) if ui_scaler else 150
            item_rect = pygame.Rect(
                (screen_width // 2) - btn_half_w, y_offset - (item_height_padding // 2),
                btn_half_w * 2, effective_item_height
            )
        else:
            max_item_w = ui_scaler.scale(400) if ui_scaler else 400
            side_inset = ui_scaler.scale(60) if ui_scaler else 60
            item_width = min(max_item_w, screen_width - side_inset)
            item_rect = pygame.Rect(
                (screen_width // 2) - (item_width // 2), y_offset - (item_height_padding // 2),
                item_width, effective_item_height
            )
        
        # Draw selection arrow (original working version with subtle animation)
        if is_selected:
            text_color = config_module.Theme.MENU_SELECTED_TEXT
            
            arrow_offset = ui_scaler.scale(10) if ui_scaler else 10
            arrow_size = ui_scaler.scale(16) if ui_scaler else 16
            arrow_x = item_rect.right + arrow_offset
            arrow_y = item_rect.centery
            
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
        y_offset += effective_item_height + item_spacing
    
    # === SCROLL INDICATORS ===
    if total_items > max_visible_items:
        font_medium = fonts['medium']
        
        scroll_indicator_offset = ui_scaler.scale(15) if ui_scaler else 15
        if visible_start > 0:
            up_indicator = "↑"
            up_surface = font_medium.render(up_indicator, True, config_module.Theme.ACCENT)
            up_rect = up_surface.get_rect(center=(screen_width // 2, content_y - scroll_indicator_offset))
            screen.blit(up_surface, up_rect)
        
        if visible_end < total_items:
            down_indicator = "↓"
            down_surface = font_medium.render(down_indicator, True, config_module.Theme.ACCENT)
            down_rect = down_surface.get_rect(center=(screen_width // 2, y_offset + ui_scaler.scale(10) if ui_scaler else 10))
            screen.blit(down_surface, down_rect)
    
    # Draw ambient tricorder effects (pass ui_scaler for consistent scaling)
    _draw_list_ambient_effects(screen, screen_width, screen_height, header_rect, content_y, current_time, config_module, ui_scaler)
    
    # === FOOTER === (Optional footer - only show if footer_hint is provided)
    if footer_hint is not None:
        if not footer_hint:
            # OS-adaptive: Pi = Left/Right/Middle, dev = A/D/Enter
            labels = config_module.get_control_labels()
            footer_hint = f"< {labels['prev']}=Up | {labels['next']}=Down | {labels['select']}=Select >"
        
        render_footer(
            screen, footer_hint, fonts,
            config_module.Theme.FOREGROUND,
            screen_width, screen_height,
            ui_scaler=ui_scaler
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




def _draw_list_ambient_effects(screen, screen_width, screen_height, header_rect, content_y, current_time, config_module, ui_scaler=None):
    """Draw ambient tricorder effects around the list menu. Uses ui_scaler for sizes when available."""
    min_w = ui_scaler.scale(300) if ui_scaler else 300
    min_h = ui_scaler.scale(200) if ui_scaler else 200
    if screen_width < min_w or screen_height < min_h:
        return
    margin = ui_scaler.margin("small") if ui_scaler else 15
    _draw_corner_status_dots(screen, screen_width, screen_height, current_time, config_module, ui_scaler, margin)
    side_stream_breakpoint = ui_scaler.scale(400) if ui_scaler else 400
    if screen_width > side_stream_breakpoint:
        _draw_side_data_streams(screen, screen_width, screen_height, header_rect, content_y, current_time, config_module, ui_scaler)
    _draw_bottom_status_line(screen, screen_width, screen_height, current_time, config_module, ui_scaler)

def _draw_corner_status_dots(screen, screen_width, screen_height, current_time, config_module, ui_scaler=None, margin=15):
    """Draw pulsing status dots in corners."""
    if ui_scaler:
        margin = ui_scaler.margin("small")
    dot_radius = ui_scaler.scale(6) if ui_scaler else 6
    dot_positions = [
        (margin, margin),
        (screen_width - margin, margin),
        (margin, screen_height - margin),
        (screen_width - margin, screen_height - margin)
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
        pygame.draw.circle(screen, dot_color, pos, dot_radius)

def _draw_side_data_streams(screen, screen_width, screen_height, header_rect, content_y, current_time, config_module, ui_scaler=None):
    """Draw flowing data streams on the sides."""
    inset = ui_scaler.scale(5) if ui_scaler else 5
    stream_w = ui_scaler.scale(20) if ui_scaler else 20
    bottom_inset = ui_scaler.scale(50) if ui_scaler else 50
    left_area = pygame.Rect(inset, content_y, stream_w, screen_height - content_y - bottom_inset)
    _draw_vertical_data_stream(screen, left_area, current_time, config_module, "left", ui_scaler)
    right_area = pygame.Rect(screen_width - inset - stream_w, content_y, stream_w, screen_height - content_y - bottom_inset)
    _draw_vertical_data_stream(screen, right_area, current_time, config_module, "right", ui_scaler)

def _draw_vertical_data_stream(screen, area, current_time, config_module, side, ui_scaler=None):
    """Draw vertical flowing data stream."""
    stream_speed = 2.0
    dot_spacing = ui_scaler.scale(20) if ui_scaler else 20
    
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

def _draw_bottom_status_line(screen, screen_width, screen_height, current_time, config_module, ui_scaler=None):
    """Draw animated status line at bottom. Uses ui_scaler for insets when available."""
    bottom_inset = ui_scaler.scale(30) if ui_scaler else 30
    side_inset = ui_scaler.margin("medium") if ui_scaler else 20
    line_y = screen_height - bottom_inset
    line_width = screen_width - side_inset * 2
    line_x = side_inset
    base_alpha = 0.3 + 0.2 * (0.5 + 0.5 * math.sin(current_time * 1.0))
    base_color = (0, int(60 * base_alpha), int(20 * base_alpha))
    pygame.draw.line(screen, base_color, (line_x, line_y), (line_x + line_width, line_y), 1)
    scan_progress = (current_time * 1.2) % 2.0
    if scan_progress < 1.0:
        scan_x = line_x + int(scan_progress * line_width)
        scan_half = ui_scaler.scale(10) if ui_scaler else 10
        scan_alpha = 0.6 + 0.4 * (0.5 + 0.5 * math.sin(current_time * 4.0))
        scan_color = (0, int(150 * scan_alpha), int(60 * scan_alpha))
        pygame.draw.line(screen, scan_color, (scan_x - scan_half, line_y), (scan_x + scan_half, line_y), 2)

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