# --- ui/views/settings/bluetooth_devices_view.py ---
# Bluetooth device list: scan, connect, disconnect

import pygame
import logging
from ui.components.text.text_display import render_footer

logger = logging.getLogger(__name__)


def draw_bluetooth_devices_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """Draw the Bluetooth devices list (Scan + devices). Select to connect/disconnect."""
    if not app_state.bluetooth_manager:
        screen.fill(config_module.Theme.BACKGROUND)
        font_medium = fonts["medium"]
        err = font_medium.render("Bluetooth manager not available", True, config_module.Theme.ALERT)
        r = err.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(err, r)
        return

    screen.fill(config_module.Theme.BACKGROUND)
    bt = app_state.bluetooth_manager
    display_list = bt.get_device_display_list()
    selected_index = bt.get_device_selected_index()

    if ui_scaler:
        screen_width = ui_scaler.screen_width
        screen_height = ui_scaler.screen_height
        safe_rect = ui_scaler.get_safe_area_rect() if ui_scaler.safe_area_enabled else pygame.Rect(0, 0, screen_width, screen_height)
        title_margin = ui_scaler.margin("medium")
        content_start_y = safe_rect.top + ui_scaler.header_height() + ui_scaler.margin("large")
        item_height = ui_scaler.scale(60)
        list_margin = ui_scaler.margin("medium")
        sidebar_space = ui_scaler.scale(65)
        max_visible = 6
    else:
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        safe_rect = pygame.Rect(0, 0, screen_width, screen_height)
        title_margin = 20
        content_start_y = safe_rect.top + 50
        item_height = 60
        list_margin = 15
        sidebar_space = 65
        max_visible = 6

    title_font = fonts["large"]
    title_text = title_font.render("Bluetooth Devices", True, config_module.Theme.FOREGROUND)
    title_top = safe_rect.top + (ui_scaler.margin("small") if ui_scaler else 15)
    screen.blit(title_text, (safe_rect.left + title_margin, title_top))

    if bt.last_scan_error:
        err_surf = fonts["medium"].render(f"Error: {bt.last_scan_error}", True, config_module.Theme.ALERT)
        screen.blit(err_surf, (safe_rect.left + title_margin, content_start_y))
        content_start_y += item_height

    if not display_list:
        no_text = fonts["large"].render("No devices. Use Scan to find devices.", True, config_module.Theme.FOREGROUND)
        screen.blit(no_text, (safe_rect.left + title_margin, content_start_y))
        labels = config_module.get_control_labels()
        render_footer(screen, f"{labels.get('back', 'Back')} to Bluetooth Settings", fonts, config_module.Theme.FOREGROUND, screen_width, screen_height, ui_scaler=ui_scaler)
        return

    scroll_offset = max(0, selected_index - max_visible + 1)
    list_bg_rect = pygame.Rect(
        safe_rect.left + list_margin,
        content_start_y - 8,
        safe_rect.width - sidebar_space - list_margin * 2,
        (max_visible * item_height) + 16,
    )
    pygame.draw.rect(screen, (15, 15, 15), list_bg_rect, border_radius=config_module.Theme.CORNER_CURVE_RADIUS)

    for i in range(max_visible):
        idx = i + scroll_offset
        if idx >= len(display_list):
            break
        item = display_list[idx]
        y_pos = content_start_y + (i * item_height)
        is_scan_row = item.get("mac") is None
        if idx == selected_index:
            highlight_rect = pygame.Rect(
                safe_rect.left + list_margin + 3,
                y_pos - 3,
                safe_rect.width - sidebar_space - list_margin * 2 - 6,
                item_height - 6,
            )
            pygame.draw.rect(screen, config_module.Theme.MENU_SELECTED_BG, highlight_rect, border_radius=config_module.Theme.CORNER_CURVE_RADIUS)
            text_color = config_module.Theme.MENU_SELECTED_TEXT
        else:
            text_color = config_module.Theme.FOREGROUND

        name = (item.get("name") or "")[:28]
        if is_scan_row:
            line = name
        else:
            line = f"{name} — {'Connected' if item.get('connected') else 'Not connected'}"
        main_surf = fonts["medium"].render(line, True, text_color)
        main_y = y_pos + (ui_scaler.scale(8) if ui_scaler else 8)
        screen.blit(main_surf, (safe_rect.left + list_margin + (ui_scaler.scale(10) if ui_scaler else 10), main_y))

    if len(display_list) > max_visible:
        scroll_bg_rect = pygame.Rect(
            safe_rect.right - sidebar_space + 10,
            content_start_y - 8,
            sidebar_space - 20,
            (max_visible * item_height) + 16,
        )
        pygame.draw.rect(screen, config_module.Theme.MENU_SELECTED_BG, scroll_bg_rect, border_radius=config_module.Theme.CORNER_CURVE_RADIUS)
        scroll_center_x = safe_rect.right - sidebar_space // 2
        if scroll_offset > 0:
            up_arrow = fonts["medium"].render("^", True, config_module.Theme.FOREGROUND)
            up_y = content_start_y + (ui_scaler.scale(15) if ui_scaler else 15)
            up_rect = up_arrow.get_rect(center=(scroll_center_x, up_y))
            screen.blit(up_arrow, up_rect)
        if scroll_offset + max_visible < len(display_list):
            down_arrow = fonts["medium"].render("v", True, config_module.Theme.FOREGROUND)
            down_y = content_start_y + (max_visible * item_height) - (ui_scaler.scale(15) if ui_scaler else 15)
            down_rect = down_arrow.get_rect(center=(scroll_center_x, down_y))
            screen.blit(down_arrow, down_rect)
        scroll_info = f"{selected_index + 1}/{len(display_list)}"
        scroll_surf = fonts["medium"].render(scroll_info, True, config_module.Theme.FOREGROUND)
        scroll_center_y = content_start_y + (max_visible * item_height) // 2
        scroll_rect = scroll_surf.get_rect(center=(scroll_center_x, scroll_center_y))
        screen.blit(scroll_surf, scroll_rect)

    labels = config_module.get_control_labels()
    hint = f"Select: connect/disconnect — {labels.get('back', 'Back')}: Back"
    render_footer(screen, hint, fonts, config_module.Theme.FOREGROUND, screen_width, screen_height, ui_scaler=ui_scaler)
