# --- ui/menu.py ---
# Handles rendering of the menu sidebar and the main menu screen layout

import pygame
import logging
import time
from datetime import datetime
from config import version

# from ui.components.ui_elements import draw_panel # Likely unused, will confirm and remove if so
from ui.components.text_display import render_footer
# from ui.views.system_info_view import draw_system_info_view # Unused in this file
# No need to import MenuItem here as it's handled by AppState
from models.menu_item import MenuItem
from models.app_state import STATE_MENU, STATE_SECRET_GAMES # Import necessary states
from config import CLASSIFIED_TEXT
# Other config values like Theme, SPLASH_LOGO_PATH, various constants for keys, states, etc.,
# are accessed via the 'config_module' parameter passed to functions.

logger = logging.getLogger(__name__)

def _get_footer_content(config_module):
    """
    Generate footer content with stardate and build number.
    
    Args:
        config_module (module): Configuration module
        
    Returns:
        str: Footer content string
    """
    try:
        # Calculate TNG-era stardate
        # TNG system: First digit 4 (24th century), then year progression
        # For real world: calculate as if we're in 24th century
        now = datetime.now()
        
        # Base stardate calculation - TNG style
        # Years since 2323 (start of TNG era) + fractional day
        years_since_2323 = now.year - 2323
        day_of_year = now.timetuple().tm_yday
        total_days_in_year = 366 if now.year % 4 == 0 else 365
        
        # Calculate fractional year progress
        year_progress = day_of_year / total_days_in_year
        
        # TNG stardate format: 4XXXX.X
        # Where XXXX represents years and progress, X represents fractional day
        stardate_base = 40000 + (years_since_2323 * 1000) + int(year_progress * 1000)
        
        # Fractional day (0.1 = 2.4 hours, so 0.5 = noon)
        fractional_day = (now.hour * 60 + now.minute) / 1440.0
        
        stardate = stardate_base + fractional_day
        
        # Get build number from version module
        build_number = version.get_build_number()
        
        return f"Stardate {stardate:.1f} | {build_number}"
        
    except Exception as e:
        logger.error(f"Error generating footer content: {e}")
        return "Stardate 47457.1 | ALPHA 0.0.1"

# Arrow indicator configuration - now moved to config/ui.py
# _arrow_config = {
#     'width': 20,        # Width of the arrow indicator area
#     'arrow_size': 12,   # Size of the arrow triangle
#     'use_item_color': True  # Whether to use menu item color or red
# }

