# --- ui/views/settings/bluetooth_settings_view.py ---
# Bluetooth settings: toggle, devices, back (driven by BluetoothManager)

import logging
from ui.components.menus.list_menu_base import draw_simple_list_menu

logger = logging.getLogger(__name__)


def draw_bluetooth_settings_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the Bluetooth settings screen using BluetoothManager: toggle, devices, back.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        ui_scaler (UIScaler, optional): UI scaling system
    """
    if not app_state.bluetooth_manager:
        draw_simple_list_menu(
            screen=screen,
            title="Bluetooth",
            menu_items=["<- Back to Settings"],
            selected_index=0,
            fonts=fonts,
            config_module=config_module,
            footer_hint="Bluetooth manager not available",
            show_footer=True,
            ui_scaler=ui_scaler,
        )
        return

    options_data = app_state.bluetooth_manager.get_current_display_options()
    menu_items = [opt["name"] for opt in options_data]
    selected_index = app_state.bluetooth_manager.get_selected_index()
    footer = None
    if getattr(app_state.bluetooth_manager, "last_toggle_message", None):
        footer = app_state.bluetooth_manager.last_toggle_message
    elif app_state.bluetooth_manager.device_str and app_state.bluetooth_manager.device_str not in (
        "N/A", "Not Available", "Windows", "Unsupported", "Available", "No Devices", "Disabled"
    ):
        footer = f"Connected: {app_state.bluetooth_manager.device_str}"

    draw_simple_list_menu(
        screen=screen,
        title="Bluetooth",
        menu_items=menu_items,
        selected_index=selected_index,
        fonts=fonts,
        config_module=config_module,
        footer_hint=footer,
        show_footer=footer is not None,
        ui_scaler=ui_scaler,
    )
