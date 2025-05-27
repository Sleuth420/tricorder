"""
Menu model that provides a single source of truth for menu items.
"""

import logging

logger = logging.getLogger(__name__)

class MenuItem:
    """
    Menu item model.
    
    This class represents a menu item in the application.
    It contains all the data needed to display and navigate to the item.
    """
    
    def __init__(self, id, name, view_id, sensor=None, color_key=None):
        """
        Initialize a menu item.
        
        Args:
            id (str): Unique identifier for the menu item
            name (str): Display name for the menu item
            view_id (str): ID of the view to display for this item
            sensor (str, optional): Sensor name for sensor-specific views
            color_key (str, optional): Configuration color key for this item
        """
        self.id = id
        self.name = name
        self.view_id = view_id
        self.sensor = sensor
        self.color_key = color_key
        
    def __repr__(self):
        return f"MenuItem(id='{self.id}', name='{self.name}', view_id='{self.view_id}')"

# Define the menu items
# This is the SINGLE source of truth for all menu items
SYSTEM_INFO_ITEM = MenuItem(
    id="system_info",
    name="System Info",
    view_id="system_view",
    color_key="COLOR_SIDEBAR_SYSTEM"
)

TEMPERATURE_ITEM = MenuItem(
    id="temperature",
    name="Temperature",
    view_id="sensor_view",
    sensor="TEMPERATURE",
    color_key="COLOR_SIDEBAR_TEMP"
)

HUMIDITY_ITEM = MenuItem(
    id="humidity",
    name="Humidity",
    view_id="sensor_view",
    sensor="HUMIDITY",
    color_key="COLOR_SIDEBAR_HUMID"
)

PRESSURE_ITEM = MenuItem(
    id="pressure",
    name="Pressure",
    view_id="sensor_view",
    sensor="PRESSURE",
    color_key="COLOR_SIDEBAR_PRESS"
)

ORIENTATION_ITEM = MenuItem(
    id="orientation",
    name="Orientation",
    view_id="sensor_view",
    sensor="ORIENTATION",
    color_key="COLOR_SIDEBAR_ORIENT"
)

ACCELERATION_ITEM = MenuItem(
    id="acceleration",
    name="Acceleration",
    view_id="sensor_view",
    sensor="ACCELERATION",
    color_key="COLOR_SIDEBAR_ACCEL"
)

ALL_SENSORS_ITEM = MenuItem(
    id="all_sensors",
    name="All Sensors",
    view_id="dashboard_view",
    color_key="COLOR_SIDEBAR_ALL"
)

SETTINGS_ITEM = MenuItem(
    id="settings",
    name="Settings",
    view_id="settings_view",
    color_key="COLOR_SIDEBAR_SETTINGS"
)

# Complete list of menu items in display order
MENU_ITEMS = [
    SYSTEM_INFO_ITEM,
    TEMPERATURE_ITEM,
    HUMIDITY_ITEM,
    PRESSURE_ITEM,
    ORIENTATION_ITEM,
    ACCELERATION_ITEM,
    ALL_SENSORS_ITEM,
    SETTINGS_ITEM
]

# Lookup dictionary for quick access by ID
MENU_ITEMS_BY_ID = {item.id: item for item in MENU_ITEMS}

def get_menu_item(item_id):
    """
    Get a menu item by ID.
    
    Args:
        item_id (str): The ID of the menu item to retrieve
        
    Returns:
        MenuItem: The menu item, or None if not found
    """
    return MENU_ITEMS_BY_ID.get(item_id)

def get_menu_items():
    """
    Get all menu items.
    
    Returns:
        list: List of all menu items
    """
    return MENU_ITEMS 