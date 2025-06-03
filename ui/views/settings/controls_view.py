# --- ui/views/settings/controls_view.py ---
# Handles rendering of the controls settings screen with scrollable interface

import pygame
import logging
from ui.components.text_display import render_footer, render_text
import config as app_config # For action names

logger = logging.getLogger(__name__)

def draw_controls_view(screen, app_state, fonts, config_module):
    """
    Draw the controls settings screen content with scrollable interface.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
    """
    screen.fill(config_module.Theme.BACKGROUND)
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    rect = pygame.Rect(0, 0, screen_width, screen_height)

    header_height = config_module.HEADER_HEIGHT
    header_rect = pygame.Rect(rect.left, rect.top, rect.width, header_height)
    pygame.draw.rect(screen, config_module.Theme.BACKGROUND, header_rect)

    font_small = fonts['small']
    header_text_str = "Controls"
    header_text_color = config_module.Theme.ACCENT
    header_text = font_small.render(header_text_str, True, header_text_color)
    screen.blit(header_text, (rect.left + 20, header_rect.centery - header_text.get_height() // 2))

    content_y = rect.top + header_height + 20
    
    # Update key names in controls manager before rendering
    app_state.controls_manager.update_key_names(config_module)
    
    # Get controls items and current selection
    controls_items = app_state.controls_manager.get_controls_items()
    current_selection_idx = app_state.controls_index
    
    # Use medium font for controls, large for section headers
    font_medium = fonts['medium']
    font_large = fonts['large']
    
    # Calculate how many items can fit on screen
    available_height = screen_height - content_y - 80  # Leave space for footer
    item_height = 35  # Fixed height per item for consistency
    max_visible_items = available_height // item_height
    
    # Only count selectable items (controls, not sections/spacers) for navigation
    selectable_items = [i for i, item in enumerate(controls_items) if item["type"] == "control"]
    
    # Find which selectable item is currently selected
    if current_selection_idx < len(selectable_items):
        selected_actual_index = selectable_items[current_selection_idx]
    else:
        selected_actual_index = selectable_items[0] if selectable_items else 0
    
    # Calculate scroll offset to keep selected item visible
    scroll_offset = 0
    if selected_actual_index >= max_visible_items // 2:
        scroll_offset = min(selected_actual_index - max_visible_items // 2, 
                          len(controls_items) - max_visible_items)
    
    # Render visible items
    y_offset = content_y + 20
    visible_start = max(0, scroll_offset)
    visible_end = min(len(controls_items), visible_start + max_visible_items)
    
    for i in range(visible_start, visible_end):
        item = controls_items[i]
        item_type = item["type"]
        item_text = item["text"]
        
        # Skip spacers
        if item_type == "spacer":
            y_offset += 15
            continue
        
        # Choose styling based on item type
        if item_type == "section":
            # Section headers - centered, large, accent color, not selectable
            font = font_large
            text_color = config_module.Theme.ACCENT
            text_surface = font.render(item_text, True, text_color)
            text_rect = text_surface.get_rect(center=(screen_width // 2, y_offset + 15))
            screen.blit(text_surface, text_rect)
            y_offset += item_height
            
        else:  # control type
            font = font_medium
            text_color = config_module.Theme.FOREGROUND
            
            # Check if this control item is selected
            control_index_in_selectable = None
            if i in selectable_items:
                control_index_in_selectable = selectable_items.index(i)
            
            is_selected = (control_index_in_selectable is not None and 
                         control_index_in_selectable == current_selection_idx)
            
            # Highlight current selection with background
            if is_selected:
                text_color = config_module.Theme.MENU_SELECTED_TEXT
                bg_color_selected = config_module.Theme.MENU_SELECTED_BG
                
                selection_bg_rect = pygame.Rect(
                    rect.left + 30,
                    y_offset + 5,
                    rect.width - 60,
                    item_height - 10
                )
                pygame.draw.rect(screen, bg_color_selected, selection_bg_rect, border_radius=8)
            
            # Render control text with nice left alignment and padding
            text_surface = font.render(item_text, True, text_color)
            text_rect = text_surface.get_rect(
                left=rect.left + 50,
                centery=y_offset + item_height // 2
            )
            screen.blit(text_surface, text_rect)
            y_offset += item_height
        
        # Stop if we're running out of space
        if y_offset >= screen_height - 80:
            break
    
    # Show scroll indicators if there are more items
    if visible_start > 0:
        up_text = "▲ More above"
        up_surface = font_small.render(up_text, True, config_module.Theme.ACCENT)
        up_rect = up_surface.get_rect(center=(screen_width // 2, content_y + 5))
        screen.blit(up_surface, up_rect)
    
    if visible_end < len(controls_items):
        down_text = "▼ More below"
        down_surface = font_small.render(down_text, True, config_module.Theme.ACCENT)
        down_rect = down_surface.get_rect(center=(screen_width // 2, screen_height - 75))
        screen.blit(down_surface, down_rect)

    # Footer hints
    key_prev_name = pygame.key.name(config_module.KEY_PREV).upper()
    key_next_name = pygame.key.name(config_module.KEY_NEXT).upper()
    
    hint = f"< {key_prev_name}=Up | {key_next_name}=Down | Hold {key_prev_name}=Back >"

    render_footer(
        screen, hint, fonts,
        config_module.Theme.FOREGROUND,
        screen_width, screen_height
    ) 