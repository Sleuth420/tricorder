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
    """Draw file info panel (title, path, duration, size) when long-press D is active."""
    w, h = screen.get_width(), screen.get_height()
    margin = ui_scaler.margin("large") if ui_scaler else 20
    font_small = fonts["small"]
    font_tiny = fonts.get("tiny", font_small)
    # Semi-transparent panel
    panel = pygame.Rect(margin, h // 2 - 50, w - 2 * margin, 100)
    s = pygame.Surface((panel.w, panel.h))
    s.set_alpha(220)
    s.fill(config_module.Theme.BACKGROUND)
    screen.blit(s, panel.topleft)
    pygame.draw.rect(screen, config_module.Theme.ACCENT, panel, 1)
    y = panel.y + 6
    name = mgr.get_current_track_name() or "—"
    screen.blit(font_small.render("Title: " + (name[:40] + "..." if len(name) > 40 else name), True, config_module.Theme.FOREGROUND), (panel.x + 6, y))
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
    y += font_tiny.get_height() + 4
    screen.blit(font_tiny.render("Long-press D = file info", True, config_module.Theme.FOREGROUND), (panel.x + 6, y))


def draw_media_player_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the media player using the shared submenu list (same as Schematics / Settings sub-menus).
    Track list, selection, and footer; VLC handles playback in the same window when playing.
    """
    mgr = getattr(app_state, "media_player_manager", None)
    if not mgr:
        screen.fill(config_module.Theme.BACKGROUND)
        err = fonts["medium"].render("Media player not available", True, config_module.Theme.ALERT)
        r = err.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
        screen.blit(err, r)
        return

    # Process end-reached from VLC (main-thread tick)
    mgr.tick()

    # Keep VLC attached when playing or paused (VLC shows video/paused frame). Detach only when stopped to show the track list.
    mgr.update_window_attachment(mgr.is_playing() or mgr.is_paused())

    if not mgr.is_playing() and not mgr.is_paused():
        # Build menu items like other sub-menus: list of track names (or placeholder)
        track_list = mgr.get_track_list()
        if track_list:
            menu_items = [name for name, _ in track_list]
        else:
            media_folder = getattr(config_module, "MEDIA_FOLDER", "assets/media")
            menu_items = [f"No media in {media_folder}"]

        selected_index = mgr.get_current_index()
        if selected_index >= len(menu_items):
            selected_index = max(0, len(menu_items) - 1)

        key_prev = pygame.key.name(config_module.KEY_PREV).upper()
        key_next = pygame.key.name(config_module.KEY_NEXT).upper()
        key_select = pygame.key.name(config_module.KEY_SELECT).upper()
        footer_hint = f"< {key_prev}=Prev | {key_next}=Next | {key_select}=Play/Pause | Long {key_next}=Info | Back=Exit >"
        if not mgr.vlc_available:
            footer_hint += "  (Install python-vlc for playback)"

        draw_scrollable_list_menu(
            screen=screen,
            title="Media Player",
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
