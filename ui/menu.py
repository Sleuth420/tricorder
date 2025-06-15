# --- ui/menu.py ---
# Handles rendering of the menu sidebar and the main menu screen layout

import pygame
import logging
import time
from datetime import datetime
from config import version

from ui.components.menu_base import draw_menu_base_layout
from ui.components.text_display import render_footer
from models.app_state import STATE_MENU, STATE_SECRET_GAMES # Import necessary states
from config import CLASSIFIED_TEXT

logger = logging.getLogger(__name__)

# Module-level flag to prevent repeated layout logging
_main_menu_logged = False

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

def draw_menu_screen(screen, app_state, fonts, config_module, sensor_values, ui_scaler):
    """
    Draw the menu screen with sidebar, arrow indicator, and main content area.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        sensor_values (dict): Dictionary of current sensor values
        ui_scaler (UIScaler): UI scaling system for responsive design
    """
    global _main_menu_logged
    
    if app_state.current_state not in [STATE_MENU, STATE_SECRET_GAMES]:
        logger.warning(f"draw_menu_screen called unexpectedly in state: {app_state.current_state}")
        return

    # Draw the base menu layout (header, sidebar, arrow indicator)
    layout_info = draw_menu_base_layout(screen, app_state, fonts, config_module, ui_scaler)
    
    # Debug logging for main menu layout - only log once
    if ui_scaler.debug_mode and not _main_menu_logged:
        logger.info(f"🎨 MainMenu: Using layout - main_content={layout_info['main_content_rect']}, total_sidebar={layout_info['total_sidebar_width']}px")
        _main_menu_logged = True

    main_content_rect = layout_info['main_content_rect']
    screen_width = layout_info['screen_width']
    screen_height = layout_info['screen_height']

    # Draw specific main content based on current state
    if app_state.current_state == STATE_MENU:
        _draw_main_menu_content(screen, main_content_rect, sensor_values, fonts, config_module, ui_scaler)
    elif app_state.current_state == STATE_SECRET_GAMES:
        _draw_secret_games_content(screen, main_content_rect, fonts, config_module, ui_scaler)
    
    # Draw footer with stardate
    _draw_main_menu_footer(screen, main_content_rect, fonts, config_module, screen_height, ui_scaler)

def _draw_main_menu_content(screen, main_content_rect, sensor_values, fonts, config_module, ui_scaler):
    """
    Draw main menu specific content (logo and WiFi status) with responsive scaling.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        main_content_rect (pygame.Rect): Rectangle for main content area
        sensor_values (dict): Dictionary of current sensor values
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        ui_scaler (UIScaler): UI scaling system for responsive design
    """
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
        
        # Use UIScaler for responsive logo sizing
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
        # Use UIScaler for responsive spacing
        wifi_text_y_start = logo_rect.bottom + ui_scaler.margin("medium")
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
    # Use UIScaler for responsive spacing between status lines
    ssid_rect = ssid_surface.get_rect(centerx=main_content_rect.centerx, y=status_rect.bottom + ui_scaler.padding("small"))
    screen.blit(status_surface, status_rect)
    screen.blit(ssid_surface, ssid_rect)
    
def _draw_secret_games_content(screen, main_content_rect, fonts, config_module, ui_scaler):
    """
    Draw secret games menu specific content with responsive scaling.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        main_content_rect (pygame.Rect): Rectangle for main content area
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        ui_scaler (UIScaler): UI scaling system for responsive design
    """
    title_font = fonts['large']
    title_text = CLASSIFIED_TEXT
    title_surface = title_font.render(title_text, True, config_module.Theme.ACCENT)
    # Use UIScaler for responsive positioning
    title_y = main_content_rect.top + ui_scaler.scale(50)
    title_rect = title_surface.get_rect(centerx=main_content_rect.centerx, centery=title_y)
    screen.blit(title_surface, title_rect)

def _draw_main_menu_footer(screen, main_content_rect, fonts, config_module, screen_height, ui_scaler):
    """
    Draw footer for main menu with stardate using responsive positioning.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        main_content_rect (pygame.Rect): Rectangle for main content area
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        screen_height (int): Screen height
        ui_scaler (UIScaler): UI scaling system for responsive design
    """
    hint_text = _get_footer_content(config_module)

    # Create a custom footer rendering that centers on main content area
    footer_font = fonts.get('small', fonts.get('medium'))
    footer_surface = footer_font.render(hint_text, True, config_module.Theme.FOREGROUND)
    # Use UIScaler for responsive footer positioning
    footer_margin = ui_scaler.margin("small")
    footer_y = screen_height - footer_surface.get_height() - footer_margin
    footer_x = main_content_rect.centerx - footer_surface.get_width() // 2
    screen.blit(footer_surface, (footer_x, footer_y))

# Note: Arrow indicator and sidebar rendering logic moved to ui/components/menu_base.py
# for shared use between main menu and sensors menu