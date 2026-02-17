# --- ui/views/schematics/media_player_view.py ---
# Media player UI: track list via shared submenu template. Long-press D = file info.

import pygame
import logging
from ui.components.menus.list_menu_base import draw_scrollable_list_menu

logger = logging.getLogger(__name__)


def _format_time(sec):
    """Format seconds as M:SS."""
    if sec is None or sec < 0:
        return "0:00"
    m = int(sec // 60)
    s = int(sec % 60)
    return f"{m}:{s:02d}"


def _format_size(bytes_size):
    """Format bytes as KB or MB."""
    if bytes_size is None or bytes_size < 0:
        return "—"
    if bytes_size < 1024:
        return f"{bytes_size} B"
    if bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f} KB"
    return f"{bytes_size / (1024 * 1024):.2f} MB"


def _draw_file_info_overlay(screen, mgr, fonts, config_module, ui_scaler):
    """Draw file info panel (name, path, duration, size) when long-press D is active. Uses ui_scaler and safe area."""
    if ui_scaler:
        w, h = ui_scaler.screen_width, ui_scaler.screen_height
        margin = ui_scaler.margin("large")
        panel_h = ui_scaler.scale(100)
        panel_y_offset = ui_scaler.scale(50)
        safe_rect = ui_scaler.get_safe_area_rect() if ui_scaler.safe_area_enabled else pygame.Rect(0, 0, w, h)
    else:
        w, h = screen.get_width(), screen.get_height()
        margin = 20
        panel_y_offset = 50
        panel_h = 100
        safe_rect = pygame.Rect(0, 0, w, h)
    font_small = fonts["small"]
    font_tiny = fonts.get("tiny", font_small)
    panel = pygame.Rect(safe_rect.left + margin, safe_rect.centery - panel_y_offset, safe_rect.width - 2 * margin, panel_h)
    s = pygame.Surface((panel.w, panel.h))
    s.set_alpha(220)
    s.fill(config_module.Theme.BACKGROUND)
    screen.blit(s, panel.topleft)
    pygame.draw.rect(screen, config_module.Theme.ACCENT, panel, 1)
    y = panel.y + 6
    name = mgr.get_current_track_name() or "—"
    screen.blit(font_small.render("File: " + (name[:40] + "..." if len(name) > 40 else name), True, config_module.Theme.FOREGROUND), (panel.x + 6, y))
    y += font_small.get_height() + 2
    path = mgr.get_current_track_path() or ""
    path_short = path[:50] + "..." if len(path) > 50 else path
    screen.blit(font_tiny.render("Path: " + path_short, True, config_module.Theme.FOREGROUND), (panel.x + 6, y))
    y += font_tiny.get_height() + 2
    length_sec = mgr.get_length_sec()
    length_str = _format_time(length_sec) if length_sec > 0 else "—"
    size_b = mgr.get_current_file_size()
    size_str = _format_size(size_b)
    screen.blit(font_tiny.render(f"Length: {length_str}  |  Size: {size_str}", True, config_module.Theme.ACCENT), (panel.x + 6, y))


def draw_media_player_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the media player using the shared submenu list (same as Schematics / Settings sub-menus).
    Track list, selection, and footer; VLC handles playback in the same window when playing.
    """
    mgr = getattr(app_state, "media_player_manager", None)
    if not mgr:
        screen.fill(config_module.Theme.BACKGROUND)
        err = fonts["medium"].render("Media player not available", True, config_module.Theme.ALERT)
        if ui_scaler and ui_scaler.safe_area_enabled:
            safe_rect = ui_scaler.get_safe_area_rect()
            r = err.get_rect(center=(safe_rect.centerx, safe_rect.centery))
        else:
            center_x = ui_scaler.screen_width // 2 if ui_scaler else screen.get_width() // 2
            center_y = ui_scaler.screen_height // 2 if ui_scaler else screen.get_height() // 2
            r = err.get_rect(center=(center_x, center_y))
        screen.blit(err, r)
        return

    # Process end-reached from VLC (main-thread tick)
    mgr.tick()

    # Keep VLC attached when playing or paused (VLC shows video/paused frame). Detach only when stopped to show the track list.
    mgr.update_window_attachment(mgr.is_playing() or mgr.is_paused())

    if not mgr.is_playing() and not mgr.is_paused():
        # Season structure: show season list first, then episode list (episode title = MP4 comment, order = filename)
        if mgr.is_browsing_seasons():
            season_folders = mgr.get_season_folders()
            menu_items = [name for name, _ in season_folders] if season_folders else ["No seasons found"]
            selected_index = mgr.get_current_index() % max(1, len(menu_items))
            title = "Media Player"
            labels = config_module.get_control_labels()
            footer_hint = f"< {labels['prev']}=Up | {labels['next']}=Down | {labels['select']}=Open | {labels['back']}=Exit >"
        else:
            track_list = mgr.get_track_list()
            if track_list:
                menu_items = [name for name, _ in track_list]  # Episode title from MP4 comment
            else:
                media_folder = getattr(config_module, "MEDIA_FOLDER", "assets/media")
                menu_items = [f"No episodes in {media_folder}"]

            selected_index = mgr.get_current_index()
            if selected_index >= len(menu_items):
                selected_index = max(0, len(menu_items) - 1)

            labels = config_module.get_control_labels()
            footer_hint = f"< {labels['prev']}=Prev | {labels['next']}=Next | {labels['select']}=Play/Pause | Long {labels['next']}=Vol+ | Double {labels['next']}=Vol- | Long {labels['select']}=Mute | {labels['back']}=Back >"
            title = "Media Player"
            if not mgr.vlc_available:
                footer_hint += "  (Install python-vlc for playback)"

        draw_scrollable_list_menu(
            screen=screen,
            title=title,
            menu_items=menu_items,
            selected_index=selected_index,
            fonts=fonts,
            config_module=config_module,
            footer_hint=footer_hint,
            item_style="simple",
            ui_scaler=ui_scaler
        )

    # File info overlay when long-press D (or equivalent) was used
    if mgr.is_showing_file_info():
        _draw_file_info_overlay(screen, mgr, fonts, config_module, ui_scaler)
