# --- ui/components/ui_elements.py ---
# Reusable UI elements like buttons, borders, etc.

import pygame
import logging

logger = logging.getLogger(__name__)

def draw_panel(screen, rect, title, fonts, colors, border_width=1):
    """
    Draw a panel with a title bar.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        rect (pygame.Rect): The rectangle for the panel
        title (str): The title for the panel
        fonts (dict): Dictionary of loaded fonts
        colors (dict): Dictionary with 'background', 'border', and 'title' colors
        border_width (int): Width of the panel border
        
    Returns:
        pygame.Rect: The content rectangle (inside the panel, below the title)
    """
    # Draw the panel background
    pygame.draw.rect(screen, colors['background'], rect)
    
    # Draw the border
    pygame.draw.rect(screen, colors['border'], rect, border_width)
    
    # Draw the title bar background
    title_height = fonts['small'].get_height() + 4
    title_rect = pygame.Rect(rect.left, rect.top, rect.width, title_height)
    pygame.draw.rect(screen, colors['title'], title_rect)
    
    # Draw title text
    font = fonts['small']
    try:
        title_surface = font.render(title, True, colors['title_text'])
        title_pos = (rect.left + 10, rect.top + (title_height - font.get_height()) // 2)
        screen.blit(title_surface, title_pos)
    except Exception as e:
        logger.error(f"Error rendering panel title '{title}': {e}", exc_info=True)
    
    # Return the content area rectangle
    content_rect = pygame.Rect(
        rect.left + border_width,
        rect.top + title_height + border_width,
        rect.width - 2 * border_width,
        rect.height - title_height - 2 * border_width
    )
    
    return content_rect

def draw_menu_item(screen, rect, text, fonts, colors, is_selected=False):
    """
    Draw a menu item.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        rect (pygame.Rect): The rectangle for the menu item
        text (str): The text for the menu item
        fonts (dict): Dictionary of loaded fonts
        colors (dict): Dictionary with 'background', 'text', 'selected_bg', and 'selected_text' colors
        is_selected (bool): Whether this item is currently selected
        
    Returns:
        pygame.Rect: The rectangle of the rendered item
    """
    # Determine colors based on selection state
    if is_selected:
        background_color = colors['selected_bg']
        text_color = colors['selected_text']
    else:
        background_color = colors['background']
        text_color = colors['text']
        
    # Draw the background
    pygame.draw.rect(screen, background_color, rect)
    
    # Draw a subtle border
    pygame.draw.rect(screen, colors['border'], rect, 1)
    
    # Draw the text
    font = fonts['medium']
    try:
        text_surface = font.render(text, True, text_color)
        # Position text centered vertically, left-aligned with padding
        text_pos = (rect.left + 20, rect.centery - text_surface.get_height() // 2)
        screen.blit(text_surface, text_pos)
    except Exception as e:
        logger.error(f"Error rendering menu item '{text}': {e}", exc_info=True)
        
    # If selected, draw a selection indicator
    if is_selected:
        # Triangle indicator on the left
        indicator_points = [
            (rect.left + 8, rect.centery - 4),
            (rect.left + 12, rect.centery),
            (rect.left + 8, rect.centery + 4)
        ]
        pygame.draw.polygon(screen, colors['selected_text'], indicator_points)
        
    return rect

def draw_menu(screen, rect, items, selected_index, fonts, colors, title="MENU"):
    """
    Draw a complete menu with multiple items.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        rect (pygame.Rect): The rectangle for the menu
        items (list): List of menu item text strings
        selected_index (int): Index of the currently selected item
        fonts (dict): Dictionary of loaded fonts
        colors (dict): Dictionary of color values
        title (str): Title for the menu panel
        
    Returns:
        list: List of rectangles for each menu item
    """
    # Draw the panel
    panel_colors = {
        'background': colors['background'],
        'border': colors['accent'],
        'title': colors['menu_header'],
        'title_text': colors['foreground']
    }
    content_rect = draw_panel(screen, rect, title, fonts, panel_colors)
    
    # Calculate item height and total menu height
    item_height = min(40, content_rect.height // max(len(items), 1))
    
    # Draw each menu item
    item_rects = []
    for i, item_text in enumerate(items):
        item_rect = pygame.Rect(
            content_rect.left + 2,
            content_rect.top + (i * item_height),
            content_rect.width - 4,
            item_height
        )
        
        item_colors = {
            'background': colors['background'],
            'text': colors['foreground'],
            'selected_bg': colors['selected_bg'],
            'selected_text': colors['selected_text'],
            'border': colors['border']
        }
        
        draw_menu_item(screen, item_rect, item_text, fonts, item_colors, i == selected_index)
        item_rects.append(item_rect)
        
    return item_rects 