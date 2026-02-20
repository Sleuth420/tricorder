# --- ui/views/schematics/crew_detail_view.py ---
# Single crew member view: image centered, name below. Select/Back returns to crew list.

import os
import pygame
import logging

logger = logging.getLogger(__name__)


def draw_crew_detail_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the selected crew member: image (scaled to fit) and name. Back/Select returns to crew list.
    """
    screen.fill(config_module.Theme.BACKGROUND)

    data = getattr(app_state, "selected_crew_data", None) or {}
    image_path = data.get("image_path")
    name = data.get("name", "Unknown")

    if ui_scaler:
        screen_width = ui_scaler.screen_width
        screen_height = ui_scaler.screen_height
        safe_rect = ui_scaler.get_safe_area_rect() if ui_scaler.safe_area_enabled else pygame.Rect(0, 0, screen_width, screen_height)
        scale = ui_scaler.scale
    else:
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        safe_rect = pygame.Rect(0, 0, screen_width, screen_height)
        scale = lambda x: int(x)

    # Load and draw image if path exists
    if image_path and os.path.isfile(image_path):
        try:
            img = pygame.image.load(image_path).convert_alpha()
            iw, ih = img.get_size()
            max_w = int(safe_rect.width * 0.85)
            max_h = int(safe_rect.height * 0.6)
            if iw > max_w or ih > max_h:
                ratio = min(max_w / iw, max_h / ih)
                new_w, new_h = int(iw * ratio), int(ih * ratio)
                img = pygame.transform.smoothscale(img, (new_w, new_h))
            else:
                new_w, new_h = iw, ih
            img_rect = img.get_rect(centerx=safe_rect.centerx, top=safe_rect.top + scale(24))
            screen.blit(img, img_rect)
            name_y = img_rect.bottom + scale(16)
        except Exception as e:
            logger.warning("Could not load crew image %s: %s", image_path, e)
            name_y = safe_rect.centery - scale(20)
    else:
        name_y = safe_rect.centery - scale(20)

    # Name below image (or centered if no image)
    font_large = fonts["large"]
    name_surf = font_large.render(name, True, config_module.Theme.ACCENT)
    name_rect = name_surf.get_rect(centerx=safe_rect.centerx, y=name_y)
    screen.blit(name_surf, name_rect)

    # Footer hint (Back is universal; Select/Prev/Next also return to list)
    labels = config_module.get_control_labels()
    footer_hint = f"< {labels['back']}=Back | {labels['select']}=Back >"
    font_small = fonts["small"]
    footer_surf = font_small.render(footer_hint, True, config_module.Theme.FOREGROUND)
    footer_rect = footer_surf.get_rect(centerx=safe_rect.centerx, bottom=safe_rect.bottom - scale(12))
    screen.blit(footer_surf, footer_rect)
