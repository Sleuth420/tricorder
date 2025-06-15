# --- utils/ui_scaler.py ---
# Centralized UI scaling system for consistent responsive design

import logging

logger = logging.getLogger(__name__)

class UIScaler:
    """
    Centralized UI scaling system that provides consistent sizing and spacing
    calculations based on screen dimensions and base resolution.
    
    This class eliminates hardcoded values and inconsistent calculations
    throughout the UI components and views.
    """
    
    def __init__(self, screen_width, screen_height, config_module=None):
        """
        Initialize the UIScaler with current screen dimensions.
        
        Args:
            screen_width (int): Current screen width in pixels
            screen_height (int): Current screen height in pixels
            config_module (module, optional): Configuration module for theme constants
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.config = config_module
        
        # Get base resolution from config or use defaults
        if config_module and hasattr(config_module, 'UI_BASE_WIDTH'):
            self.base_width = config_module.UI_BASE_WIDTH
            self.base_height = config_module.UI_BASE_HEIGHT
        else:
            # Fallback to hardcoded values if config not available
            self.base_width = 320
            self.base_height = 240
        
        # Calculate scaling factors
        self.width_scale = screen_width / self.base_width
        self.height_scale = screen_height / self.base_height
        
        # Use the smaller scale factor to maintain aspect ratio
        self.scale_factor = min(self.width_scale, self.height_scale)
        
        # Set debug mode from config
        self.debug_mode = getattr(config_module, 'UI_DEBUG_DRAWING', False) if config_module else False
        
        # Basic initialization logging
        logger.debug(f"UIScaler initialized: {screen_width}x{screen_height}, scale={self.scale_factor:.2f}")
        
        if self.debug_mode:
            logger.info(f"🎨 UIScaler DEBUG MODE: {screen_width}x{screen_height}, scale_factor={self.scale_factor:.2f}")
    
    def scale(self, base_value):
        """
        Scale a base value proportionally to current screen size.
        
        Args:
            base_value (int|float): Base value at 320x240 resolution
            
        Returns:
            int: Scaled value for current resolution
        """
        result = max(1, int(base_value * self.scale_factor))
        
        # Only log very significant scaling operations to avoid spam
        if self.debug_mode and base_value >= 50:  # Only log large values
            logger.info(f"🎨 UIScaler.scale: {base_value} → {result}px (factor: {self.scale_factor:.2f})")
        
        return result
    
    def margin(self, size="medium"):
        """
        Get standardized margins for consistent spacing.
        
        Args:
            size (str): "small", "medium", "large", "xlarge"
            
        Returns:
            int: Margin size in pixels
        """
        # Reduced base margins for better proportions
        base_margins = {
            "small": 4,      # Reduced from 6
            "medium": 8,     # Reduced from 12
            "large": 12,     # Reduced from 18
            "xlarge": 16     # Reduced from 24
        }
        
        base_value = base_margins.get(size, base_margins["medium"])
        result = self.scale(base_value)
        
        # Remove debug logging to avoid spam - margins are called every frame
        
        return result
    
    def padding(self, size="medium"):
        """
        Get standardized padding for consistent spacing.
        
        Args:
            size (str): "small", "medium", "large", "xlarge"
            
        Returns:
            int: Padding size in pixels
        """
        # Reduced base paddings for better proportions
        base_paddings = {
            "small": 2,      # Reduced from 3
            "medium": 5,     # Reduced from 8
            "large": 8,      # Reduced from 12
            "xlarge": 12     # Reduced from 16
        }
        
        base_value = base_paddings.get(size, base_paddings["medium"])
        result = self.scale(base_value)
        
        # Remove debug logging to avoid spam - paddings are called every frame
        
        return result
    
    def header_height(self):
        """
        Get standardized header height using proportional calculation.
        Original approach: approximately screen_height // 10 to // 12
        
        Returns:
            int: Header height in pixels
        """
        # Revert to original proportional calculation - // 10 was correct
        # This matches the original design proportions
        result = max(20, self.screen_height // 10)  # 10% of screen height, minimum 20px
        
        if self.debug_mode:
            logger.info(f"🎨 UIScaler.header_height: {result}px ({result/self.screen_height*100:.1f}% of {self.screen_height}px)")
        
        return result
    
    def header_top_margin(self):
        """
        Get standardized header top margin.
        Replaces: screen_height // 20
        
        Returns:
            int: Header top margin in pixels
        """
        # Use original proportional calculation
        result = self.screen_height // 20
        
        if self.debug_mode:
            logger.info(f"🎨 UIScaler.header_top_margin: {result}px ({result/self.screen_height*100:.1f}% of {self.screen_height}px)")
        
        return result
    
    def content_margin(self):
        """
        Get standardized content margin.
        Replaces: max(8, screen_width // 30)
        
        Returns:
            int: Content margin in pixels
        """
        # Use original proportional calculation
        result = max(8, self.screen_width // 30)
        
        if self.debug_mode:
            logger.info(f"🎨 UIScaler.content_margin: {result}px ({result/self.screen_width*100:.1f}% of {self.screen_width}px)")
        
        return result
    
    def item_height(self, size="medium"):
        """
        Get standardized item heights for lists and menus.
        
        Args:
            size (str): "small", "medium", "large"
            
        Returns:
            int: Item height in pixels
        """
        base_heights = {
            "small": 20,
            "medium": 25,
            "large": 30
        }
        
        base_value = base_heights.get(size, base_heights["medium"])
        return self.scale(base_value)
    
    def item_spacing(self, size="medium"):
        """
        Get standardized spacing between items.
        
        Args:
            size (str): "small", "medium", "large"
            
        Returns:
            int: Spacing in pixels
        """
        base_spacings = {
            "small": 10,
            "medium": 15,
            "large": 20
        }
        
        base_value = base_spacings.get(size, base_spacings["medium"])
        return self.scale(base_value)
    
    def font_size(self, base_size):
        """
        Scale font size proportionally.
        
        Args:
            base_size (int): Base font size
            
        Returns:
            int: Scaled font size with minimum bounds
        """
        scaled_size = self.scale(base_size)
        # Ensure minimum readable font sizes
        if base_size <= 12:
            return max(8, scaled_size)
        elif base_size <= 18:
            return max(10, scaled_size)
        else:
            return max(12, scaled_size)
    
    def component_size(self, base_width, base_height):
        """
        Scale component dimensions proportionally.
        
        Args:
            base_width (int): Base width at 320x240
            base_height (int): Base height at 320x240
            
        Returns:
            tuple: (scaled_width, scaled_height)
        """
        return (self.scale(base_width), self.scale(base_height))
    
    def status_bar_dimensions(self):
        """
        Get standardized status bar dimensions.
        Replaces hardcoded values in horizontal_status_bar.py
        
        Returns:
            dict: Dictionary with bar dimensions
        """
        return {
            "height": self.scale(12),
            "margin": self.scale(5),
            "label_width_ratio": 0.2,  # 20% of total width
            "value_width_ratio": 0.17,  # 17% of total width
        }
    
    def graph_dimensions(self):
        """
        Get standardized graph dimensions and spacing.
        Replaces hardcoded values in vertical_bar_graph.py
        
        Returns:
            dict: Dictionary with graph dimensions
        """
        return {
            "top_padding": self.scale(15),
            "bottom_padding": self.scale(15),
            "tick_length": self.scale(20),
            "label_offset": self.scale(35),
            "pointer_width": self.scale(35),
            "pointer_height": self.scale(20),
            "zone_width": self.scale(8)
        }
    
    def menu_dimensions(self):
        """
        Get standardized menu dimensions.
        
        Returns:
            dict: Dictionary with menu dimensions
        """
        return {
            "max_visible_items": 4,  # Fixed for small screen
            "item_height": self.scale(25),
            "item_spacing": self.scale(15),
            "arrow_size": self.scale(16),
            "button_width": self.scale(300),
            "button_height": self.scale(25)
        }
    
    def get_responsive_breakpoint(self):
        """
        Get current responsive breakpoint based on screen size.
        
        Returns:
            str: "small", "medium", or "large"
        """
        # Use config breakpoints if available
        if self.config:
            small_bp = getattr(self.config, 'UI_BREAKPOINT_SMALL', 320)
            medium_bp = getattr(self.config, 'UI_BREAKPOINT_MEDIUM', 800)
            
            if self.screen_width <= small_bp:
                return "small"
            elif self.screen_width <= medium_bp:
                return "medium"
            else:
                return "large"
        else:
            # Fallback breakpoints
            if self.screen_width <= 320:
                return "small"
            elif self.screen_width <= 800:
                return "medium"
            else:
                return "large"
    
    def is_small_screen(self):
        """
        Check if current screen is considered small (Pi-sized).
        
        Returns:
            bool: True if screen is small (<=400px wide)
        """
        return self.screen_width <= 400
    
    def debug_info(self):
        """
        Get debug information about current scaling.
        
        Returns:
            dict: Debug information
        """
        return {
            "screen_size": f"{self.screen_width}x{self.screen_height}",
            "scale_factor": round(self.scale_factor, 2),
            "breakpoint": self.get_responsive_breakpoint(),
            "is_small_screen": self.is_small_screen(),
            "sample_margin": self.margin("medium"),
            "sample_padding": self.padding("medium"),
            "header_height": self.header_height()
        } 