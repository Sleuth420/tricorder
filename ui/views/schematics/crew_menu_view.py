# --- ui/views/schematics/crew_menu_view.py ---
# Crew list under Schematics: select a crew member to view image + name

import pygame
import logging
from ui.components.menus.list_menu_base import draw_scrollable_list_menu

logger = logging.getLogger(__name__)


def draw_crew_menu_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the crew list menu (names from assets/ship/Crew). Selecting opens crew detail view.
    """
    menu_items = app_state.get_current_menu_items()
    selected_index = app_state.get_current_menu_index()

    labels = config_module.get_control_labels()
    footer_hint = f"< {labels['prev']}=Up | {labels['next']}=Down | {labels['select']}=Select >"

    draw_scrollable_list_menu(
        screen=screen,
        title="Crew",
        menu_items=menu_items,
        selected_index=selected_index,
        fonts=fonts,
        config_module=config_module,
        footer_hint=footer_hint,
        item_style="simple",
        ui_scaler=ui_scaler
    )