def _draw_arrow_indicator(screen, arrow_area_rect, selected_item_rect, item_color, config_module):
    """
    Draw a simple arrow indicator pointing left toward the selected menu item.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        arrow_area_rect (pygame.Rect): Rectangle of the arrow indicator area
        selected_item_rect (pygame.Rect): Rectangle of the selected menu item
        item_color (tuple): RGB color of the selected menu item
        config_module (module): Configuration module for colors
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
    
    # Create arrow triangle pointing left
    arrow_size = config_module.ARROW_INDICATOR_SIZE
    arrow_points = [
        (arrow_center_x - arrow_size // 2, arrow_center_y),  # Left point (tip)
        (arrow_center_x + arrow_size // 2, arrow_center_y - arrow_size // 2),  # Top right
        (arrow_center_x + arrow_size // 2, arrow_center_y + arrow_size // 2)   # Bottom right
    ]
    
    # Draw the arrow
    pygame.draw.polygon(screen, arrow_color, arrow_points)
    
    # Optional: Add a subtle border to the arrow
    pygame.draw.polygon(screen, config_module.Palette.BLACK, arrow_points, 1)

# REMOVED MENU_CATEGORIES - now driven by app_state.menu_items

def draw_menu_screen(screen, app_state, fonts, config_module, sensor_values):
    """
    Draw the menu screen with sidebar, arrow indicator, and main content area.
    """
    screen.fill(config_module.Theme.BACKGROUND) 

    screen_width = screen.get_width()
    screen_height = screen.get_height()

    if app_state.current_state not in [STATE_MENU, STATE_SECRET_GAMES]:
        logger.warning(f"draw_menu_screen called unexpectedly in state: {app_state.current_state}")
        return

    # Layout calculations with arrow indicator area
    base_sidebar_width = min(screen_width // 4, 150)
    arrow_indicator_width = config_module.ARROW_INDICATOR_WIDTH
    
    header_height = config_module.HEADER_HEIGHT
    header_color = config_module.Theme.HEADER_CORNER_FILL 
    corner_color = config_module.Theme.HEADER_CORNER_FILL
    curve_radius = config_module.Theme.CORNER_CURVE_RADIUS
    border_width_val = config_module.Theme.BORDER_WIDTH

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
                # item.color_key should be a string like "SIDEBAR_SYSTEM"
                # Get the color directly from config_module.Theme using getattr
                item_bg_color = getattr(config_module.Theme, item.color_key) if item.color_key else config_module.Theme.ACCENT
            except AttributeError:
                logger.warning(f"Theme color attribute '{item.color_key}' not found for menu item '{item.name}'. Using default accent.")
                item_bg_color = config_module.COLOR_ACCENT # Fallback color
            
            pygame.draw.rect(screen, item_bg_color, item_rect)
            # Draw border outline for item
            pygame.draw.rect(screen, config_module.COLOR_BORDER, item_rect, width=config_module.Theme.BORDER_WIDTH)

            # Draw the category name
            font = fonts['medium']
            if item.name == "SECRET GAMES": # TODO: make this more robust. Use item.name
                # Special handling for "SECRET GAMES"
                title_text = CLASSIFIED_TEXT
            else:
                title_text = item.name # Use item.name
            text_surface = font.render(title_text, True, config_module.Palette.BLACK) 
            text_pos = (item_rect.left + 10, item_rect.centery - text_surface.get_height() // 2)
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
        _draw_arrow_indicator(screen, arrow_area_rect, selected_item_rect, selected_item_color, config_module)

    # --- Part 5: Draw Main Content Area ---
    total_sidebar_width = base_sidebar_width + arrow_indicator_width
    main_content_rect = pygame.Rect(
        total_sidebar_width,
        header_height,
        screen_width - total_sidebar_width,
        screen_height - header_height
    )
    pygame.draw.rect(screen, config_module.Theme.BACKGROUND, main_content_rect)

    if app_state.current_state == STATE_MENU:
        logo_surface = None
        scaled_logo_height = 0 
        try:
            logo_surface = pygame.image.load(config_module.SPLASH_LOGO_PATH).convert_alpha()
        except pygame.error as e:
            logger.warning(f"Could not load logo '{config_module.SPLASH_LOGO_PATH}' for menu: {e}")

        if logo_surface:
            content_width = main_content_rect.width
            content_height = main_content_rect.height
            logo_orig_width, logo_orig_height = logo_surface.get_size()
            max_logo_width = int(content_width * 0.6)
            max_logo_height = int(content_height * 0.5)
            scaled_width = logo_orig_width
            scaled_logo_height = logo_orig_height
            if logo_orig_width > max_logo_width:
                scale_ratio = max_logo_width / logo_orig_width
                scaled_width = max_logo_width
                scaled_logo_height = int(logo_orig_height * scale_ratio)
            if scaled_logo_height > max_logo_height:
                scale_ratio = max_logo_height / scaled_logo_height
                scaled_logo_height = max_logo_height
                scaled_width = int(scaled_width * scale_ratio)
            if scaled_width != logo_orig_width or scaled_logo_height != logo_orig_height:
                try:
                    logo_surface = pygame.transform.smoothscale(logo_surface, (scaled_width, scaled_logo_height))
                except pygame.error as e:
                    logger.warning(f"Could not scale logo: {e}")
                    logo_surface = None
        
        logo_display_y = main_content_rect.top + (main_content_rect.height // 3) - (scaled_logo_height // 2 if logo_surface else 0)
        if logo_surface:
            logo_rect = logo_surface.get_rect(centerx=main_content_rect.centerx, y=logo_display_y)
            screen.blit(logo_surface, logo_rect)
            wifi_text_y_start = logo_rect.bottom + 20
        else:
            wifi_text_y_start = main_content_rect.centery - fonts['medium'].get_height()

        wifi_status_text = "WiFi: N/A"
        wifi_ssid_text = "SSID: N/A"
        wifi_status_color = config_module.Theme.ALERT 
        # Access sensor_values using INFO_WIFI_STATUS etc. from config_module
        wifi_status_data = sensor_values.get(config_module.INFO_WIFI_STATUS, {})
        wifi_ssid_data = sensor_values.get(config_module.INFO_WIFI_SSID, {})
        wifi_status_val = wifi_status_data.get("text", "N/A")
        wifi_ssid_val = wifi_ssid_data.get("text", "N/A")
        if wifi_status_val and wifi_status_val != "N/A":
            wifi_status_text = f"Status: {wifi_status_val}"
            if wifi_status_val.lower() == "online":
                wifi_status_color = config_module.Theme.CONTENT_WIFI_ONLINE_STATUS
        if wifi_ssid_val and wifi_ssid_val != "N/A":
            wifi_ssid_text = f"SSID: {wifi_ssid_val}"

        font_medium = fonts['medium']
        status_surface = font_medium.render(wifi_status_text, True, wifi_status_color)
        ssid_surface = font_medium.render(wifi_ssid_text, True, config_module.Theme.FOREGROUND)
        status_rect = status_surface.get_rect(centerx=main_content_rect.centerx, y=wifi_text_y_start)
        ssid_rect = ssid_surface.get_rect(centerx=main_content_rect.centerx, y=status_rect.bottom + 5)
        screen.blit(status_surface, status_rect)
        screen.blit(ssid_surface, ssid_rect)
    
    elif app_state.current_state == STATE_SECRET_GAMES:
        title_font = fonts['large']
        title_text = CLASSIFIED_TEXT
        title_surface = title_font.render(title_text, True, config_module.Theme.ACCENT)
        title_rect = title_surface.get_rect(centerx=main_content_rect.centerx, centery=main_content_rect.top + 50)
        screen.blit(title_surface, title_rect)

    # --- Part 6: Draw Footer (centered on main content area only) ---
    key_prev_name = pygame.key.name(config_module.KEY_PREV).upper()
    key_select_name = pygame.key.name(config_module.KEY_SELECT).upper()
    key_next_name = pygame.key.name(config_module.KEY_NEXT).upper()
    hint_text = _get_footer_content(config_module)

    # Create a custom footer rendering that centers on main content area
    footer_font = fonts.get('small', fonts.get('medium'))
    footer_surface = footer_font.render(hint_text, True, config_module.Theme.FOREGROUND)
    footer_y = screen_height - footer_surface.get_height() - 5
    footer_x = main_content_rect.centerx - footer_surface.get_width() // 2
    screen.blit(footer_surface, (footer_x, footer_y))

# REMOVED _draw_sidebar function - logic integrated above
# def _draw_sidebar(screen, rect, menu_items, selected_index, fonts, config, header_height):
#    ...

# REMOVED _draw_system_info function - moved to ui/views/system_info_view.py

# REMOVED _draw_settings function - moved to ui/views/settings_view.py 

 