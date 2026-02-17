# --- ui/views/settings/stapi_settings_view.py ---
# Settings screen for fetching Star Trek data from STAPI (runs scripts/fetch_stapi_data.py).

import pygame
import logging
from ui.components.menus.list_menu_base import draw_simple_list_menu

logger = logging.getLogger(__name__)


def draw_stapi_settings_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the Star Trek Data settings screen: Fetch data from STAPI or Back.
    Menu items and selection come from app_state (st_wiki_manager manifest + local index).
    """
    # Build menu: "Fetch Star Trek Data", "<- Back"
    menu_items = ["Fetch Star Trek Data", "<- Back"]
    selected_index = getattr(app_state, "stapi_settings_index", 0)
    selected_index = max(0, min(selected_index, len(menu_items) - 1))

    draw_simple_list_menu(
        screen=screen,
        title="Star Trek Data",
        menu_items=menu_items,
        selected_index=selected_index,
        fonts=fonts,
        config_module=config_module,
        footer_hint="Requires network. Data saved to data/stapi/.",
        show_footer=True,
        ui_scaler=ui_scaler
    )
