# --- ui/views/schematics/star_trek_wiki_view.py ---
# Star Trek wiki: category list -> item list -> scrollable detail view.
# Uses: draw_scrollable_list_menu (list_menu_base), config.get_control_labels(), UIScaler (safe_rect, margin, scale).
# Detail view has no footer so scroll numbers don't overlap; navigation is self-explanatory.

import pygame
import logging
from ui.components.menus.list_menu_base import draw_scrollable_list_menu
from models.st_wiki_manager import VIEW_MODE_CATEGORY, VIEW_MODE_LIST, VIEW_MODE_DETAIL

logger = logging.getLogger(__name__)


def draw_star_trek_wiki_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the Star Trek wiki: category picker, then item list, then scrollable detail.
    """
    mgr = getattr(app_state, "st_wiki_manager", None)
    if not mgr:
        _draw_error(screen, fonts, config_module, ui_scaler, "Star Trek wiki not available")
        return

    if not mgr.has_data():
        _draw_no_data(screen, fonts, config_module, ui_scaler)
        return

    mode = mgr.get_view_mode()
    if mode == VIEW_MODE_CATEGORY:
        _draw_category_list(screen, mgr, fonts, config_module, ui_scaler)
    elif mode == VIEW_MODE_LIST:
        _draw_item_list(screen, mgr, fonts, config_module, ui_scaler)
    else:
        _draw_detail_view(screen, mgr, fonts, config_module, ui_scaler)


def _draw_error(screen, fonts, config_module, ui_scaler, msg):
    """Error state: centered message, same safe-area pattern as other views."""
    screen.fill(config_module.Theme.BACKGROUND)
    if ui_scaler:
        safe_rect = ui_scaler.get_safe_area_rect() if ui_scaler.safe_area_enabled else pygame.Rect(0, 0, ui_scaler.screen_width, ui_scaler.screen_height)
    else:
        safe_rect = pygame.Rect(0, 0, screen.get_width(), screen.get_height())
    surf = fonts["medium"].render(msg, True, config_module.Theme.ALERT)
    r = surf.get_rect(center=(safe_rect.centerx, safe_rect.centery))
    screen.blit(surf, r)


def _draw_no_data(screen, fonts, config_module, ui_scaler):
    """No-data state: message + back hint, uses config control labels and safe area."""
    screen.fill(config_module.Theme.BACKGROUND)
    if ui_scaler:
        safe_rect = ui_scaler.get_safe_area_rect() if ui_scaler.safe_area_enabled else pygame.Rect(0, 0, ui_scaler.screen_width, ui_scaler.screen_height)
        margin_sm = ui_scaler.margin("small")
    else:
        safe_rect = pygame.Rect(0, 0, screen.get_width(), screen.get_height())
        margin_sm = 8
    msg = "No Star Trek data. Use Settings > Star Trek Data to fetch."
    surf = fonts["medium"].render(msg, True, config_module.Theme.FOREGROUND)
    r = surf.get_rect(center=(safe_rect.centerx, safe_rect.centery))
    screen.blit(surf, r)
    labels = config_module.get_control_labels()
    font_tiny = fonts.get("tiny", fonts["small"])
    hint = font_tiny.render(f"{labels['back']}=Back", True, config_module.Theme.ACCENT)
    screen.blit(hint, (r.centerx - hint.get_width() // 2, r.bottom + margin_sm))


def _draw_category_list(screen, mgr, fonts, config_module, ui_scaler):
    """Category picker: Characters, Spacecraft, Species, Technology, Locations."""
    categories = mgr.get_categories()
    menu_items = [display_name for _, display_name in categories]
    selected_index = mgr.get_category_index()
    labels = config_module.get_control_labels()
    footer = f"< {labels['prev']}=Up | {labels['next']}=Down | {labels['select']}=Open | {labels['back']}=Exit >"
    draw_scrollable_list_menu(
        screen=screen,
        title="Star Trek Wiki",
        menu_items=menu_items,
        selected_index=selected_index,
        fonts=fonts,
        config_module=config_module,
        footer_hint=footer,
        item_style="simple",
        ui_scaler=ui_scaler,
    )


def _draw_item_list(screen, mgr, fonts, config_module, ui_scaler):
    """Item list within current category. Select opens detail."""
    categories = mgr.get_categories()
    cat_key = categories[mgr.get_category_index()][0]
    cat_display = mgr.get_current_category_name()
    items = mgr.get_category_items(cat_key)
    menu_items = []
    for it in items:
        summary = mgr.format_item_summary(it, cat_key)
        menu_items.append(summary[:55] + "..." if len(summary) > 55 else summary)
    if not menu_items:
        menu_items = ["(No entries)"]
    selected_index = min(mgr.get_item_index(), len(menu_items) - 1) if menu_items else 0
    labels = config_module.get_control_labels()
    footer = f"< {labels['prev']}=Up | {labels['next']}=Down | {labels['select']}=View | {labels['back']}=Categories >"
    draw_scrollable_list_menu(
        screen=screen,
        title=f"Star Trek — {cat_display}",
        menu_items=menu_items,
        selected_index=selected_index,
        fonts=fonts,
        config_module=config_module,
        footer_hint=footer,
        item_style="simple",
        ui_scaler=ui_scaler,
    )


def _draw_detail_view(screen, mgr, fonts, config_module, ui_scaler):
    """Scrollable detail for the selected item. Layout and wrap logic match log_viewer_view (same UIScaler/margins/footer)."""
    screen.fill(config_module.Theme.BACKGROUND)
    if ui_scaler:
        screen_width = ui_scaler.screen_width
        screen_height = ui_scaler.screen_height
        safe_rect = ui_scaler.get_safe_area_rect() if ui_scaler.safe_area_enabled else pygame.Rect(0, 0, screen_width, screen_height)
        margin_sm = ui_scaler.margin("small")
        footer_space = ui_scaler.scale(40)
    else:
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        safe_rect = pygame.Rect(0, 0, screen_width, screen_height)
        margin_sm = 8
        footer_space = 40

    is_small = screen_width <= 400 if not ui_scaler else ui_scaler.is_small_screen()
    if is_small:
        title_font = fonts["small"]
        content_font = fonts.get("tiny", fonts["small"])
        line_height = ui_scaler.scale(16) if ui_scaler else 16
        start_y = ui_scaler.margin("large") if ui_scaler else 30
        margin = margin_sm
        max_chars_per_line = 30
        max_lines = max(1, min(8, (safe_rect.height - start_y - footer_space) // line_height))
    else:
        title_font = fonts["medium"]
        content_font = fonts["small"]
        line_height = ui_scaler.scale(20) if ui_scaler else 20
        start_y = ui_scaler.scale(50) if ui_scaler else 50
        margin = ui_scaler.margin("medium") if ui_scaler else 15
        max_chars_per_line = 42
        max_lines = max(1, min(12, (safe_rect.height - start_y - footer_space) // line_height))

    all_lines = mgr.get_detail_lines()
    scroll_index = mgr.get_detail_scroll_line()
    max_scroll = max(0, len(all_lines) - max_lines)
    scroll_index = min(scroll_index, max_scroll)
    log_lines = all_lines[scroll_index : scroll_index + max_lines]

    title_top = safe_rect.top + (ui_scaler.margin("small") if ui_scaler else 10)
    item = mgr.get_current_item()
    title_text = (item.get("name") or "Detail")[:32]
    title_surface = title_font.render(title_text, True, config_module.Theme.ACCENT)
    title_rect = title_surface.get_rect(centerx=safe_rect.centerx)
    screen.blit(title_surface, (title_rect.x, title_top))

    y_offset = safe_rect.top + start_y
    lines_drawn = 0
    for line in log_lines:
        if lines_drawn >= max_lines:
            break
        color = config_module.Theme.FOREGROUND
        if len(line) <= max_chars_per_line:
            line_surface = content_font.render(line, True, color)
            screen.blit(line_surface, (safe_rect.left + margin, y_offset))
            y_offset += line_height
            lines_drawn += 1
        else:
            words = line.split(" ")
            current_line = ""
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                if len(test_line) <= max_chars_per_line:
                    current_line = test_line
                else:
                    if current_line and lines_drawn < max_lines:
                        line_surface = content_font.render(current_line, True, color)
                        screen.blit(line_surface, (safe_rect.left + margin, y_offset))
                        y_offset += line_height
                        lines_drawn += 1
                    if len(word) <= max_chars_per_line:
                        current_line = word
                    else:
                        while len(word) > max_chars_per_line:
                            if lines_drawn >= max_lines:
                                break
                            chunk = word[: max_chars_per_line - 3] + "..."
                            line_surface = content_font.render(chunk, True, color)
                            screen.blit(line_surface, (safe_rect.left + margin, y_offset))
                            y_offset += line_height
                            lines_drawn += 1
                            word = word[max_chars_per_line - 3 :]
                        current_line = word if word else ""
            if current_line and lines_drawn < max_lines:
                line_surface = content_font.render(current_line, True, color)
                screen.blit(line_surface, (safe_rect.left + margin, y_offset))
                y_offset += line_height
                lines_drawn += 1

    if len(all_lines) > max_lines:
        scroll_text = f"{scroll_index + 1}-{min(scroll_index + max_lines, len(all_lines))} of {len(all_lines)}"
        scroll_surface = content_font.render(scroll_text, True, config_module.Theme.ACCENT)
        scroll_bottom = safe_rect.bottom - (ui_scaler.scale(25) if ui_scaler else 25)
        screen.blit(scroll_surface, (safe_rect.left + margin, scroll_bottom))
    # No footer in detail view so scroll numbers don't overlap; simple navigation is self-explanatory.
