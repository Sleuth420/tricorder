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
        
        # Visual parameters
        self.bar_width = min(400, screen_width - 100)
        self.bar_height = 20
        self.bar_x = (screen_width - self.bar_width) // 2
        self.bar_y = (screen_height // 2) + 50
        
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
        
        # Draw title
        title_font = fonts.get('large', fonts.get('medium'))
        title_text = "TRICORDER"
        title_surface = title_font.render(title_text, True, self.config.Theme.ACCENT)
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 100))
        screen.blit(title_surface, title_rect)
        
        # Draw spinning animation
        self._draw_spinner(screen, title_rect.centerx, title_rect.bottom + 30)
        
        # Draw status text
        status_font = fonts.get('medium', fonts.get('small'))
        status_surface = status_font.render(self.status_text, True, self.config.Theme.FOREGROUND)
        status_rect = status_surface.get_rect(center=(self.screen_width // 2, self.bar_y - 40))
        screen.blit(status_surface, status_rect)
        
        # Draw detail text if provided
        if self.detail_text:
            detail_font = fonts.get('small', fonts.get('medium'))
            detail_surface = detail_font.render(self.detail_text, True, self.config.Theme.FOREGROUND)
            detail_rect = detail_surface.get_rect(center=(self.screen_width // 2, status_rect.bottom + 20))
            screen.blit(detail_surface, detail_rect)
        
        # Draw progress bar
        self._draw_progress_bar(screen)
        
        # Draw footer
        footer_font = fonts.get('small', fonts.get('medium'))
        footer_text = "Please wait..."
        footer_surface = footer_font.render(footer_text, True, self.config.Theme.FOREGROUND)
        footer_rect = footer_surface.get_rect(center=(self.screen_width // 2, self.bar_y + 60))
        screen.blit(footer_surface, footer_rect)
    
    def _draw_spinner(self, screen, center_x, center_y):
        """Draw a spinning loading indicator."""
        current_time = time.time()
        angle = (current_time - self.start_time) * 180  # Degrees per second
        
        radius = 15
        thickness = 3
        
        # Draw spinning arc
        arc_length = 120  # Degrees
        start_angle = angle % 360
        end_angle = (start_angle + arc_length) % 360
        
        # Convert to radians for drawing
        start_rad = math.radians(start_angle)
        end_rad = math.radians(end_angle)
        
        # Draw arc using multiple small lines
        steps = 20
        for i in range(steps):
            t = i / (steps - 1)
            current_angle = start_rad + (end_rad - start_rad) * t
            x = center_x + radius * math.cos(current_angle)
            y = center_y + radius * math.sin(current_angle)
            
            # Draw small circle at this position
            pygame.draw.circle(screen, self.config.Theme.ACCENT, (int(x), int(y)), thickness)
    
    def _draw_progress_bar(self, screen):
        """Draw the progress bar."""
        # Draw background bar
        bar_rect = pygame.Rect(self.bar_x, self.bar_y, self.bar_width, self.bar_height)
        pygame.draw.rect(screen, self.config.Theme.GRAPH_BORDER, bar_rect)
        pygame.draw.rect(screen, self.config.Theme.BACKGROUND, bar_rect)
        
        # Draw progress fill
        if self.progress > 0:
            fill_width = int(self.bar_width * self.progress)
            fill_rect = pygame.Rect(self.bar_x, self.bar_y, fill_width, self.bar_height)
            pygame.draw.rect(screen, self.config.Theme.ACCENT, fill_rect)
        
        # Draw border
        pygame.draw.rect(screen, self.config.Theme.FOREGROUND, bar_rect, 2)
        
        # Draw percentage text
        if hasattr(self, 'config') and hasattr(self.config, 'Theme'):
            percent_text = f"{int(self.progress * 100)}%"
            # Use a simple font for percentage
            try:
                font = pygame.font.Font(None, 16)
                percent_surface = font.render(percent_text, True, self.config.Theme.FOREGROUND)
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