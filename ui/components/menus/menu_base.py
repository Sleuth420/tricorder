# --- ui/components/menu_base.py ---
# Shared base component for menu rendering (sidebar, header, arrow indicator)

import pygame
import logging
import time
import math
from config import CLASSIFIED_TEXT

logger = logging.getLogger(__name__)


def _lighten(rgb, factor=0.25):
    """Return a lighter shade of the color for highlights."""
    return tuple(min(255, int(c + (255 - c) * factor)) for c in rgb)


def _darken(rgb, factor=0.2):
    """Return a darker shade for depth/shadows."""
    return tuple(max(0, int(c * (1 - factor))) for c in rgb)

# Module-level flag to prevent repeated layout logging
_layout_logged = False

def draw_menu_base_layout(screen, app_state, fonts, config_module, ui_scaler, base_sidebar_width=None):
    """
    Draw the shared menu base layout (header, sidebar, arrow indicator) with responsive scaling.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        ui_scaler (UIScaler): UI scaling system for responsive design
        base_sidebar_width (int, optional): Override default sidebar width
        
    Returns:
        dict: Layout information for the main content area
    """
    global _layout_logged
    
    screen.fill(config_module.Theme.BACKGROUND)
    screen_width = ui_scaler.screen_width
    screen_height = ui_scaler.screen_height
    menu_items = app_state.get_current_menu_items()
    text_padding = ui_scaler.padding("medium")
    safe_left = ui_scaler.get_safe_area_margins()["left"] if (ui_scaler and ui_scaler.safe_area_enabled) else 0
    
    # Layout calculations with arrow indicator area using UIScaler
    if base_sidebar_width is None:
        # Compute minimum sidebar width so longest label fits (main + submenus e.g. "Env: Humid", "Schematics")
        font = fonts.get("medium", fonts.get("default"))
        max_text_width = 0
        if menu_items and font:
            for item in menu_items:
                label = CLASSIFIED_TEXT if item.name == "SECRET GAMES" else item.name
                w = font.size(label)[0]
                max_text_width = max(max_text_width, w)
        # Extra right margin so text doesn't clip at arrow column; room for Settings "!" badge
        extra_right = ui_scaler.scale(22) if ui_scaler else 22
        min_sidebar_for_text = (max_text_width + 2 * text_padding + safe_left + extra_right) if max_text_width else (safe_left + extra_right + 60)
        
        if ui_scaler.is_small_screen():
            # For small screens (Pi): wider minimum so "Env: Humid", "Environmental" etc. don't cut off
            base_sidebar_width = max(min_sidebar_for_text, 132, screen_width // 3)
        else:
            # For larger screens, use original proportion: ~25% of screen width
            base_sidebar_width = max(130, min(screen_width // 4, 200))

    arrow_indicator_width = ui_scaler.scale(config_module.ARROW_INDICATOR_WIDTH)
    header_height = ui_scaler.header_height()
    
    # Debug logging for layout calculations - only log once
    if ui_scaler.debug_mode and not _layout_logged:
        total_sidebar_width = base_sidebar_width + arrow_indicator_width
        main_content_width = screen_width - total_sidebar_width
        main_content_height = screen_height - header_height
        logger.info(f"🎨 MenuBase Layout: screen={screen_width}x{screen_height}, header={header_height}px, sidebar={base_sidebar_width}px, arrow={arrow_indicator_width}px, main_content={main_content_width}x{main_content_height}px")
        _layout_logged = True

    header_color = config_module.Theme.HEADER_CORNER_FILL 
    corner_color = config_module.Theme.HEADER_CORNER_FILL
    curve_radius = config_module.Theme.CORNER_CURVE_RADIUS

    selected_index = app_state.get_current_menu_index()

    # --- Part 1: Draw Corner Rectangle (Distinct block, Orange) ---
    # Respect safe area margins for corner rectangle
    if ui_scaler and ui_scaler.safe_area_enabled:
        safe_margins = ui_scaler.get_safe_area_margins()
        corner_rect = pygame.Rect(
            safe_margins['left'], 
            safe_margins['top'], 
            base_sidebar_width - safe_margins['left'], 
            header_height - safe_margins['top']
        )
    else:
        corner_rect = pygame.Rect(0, 0, base_sidebar_width, header_height)
    
    # Apply rounding only to the top-left corner
    pygame.draw.rect(screen, corner_color, corner_rect, border_top_left_radius=curve_radius)
    # Draw border outline (should respect rounding)
    pygame.draw.rect(screen, config_module.COLOR_BORDER, corner_rect, width=config_module.Theme.BORDER_WIDTH, border_top_left_radius=curve_radius)
    # Bevel: bottom edge highlight where corner meets sidebar (raised panel)
    corner_highlight = _lighten(corner_color, 0.3)
    pygame.draw.line(screen, corner_highlight, (corner_rect.left, corner_rect.bottom - 1), (corner_rect.right, corner_rect.bottom - 1), 1)
    # Tricorder corner: tiny "READY" + small data bars (like status indicators)
    _draw_corner_tricorder_effects(screen, corner_rect, corner_color, config_module, fonts, ui_scaler)

    # --- Part 2: Draw Header Bar (Starts AFTER base sidebar width, Orange) ---
    # Header should span from base_sidebar_width to screen_width (no gap for arrow area)
    # Respect safe area margins for header bar
    if ui_scaler and ui_scaler.safe_area_enabled:
        safe_margins = ui_scaler.get_safe_area_margins()
        header_rect = pygame.Rect(
            base_sidebar_width, 
            safe_margins['top'], 
            screen_width - base_sidebar_width - safe_margins['right'], 
            header_height - safe_margins['top']
        )
    else:
        header_rect = pygame.Rect(base_sidebar_width, 0, screen_width - base_sidebar_width, header_height)
    
    pygame.draw.rect(screen, header_color, header_rect)
    # Draw border outline
    pygame.draw.rect(screen, config_module.COLOR_BORDER, header_rect, width=config_module.Theme.BORDER_WIDTH)
    # Bevel: top highlight and bottom shadow (raised panel)
    header_highlight = _lighten(header_color, 0.3)
    header_shadow = _darken(header_color, 0.25)
    pygame.draw.line(screen, header_highlight, (header_rect.left, header_rect.top), (header_rect.right, header_rect.top), 1)
    pygame.draw.line(screen, header_shadow, (header_rect.left, header_rect.bottom - 1), (header_rect.right, header_rect.bottom - 1), 1)
    # Tricorder header: scanning line + centre location + IP/freq on right
    _draw_header_tricorder_effects(screen, header_rect, header_color, config_module, fonts, ui_scaler, app_state)
    # Update-available indicator: red dot in top-right of header (not on Settings item)
    if hasattr(app_state, 'update_available') and app_state.update_available:
        _draw_update_indicator_header(screen, header_rect, config_module, fonts, ui_scaler)

    # --- Part 3: Draw Sidebar Items (Starts BELOW header height, no gap) ---
    sidebar_content_y_start = header_height  # Items start directly under header (no black strip)
    sidebar_content_height = screen_height - header_height
    
    # Respect safe area: items start at header_height (no top gap), reserve bottom for curve
    if ui_scaler and ui_scaler.safe_area_enabled:
        safe_margins = ui_scaler.get_safe_area_margins()
        sidebar_items_area = pygame.Rect(
            safe_margins['left'],
            sidebar_content_y_start,  # No +safe_margins['top'] — eliminates black gap under orange corner
            base_sidebar_width - safe_margins['left'],
            sidebar_content_height - safe_margins['bottom']
        )
        # Tricorder/LCARS: thin orange connector strip so corner flows into sidebar (no visible seam)
        connector_rect = pygame.Rect(safe_margins['left'], header_height, base_sidebar_width - safe_margins['left'], 2)
        pygame.draw.rect(screen, header_color, connector_rect)
    else:
        sidebar_items_area = pygame.Rect(0, sidebar_content_y_start, base_sidebar_width, sidebar_content_height)

    selected_item_rect = None
    selected_item_color = config_module.Theme.ACCENT

    if menu_items:
        # Use sidebar_items_area height so last item is not cut off by bottom curve
        available_sidebar_height = max(1, sidebar_items_area.height)
        item_height = available_sidebar_height // len(menu_items)
        for i, item in enumerate(menu_items): # item is now a MenuItem object
            item_rect = pygame.Rect(
                sidebar_items_area.left,
                sidebar_items_area.top + (i * item_height),
                sidebar_items_area.width,
                item_height
            )

            try:
                # item.color_key should be a string like "SIDEBAR_SYSTEM" or a Palette color name
                # Try Theme first, then Palette for backwards compatibility
                if hasattr(config_module.Theme, item.color_key):
                    item_bg_color = getattr(config_module.Theme, item.color_key)
                elif hasattr(config_module.Palette, item.color_key):
                    item_bg_color = getattr(config_module.Palette, item.color_key)
                else:
                    item_bg_color = config_module.Theme.ACCENT
            except AttributeError:
                logger.warning(f"Color attribute '{item.color_key}' not found in Theme or Palette for menu item '{item.name}'. Using default accent.")
                item_bg_color = config_module.COLOR_ACCENT # Fallback color
            
            # Tricorder/LCARS: rounded corners on first/last items only (panel feel)
            if len(menu_items) > 1:
                if i == 0:
                    # Only round top-left so it joins the header; keep others square
                    r = min(8, getattr(config_module.Theme, 'CORNER_CURVE_RADIUS', 60))
                    pygame.draw.rect(screen, item_bg_color, item_rect, border_top_left_radius=r)
                elif i == len(menu_items) - 1:
                    pygame.draw.rect(screen, item_bg_color, item_rect, border_bottom_left_radius=min(8, getattr(config_module.Theme, 'CORNER_CURVE_RADIUS', 60)))
                else:
                    pygame.draw.rect(screen, item_bg_color, item_rect)
            else:
                pygame.draw.rect(screen, item_bg_color, item_rect)
            # Draw border outline for item
            if len(menu_items) > 1 and i == 0:
                pygame.draw.rect(screen, config_module.COLOR_BORDER, item_rect, width=config_module.Theme.BORDER_WIDTH, border_top_left_radius=min(8, getattr(config_module.Theme, 'CORNER_CURVE_RADIUS', 60)))
            elif len(menu_items) > 1 and i == len(menu_items) - 1:
                pygame.draw.rect(screen, config_module.COLOR_BORDER, item_rect, width=config_module.Theme.BORDER_WIDTH, border_bottom_left_radius=min(8, getattr(config_module.Theme, 'CORNER_CURVE_RADIUS', 60)))
            else:
                pygame.draw.rect(screen, config_module.COLOR_BORDER, item_rect, width=config_module.Theme.BORDER_WIDTH)

            # Bevel: 1px top highlight and bottom shadow (raised panel look)
            top_highlight = _lighten(item_bg_color, 0.35)
            pygame.draw.line(screen, top_highlight, (item_rect.left, item_rect.top), (item_rect.right, item_rect.top), 1)
            bottom_shadow = _darken(item_bg_color, 0.25)
            pygame.draw.line(screen, bottom_shadow, (item_rect.left, item_rect.bottom - 1), (item_rect.right, item_rect.bottom - 1), 1)

            # LCARS-style: selected item — pulsing outer glow then bright left-edge accent (accent on top)
            if i == selected_index:
                t = time.time()
                pulse = 0.55 + 0.45 * (0.5 + 0.5 * math.sin(t * 2.2))
                glow_color = tuple(min(255, int(c * pulse)) for c in _lighten(item_bg_color, 0.4))
                glow_rect = item_rect.inflate(4, 4)
                pygame.draw.rect(screen, glow_color, glow_rect, width=2)
                accent_x = item_rect.left
                accent_w = max(2, ui_scaler.scale(3))
                accent_rect = pygame.Rect(accent_x, item_rect.top, accent_w, item_rect.height)
                pygame.draw.rect(screen, config_module.Palette.WHITE, accent_rect)

            # Draw the category name with responsive text positioning
            font = fonts['medium']
            if item.name == "SECRET GAMES": # Special handling for "SECRET GAMES"
                title_text = CLASSIFIED_TEXT
            else:
                title_text = item.name # Use item.name
            text_surface = font.render(title_text, True, config_module.Palette.BLACK) 
            # Use UIScaler for responsive text padding
            text_padding = ui_scaler.padding("medium")
            text_pos = (item_rect.left + text_padding, item_rect.centery - text_surface.get_height() // 2)
            screen.blit(text_surface, text_pos)
            
            # (Update-available indicator is drawn in header top-right, not on Settings item)

            # Store selected item info for arrow indicator
            if i == selected_index:
                selected_item_rect = item_rect
                selected_item_color = item_bg_color

    # --- Part 4: Draw Arrow Indicator Area (ONLY below header) ---
    arrow_area_rect = pygame.Rect(
        base_sidebar_width,
        sidebar_content_y_start,
        arrow_indicator_width,
        sidebar_content_height
    )
    
    # Draw arrow indicator if we have a selected item
    if selected_item_rect:
        _draw_arrow_indicator(screen, arrow_area_rect, selected_item_rect, selected_item_color, config_module, ui_scaler)

    # --- Part 5: Calculate Main Content Area ---
    total_sidebar_width = base_sidebar_width + arrow_indicator_width
    main_content_width = screen_width - total_sidebar_width
    main_content_height = screen_height - header_height
    if ui_scaler and ui_scaler.safe_area_enabled:
        safe_margins = ui_scaler.get_safe_area_margins()
        main_content_width -= safe_margins['right']
        main_content_height -= safe_margins['bottom']
    main_content_rect = pygame.Rect(
        total_sidebar_width,
        header_height,
        main_content_width,
        main_content_height
    )
    pygame.draw.rect(screen, config_module.Theme.BACKGROUND, main_content_rect)
    
    # Return layout information for the calling function to use
    return {
        'main_content_rect': main_content_rect,
        'base_sidebar_width': base_sidebar_width,
        'arrow_indicator_width': arrow_indicator_width,
        'total_sidebar_width': total_sidebar_width,
        'header_height': header_height,
        'screen_width': screen_width,
        'screen_height': screen_height
    }

def _draw_arrow_indicator(screen, arrow_area_rect, selected_item_rect, item_color, config_module, ui_scaler):
    """
    Draw a simple arrow indicator pointing left toward the selected menu item with responsive sizing.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        arrow_area_rect (pygame.Rect): Rectangle of the arrow indicator area
        selected_item_rect (pygame.Rect): Rectangle of the selected menu item
        item_color (tuple): RGB color of the selected menu item
        config_module (module): Configuration module for colors
        ui_scaler (UIScaler): UI scaling system for responsive design
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
    
    # Create arrow triangle pointing left with responsive sizing
    arrow_size = ui_scaler.scale(config_module.ARROW_INDICATOR_SIZE) // 2
    arrow_points = [
        (arrow_center_x - arrow_size // 2, arrow_center_y),  # Left point (tip)
        (arrow_center_x + arrow_size // 2, arrow_center_y - arrow_size // 2),  # Top right
        (arrow_center_x + arrow_size // 2, arrow_center_y + arrow_size // 2)   # Bottom right
    ]
    
    # Draw the arrow
    pygame.draw.polygon(screen, arrow_color, arrow_points)
    
    # Optional: Add a subtle border to the arrow
    pygame.draw.polygon(screen, config_module.Palette.BLACK, arrow_points, 1)

def _draw_exclamation_badge(screen, item_rect, config_module, fonts, ui_scaler=None):
    """Draw a red circle with exclamation mark badge. Uses ui_scaler for size/inset when provided."""
    badge_size = ui_scaler.scale(16) if ui_scaler else 16
    inset = ui_scaler.scale(8) if ui_scaler else 8
    badge_x = item_rect.right - badge_size - inset
    badge_y = item_rect.top + inset
    badge_rect = pygame.Rect(badge_x, badge_y, badge_size, badge_size)
    pygame.draw.circle(screen, config_module.Theme.ALERT, badge_rect.center, max(1, badge_size // 2))
    exclamation_surface = fonts['tiny'].render("!", True, config_module.Theme.WHITE)
    exclamation_rect = exclamation_surface.get_rect(center=badge_rect.center)
    screen.blit(exclamation_surface, exclamation_rect)


def _draw_corner_tricorder_effects(screen, corner_rect, corner_color, config_module, fonts, ui_scaler):
    """Tricorder-style corner panel (no READY/bars on small Pi screen)."""
    pass


def _draw_header_tricorder_effects(screen, header_rect, header_color, config_module, fonts, ui_scaler, app_state=None):
    """LCARS-style header: scan beam, EARTH: location on left, local/public IP alternating on right."""
    t = time.time()
    pad = ui_scaler.scale(6) if ui_scaler else 6
    right_inset = ui_scaler.scale(18) if ui_scaler else 18

    # Scan beam: bright leading edge + short fading trail (sweeps across header)
    scan_speed = 0.35
    phase = (t * scan_speed) % 1.0
    lead_x = header_rect.left + int(phase * (header_rect.width + 40)) - 20
    beam_w = max(3, ui_scaler.scale(6) if ui_scaler else 6)
    trail_len = max(2, ui_scaler.scale(14) if ui_scaler else 14)
    scan_y = header_rect.centery - 1
    scan_h = 2
    clip = screen.get_clip()
    screen.set_clip(header_rect)
    for i in range(3):
        seg_x = lead_x - trail_len - (i * (beam_w + 2))
        seg_w = beam_w
        trail_color = _darken(header_color, 0.35 + i * 0.15)
        trail_rect = pygame.Rect(seg_x, scan_y, seg_w, scan_h)
        if header_rect.colliderect(trail_rect):
            pygame.draw.rect(screen, trail_color, trail_rect)
    lead_color = _lighten(header_color, 0.65)
    lead_rect = pygame.Rect(lead_x, scan_y, beam_w, scan_h)
    if header_rect.colliderect(lead_rect):
        pygame.draw.rect(screen, lead_color, lead_rect)
    screen.set_clip(clip)

    font_tiny = fonts.get('tiny', fonts.get('small', fonts.get('default')))
    digit_color = _darken(header_color, 0.5)

    # Left: EARTH: <location> (LCARS-style); truncate if too long
    loc_text = (app_state and getattr(app_state, 'location_from_ip', None) and app_state.location_from_ip) or "--"
    left_label = f"EARTH: {loc_text}"
    left_surf = font_tiny.render(left_label, True, digit_color)
    max_left_width = int(header_rect.width * 0.55)
    if left_surf.get_width() > max_left_width and len(loc_text) > 3:
        # Shorten to fit (keep EARTH: prefix)
        for n in range(len(loc_text), 0, -1):
            trial = f"EARTH: {loc_text[:n]}…"
            s = font_tiny.render(trial, True, digit_color)
            if s.get_width() <= max_left_width:
                left_surf = s
                break
    left_rect = left_surf.get_rect(midleft=(header_rect.left + pad, header_rect.centery))
    if left_rect.right <= header_rect.right:
        screen.blit(left_surf, left_rect)

    # Right: alternate local IP / public IP every 4 seconds when both available
    local_ip = (app_state and getattr(app_state, 'network_manager', None) and app_state.network_manager.get_ip_cached()) or None
    public_ip = (app_state and getattr(app_state, 'public_ip', None)) or None
    if local_ip and public_ip:
        show_public = int(t / 4) % 2 == 1
        ip_str = public_ip if show_public else local_ip
    else:
        ip_str = local_ip
    if ip_str:
        right_surf = font_tiny.render(ip_str, True, digit_color)
    else:
        freq = int((t * 10) % 1000)
        right_surf = font_tiny.render(f"{freq:03d}", True, digit_color)
    right_rect = right_surf.get_rect(midright=(header_rect.right - right_inset, header_rect.centery))
    if right_rect.left >= header_rect.left:
        screen.blit(right_surf, right_rect)


def _draw_update_indicator_header(screen, header_rect, config_module, fonts, ui_scaler):
    """Draw update-available red dot in top-right of the header panel."""
    inset = ui_scaler.scale(6) if ui_scaler else 6
    badge_size = ui_scaler.scale(12) if ui_scaler else 12
    dot_x = header_rect.right - inset - badge_size // 2
    dot_y = header_rect.top + inset + badge_size // 2
    pygame.draw.circle(screen, config_module.Theme.ALERT, (dot_x, dot_y), max(2, badge_size // 2))
    exclamation_surface = fonts.get('tiny', fonts.get('small')).render("!", True, config_module.Theme.WHITE)
    exclamation_rect = exclamation_surface.get_rect(center=(dot_x, dot_y))
    screen.blit(exclamation_surface, exclamation_rect)