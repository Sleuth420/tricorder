"""
Base view class that all views must extend.
"""

import logging

logger = logging.getLogger(__name__)

class BaseView:
    """
    Base view class that all views must extend.
    
    This abstract class defines the interface that all views must implement.
    It also provides common functionality for all views.
    """
    
    def __init__(self, app, view_args=None):
        """
        Initialize the view.
        
        Args:
            app (App): The application instance
            view_args (dict, optional): Additional arguments for the view
        """
        self.app = app
        self.view_args = view_args or {}
        
        # Get common objects for convenience
        self.config = app.config
        self.event_bus = app.event_bus
        self.state_machine = app.state_machine
        self.sensor_service = app.sensor_service
        self.settings_service = app.settings_service
        self.reading_history = app.reading_history
        
        # Initialize view
        self._initialize()
        
    def _initialize(self):
        """
        Initialize the view. Can be overridden by subclasses.
        """
        pass
        
    def handle_input(self, events):
        """
        Handle user input for this view.
        
        Args:
            events (list): List of pygame events
            
        Returns:
            bool: True if input was handled
        """
        # This should be implemented by subclasses
        raise NotImplementedError("Subclasses must implement handle_input")
        
    def render(self, screen):
        """
        Render the view on the screen.
        
        Args:
            screen (pygame.Surface): The screen to render on
            
        Returns:
            bool: True if rendering was successful
        """
        # This should be implemented by subclasses
        raise NotImplementedError("Subclasses must implement render")
        
    def update(self, delta_time):
        """
        Update the view's state.
        
        Args:
            delta_time (float): Time since last update in seconds
            
        Returns:
            bool: True if the update was successful
        """
        # Default implementation does nothing
        return True 