# --- ui/views/settings/debug_settings_view.py ---
# Debug Settings: View Logs, Debug Overlay, Admin Timer (toggle), Back

import pygame
import logging
from ui.components.menus.list_menu_base import draw_simple_list_menu
import config as app_config

logger = logging.getLogger(__name__)


def draw_debug_settings_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the Debug Settings screen: View Logs, Debug Overlay, Admin Timer toggle, Back.
    """
    timer_on = getattr(app_state, "admin_timer_enabled", False)
    menu_items = [
        "View Logs",
        "Debug Overlay",
        f"Admin Timer: {'ON' if timer_on else 'OFF'}",
        "<- Back to Settings",
    ]
    selected_index = getattr(app_state, "debug_settings_option_index", 0)
    draw_simple_list_menu(
        screen=screen,
        title="Debug Settings",
        menu_items=menu_items,
        selected_index=selected_index,
        fonts=fonts,
        config_module=config_module,
        footer_hint=f"{config_module.get_control_labels()['select']} open / toggle",
        ui_scaler=ui_scaler,
    )
