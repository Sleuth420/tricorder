# --- ui/menu.py ---
# Handles rendering of the menu sidebar and the main menu screen layout

import pygame
import logging
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

# REMOVED MENU_CATEGORIES - now driven by app_state.menu_items

def draw_menu_screen(screen, app_state, fonts, config_module, sensor_values):
    """
    Draw the menu screen with sidebar and main content area.
    """
    screen.fill(config_module.Theme.BACKGROUND) 

    screen_width = screen.get_width()
    screen_height = screen.get_height()

    if app_state.current_state not in [STATE_MENU, STATE_SECRET_GAMES]:
        logger.warning(f"draw_menu_screen called unexpectedly in state: {app_state.current_state}")
        return

    sidebar_width = min(screen_width // 4, 150)
    header_height = config_module.HEADER_HEIGHT
    header_color = config_module.Theme.HEADER_CORNER_FILL 
    corner_color = config_module.Theme.HEADER_CORNER_FILL
    curve_radius = config_module.Theme.CORNER_CURVE_RADIUS
    border_width_val = config_module.Theme.BORDER_WIDTH

    menu_items = app_state.get_current_menu_items()
    selected_index = app_state.get_current_menu_index()

    # --- Part 1: Draw Corner Rectangle ---
    corner_rect = pygame.Rect(0, 0, sidebar_width, header_height)
    pygame.draw.rect(screen, corner_color, corner_rect, border_top_left_radius=curve_radius)
    pygame.draw.rect(screen, config_module.Theme.BORDER_GENERAL, corner_rect, width=border_width_val, border_top_left_radius=curve_radius)

    # --- Part 2: Draw Header Bar ---
    header_rect = pygame.Rect(sidebar_width, 0, screen_width - sidebar_width, header_height)
    pygame.draw.rect(screen, header_color, header_rect)
    pygame.draw.rect(screen, config_module.Theme.BORDER_GENERAL, header_rect, width=border_width_val)

    # --- Part 3: Draw Sidebar Items ---
    sidebar_content_y_start = header_height
    sidebar_content_height = screen_height - header_height
    sidebar_items_area = pygame.Rect(0, sidebar_content_y_start, sidebar_width, sidebar_content_height)

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
                item_bg_color = config_module.Theme.ACCENT # Fallback color
            
            pygame.draw.rect(screen, item_bg_color, item_rect)
            pygame.draw.rect(screen, config_module.Theme.BORDER_GENERAL, item_rect, width=border_width_val)

            font_to_use = fonts['medium'] 
            if item.name == "SECRET GAMES": # TODO: make this more robust. Use item.name
                # Special handling for "SECRET GAMES"
                title_text = CLASSIFIED_TEXT
            else:
                title_text = item.name # Use item.name
            text_surface = font_to_use.render(title_text, True, config_module.Theme.WHITE) 
            text_pos = (item_rect.left + 10, item_rect.centery - text_surface.get_height() // 2)
            screen.blit(text_surface, text_pos)

            if i == selected_index:
                selection_border_width = 3 # Make selection border thicker
                selection_rect = pygame.Rect(
                    item_rect.left + selection_border_width // 2,
                    item_rect.top + selection_border_width // 2,
                    item_rect.width - selection_border_width,
                    item_rect.height - selection_border_width
                )
                pygame.draw.rect(screen, config_module.Theme.WHITE, selection_rect, selection_border_width)

    # --- Part 4: Draw Main Content Area ---
    main_content_rect = pygame.Rect(
        sidebar_width,
        header_height,
        screen_width - sidebar_width,
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

    # --- Part 5: Draw Footer ---
    key_prev_name = pygame.key.name(config_module.KEY_PREV).upper()
    key_next_name = pygame.key.name(config_module.KEY_NEXT).upper()
    key_select_name = pygame.key.name(config_module.KEY_SELECT).upper()
    hint_text = f"< {key_prev_name}=Up | {key_select_name}=Select | {key_next_name}=Down >"

    render_footer(
        screen, hint_text, fonts,
        config_module.Theme.FOREGROUND,
        screen_width, screen_height
    )

# REMOVED _draw_sidebar function - logic integrated above
# def _draw_sidebar(screen, rect, menu_items, selected_index, fonts, config, header_height):
#    ...

# REMOVED _draw_system_info function - moved to ui/views/system_info_view.py

# REMOVED _draw_settings function - moved to ui/views/settings_view.py 