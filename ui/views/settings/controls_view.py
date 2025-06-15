# --- ui/views/settings/controls_view.py ---
# Handles rendering of the controls settings screen with scrollable interface

import pygame
import logging
from ui.components.text.text_display import render_footer, render_text
import config as app_config # For action names

logger = logging.getLogger(__name__)

def draw_controls_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the controls settings screen content with scrollable interface.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
        ui_scaler (UIScaler, optional): UI scaling system for responsive design
    """
    screen.fill(config_module.Theme.BACKGROUND)
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    rect = pygame.Rect(0, 0, screen_width, screen_height)

    # Use UIScaler for responsive dimensions if available
    if ui_scaler:
        header_height = ui_scaler.header_height()
        header_margin = ui_scaler.margin("medium")
        content_spacing = ui_scaler.margin("large")
        item_height = ui_scaler.scale(35)
        footer_space = ui_scaler.scale(80)
        section_spacing = ui_scaler.scale(15)
        
        # Debug logging for controls view layout
        if ui_scaler.debug_mode:
            logger.info(f"🎨 ControlsView: screen={screen_width}x{screen_height}, header={header_height}px, item_height={item_height}px")
    else:
        # Fallback to original calculations
        header_height = config_module.HEADER_HEIGHT
        header_margin = 20
        content_spacing = 20
        item_height = 35
        footer_space = 80
        section_spacing = 15

    header_rect = pygame.Rect(rect.left, rect.top, rect.width, header_height)
    pygame.draw.rect(screen, config_module.Theme.BACKGROUND, header_rect)

    font_small = fonts['small']
    header_text_str = "Controls"
    header_text_color = config_module.Theme.ACCENT
    header_text = font_small.render(header_text_str, True, header_text_color)
    screen.blit(header_text, (rect.left + header_margin, header_rect.centery - header_text.get_height() // 2))

    content_y = rect.top + header_height + content_spacing
    
    # Update key names in controls manager before rendering
    app_state.controls_manager.update_key_names(config_module)
    
    # Get controls items and current selection
    controls_items = app_state.controls_manager.get_controls_items()
    current_selection_idx = app_state.controls_index
    
    # Use medium font for controls, large for section headers
    font_medium = fonts['medium']
    font_large = fonts['large']
    
    # Calculate how many items can fit on screen
    available_height = screen_height - content_y - footer_space
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
    y_offset = content_y + content_spacing
    visible_start = max(0, scroll_offset)
    visible_end = min(len(controls_items), visible_start + max_visible_items)
    
    for i in range(visible_start, visible_end):
        item = controls_items[i]
        item_type = item["type"]
        item_text = item["text"]
        
        # Skip spacers
        if item_type == "spacer":
            y_offset += section_spacing
            continue
        
        # Choose styling based on item type
        if item_type == "section":
            # Section headers - centered, large, accent color, not selectable
            font = font_large
            text_color = config_module.Theme.ACCENT
            text_surface = font.render(item_text, True, text_color)
            text_rect = text_surface.get_rect(center=(screen_width // 2, y_offset + (item_height // 2)))
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
                
                # Responsive selection background
                selection_padding = ui_scaler.padding("large") if ui_scaler else 30
                selection_bg_rect = pygame.Rect(
                    rect.left + selection_padding,
                    y_offset + 5,
                    rect.width - (selection_padding * 2),
                    item_height - 10
                )
                pygame.draw.rect(screen, bg_color_selected, selection_bg_rect, border_radius=8)
            
            # Render control text with responsive alignment and padding
            text_padding = ui_scaler.padding("large") + ui_scaler.margin("medium") if ui_scaler else 50
            text_surface = font.render(item_text, True, text_color)
            text_rect = text_surface.get_rect(
                left=rect.left + text_padding,
                centery=y_offset + item_height // 2
            )
            screen.blit(text_surface, text_rect)
            y_offset += item_height
        
        # Stop if we're running out of space
        if y_offset >= screen_height - footer_space:
            break
    
    # Show scroll indicators if there are more items
    if visible_start > 0:
        up_text = "▲ More above"
        up_surface = font_small.render(up_text, True, config_module.Theme.ACCENT)
        up_y = content_y + (ui_scaler.scale(5) if ui_scaler else 5)
        up_rect = up_surface.get_rect(center=(screen_width // 2, up_y))
        screen.blit(up_surface, up_rect)
    
    if visible_end < len(controls_items):
        down_text = "▼ More below"
        down_surface = font_small.render(down_text, True, config_module.Theme.ACCENT)
        down_y = screen_height - (ui_scaler.scale(75) if ui_scaler else 75)
        down_rect = down_surface.get_rect(center=(screen_width // 2, down_y))
        screen.blit(down_surface, down_rect)

    # Footer hints with responsive positioning
    key_prev_name = pygame.key.name(config_module.KEY_PREV).upper()
    key_next_name = pygame.key.name(config_module.KEY_NEXT).upper()
    
    hint = f"< {key_prev_name}=Up | {key_next_name}=Down | Hold {key_prev_name}=Back >"

    render_footer(
        screen, hint, fonts,
        config_module.Theme.FOREGROUND,
        screen_width, screen_height
    ) 