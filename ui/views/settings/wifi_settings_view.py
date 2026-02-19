# --- ui/views/settings/wifi_settings_view.py ---
# Handles rendering of the WiFi settings screen

import pygame
import logging
from ui.components.menus.list_menu_base import draw_simple_list_menu
from ui.components.text.text_display import render_footer, render_text
import config as app_config  # For key names, Theme colors

logger = logging.getLogger(__name__)


def _draw_wifi_bars(screen, x, y, signal_pct, bar_w, bar_gap, max_bar_h, config_module, ui_scaler=None):
    """Draw a prominent 4-bar WiFi signal indicator (scaled for small Pi screen). Returns total width drawn."""
    scale = ui_scaler.scale if ui_scaler else lambda v: v
    # Bar dimensions (all scaled so they stay visible on 320x240)
    w = max(1, scale(bar_w))
    gap = max(1, scale(bar_gap))
    heights = [max(1, scale(h)) for h in (max_bar_h * 0.25, max_bar_h * 0.45, max_bar_h * 0.65, max_bar_h)]
    total_w = 4 * w + 3 * gap
    # Colors from theme: strong -> weak
    if signal_pct >= 70:
        fill = getattr(config_module.Theme, 'CONTENT_WIFI_ONLINE_STATUS', (0, 200, 0))
    elif signal_pct >= 40:
        fill = getattr(config_module.Theme, 'ACCENT', (255, 165, 0))
    else:
        fill = getattr(config_module.Theme, 'ALERT', (255, 100, 100))
    dim = tuple(max(0, min(255, c // 3)) for c in fill)
    for i, h in enumerate(heights):
        bx = x + i * (w + gap)
        by = y + (heights[-1] - h)
        # Show filled up to bars that represent current signal
        bars_filled = min(4, max(0, int((signal_pct / 100.0) * 4 + 0.5)))
        rect = pygame.Rect(bx, by, w, h)
        pygame.draw.rect(screen, dim, rect, border_radius=1)
        if i < bars_filled:
            pygame.draw.rect(screen, fill, rect, border_radius=1)
    return total_w

def draw_wifi_settings_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the WiFi settings screen content using the shared list menu component.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state, which provides access to WifiManager
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
        ui_scaler (UIScaler, optional): UI scaling system for responsive design
    """
    # Check if WifiManager is available
    if not app_state.wifi_manager:
        screen.fill(config_module.Theme.BACKGROUND)
        if ui_scaler:
            screen_width = ui_scaler.screen_width
            screen_height = ui_scaler.screen_height
            safe_rect = ui_scaler.get_safe_area_rect() if ui_scaler.safe_area_enabled else pygame.Rect(0, 0, screen_width, screen_height)
        else:
            screen_width = screen.get_width()
            screen_height = screen.get_height()
            safe_rect = pygame.Rect(0, 0, screen_width, screen_height)
        error_msg = "WifiManager not available in AppState"
        logger.error(error_msg)
        font_medium = fonts['medium']
        err_surf = font_medium.render(error_msg, True, config_module.Theme.ALERT)
        err_rect = err_surf.get_rect(center=(safe_rect.centerx, safe_rect.centery))
        screen.blit(err_surf, err_rect)
        labels = config_module.get_control_labels()
        render_footer(screen, f"Error - Press {labels['back']}", fonts, config_module.Theme.FOREGROUND, screen_width, screen_height, ui_scaler=ui_scaler, content_center_x=safe_rect.centerx)
        return

    # Get menu items and selected index from WifiManager
    menu_items_data = app_state.wifi_manager.get_current_wifi_display_options()
    current_selection_index = app_state.wifi_manager.get_selected_index()
    
    # Extract just the names for the list menu component
    menu_items = [item_data["name"] for item_data in menu_items_data]
    
    # Use the shared list menu component
    draw_simple_list_menu(
        screen=screen,
        title="Wi-Fi Settings",
        menu_items=menu_items,
        selected_index=current_selection_index,
        fonts=fonts,
        config_module=config_module,
        footer_hint=None,  # No footer for this view
        ui_scaler=ui_scaler
    )

def draw_wifi_networks_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw a WiFi network list with responsive design.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
        ui_scaler (UIScaler, optional): UI scaling system for responsive design
    """
    screen.fill(config_module.Theme.BACKGROUND)
    
    networks = app_state.wifi_manager.get_available_networks()
    selected_index = app_state.wifi_manager.get_network_selected_index()
    
    if ui_scaler:
        screen_width = ui_scaler.screen_width
        screen_height = ui_scaler.screen_height
        safe_rect = ui_scaler.get_safe_area_rect() if ui_scaler.safe_area_enabled else pygame.Rect(0, 0, screen_width, screen_height)
    else:
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        safe_rect = pygame.Rect(0, 0, screen_width, screen_height)
    # Layout tuned for small Pi screen (320x240): compact rows, fit within safe area + footer
    list_margin = ui_scaler.margin("medium") if ui_scaler else 15
    title_margin = list_margin
    footer_reserved = (ui_scaler.scale(32) if ui_scaler else 32)  # Space for footer so it doesn't overlap list
    if ui_scaler:
        header_block = ui_scaler.header_height() + ui_scaler.margin("medium")  # Tighter than "large" for Pi
        content_start_y = safe_rect.top + header_block
        available_list_height = safe_rect.height - header_block - footer_reserved
        # Compact row height so 4 rows fit on 240p (e.g. 4 * 32 = 128px list + header + footer)
        item_height = ui_scaler.scale(32)
        max_visible_cap = getattr(config_module, 'LIST_MENU_MAX_VISIBLE_ITEMS', 4)
        max_visible = max(1, min(max_visible_cap, available_list_height // max(item_height, 1)))
        sidebar_space = ui_scaler.scale(44)   # Narrower on Pi so more room for SSID
        signal_column_width = ui_scaler.scale(52)  # 4-bar + "%" compact
        inset = ui_scaler.scale(2)
        if ui_scaler.debug_mode:
            logger.info(f"🎨 WiFiNetworks: screen={screen_width}x{screen_height}, item_height={item_height}px, max_visible={max_visible}, available_h={available_list_height}px")
    else:
        content_start_y = safe_rect.top + 50
        item_height = 32
        max_visible = 4
        sidebar_space = 44
        signal_column_width = 52
        inset = 2
    
    title_font = fonts['large']
    title_text = title_font.render("WiFi Networks", True, config_module.Theme.FOREGROUND)
    title_top = safe_rect.top + (ui_scaler.margin("small") if ui_scaler else 8)
    screen.blit(title_text, (safe_rect.left + title_margin, title_top))
    
    # Show error states only - scanning is handled by the reusable loading screen
    if app_state.wifi_manager.last_scan_error:
        error_text = fonts['large'].render(f"Error: {app_state.wifi_manager.last_scan_error}", True, config_module.Theme.ALERT)
        screen.blit(error_text, (safe_rect.left + title_margin, content_start_y))
        labels = config_module.get_control_labels()
        render_footer(screen, f"{labels.get('back', 'Back')} to Wi‑Fi Settings", fonts, config_module.Theme.FOREGROUND, screen_width, screen_height, ui_scaler=ui_scaler)
        return
    
    if not networks:
        no_networks_text = fonts['large'].render("No networks found", True, config_module.Theme.FOREGROUND)
        screen.blit(no_networks_text, (safe_rect.left + title_margin, content_start_y))
        labels = config_module.get_control_labels()
        render_footer(screen, f"{labels.get('back', 'Back')} to Wi‑Fi Settings", fonts, config_module.Theme.FOREGROUND, screen_width, screen_height, ui_scaler=ui_scaler)
        return
    
    # Calculate scroll offset
    scroll_offset = max(0, selected_index - max_visible + 1)
    
    list_content_width = safe_rect.width - list_margin * 2 - signal_column_width - sidebar_space
    list_pad_v = ui_scaler.scale(6) if ui_scaler else 6
    list_bg_rect = pygame.Rect(safe_rect.left + list_margin, content_start_y - list_pad_v, list_content_width + signal_column_width, (max_visible * item_height) + list_pad_v * 2)
    pygame.draw.rect(screen, (15, 15, 15), list_bg_rect, border_radius=config_module.Theme.CORNER_CURVE_RADIUS)
    
    for i in range(max_visible):
        net_index = i + scroll_offset
        if net_index >= len(networks):
            break
        
        network = networks[net_index]
        y_pos = content_start_y + (i * item_height)
        pad = ui_scaler.scale(2) if ui_scaler else 2
        row_h = item_height - pad * 2
        
        # Highlight selected item (all scaled)
        if net_index == selected_index:
            highlight_rect = pygame.Rect(safe_rect.left + list_margin + pad, y_pos - pad, list_content_width + signal_column_width - pad * 2, row_h)
            pygame.draw.rect(screen, config_module.Theme.MENU_SELECTED_BG, highlight_rect, border_radius=config_module.Theme.CORNER_CURVE_RADIUS)
            text_color = config_module.Theme.MENU_SELECTED_TEXT
        else:
            text_color = config_module.Theme.FOREGROUND
        
        # On small screens use shorter SSID truncation so it fits
        max_ssid_len = 12 if (ui_scaler and ui_scaler.screen_width <= 320) else 20
        ssid = network['ssid'][:max_ssid_len]
        signal = network['signal_strength']
        saved = "SAVED" if network['is_saved'] else ""
        secure = "SECURE" if network['security'] != 'Open' else "OPEN"
        
        text_left = safe_rect.left + list_margin + (ui_scaler.scale(6) if ui_scaler else 6)
        main_y = y_pos + (ui_scaler.scale(4) if ui_scaler else 4)
        main_surface = fonts['medium'].render(ssid, True, text_color)
        screen.blit(main_surface, (text_left, main_y))
        
        # Second line only when row is tall enough (avoid overlap on Pi compact rows)
        row_tall_enough = item_height >= (ui_scaler.scale(44) if ui_scaler else 44)
        if row_tall_enough and (saved or secure != "OPEN"):
            status_line = f"{saved} {secure}".strip()
            status_surface = fonts['small'].render(status_line, True, text_color)
            status_y = y_pos + (ui_scaler.scale(28) if ui_scaler else 28)
            screen.blit(status_surface, (text_left, status_y))
        
        # Prominent 4-bar WiFi signal indicator; smaller bar height on compact rows
        signal_anchor_x = safe_rect.right - sidebar_space - signal_column_width - (ui_scaler.scale(4) if ui_scaler else 4)
        max_bar_h = 14 if (ui_scaler and ui_scaler.screen_height <= 240) else 22
        bar_w, bar_gap = 4, 1
        bars_center_y = y_pos + item_height // 2
        bars_x = signal_anchor_x
        bars_y = bars_center_y - (ui_scaler.scale(max_bar_h) if ui_scaler else max_bar_h) // 2
        _draw_wifi_bars(screen, bars_x, bars_y, signal, bar_w, bar_gap, max_bar_h, config_module, ui_scaler)
        pct_text = f"{signal}%"
        pct_surf = fonts['small'].render(pct_text, True, text_color)
        pct_x = signal_anchor_x + (ui_scaler.scale(22) if ui_scaler else 22)
        pct_rect = pct_surf.get_rect(midleft=(pct_x, bars_center_y))
        screen.blit(pct_surf, pct_rect)
    
    if len(networks) > max_visible:
        scroll_inset = ui_scaler.scale(6) if ui_scaler else 6
        scroll_bg_rect = pygame.Rect(safe_rect.right - sidebar_space + scroll_inset, content_start_y - list_pad_v, sidebar_space - scroll_inset * 2, (max_visible * item_height) + list_pad_v * 2)
        pygame.draw.rect(screen, config_module.Theme.MENU_SELECTED_BG, scroll_bg_rect, border_radius=config_module.Theme.CORNER_CURVE_RADIUS)
        
        scroll_center_x = safe_rect.right - sidebar_space // 2
        arrow_inset = ui_scaler.scale(10) if ui_scaler else 10
        if scroll_offset > 0:
            up_arrow = fonts['medium'].render("^", True, config_module.Theme.FOREGROUND)
            up_y = content_start_y + arrow_inset
            up_rect = up_arrow.get_rect(center=(scroll_center_x, up_y))
            screen.blit(up_arrow, up_rect)
        if scroll_offset + max_visible < len(networks):
            down_arrow = fonts['medium'].render("v", True, config_module.Theme.FOREGROUND)
            down_y = content_start_y + (max_visible * item_height) - arrow_inset
            down_rect = down_arrow.get_rect(center=(scroll_center_x, down_y))
            screen.blit(down_arrow, down_rect)
        scroll_info = f"{selected_index + 1}/{len(networks)}"
        scroll_surface = fonts['small'].render(scroll_info, True, config_module.Theme.FOREGROUND)
        scroll_center_y = content_start_y + (max_visible * item_height) // 2
        scroll_rect = scroll_surface.get_rect(center=(scroll_center_x, scroll_center_y))
        screen.blit(scroll_surface, scroll_rect)
    
    # Footer hint (consistent with other settings list views)
    labels = config_module.get_control_labels()
    render_footer(screen, f"{labels.get('select', 'Select')} to connect · {labels.get('back', 'Back')} to Wi‑Fi Settings", fonts, config_module.Theme.FOREGROUND, screen_width, screen_height, ui_scaler=ui_scaler)


def draw_wifi_forget_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the "Forget a network" list (saved networks only).
    """
    screen.fill(config_module.Theme.BACKGROUND)
    wm = app_state.wifi_manager
    if not wm:
        return
    saved = wm.get_saved_networks()
    selected_index = wm.forget_list_selected_index
    if ui_scaler:
        screen_width = ui_scaler.screen_width
        screen_height = ui_scaler.screen_height
        safe_rect = ui_scaler.get_safe_area_rect() if ui_scaler.safe_area_enabled else pygame.Rect(0, 0, screen_width, screen_height)
    else:
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        safe_rect = pygame.Rect(0, 0, screen_width, screen_height)
    list_margin = ui_scaler.margin("medium") if ui_scaler else 15
    title_margin = list_margin
    footer_reserved = ui_scaler.scale(32) if ui_scaler else 32
    if ui_scaler:
        header_block = ui_scaler.header_height() + ui_scaler.margin("medium")
        content_start_y = safe_rect.top + header_block
        item_height = ui_scaler.scale(32)
    else:
        content_start_y = safe_rect.top + 50
        item_height = 32
    title_font = fonts['large']
    title_text = title_font.render("Forget a network", True, config_module.Theme.FOREGROUND)
    title_top = safe_rect.top + (ui_scaler.margin("small") if ui_scaler else 8)
    screen.blit(title_text, (safe_rect.left + title_margin, title_top))
    if not saved:
        no_saved = fonts['medium'].render("No saved networks", True, config_module.Theme.FOREGROUND)
        screen.blit(no_saved, (safe_rect.left + title_margin, content_start_y))
    else:
        max_visible = 4
        scroll_offset = max(0, selected_index - max_visible + 1)
        for i in range(max_visible):
            idx = i + scroll_offset
            if idx >= len(saved):
                break
            ssid = saved[idx]
            y_pos = content_start_y + (i * item_height)
            pad = ui_scaler.scale(2) if ui_scaler else 2
            row_h = item_height - pad * 2
            is_selected = idx == selected_index
            if is_selected:
                highlight_rect = pygame.Rect(safe_rect.left + list_margin + pad, y_pos - pad, safe_rect.width - list_margin * 2 - pad * 2, row_h)
                pygame.draw.rect(screen, config_module.Theme.MENU_SELECTED_BG, highlight_rect, border_radius=config_module.Theme.CORNER_CURVE_RADIUS)
                text_color = config_module.Theme.MENU_SELECTED_TEXT
            else:
                text_color = config_module.Theme.FOREGROUND
            display_ssid = ssid[:20] + "..." if len(ssid) > 20 else ssid
            surf = fonts['medium'].render(display_ssid, True, text_color)
            screen.blit(surf, (safe_rect.left + list_margin + (ui_scaler.scale(6) if ui_scaler else 6), y_pos + 4))
    labels = config_module.get_control_labels()
    render_footer(screen, f"{labels.get('select', 'Select')} to forget · {labels.get('back', 'Back')} to Wi‑Fi", fonts, config_module.Theme.FOREGROUND, screen_width, screen_height, ui_scaler=ui_scaler) 