# --- ui/views/secret_games_view.py ---
# View for the secret games menu with image preview

import pygame
import logging
import os # Import os for path joining
from ui.components.text_display import render_title, render_footer

logger = logging.getLogger(__name__)

# Keep track of loaded images to avoid reloading every frame
loaded_images = {}

def _draw_secret_sidebar(screen, rect, menu_items, selected_index, fonts, config):
    """
    Draws the sidebar menu for the secret games.
    Similar to the main menu sidebar but simpler.
    """
    item_height = min(40, rect.height // max(len(menu_items), 1))
    sidebar_bg = (20, 20, 20) # Darker background for secret menu?

    pygame.draw.rect(screen, sidebar_bg, rect)

    for i, item in enumerate(menu_items):
        item_rect = pygame.Rect(
            rect.left,
            rect.top + (i * item_height),
            rect.width,
            item_height
        )

        # Determine colors based on selection state
        if i == selected_index:
            bg_color = config.COLOR_SELECTED_BG
            text_color = config.COLOR_SELECTED_TEXT
        else:
            bg_color = sidebar_bg
            text_color = (200, 200, 200) # Lighter gray for unselected

        pygame.draw.rect(screen, bg_color, item_rect)
        pygame.draw.rect(screen, config.COLOR_GRAPH_BORDER, item_rect, 1) # Subtle border

        # Draw the game name
        font = fonts['medium']
        text_surface = font.render(item["name"], True, text_color)
        text_pos = (item_rect.left + 10, item_rect.centery - text_surface.get_height() // 2)
        screen.blit(text_surface, text_pos)

def draw_secret_games_view(screen, app_state, fonts, config):
    """
    Draw the secret games menu screen with sidebar and image preview.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config (module): Configuration module
    """
    screen.fill(config.COLOR_BACKGROUND)
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # Layout: Sidebar on left, Image preview on right
    sidebar_width = min(screen_width // 3, 120)
    content_x = sidebar_width
    content_width = screen_width - sidebar_width

    # Draw Sidebar
    sidebar_rect = pygame.Rect(0, 0, sidebar_width, screen_height)
    _draw_secret_sidebar(screen, sidebar_rect, app_state.secret_menu_items, app_state.secret_menu_index, fonts, config)

    # Draw Main Content Area (Image Preview)
    content_rect = pygame.Rect(content_x, 0, content_width, screen_height)
    pygame.draw.rect(screen, config.COLOR_BACKGROUND, content_rect) # Clear content area

    # Get selected game info
    selected_game = app_state.secret_menu_items[app_state.secret_menu_index]
    image_path_relative = selected_game.get("image")
    image_to_display = None

    if image_path_relative:
        # Construct absolute path safely
        image_path_abs = os.path.abspath(image_path_relative)

        # Load image if not already loaded, handle errors
        if image_path_abs not in loaded_images:
            try:
                logger.debug(f"Loading image: {image_path_abs}")
                loaded_image = pygame.image.load(image_path_abs).convert_alpha()
                loaded_images[image_path_abs] = loaded_image # Cache it
            except pygame.error as e:
                logger.error(f"Failed to load image '{image_path_abs}': {e}")
                loaded_images[image_path_abs] = None # Cache failure
            except FileNotFoundError:
                 logger.error(f"Image file not found: '{image_path_abs}'")
                 loaded_images[image_path_abs] = None # Cache failure

        image_to_display = loaded_images.get(image_path_abs)

    # Display the image (or fallback)
    if image_to_display:
        # Scale image to fit content area while maintaining aspect ratio
        img_rect = image_to_display.get_rect()
        scale = min(content_rect.width / img_rect.width, content_rect.height / img_rect.height) * 0.9 # 90% scale
        scaled_width = int(img_rect.width * scale)
        scaled_height = int(img_rect.height * scale)
        scaled_image = pygame.transform.smoothscale(image_to_display, (scaled_width, scaled_height))
        # Center the scaled image in the content area
        display_rect = scaled_image.get_rect(center=content_rect.center)
        screen.blit(scaled_image, display_rect)
    else:
        # Fallback text if no image or failed to load
        fallback_font = fonts['medium']
        fallback_text = "No Image Preview"
        if image_path_relative:
            fallback_text = f"Cannot Load Image"

        fallback_surf = fallback_font.render(fallback_text, True, config.COLOR_ALERT)
        fallback_rect = fallback_surf.get_rect(center=content_rect.center)
        screen.blit(fallback_surf, fallback_rect)


    # Draw Footer
    key_prev_name = pygame.key.name(config.KEY_PREV).upper()
    key_next_name = pygame.key.name(config.KEY_NEXT).upper()
    key_select_name = pygame.key.name(config.KEY_SELECT).upper()

    # Update hint for secret menu navigation
    selected_game_name = app_state.secret_menu_items[app_state.secret_menu_index]['name']
    hint = f"< {key_prev_name}=Up | {key_select_name}=Launch {selected_game_name} | {key_next_name}=Down > (Hold {key_prev_name}=Back)"

    render_footer(
        screen,
        hint,
        fonts,
        config.COLOR_FOREGROUND,
        screen_width,
        screen_height
    ) 