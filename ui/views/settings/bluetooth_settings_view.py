# --- ui/views/settings/bluetooth_settings_view.py ---
# Bluetooth status and back to settings

import logging
from data import system_info
from ui.components.menus.list_menu_base import draw_simple_list_menu

logger = logging.getLogger(__name__)


def draw_bluetooth_settings_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the Bluetooth settings screen: current status and Back to Settings.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        ui_scaler (UIScaler, optional): UI scaling system
    """
    try:
        status, device = system_info.get_bluetooth_info()
        status_text = f"Bluetooth: {status}"
        if device and device not in (
            "N/A", "Not Available", "Windows", "Unsupported",
            "Available", "No Devices", "Disabled"
        ):
            status_text += f" — {device}"
    except Exception as e:
        logger.debug("Bluetooth status failed: %s", e)
        status_text = "Bluetooth: N/A"

    draw_simple_list_menu(
        screen=screen,
        title="Bluetooth",
        menu_items=["<- Back to Settings"],
        selected_index=0,
        fonts=fonts,
        config_module=config_module,
        footer_hint=status_text,
        show_footer=True,
        ui_scaler=ui_scaler
    )
