# --- ui/menu.py ---
# Handles rendering of the menu sidebar and the main menu screen layout

import pygame
import logging
from ui.components.ui_elements import draw_panel # Keep draw_panel if needed elsewhere, or remove
from ui.components.text_display import render_footer
# Import the new view functions
from ui.views.system_info_view import draw_system_info_view

logger = logging.getLogger(__name__)

# REMOVED MENU_CATEGORIES - now driven by app_state.menu_items

def draw_menu_screen(screen, app_state, fonts, config, sensor_values):
    """
    Draw the menu screen with sidebar and main content area (System Info).
    Structured into distinct rectangular parts: Corner (TEMP RED), Header, Sidebar Items.
    """
    # Clear screen with background color
    screen.fill(config.COLOR_BACKGROUND)

    screen_width = screen.get_width()
    screen_height = screen.get_height()

    # Ensure we are in the MENU state to draw this layout
    if app_state.current_state != "MENU":
        logger.warning(f"draw_menu_screen called unexpectedly in state: {app_state.current_state}")
        return

    # Define dimensions and colors using config
    sidebar_width = min(screen_width // 4, 150)
    header_height = config.HEADER_HEIGHT # Use constant from config
    header_color = config.COLOR_HEADER_CORNER # Use new Orange constant
    corner_color = config.COLOR_HEADER_CORNER # Corner uses same Orange constant
    curve_radius = config.CORNER_CURVE_RADIUS # Use constant from config

    # Get menu items and selected index
    menu_items = app_state.get_current_menu_items()
    selected_index = app_state.get_current_menu_index()

    # --- Part 1: Draw Corner Rectangle (Distinct block, Orange) ---
    corner_rect = pygame.Rect(0, 0, sidebar_width, header_height)
    # Apply rounding only to the top-left corner
    pygame.draw.rect(screen, corner_color, corner_rect, border_top_left_radius=curve_radius)
    # Draw border outline (should respect rounding)
    pygame.draw.rect(screen, config.COLOR_BORDER, corner_rect, width=config.BORDER_WIDTH, border_top_left_radius=curve_radius)

    # --- Part 2: Draw Header Bar (Starts AFTER sidebar width, Orange) ---
    header_rect = pygame.Rect(sidebar_width, 0, screen_width - sidebar_width, header_height)
    pygame.draw.rect(screen, header_color, header_rect)
    # Draw border outline
    pygame.draw.rect(screen, config.COLOR_BORDER, header_rect, width=config.BORDER_WIDTH)

    # --- Part 3: Draw Sidebar Items (Starts BELOW header height) ---
    sidebar_content_y_start = header_height # Items start below the header/corner
    sidebar_content_height = screen_height - header_height
    sidebar_items_area = pygame.Rect(0, sidebar_content_y_start, sidebar_width, sidebar_content_height)

    if menu_items: # Avoid division by zero
        item_height = sidebar_content_height // len(menu_items)
        for i, item in enumerate(menu_items):
            item_rect = pygame.Rect(
                sidebar_items_area.left,
                sidebar_content_y_start + (i * item_height),
                sidebar_items_area.width,
                item_height
            )

            # Draw the background using the color_key from the item
            try:
                item_bg_color = getattr(config, item["color_key"])
            except (AttributeError, KeyError):
                logger.warning(f"Color key '{item.get('color_key')}' not found for '{item.get('name')}'. Using default.")
                item_bg_color = config.COLOR_ACCENT # Fallback color
            pygame.draw.rect(screen, item_bg_color, item_rect)
            # Draw border outline for item
            pygame.draw.rect(screen, config.COLOR_BORDER, item_rect, width=config.BORDER_WIDTH)

            # Draw the category name
            font = fonts['medium']
            text_surface = font.render(item["name"], True, (255, 255, 255)) # White text
            text_pos = (item_rect.left + 10, item_rect.centery - text_surface.get_height() // 2)
            screen.blit(text_surface, text_pos)

            # Draw selection indicator if this item is selected
            if i == selected_index:
                # Draw a white border indicator
                border_width = 1
                selection_rect = pygame.Rect(
                    item_rect.left + border_width // 2,
                    item_rect.top + border_width // 2,
                    item_rect.width - border_width,
                    item_rect.height - border_width
                )
                pygame.draw.rect(screen, (255, 255, 255), selection_rect, border_width)

    # --- Part 4: Draw Main Content Area --- (Below header, right of sidebar)
    main_content_rect = pygame.Rect(
        sidebar_width,
        header_height, # Start below the header
        screen_width - sidebar_width,
        screen_height - header_height # Adjust height
    )
    # Clear main content area (it used to be cleared by draw_system_info_view)
    pygame.draw.rect(screen, config.COLOR_BACKGROUND, main_content_rect)

    # Load Logo
    logo_surface = None
    try:
        logo_surface = pygame.image.load("images/logo.png").convert_alpha()
    except pygame.error as e:
        logger.warning(f"Could not load logo.png for menu: {e}")

    if logo_surface:
        # Scale logo to fit nicely in the main content area, e.g., 50% of width or height
        content_width = main_content_rect.width
        content_height = main_content_rect.height
        
        logo_orig_width, logo_orig_height = logo_surface.get_size()
        
        # Define a max size for the logo, e.g., 60% of content width
        # and ensure it's not too tall, e.g., 50% of content height minus some padding for WiFi
        max_logo_width = int(content_width * 0.6)
        max_logo_height = int(content_height * 0.5) # Reserve space for WiFi text

        scaled_width = logo_orig_width
        scaled_height = logo_orig_height

        if logo_orig_width > max_logo_width:
            scale_ratio = max_logo_width / logo_orig_width
            scaled_width = max_logo_width
            scaled_height = int(logo_orig_height * scale_ratio)

        if scaled_height > max_logo_height:
            scale_ratio = max_logo_height / scaled_height
            scaled_height = max_logo_height
            scaled_width = int(scaled_width * scale_ratio)
        
        if scaled_width != logo_orig_width or scaled_height != logo_orig_height:
            try:
                logo_surface = pygame.transform.smoothscale(logo_surface, (scaled_width, scaled_height))
            except pygame.error as e:
                logger.warning(f"Could not scale logo: {e}")
                logo_surface = None # Don't draw if scaling failed badly

    logo_display_y = main_content_rect.top + (main_content_rect.height // 3) - (scaled_height // 2 if logo_surface else 0)


    if logo_surface:
        logo_rect = logo_surface.get_rect(centerx=main_content_rect.centerx, y=logo_display_y)
        screen.blit(logo_surface, logo_rect)
        wifi_text_y_start = logo_rect.bottom + 20 # Position WiFi info below logo
    else:
        # If logo fails to load/scale, position WiFi info more centrally
        wifi_text_y_start = main_content_rect.centery - fonts['medium'].get_height() 


    # Display Wi-Fi Information
    wifi_status_text = "WiFi: N/A"
    wifi_ssid_text = "SSID: N/A"
    wifi_status_color = config.COLOR_ALERT # Default to alert color

    wifi_status_val = sensor_values.get("WIFI_STATUS", ("N/A", "", ""))[0]
    wifi_ssid_val = sensor_values.get("WIFI_SSID", ("N/A", "", ""))[0]

    if wifi_status_val and wifi_status_val != "N/A":
        wifi_status_text = f"Status: {wifi_status_val}"
        if wifi_status_val.lower() == "online":
            wifi_status_color = config.COLOR_WIFI_ONLINE
    
    if wifi_ssid_val and wifi_ssid_val != "N/A":
        wifi_ssid_text = f"SSID: {wifi_ssid_val}"

    font_medium = fonts['medium']
    status_surface = font_medium.render(wifi_status_text, True, wifi_status_color)
    ssid_surface = font_medium.render(wifi_ssid_text, True, config.COLOR_FOREGROUND)

    status_rect = status_surface.get_rect(centerx=main_content_rect.centerx, y=wifi_text_y_start)
    ssid_rect = ssid_surface.get_rect(centerx=main_content_rect.centerx, y=status_rect.bottom + 5)
    
    screen.blit(status_surface, status_rect)
    screen.blit(ssid_surface, ssid_rect)

    # --- Part 5: Draw Footer --- (For the overall menu screen)
    key_prev_name = pygame.key.name(config.KEY_PREV).upper()
    key_next_name = pygame.key.name(config.KEY_NEXT).upper()
    key_select_name = pygame.key.name(config.KEY_SELECT).upper()
    hint_text = f"< {key_prev_name}=Up | {key_select_name}=Select | {key_next_name}=Down >"

    render_footer(
        screen,
        hint_text,
        fonts,
        config.COLOR_FOREGROUND,
        screen_width,
        screen_height
    )

# REMOVED _draw_sidebar function - logic integrated above
# def _draw_sidebar(screen, rect, menu_items, selected_index, fonts, config, header_height):
#    ...

# REMOVED _draw_system_info function - moved to ui/views/system_info_view.py

# REMOVED _draw_settings function - moved to ui/views/settings_view.py 