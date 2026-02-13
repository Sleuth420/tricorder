# --- ui/menu.py ---
# Handles rendering of the menu sidebar and the main menu screen layout

import pygame
import logging
import time
from datetime import datetime
from config import version

from ui.components.menus.menu_base import draw_menu_base_layout
from ui.components.text.text_display import render_footer
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
        _draw_main_menu_content(screen, main_content_rect, sensor_values, fonts, config_module, ui_scaler, app_state)
    elif app_state.current_state == STATE_SECRET_GAMES:
        _draw_secret_games_content(screen, main_content_rect, fonts, config_module, ui_scaler)
    
    # Draw footer with stardate
    _draw_main_menu_footer(screen, main_content_rect, fonts, config_module, screen_height, ui_scaler)

def _draw_main_menu_content(screen, main_content_rect, sensor_values, fonts, config_module, ui_scaler, app_state):
    """
    Draw main menu specific content with Star Trek tricorder theming and animations.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        main_content_rect (pygame.Rect): Rectangle for main content area
        sensor_values (dict): Dictionary of current sensor values
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        ui_scaler (UIScaler): UI scaling system for responsive design
        app_state (AppState): Application state for timing and animations
    """
    # Get current time for animations
    current_time = time.time()
    
    # Logo cycling system - change logo every 10 seconds
    logo_cycle_interval = 10.0
    logo_cycle_phase = int(current_time / logo_cycle_interval) % 2
    
    # Available logo images (you can add more to assets/images/)
    logo_paths = [
        config_module.SPLASH_LOGO_PATH,  # Main logo
        "assets/images/spork.png"        # Alternative image
    ]
    
    current_logo_path = logo_paths[logo_cycle_phase]
    
    logo_surface = None
    scaled_logo_height = 0 
    try:
        logo_surface = pygame.image.load(current_logo_path).convert_alpha()
    except pygame.error as e:
        logger.warning(f"Could not load logo '{current_logo_path}' for menu: {e}")
        # Fallback to main logo
        try:
            logo_surface = pygame.image.load(config_module.SPLASH_LOGO_PATH).convert_alpha()
        except pygame.error as e2:
            logger.warning(f"Could not load fallback logo: {e2}")
    
    if logo_surface:
        content_width = main_content_rect.width
        content_height = main_content_rect.height
        logo_orig_width, logo_orig_height = logo_surface.get_size()
        
        # Use UIScaler for responsive logo sizing - make it larger since we removed WiFi info
        max_logo_width = int(content_width * 0.8)  # Increased from 0.6
        max_logo_height = int(content_height * 0.7)  # Increased from 0.5
        
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
    
    # Center the logo vertically in the available space
    logo_display_y = main_content_rect.top + (main_content_rect.height // 2) - (scaled_logo_height // 2 if logo_surface else 0)
    
    if logo_surface:
        logo_rect = logo_surface.get_rect(centerx=main_content_rect.centerx, y=logo_display_y)
        
        # Improved fade transition effect with smoother timing
        fade_duration = 1.5  # Longer, smoother fade duration
        cycle_progress = (current_time % logo_cycle_interval) / logo_cycle_interval
        
        # Smoother fade curve using sine function
        if cycle_progress > (1.0 - fade_duration / logo_cycle_interval):
            # Fading out with smooth curve
            fade_progress = (cycle_progress - (1.0 - fade_duration / logo_cycle_interval)) / (fade_duration / logo_cycle_interval)
            # Use sine curve for smoother fade
            alpha = int(255 * (0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate((1.0 - fade_progress) * 90).x))
        elif cycle_progress < (fade_duration / logo_cycle_interval):
            # Fading in with smooth curve
            fade_progress = cycle_progress / (fade_duration / logo_cycle_interval)
            # Use sine curve for smoother fade
            alpha = int(255 * (0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate(fade_progress * 90).x))
        else:
            alpha = 255
        
        # Apply alpha if fading
        if alpha < 255:
            logo_surface = logo_surface.copy()
            logo_surface.set_alpha(alpha)
        
        # Improved breathing effect with smoother, less frequent scaling
        breathing_cycle = 12.0  # Slower, more relaxed breathing cycle
        breathing_progress = (current_time % breathing_cycle) / breathing_cycle
        # Reduced scale range and smoother curve
        breathing_scale = 1.0 + (0.015 * (0.5 + 0.5 * pygame.math.Vector2(1, 0).rotate(breathing_progress * 360).x))
        
        # Only apply breathing when not fading to avoid compound scaling issues
        if alpha >= 240 and breathing_scale != 1.0:
            # Scale the logo slightly for breathing effect
            new_width = int(logo_surface.get_width() * breathing_scale)
            new_height = int(logo_surface.get_height() * breathing_scale)
            if new_width > 0 and new_height > 0:
                try:
                    logo_surface = pygame.transform.smoothscale(logo_surface, (new_width, new_height))
                    # Recalculate position to keep centered
                    logo_rect = logo_surface.get_rect(centerx=main_content_rect.centerx, centery=logo_display_y + scaled_logo_height // 2)
                except pygame.error:
                    pass  # Use original if scaling fails
        
        screen.blit(logo_surface, logo_rect)
        
        # Add multiple tricorder-style animations
        _draw_tricorder_scanning_effect(screen, main_content_rect, logo_rect, current_time, config_module, ui_scaler)
        _draw_data_stream_animation(screen, main_content_rect, current_time, config_module, ui_scaler)
        _draw_corner_status_indicators(screen, main_content_rect, current_time, config_module, ui_scaler)
    
def _draw_tricorder_scanning_effect(screen, main_content_rect, logo_rect, current_time, config_module, ui_scaler):
    """
    Draw subtle tricorder-style scanning lines animation.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        main_content_rect (pygame.Rect): Rectangle for main content area
        logo_rect (pygame.Rect): Rectangle of the logo
        current_time (float): Current time for animation
        config_module (module): Configuration module
        ui_scaler (UIScaler): UI scaling system for responsive design
    """
    # Animation parameters
    scan_speed = 2.0  # Speed of scanning animation
    scan_height = 2   # Height of scanning lines
    scan_spacing = 20 # Spacing between scan lines
    
    # Calculate scanning area below logo
    scan_area_top = logo_rect.bottom + ui_scaler.margin("medium")
    scan_area_bottom = main_content_rect.bottom - ui_scaler.margin("large")
    scan_area_height = scan_area_bottom - scan_area_top
    
    if scan_area_height > 40:  # Only draw if we have enough space
        # Calculate number of scan lines that fit
        num_lines = max(1, scan_area_height // scan_spacing)
        
        for i in range(num_lines):
            # Stagger the animation timing for each line
            line_offset = i * 0.3
            line_progress = (current_time * scan_speed + line_offset) % 4.0
            
            # Only draw line during certain phases of the animation
            if line_progress < 2.0:  # Line is "active" for half the cycle
                line_y = scan_area_top + (i * scan_spacing)
                
                # Calculate line width and position for scanning effect
                max_width = main_content_rect.width * 0.6
                if line_progress < 1.0:
                    # Growing phase
                    line_width = int(max_width * line_progress)
                else:
                    # Shrinking phase
                    line_width = int(max_width * (2.0 - line_progress))
                
                if line_width > 4:  # Only draw if line is visible
                    line_x = main_content_rect.centerx - line_width // 2
                    line_rect = pygame.Rect(line_x, line_y, line_width, scan_height)
                    
                    # Use a dim green color for subtle effect
                    scan_color = (0, 100, 30)  # Dim green
                    pygame.draw.rect(screen, scan_color, line_rect)

def _draw_data_stream_animation(screen, main_content_rect, current_time, config_module, ui_scaler):
    """
    Draw subtle data stream animation in corners - like tricorder data processing.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        main_content_rect (pygame.Rect): Rectangle for main content area
        current_time (float): Current time for animation
        config_module (module): Configuration module
        ui_scaler (UIScaler): UI scaling system for responsive design
    """
    # Only draw if we have enough space
    if main_content_rect.width < 200 or main_content_rect.height < 150:
        return
    
    # Animation parameters
    stream_speed = 3.0
    dot_size = 2
    stream_length = 8
    
    # Top-right corner data stream
    corner_margin = ui_scaler.margin("small")
    start_x = main_content_rect.right - corner_margin - 60
    start_y = main_content_rect.top + corner_margin
    
    for i in range(stream_length):
        # Calculate position with flowing animation
        flow_offset = (current_time * stream_speed + i * 0.5) % 6.0
        
        if flow_offset < 3.0:  # Dot is visible during first half of cycle
            dot_x = start_x + int(flow_offset * 8)
            dot_y = start_y + (i * 4)
            
            # Fade in/out effect
            if flow_offset < 1.0:
                alpha_factor = flow_offset
            elif flow_offset > 2.0:
                alpha_factor = 3.0 - flow_offset
            else:
                alpha_factor = 1.0
            
            # Dim green dots
            dot_color = (0, int(80 * alpha_factor), int(20 * alpha_factor))
            if dot_color[1] > 10:  # Only draw if visible
                pygame.draw.circle(screen, dot_color, (dot_x, dot_y), dot_size)

def _draw_corner_status_indicators(screen, main_content_rect, current_time, config_module, ui_scaler):
    """
    Draw subtle pulsing status indicators in corners - like system status lights.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        main_content_rect (pygame.Rect): Rectangle for main content area
        current_time (float): Current time for animation
        config_module (module): Configuration module
        ui_scaler (UIScaler): UI scaling system for responsive design
    """
    # Only draw if we have enough space
    if main_content_rect.width < 150 or main_content_rect.height < 100:
        return
    
    corner_margin = ui_scaler.margin("small")
    indicator_size = 4
    
    # Bottom-left status indicator (slow pulse)
    pulse_1 = (current_time * 0.8) % 2.0
    if pulse_1 < 1.0:
        pulse_alpha_1 = pulse_1
    else:
        pulse_alpha_1 = 2.0 - pulse_1
    
    indicator_1_pos = (main_content_rect.left + corner_margin, 
                      main_content_rect.bottom - corner_margin - indicator_size)
    indicator_1_color = (0, int(120 * pulse_alpha_1), int(40 * pulse_alpha_1))
    if indicator_1_color[1] > 20:
        pygame.draw.circle(screen, indicator_1_color, indicator_1_pos, indicator_size)
    
    # Bottom-right status indicator (faster pulse, offset timing)
    pulse_2 = (current_time * 1.2 + 1.0) % 2.0
    if pulse_2 < 1.0:
        pulse_alpha_2 = pulse_2
    else:
        pulse_alpha_2 = 2.0 - pulse_2
    
    indicator_2_pos = (main_content_rect.right - corner_margin - indicator_size, 
                      main_content_rect.bottom - corner_margin - indicator_size)
    indicator_2_color = (int(100 * pulse_alpha_2), int(100 * pulse_alpha_2), 0)  # Amber
    if indicator_2_color[0] > 20:
        pygame.draw.circle(screen, indicator_2_color, indicator_2_pos, indicator_size)

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
    # Use UIScaler for responsive footer positioning; inset for safe area / overscan on Pi
    footer_margin = ui_scaler.margin("small")
    safe_bottom = ui_scaler.get_safe_area_margins()["bottom"] if (ui_scaler and ui_scaler.safe_area_enabled) else 0
    footer_y = screen_height - footer_surface.get_height() - footer_margin - safe_bottom
    footer_x = main_content_rect.centerx - footer_surface.get_width() // 2
    screen.blit(footer_surface, (footer_x, footer_y))

# Note: Arrow indicator and sidebar rendering logic moved to ui/components/menu_base.py
# for shared use between main menu and sensors menu