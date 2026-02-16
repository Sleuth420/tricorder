# --- ui/views/settings/volume_settings_view.py ---
# Device settings: volume control (app audio; can be tied to media player later)

import pygame
import logging

logger = logging.getLogger(__name__)

VOLUME_STEP = 0.05  # 5% per next/prev

def _get_display_volume(app_state):
    """Get current volume 0.0–1.0 from AudioManager, or 0 if unavailable."""
    if not getattr(app_state, "audio_manager", None):
        return 0.0
    return app_state.audio_manager.get_volume()

def draw_volume_settings_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the volume control screen: title, current volume %, and bar.
    Next/Prev adjust volume; Back returns to Device Settings.
    """
    screen.fill(config_module.Theme.BACKGROUND)

    if ui_scaler:
        screen_width = ui_scaler.screen_width
        screen_height = ui_scaler.screen_height
        safe_rect = ui_scaler.get_safe_area_rect() if ui_scaler.safe_area_enabled else pygame.Rect(0, 0, screen_width, screen_height)
        scale = ui_scaler.scale
        header_top = safe_rect.top + (ui_scaler.header_top_margin() if hasattr(ui_scaler, "header_top_margin") else 0)
        header_h = (ui_scaler.header_height() + ui_scaler.scale(20)) if hasattr(ui_scaler, "header_height") else 50
    else:
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        safe_rect = pygame.Rect(0, 0, screen_width, screen_height)
        scale = lambda x: x
        header_top = safe_rect.top + screen_height // 20
        header_h = 50

    # Title
    font_large = fonts["large"]
    title_text = "Volume"
    title_surf = font_large.render(title_text, True, config_module.Theme.FOREGROUND)
    title_rect = title_surf.get_rect(centerx=safe_rect.centerx, top=header_top)
    screen.blit(title_surf, title_rect)

    # Current volume and bar
    vol = _get_display_volume(app_state)
    vol_pct = int(round(vol * 100))
    font_medium = fonts["medium"]
    font_small = fonts["small"]

    content_y = title_rect.bottom + scale(40)
    pct_text = f"{vol_pct}%"
    pct_surf = font_medium.render(pct_text, True, config_module.Theme.ACCENT)
    pct_rect = pct_surf.get_rect(centerx=safe_rect.centerx, top=content_y)
    screen.blit(pct_surf, pct_rect)

    # Bar
    bar_width = min(safe_rect.width - scale(80), scale(280))
    bar_height = scale(24)
    bar_x = safe_rect.centerx - bar_width // 2
    bar_y = pct_rect.bottom + scale(20)
    bar_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
    pygame.draw.rect(screen, config_module.Theme.FOREGROUND, bar_rect, 1)
    fill_width = int(bar_width * vol)
    if fill_width > 0:
        fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
        pygame.draw.rect(screen, config_module.Theme.ACCENT, fill_rect)

    # Footer hint
    hint_y = safe_rect.bottom - scale(36)
    hint_text = "Next / Prev: adjust   Back: Device Settings"
    hint_surf = font_small.render(hint_text, True, config_module.Theme.FOREGROUND)
    hint_rect = hint_surf.get_rect(centerx=safe_rect.centerx, bottom=hint_y)
    screen.blit(hint_surf, hint_rect)
