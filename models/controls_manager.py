# --- models/controls_manager.py ---
# Manages controls display state and navigation

import logging
import config as app_config

logger = logging.getLogger(__name__)

class ControlsManager:
    """Manages the controls view state and scrolling."""
    
    def __init__(self, config_module):
        """
        Initialize the controls manager.
        
        Args:
            config_module: The configuration module
        """
        self.config = config_module
        self.controls_index = 0  # Current selected control item
        
        # Generate the controls items list
        self.controls_items = self._generate_controls_items()
        
    def _generate_controls_items(self):
        """Generate the list of control items for display. Uses OS-adaptive labels (Left/Right/Middle on Pi, key names on dev)."""
        labels = self.config.get_control_labels()
        prev_l, next_l, select_l, back_l = labels["prev"], labels["next"], labels["select"], labels["back"]

        controls_items = [
            {"type": "section", "text": "MENU NAVIGATION:"},
            {"type": "control", "text": f"{prev_l} = Left/Previous/Up"},
            {"type": "control", "text": f"{back_l} = Back to Menu"},
            {"type": "control", "text": f"{next_l} = Right/Next/Down"},
            {"type": "control", "text": f"{select_l} = Select"},
            {"type": "control", "text": "Joystick: Up/Down/Left/Right/Press"},
            {"type": "control", "text": "Mouse: Left=Prev, Right=Next, Middle=Select"},
            {"type": "control", "text": "Long Mouse Left = Back to Menu"},
            {"type": "spacer", "text": ""},
            {"type": "section", "text": "SCHEMATICS VIEW:"},
            {"type": "control", "text": f"{prev_l} = Rotate Left"},
            {"type": "control", "text": f"Long {prev_l} = Rotate Up"},
            {"type": "control", "text": f"{next_l} = Rotate Right"},
            {"type": "control", "text": f"Long {next_l} = Rotate Down"},
            {"type": "control", "text": f"{select_l} = Select/Pause"},
            {"type": "control", "text": "Mouse Left = Rotate Left, Mouse Right = Rotate Right"},
            {"type": "control", "text": "Long Mouse Right = Pause Menu"},
            {"type": "spacer", "text": ""},
            {"type": "section", "text": "MEDIA PLAYER:"},
            {"type": "control", "text": f"{back_l} = Exit / close pause menu (long press)"},
            {"type": "control", "text": f"{prev_l} = Volume down (when playing) / list or menu up"},
            {"type": "control", "text": f"{next_l} = Volume up (when playing) / list or menu down"},
            {"type": "control", "text": f"{select_l} = Play (from list) / Pause menu (when playing)"},
            {"type": "control", "text": "Pause menu: Resume, Volume, Mute, Prev/Next track, Back to list"},
            {"type": "spacer", "text": ""},
            {"type": "section", "text": "GAMES:"},
            {"type": "control", "text": f"Snake: {prev_l}=Left, {next_l}=Right"},
            {"type": "control", "text": f"Pong: {prev_l}=Up, {next_l}=Down"},
            {"type": "control", "text": f"{select_l} = Pause (all games)"},
            {"type": "control", "text": "Mouse: Left=Prev, Right=Next, Middle=Pause"},
            {"type": "spacer", "text": ""},
            {"type": "section", "text": "SECRET COMBO:"},
            {"type": "control", "text": f"Hold {prev_l} + {next_l} simultaneously"},
            {"type": "spacer", "text": ""},
            {"type": "section", "text": "KEY REMAPPING:"},
            {"type": "control", "text": "Coming Soon - Remap keys to arrows, WASD, etc."},
        ]

        return controls_items
        
    def navigate_next(self):
        """Navigate to the next selectable control item (skip sections/spacers)."""
        selectable_items = [i for i, item in enumerate(self.controls_items) if item["type"] == "control"]
        if not selectable_items:
            return False
        current_selectable_index = self.controls_index % len(selectable_items)
        self.controls_index = (current_selectable_index + 1) % len(selectable_items)
        logger.debug(f"Controls NEXT: selectable index={self.controls_index}")
        return True

    def navigate_prev(self):
        """Navigate to the previous selectable control item (skip sections/spacers)."""
        selectable_items = [i for i, item in enumerate(self.controls_items) if item["type"] == "control"]
        if not selectable_items:
            return False
        current_selectable_index = self.controls_index % len(selectable_items)
        self.controls_index = (current_selectable_index - 1 + len(selectable_items)) % len(selectable_items)
        logger.debug(f"Controls PREV: selectable index={self.controls_index}")
        return True
        
    def get_controls_items(self):
        """Get the list of control items."""
        return self.controls_items
        
    def get_current_index(self):
        """Get the current selected index."""
        return self.controls_index
        
    def update_key_names(self, config_module):
        """Update the controls items with OS-adaptive labels (Left/Right/Middle on Pi, key names on dev)."""
        labels = config_module.get_control_labels()
        prev_l, next_l, select_l, back_l = labels["prev"], labels["next"], labels["select"], labels["back"]

        self.controls_items = [
            {"type": "section", "text": "MENU NAVIGATION:"},
            {"type": "control", "text": f"{prev_l} = Left/Previous/Up"},
            {"type": "control", "text": f"{back_l} = Back to Menu"},
            {"type": "control", "text": f"{next_l} = Right/Next/Down"},
            {"type": "control", "text": f"{select_l} = Select"},
            {"type": "control", "text": "Joystick: Up/Down/Left/Right/Press"},
            {"type": "spacer", "text": ""},
            {"type": "section", "text": "SCHEMATICS VIEW:"},
            {"type": "control", "text": f"{prev_l} = Rotate Left"},
            {"type": "control", "text": f"Long {prev_l} = Rotate Up"},
            {"type": "control", "text": f"{next_l} = Rotate Right"},
            {"type": "control", "text": f"Long {next_l} = Rotate Down"},
            {"type": "control", "text": f"{select_l} = Select/Pause"},
            {"type": "spacer", "text": ""},
            {"type": "section", "text": "MEDIA PLAYER:"},
            {"type": "control", "text": f"{back_l} = Exit / close pause menu (long press)"},
            {"type": "control", "text": f"{prev_l} = Volume down (when playing) / list or menu up"},
            {"type": "control", "text": f"{next_l} = Volume up (when playing) / list or menu down"},
            {"type": "control", "text": f"{select_l} = Play (from list) / Pause menu (when playing)"},
            {"type": "control", "text": "Pause menu: Resume, Volume, Mute, Prev/Next track, Back to list"},
            {"type": "spacer", "text": ""},
            {"type": "section", "text": "GAMES:"},
            {"type": "control", "text": f"Snake: {prev_l}=Left, {next_l}=Right"},
            {"type": "control", "text": f"Pong: {prev_l}=Up, {next_l}=Down"},
            {"type": "control", "text": f"{select_l} = Pause (all games)"},
            {"type": "spacer", "text": ""},
            {"type": "section", "text": "SECRET COMBO:"},
            {"type": "control", "text": f"Hold {prev_l} + {next_l} simultaneously"},
            {"type": "spacer", "text": ""},
            {"type": "section", "text": "KEY REMAPPING:"},
            {"type": "control", "text": "Coming Soon - Remap keys to arrows, WASD, etc."},
        ]
        
        logger.debug("Updated controls items with current key names") 