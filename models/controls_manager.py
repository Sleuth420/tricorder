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
        """Generate the list of control items for display."""
        # Get key names from config
        key_prev_name = f"'{self.config.KEY_PREV_NAME}'" if hasattr(self.config, 'KEY_PREV_NAME') else "'A'"
        key_next_name = f"'{self.config.KEY_NEXT_NAME}'" if hasattr(self.config, 'KEY_NEXT_NAME') else "'D'"
        key_select_name = f"'{self.config.KEY_SELECT_NAME}'" if hasattr(self.config, 'KEY_SELECT_NAME') else "'RETURN'"
        
        # We'll dynamically get the actual key names when rendering
        controls_items = [
            {"type": "section", "text": "MENU NAVIGATION:"},
            {"type": "control", "text": f"{key_prev_name} = Left/Previous/Up"},
            {"type": "control", "text": f"Long {key_prev_name} = Back to Menu"},
            {"type": "control", "text": f"{key_next_name} = Right/Next/Down"},
            {"type": "control", "text": f"'RETURN' = Select"},
            {"type": "control", "text": "Joystick: Up/Down/Left/Right/Press"},
            {"type": "control", "text": "Mouse: Left=Prev, Right=Next, Middle=Select"},
            {"type": "control", "text": "Long Mouse Left = Back to Menu"},
            {"type": "spacer", "text": ""},
            {"type": "section", "text": "SCHEMATICS VIEW:"},
            {"type": "control", "text": f"{key_prev_name} = Rotate Left"},
            {"type": "control", "text": f"Long {key_prev_name} = Rotate Up"},
            {"type": "control", "text": f"{key_next_name} = Rotate Right"},
            {"type": "control", "text": f"Long {key_next_name} = Rotate Down"},
            {"type": "control", "text": f"'RETURN' = Select/Pause"},
            {"type": "control", "text": "Mouse Left = Rotate Left, Mouse Right = Rotate Right"},
            {"type": "control", "text": "Long Mouse Right = Pause Menu"},
            {"type": "spacer", "text": ""},
            {"type": "section", "text": "GAMES:"},
            {"type": "control", "text": f"Snake: {key_prev_name}=Left, {key_next_name}=Right"},
            {"type": "control", "text": f"Pong: {key_prev_name}=Up, {key_next_name}=Down"},
            {"type": "control", "text": f"'RETURN' = Pause (all games)"},
            {"type": "control", "text": "Mouse: Left=Prev, Right=Next, Middle=Pause"},
            {"type": "spacer", "text": ""},
            {"type": "section", "text": "SECRET COMBO:"},
            {"type": "control", "text": f"Hold {key_prev_name} + {key_next_name} simultaneously"},
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
        """Update the controls items with current key names from config."""
        import pygame
        
        # Get actual key names from pygame
        key_prev_name = f"'{pygame.key.name(config_module.KEY_PREV).upper()}'"
        key_next_name = f"'{pygame.key.name(config_module.KEY_NEXT).upper()}'"
        key_select_name = f"'{pygame.key.name(config_module.KEY_SELECT).upper()}'"
        
        # Regenerate controls items with updated key names
        self.controls_items = [
            {"type": "section", "text": "MENU NAVIGATION:"},
            {"type": "control", "text": f"{key_prev_name} = Left/Previous/Up"},
            {"type": "control", "text": f"Long {key_prev_name} = Back to Menu"},
            {"type": "control", "text": f"{key_next_name} = Right/Next/Down"},
            {"type": "control", "text": f"{key_select_name} = Select"},
            {"type": "control", "text": "Joystick: Up/Down/Left/Right/Press"},
            {"type": "spacer", "text": ""},
            {"type": "section", "text": "SCHEMATICS VIEW:"},
            {"type": "control", "text": f"{key_prev_name} = Rotate Left"},
            {"type": "control", "text": f"Long {key_prev_name} = Rotate Up"},
            {"type": "control", "text": f"{key_next_name} = Rotate Right"},
            {"type": "control", "text": f"Long {key_next_name} = Rotate Down"},
            {"type": "control", "text": f"{key_select_name} = Select/Pause"},
            {"type": "spacer", "text": ""},
            {"type": "section", "text": "GAMES:"},
            {"type": "control", "text": f"Snake: {key_prev_name}=Left, {key_next_name}=Right"},
            {"type": "control", "text": f"Pong: {key_prev_name}=Up, {key_next_name}=Down"},
            {"type": "control", "text": f"{key_select_name} = Pause (all games)"},
            {"type": "spacer", "text": ""},
            {"type": "section", "text": "SECRET COMBO:"},
            {"type": "control", "text": f"Hold {key_prev_name} + {key_next_name} simultaneously"},
            {"type": "spacer", "text": ""},
            {"type": "section", "text": "KEY REMAPPING:"},
            {"type": "control", "text": "Coming Soon - Remap keys to arrows, WASD, etc."},
        ]
        
        logger.debug("Updated controls items with current key names") 