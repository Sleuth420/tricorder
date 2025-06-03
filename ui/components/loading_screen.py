# --- ui/components/loading_screen.py ---
# Loading screen component for showing progress during long operations

import pygame
import logging
import time
import math

logger = logging.getLogger(__name__)

class LoadingScreen:
    """A loading screen component with progress bar and status text."""
    
    def __init__(self, screen_width, screen_height, config_module):
        """Initialize the loading screen."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.config = config_module
        
        # Animation state
        self.start_time = time.time()
        self.progress = 0.0  # 0.0 to 1.0
        self.status_text = "Loading..."
        self.detail_text = ""
        
        # Visual parameters optimized for small screens
        # Make progress bar much larger and use more screen space
        if screen_width <= 320:  # Small screen optimizations
            self.bar_width = screen_width - 40  # Use most of the width (was screen_width - 60)
            self.bar_height = 45  # Much taller bar for visibility (was 30)
            self.bar_x = 20  # Smaller side margins
            self.bar_y = (screen_height // 2) + 20  # Position closer to center
        else:  # Larger screens
            self.bar_width = min(300, screen_width - 80)  # Wider than before
            self.bar_height = 35  # Taller than original
            self.bar_x = (screen_width - self.bar_width) // 2
            self.bar_y = (screen_height // 2) + 40
        
        logger.info("Loading screen initialized")
    
    def update_progress(self, progress: float, status: str = None, detail: str = None):
        """
        Update the loading progress and status.
        
        Args:
            progress (float): Progress from 0.0 to 1.0
            status (str): Main status text
            detail (str): Detailed status text
        """
        self.progress = max(0.0, min(1.0, progress))
        if status:
            self.status_text = status
        if detail:
            self.detail_text = detail
    
    def draw(self, screen, fonts):
        """
        Draw the loading screen.
        
        Args:
            screen (pygame.Surface): Surface to draw on
            fonts (dict): Dictionary of loaded fonts
        """
        # Clear screen
        screen.fill(self.config.Theme.BACKGROUND)
        
        # Draw title - bigger for small screens
        title_font = fonts.get('large', fonts.get('medium'))
        title_text = "TRICORDER"
        title_surface = title_font.render(title_text, True, self.config.Theme.ACCENT)
        # Position title higher for small screens to make room for larger progress bar
        title_y = self.screen_height // 2 - 80 if self.screen_width <= 320 else self.screen_height // 2 - 60
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, title_y))
        screen.blit(title_surface, title_rect)
        
        # Skip spinner - progress bar is enough for small screens
        # Focus on one clear progress indicator instead of both
        
        # Draw status text - bigger font and closer positioning
        status_font = fonts.get('large' if self.screen_width <= 320 else 'medium', fonts.get('medium'))  # Bigger on small screens
        status_surface = status_font.render(self.status_text, True, self.config.Theme.FOREGROUND)
        status_rect = status_surface.get_rect(center=(self.screen_width // 2, self.bar_y - 60))  # More space for larger bar
        screen.blit(status_surface, status_rect)
        
        # Draw progress bar - larger and more prominent
        self._draw_progress_bar(screen)
        
        # Show detail text if provided and short enough for small screens
        if self.detail_text and len(self.detail_text) <= 25:  # Keep it short for small screens
            detail_font = fonts.get('small', fonts.get('medium'))
            detail_surface = detail_font.render(self.detail_text, True, self.config.Theme.FOREGROUND)
            detail_rect = detail_surface.get_rect(center=(self.screen_width // 2, self.bar_y + self.bar_height + 25))
            screen.blit(detail_surface, detail_rect)
    
    def _draw_progress_bar(self, screen):
        """Draw the progress bar - optimized for small screens."""
        # Draw background bar with more prominent styling
        bar_rect = pygame.Rect(self.bar_x, self.bar_y, self.bar_width, self.bar_height)
        
        # Draw background with darker color for better contrast
        pygame.draw.rect(screen, self.config.Theme.GRAPH_BORDER, bar_rect)
        
        # Draw progress fill
        if self.progress > 0:
            fill_width = int(self.bar_width * self.progress)
            fill_rect = pygame.Rect(self.bar_x, self.bar_y, fill_width, self.bar_height)
            pygame.draw.rect(screen, self.config.Theme.ACCENT, fill_rect)
        
        # Draw border - thicker for better visibility
        pygame.draw.rect(screen, self.config.Theme.FOREGROUND, bar_rect, 3)  # Thicker border (was 2)
        
        # Draw percentage text - bigger font for small screens
        if hasattr(self, 'config') and hasattr(self.config, 'Theme'):
            percent_text = f"{int(self.progress * 100)}%"
            # Use much larger font for percentage on small screens
            try:
                if self.screen_width <= 320:
                    font_size = 28  # Much bigger for small screens
                else:
                    font_size = 20  # Bigger than original 16
                font = pygame.font.Font(None, font_size)
                percent_surface = font.render(percent_text, True, self.config.Theme.FOREGROUND)
                
                # Position percentage text inside the bar
                percent_rect = percent_surface.get_rect(center=(self.bar_x + self.bar_width // 2, self.bar_y + self.bar_height // 2))
                screen.blit(percent_surface, percent_rect)
            except:
                pass  # Skip percentage display if font fails

class LoadingOperation:
    """Context manager for loading operations with progress tracking."""
    
    def __init__(self, loading_screen, total_steps: int, operation_name: str = "Loading"):
        """
        Initialize loading operation.
        
        Args:
            loading_screen (LoadingScreen): The loading screen to update
            total_steps (int): Total number of steps in the operation
            operation_name (str): Name of the operation
        """
        self.loading_screen = loading_screen
        self.total_steps = total_steps
        self.current_step = 0
        self.operation_name = operation_name
        
    def __enter__(self):
        """Start the loading operation."""
        self.current_step = 0
        self.loading_screen.update_progress(0.0, self.operation_name)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Complete the loading operation."""
        self.loading_screen.update_progress(1.0, "Complete!")
    
    def step(self, description: str = None):
        """Advance to the next step."""
        self.current_step += 1
        progress = self.current_step / self.total_steps
        status = f"{self.operation_name} ({self.current_step}/{self.total_steps})"
        self.loading_screen.update_progress(progress, status, description)
    
    def set_detail(self, detail: str):
        """Update the detail text without advancing step."""
        self.loading_screen.update_progress(
            self.current_step / self.total_steps,
            f"{self.operation_name} ({self.current_step}/{self.total_steps})",
            detail
        ) 