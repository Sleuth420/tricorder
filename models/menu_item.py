from dataclasses import dataclass, field
from typing import Optional, Callable, Any

# Application states - It's often better to have these constants defined in a central place,
# but for the MenuItem to reference them, they might be passed in or defined here/imported.
# For now, we'll assume target_state is a string that matches constants in AppState.

@dataclass
class MenuItem:
    """Represents an item in a menu."""
    name: str
    
    # Action to perform when selected. Can be a state transition or a function call.
    target_state: Optional[str] = None  # Name of the state to transition to
    action_name: Optional[str] = None   # String identifier for a custom action (e.g., "LAUNCH_PONG")
    
    # Data associated with the menu item, e.g., sensor type or game parameters
    data: Optional[Any] = None # Can be a string (like sensor type) or a dict for more complex data

    # UI specific attributes
    color_key: Optional[str] = None   # Key to look up color in config.Theme
    image_path: Optional[str] = None  # Path to an image/icon for the menu item
    
    # Sub-menu (optional)
    # sub_menu_items: list["MenuItem"] = field(default_factory=list) # For nested menus

    def __post_init__(self):
        # Ensure that either target_state or action_name is provided, but not both usually.
        # This logic can be adjusted based on how actions vs. state transitions are handled.
        if self.target_state and self.action_name:
            # This could be a warning or an error depending on design
            # print(f"Warning: MenuItem '{self.name}' has both target_state and action_name.")
            pass # Allow both for now, AppState logic will decide precedence
        elif not self.target_state and not self.action_name:
            # print(f"Warning: MenuItem '{self.name}' has neither target_state nor action_name.")
            pass # Item might be a non-interactive label or a parent for a sub_menu 