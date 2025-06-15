# --- models/loading_manager.py ---
# Manages loading operations with progress tracking

import logging

logger = logging.getLogger(__name__)

class LoadingManager:
    """Manages loading operations with progress tracking."""
    
    def __init__(self, config_module, screen_width, screen_height):
        """Initialize the loading manager."""
        self.config = config_module
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ui_scaler = None
        
        # Loading state
        self.loading_screen = None
        self.loading_target_state = None
        self.loading_operation = None
        self.pending_model_load = None
        
        logger.info("Loading manager initialized")
    
    # UIScaler removed - UI concerns handled by display_manager.py
    
    def start_loading_operation(self, target_state, operation_name="Loading", total_steps=3):
        """
        Start a loading operation with progress tracking.
        
        Args:
            target_state (str): State to transition to after loading
            operation_name (str): Name of the operation
            total_steps (int): Total number of loading steps
            
        Returns:
            LoadingOperation: The loading operation context manager
        """
        from ui.components.loading_screen import LoadingScreen, LoadingOperation
        
        # Create loading screen if needed
        if not self.loading_screen:
            self.loading_screen = LoadingScreen(
                self.screen_width, 
                self.screen_height, 
                self.config,
                self.ui_scaler
            )
        
        # Set up loading state
        self.loading_target_state = target_state
        self.loading_operation = LoadingOperation(self.loading_screen, total_steps, operation_name)
        
        logger.info(f"Started loading operation: {operation_name} -> {target_state}")
        return self.loading_operation
    
    def complete_loading_operation(self):
        """Complete the current loading operation and return target state."""
        if self.loading_target_state:
            target = self.loading_target_state
            self.loading_target_state = None
            self.loading_operation = None
            logger.info(f"Loading operation completed, target: {target}")
            return target
        else:
            logger.warning("No loading target state set")
            return None
    
    def get_loading_screen(self):
        """Get the current loading screen instance."""
        return self.loading_screen
    
    def is_loading(self):
        """Check if currently in loading state."""
        return self.loading_target_state is not None
    
    def set_pending_model_load(self, schematics_model_key, loading_operation):
        """Set a pending model load operation."""
        self.pending_model_load = {
            'schematics_model_key': schematics_model_key,
            'loading_operation': loading_operation
        }
    
    def get_pending_model_load(self):
        """Get and clear the pending model load."""
        pending = self.pending_model_load
        self.pending_model_load = None
        return pending
    
    def has_pending_model_load(self):
        """Check if there's a pending model load."""
        return self.pending_model_load is not None 