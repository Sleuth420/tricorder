# --- ui/components/text_display.py ---
# Reusable text display components

import pygame
import logging

logger = logging.getLogger(__name__)

def render_text(screen, text, font, color, position, align="center"):
    """
    Render text on the screen with various alignment options.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        text (str): The text to render
        font (pygame.font.Font): The font to use
        color (tuple): RGB color tuple
        position (tuple): (x, y) position for text
        align (str): Alignment - "left", "center", or "right"
    
    Returns:
        pygame.Rect: The rectangle of the rendered text
    """
    try:
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        
        # Set position based on alignment
        if align == "center":
            text_rect.center = position
        elif align == "left":
            text_rect.left, text_rect.centery = position
        elif align == "right":
            text_rect.right, text_rect.centery = position
        
        screen.blit(text_surface, text_rect)
        return text_rect
    except Exception as e:
        logger.error(f"Error rendering text '{text}': {e}", exc_info=True)
        return pygame.Rect(0, 0, 0, 0)

def render_title(screen, text, fonts, color, y_pos, width, is_frozen=False, frozen_color=None):
    """
    Render a title at the top of the screen.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        text (str): The title text
        fonts (dict): Dictionary of loaded fonts
        color (tuple): RGB color tuple for normal state
        y_pos (int): Vertical position
        width (int): Screen width for centering
        is_frozen (bool): Whether display is in frozen state
        frozen_color (tuple): Color to use if frozen (optional)
    
    Returns:
        pygame.Rect: The rectangle of the rendered text
    """
    if is_frozen:
        display_text = f"{text} [FROZEN]"
        text_color = frozen_color if frozen_color else color
    else:
        display_text = text
        text_color = color
        
    return render_text(
        screen, 
        display_text, 
        fonts['medium'] if 'medium' in fonts else fonts['default'], 
        text_color, 
        (width // 2, y_pos)
    )

def render_value(screen, value, unit, fonts, color, position, align="center"):
    """
    Render a sensor value with its unit.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        value (str): The value to display
        unit (str): The unit to display
        fonts (dict): Dictionary of loaded fonts
        color (tuple): RGB color tuple
        position (tuple): (x, y) position for text
        align (str): Alignment - "left", "center", or "right"
    
    Returns:
        pygame.Rect: The rectangle of the rendered text
    """
    full_text = f"{value} {unit}".strip()
    return render_text(
        screen, 
        full_text, 
        fonts['large'] if 'large' in fonts else fonts['default'],
        color, 
        position,
        align
    )

def render_note(screen, note, fonts, color, position):
    """
    Render a note or additional information.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        note (str): The note text
        fonts (dict): Dictionary of loaded fonts
        color (tuple): RGB color tuple
        position (tuple): (x, y) position for text
    
    Returns:
        pygame.Rect: The rectangle of the rendered text
    """
    if not note:
        return pygame.Rect(0, 0, 0, 0)
        
    return render_text(
        screen, 
        note, 
        fonts['small'] if 'small' in fonts else fonts['default'],
        color, 
        position
    )

def render_footer(screen, text, fonts, color, width, height):
    """
    Render footer text at the bottom of the screen.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        text (str): The footer text
        fonts (dict): Dictionary of loaded fonts
        color (tuple): RGB color tuple
        width (int): Screen width for centering
        height (int): Screen height for positioning
    
    Returns:
        pygame.Rect: The rectangle of the rendered text
    """
    font = fonts['small'] if 'small' in fonts else fonts['default']
    
    # Position near the bottom of the screen
    footer_y = height - (font.get_height() * 1.5)
    
    return render_text(
        screen, 
        text, 
        font,
        color, 
        (width // 2, footer_y)
    ) 