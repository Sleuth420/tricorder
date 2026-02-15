# --- ui/views/schematics/schematics_category_view.py ---
# Menu view: Schematics (3D) | Media Player

import pygame
import logging
from ui.components.menus.list_menu_base import draw_scrollable_list_menu

logger = logging.getLogger(__name__)


def draw_schematics_category_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the schematics category submenu (Schematics | Media Player).
    """
    menu_items = app_state.get_current_menu_items()
    selected_index = app_state.get_current_menu_index()

    labels = config_module.get_control_labels()
    footer_hint = f"< {labels['prev']}=Up | {labels['next']}=Down | {labels['select']}=Select >"

    draw_scrollable_list_menu(
        screen=screen,
        title="Schematics",
        menu_items=menu_items,
        selected_index=selected_index,
        fonts=fonts,
        config_module=config_module,
        footer_hint=footer_hint,
        item_style="simple",
        ui_scaler=ui_scaler
    )
