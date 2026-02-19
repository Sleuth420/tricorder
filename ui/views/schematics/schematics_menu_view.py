# --- ui/views/schematics_menu_view.py ---
# Handles rendering of the schematics selection submenu (Ship, Logs, Data)

import pygame
import logging
from ui.components.menus.list_menu_base import draw_scrollable_list_menu
from models.app_state import STATE_SCHEMATICS_MENU, STATE_LOGS_MENU, STATE_DATA_MENU

logger = logging.getLogger(__name__)

def draw_schematics_menu_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the schematics submenu view (Ship, Logs, or Data) using the standardized list menu component.
    """
    menu_items = app_state.get_current_menu_items()
    selected_index = app_state.get_current_menu_index()

    if app_state.current_state == STATE_SCHEMATICS_MENU:
        title = "Ship"
    elif app_state.current_state == STATE_LOGS_MENU:
        title = "Logs"
    elif app_state.current_state == STATE_DATA_MENU:
        title = "Data"
    else:
        title = "Schematics"

    labels = config_module.get_control_labels()
    footer_hint = f"< {labels['prev']}=Up | {labels['next']}=Down | {labels['select']}=Select >"

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