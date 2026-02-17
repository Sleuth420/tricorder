# --- ui/views/settings/display_settings_view.py ---
# Display settings: main menu and dashboard cycle interval picker sub-screen

import pygame
import logging
from ui.components.menus.list_menu_base import draw_simple_list_menu

logger = logging.getLogger(__name__)


def _build_display_settings_menu_items(app_state):
    """Build Display Settings main menu items."""
    led_on = getattr(app_state, "led_matrix_enabled", True)
    return [
        "Dashboard auto-cycle",
        "LED matrix (lid open): " + ("On" if led_on else "Off"),
        "<- Back to Settings",
    ]


def draw_display_settings_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the Display Settings main menu: Dashboard auto-cycle, Safe area, Debug layout, Back.
    """
    current_selection_idx = getattr(app_state.settings_manager, "display_settings_option_index", 0)
    menu_items = _build_display_settings_menu_items(app_state)
    draw_simple_list_menu(
        screen=screen,
        title="Display Settings",
        menu_items=menu_items,
        selected_index=current_selection_idx,
        fonts=fonts,
        config_module=config_module,
        footer_hint=None,
        ui_scaler=ui_scaler,
    )


def draw_display_cycle_interval_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the Dashboard auto-cycle interval picker (sub-screen of Display Settings).
    """
    info = getattr(app_state.settings_manager, "get_display_cycle_interval_info", lambda: {})()
    options = info.get("options", [1, 5, 10, 15, 30, 60])
    selected_index = info.get("selected_index", 0)
    menu_items = [f"{v}s" for v in options] + ["<- Back to Display Settings"]
    # Selected index matches: 0..len(options)-1 for intervals, len(options) for Back
    draw_simple_list_menu(
        screen=screen,
        title="Dashboard auto-cycle",
        menu_items=menu_items,
        selected_index=selected_index,
        fonts=fonts,
        config_module=config_module,
        footer_hint=None,
        ui_scaler=ui_scaler,
    )
