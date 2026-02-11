# --- ui/views/schematics/media_player_view.py ---
# Media player UI: track list, play/pause, prev/next. Long-press D = file info. Tricorder overlay.

import pygame
import logging

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


def _draw_tricorder_overlay(screen, config_module, ui_scaler):
    """Draw a tricorder-style frame around the content (visible border + corner brackets)."""
    w, h = screen.get_width(), screen.get_height()
    margin = ui_scaler.margin("small") if ui_scaler else 8
    if w < 2 * margin or h < 2 * margin:
        return
    radius = getattr(config_module.Theme, "CORNER_CURVE_RADIUS", 15)
    accent = config_module.Theme.ACCENT
    rect = pygame.Rect(margin, margin, w - 2 * margin, h - 2 * margin)
    # Outer frame (accent color so it's visible)
    try:
        pygame.draw.rect(screen, accent, rect, 2, border_radius=radius)
    except TypeError:
        pygame.draw.rect(screen, accent, rect, 2)
    # Corner brackets (tricorder-style)
    bracket_len = min(25, rect.width // 8, rect.height // 8)
    if bracket_len < 4:
        bracket_len = 4
    for (cx, cy, dx, dy) in [
        (rect.left, rect.top, 1, 1),
        (rect.right, rect.top, -1, 1),
        (rect.right, rect.bottom, -1, -1),
        (rect.left, rect.bottom, 1, -1),
    ]:
        pygame.draw.line(screen, accent, (cx, cy), (cx + dx * bracket_len, cy), 2)
        pygame.draw.line(screen, accent, (cx, cy), (cx, cy + dy * bracket_len), 2)


def _draw_file_info_overlay(screen, mgr, fonts, config_module, ui_scaler):
    """Draw file info panel (name, path, duration, size) when long-press D is active."""
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
    y += font_tiny.get_height() + 4
    screen.blit(font_tiny.render("Long-press D = file info", True, config_module.Theme.FOREGROUND), (panel.x + 6, y))


def draw_media_player_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the media player: title, current track, play state, position/length, track list.
    Playback is handled by VLC in a separate window; this view only shows status and controls.
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

    # When we need to show Pygame UI (paused or file info overlay), detach VLC from the window
    # so our draw isn't covered. When playing and no overlay, attach so VLC draws video.
    if mgr.is_paused() or mgr.is_showing_file_info() or not mgr.is_playing():
        mgr.detach_from_window()
    else:
        mgr.attach_to_window()

    screen.fill(config_module.Theme.BACKGROUND)
    screen_width = screen.get_width()
    screen_height = screen.get_height()

    if ui_scaler:
        margin_l = ui_scaler.margin("large")
        margin_s = ui_scaler.margin("small")
    else:
        margin_l = 20
        margin_s = 10

    font_large = fonts["large"]
    font_medium = fonts["medium"]
    font_small = fonts["small"]

    # Header
    title = "Media Player"
    title_surf = font_large.render(title, True, config_module.Theme.ACCENT)
    title_rect = title_surf.get_rect(centerx=screen_width // 2, y=margin_l)
    screen.blit(title_surf, title_rect)

    y = title_rect.bottom + margin_s

    # VLC unavailable message
    if not mgr.vlc_available:
        msg = "VLC not available. Install python-vlc and VLC app."
        msg_surf = font_small.render(msg, True, config_module.Theme.ALERT)
        screen.blit(msg_surf, msg_surf.get_rect(centerx=screen_width // 2, y=y))
        y += msg_surf.get_height() + margin_s
        hint = "pip install python-vlc  (and install VLC)"
        hint_surf = font_small.render(hint, True, config_module.Theme.FOREGROUND)
        screen.blit(hint_surf, hint_surf.get_rect(centerx=screen_width // 2, y=y))
        y += hint_surf.get_height() + margin_l

    # Current track and state
    track_name = mgr.get_current_track_name() or "No track"
    short_name = track_name[:36] + ("..." if len(track_name) > 36 else "")
    state_text = "Playing" if mgr.is_playing() else ("Paused" if mgr.is_paused() else "Stopped")
    state_color = config_module.Theme.ACCENT if mgr.is_playing() else config_module.Theme.FOREGROUND
    track_surf = font_medium.render(short_name, True, config_module.Theme.FOREGROUND)
    track_rect = track_surf.get_rect(centerx=screen_width // 2, y=y)
    screen.blit(track_surf, track_rect)
    y = track_rect.bottom + 4
    state_surf = font_small.render(state_text, True, state_color)
    state_rect = state_surf.get_rect(centerx=screen_width // 2, y=y)
    screen.blit(state_surf, state_rect)
    y = state_rect.bottom + margin_s

    # Position / length (when we have a player)
    pos_sec = mgr.get_position_sec()
    len_sec = mgr.get_length_sec()
    time_str = f"{_format_time(pos_sec)} / {_format_time(len_sec) if len_sec > 0 else '--:--'}"
    time_surf = font_small.render(time_str, True, config_module.Theme.FOREGROUND)
    time_rect = time_surf.get_rect(centerx=screen_width // 2, y=y)
    screen.blit(time_surf, time_rect)
    y = time_rect.bottom + margin_s

    # Hint: playback in this window (embedded like 3D schematics)
    if mgr.vlc_available and mgr.track_list:
        vlc_hint = "Playback in this window"
        vlc_surf = font_small.render(vlc_hint, True, config_module.Theme.FOREGROUND)
        screen.blit(vlc_surf, vlc_surf.get_rect(centerx=screen_width // 2, y=y))
        y += vlc_surf.get_height() + margin_l

    # Track list (names around current)
    track_list = mgr.get_track_list()
    current_idx = mgr.get_current_index()
    if track_list:
        list_y = y
        max_visible = 4
        start = max(0, current_idx - 1)
        end = min(len(track_list), start + max_visible)
        if end - start < max_visible:
            start = max(0, end - max_visible)
        for i in range(start, end):
            name, _ = track_list[i]
            short = (name[:26] + "..") if len(name) > 28 else name
            is_current = i == current_idx
            color = config_module.Theme.MENU_SELECTED_TEXT if is_current else config_module.Theme.FOREGROUND
            surf = font_small.render(short, True, color)
            screen.blit(surf, (margin_l, list_y))
            list_y += font_small.get_height() + 4
    else:
        no_tracks = font_small.render("No media in " + getattr(config_module, "MEDIA_FOLDER", "assets/media"), True, config_module.Theme.FOREGROUND)
        screen.blit(no_tracks, no_tracks.get_rect(centerx=screen_width // 2, y=y))

    # Footer: controls only visible when paused (or stopped)
    if mgr.is_paused() or not mgr.is_playing():
        key_prev = pygame.key.name(config_module.KEY_PREV).upper()
        key_next = pygame.key.name(config_module.KEY_NEXT).upper()
        key_select = pygame.key.name(config_module.KEY_SELECT).upper()
        footer = f"< {key_prev}=Prev | {key_next}=Next | {key_select}=Play/Pause | Long {key_next}=Info | Back=Exit >"
        footer_surf = font_small.render(footer, True, config_module.Theme.FOREGROUND)
        footer_rect = footer_surf.get_rect(centerx=screen_width // 2, bottom=screen_height - margin_s)
        screen.blit(footer_surf, footer_rect)

    # Tricorder-style overlay (frame + corner brackets)
    _draw_tricorder_overlay(screen, config_module, ui_scaler)

    # File info overlay when long-press D (or equivalent) was used
    if mgr.is_showing_file_info():
        _draw_file_info_overlay(screen, mgr, fonts, config_module, ui_scaler)
