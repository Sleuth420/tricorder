# --- ui/views/secret_games_view.py ---
# Simple secret games menu with background preview images

import pygame
import logging
import os 

logger = logging.getLogger(__name__)

# Keep track of loaded images to avoid reloading every frame
loaded_images = {}

def _get_background_image(selected_game, config):
    """Get the background image for the selected game."""
    if not selected_game.image_path:
        return None
        
    image_path_abs = os.path.abspath(selected_game.image_path)
    if image_path_abs not in loaded_images:
        try:
            logger.debug(f"Loading background image: {image_path_abs}")
            loaded_image = pygame.image.load(image_path_abs).convert_alpha()
            loaded_images[image_path_abs] = loaded_image
        except (pygame.error, FileNotFoundError) as e:
            logger.error(f"Failed to load background image '{image_path_abs}': {e}")
            loaded_images[image_path_abs] = None
    
    return loaded_images.get(image_path_abs)

def draw_secret_games_view(screen, app_state, fonts, config):
    """
    Simple secret games menu similar to pong pause menu with background images.
    """
    logger.debug(f"Drawing secret games view - items: {len(app_state.secret_menu_items)}, index: {app_state.secret_menu_index}")
    
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Get selected game and background image
    selected_game = app_state.secret_menu_items[app_state.secret_menu_index]
    bg_image = _get_background_image(selected_game, config)
    
    # Fill background
    screen.fill(config.Theme.BACKGROUND)
    
    # Draw background image if available (scaled and tiled)
    if bg_image:
        # Scale the background image to fill screen while maintaining aspect ratio
        bg_rect = bg_image.get_rect()
        scale_x = screen_width / bg_rect.width
        scale_y = screen_height / bg_rect.height
        scale = max(scale_x, scale_y) * 2  # Scale up for tiled effect
        
        scaled_width = int(bg_rect.width * scale)
        scaled_height = int(bg_rect.height * scale)
        
        if scaled_width > 0 and scaled_height > 0:
            try:
                scaled_bg = pygame.transform.smoothscale(bg_image, (scaled_width, scaled_height))
                # Tile the background
                for x in range(0, screen_width + scaled_width, scaled_width):
                    for y in range(0, screen_height + scaled_height, scaled_height):
                        screen.blit(scaled_bg, (x - scaled_width//2, y - scaled_height//2))
            except pygame.error:
                pass  # If scaling fails, just use solid background
    
    # Draw semi-transparent overlay for readability
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.set_alpha(180)  # Semi-transparent
    overlay.fill(config.Theme.BACKGROUND)
    screen.blit(overlay, (0, 0))
    
    # Add spacing around edges (20px margin)
    margin = 20
    content_rect = pygame.Rect(margin, margin, screen_width - 2*margin, screen_height - 2*margin)
    
    # Draw title at top
    title_font = fonts.get('large', fonts.get('medium'))
    title_text = title_font.render("SECRET GAMES", True, config.Theme.ACCENT)
    title_x = content_rect.centerx - title_text.get_width() // 2
    title_y = content_rect.top + 10
    screen.blit(title_text, (title_x, title_y))
    
    # Calculate menu area (centered, similar to pong pause menu)
    menu_items = app_state.secret_menu_items
    item_height = 35  # Larger height for better readability
    menu_height = len(menu_items) * item_height
    menu_width = max(150, content_rect.width // 2)  # Bigger menu for text to fit
    
    menu_x = content_rect.centerx - menu_width // 2
    menu_y = content_rect.centery - menu_height // 2
    
    # Draw menu background
    menu_bg_rect = pygame.Rect(menu_x - 15, menu_y - 10, menu_width + 30, menu_height + 20)
    pygame.draw.rect(screen, config.Palette.DARK_GREY, menu_bg_rect)
    pygame.draw.rect(screen, config.Theme.ACCENT, menu_bg_rect, 2)
    
    # Draw menu items
    for i, item in enumerate(menu_items):
        item_rect = pygame.Rect(menu_x, menu_y + i * item_height, menu_width, item_height)
        
        # Highlight selected item
        if i == app_state.secret_menu_index:
            pygame.draw.rect(screen, config.Theme.MENU_SELECTED_BG, item_rect)
            text_color = config.Theme.MENU_SELECTED_TEXT
        else:
            text_color = config.Theme.WHITE
        
        # Draw item text (centered)
        font = fonts.get('medium', fonts.get('small'))
        text_surface = font.render(item.name, True, text_color)
        text_x = item_rect.centerx - text_surface.get_width() // 2
        text_y = item_rect.centery - text_surface.get_height() // 2
        screen.blit(text_surface, (text_x, text_y))
    
    # Draw controls at bottom
    controls_y = content_rect.bottom - 30
    key_prev_name = pygame.key.name(config.KEY_PREV).upper()
    key_next_name = pygame.key.name(config.KEY_NEXT).upper()
    key_select_name = pygame.key.name(config.KEY_SELECT).upper()
    
    controls_text = ""
    
    controls_font = fonts.get('small', fonts.get('medium'))
    controls_surface = controls_font.render(controls_text, True, config.Theme.FOREGROUND)
    controls_x = content_rect.centerx - controls_surface.get_width() // 2
    screen.blit(controls_surface, (controls_x, controls_y)) 