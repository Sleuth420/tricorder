# --- ui/components/loading_screen.py ---
# Loading screen component for showing progress during long operations

import pygame
import logging
import time
import math

logger = logging.getLogger(__name__)

class LoadingScreen:
    """A loading screen component with progress bar and status text, optimized for 320x240 displays."""
    
    def __init__(self, screen_width, screen_height, config_module, ui_scaler=None):
        """Initialize the loading screen."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.config = config_module
        self.ui_scaler = ui_scaler
        
        # Animation state
        self.start_time = time.time()
        self.progress = 0.0  # 0.0 to 1.0
        self.status_text = "Loading... Please do not exit..."
        self.detail_text = ""
        
        # Calculate responsive layout
        self._calculate_layout()
        
        logger.info(f"Loading screen initialized for {screen_width}x{screen_height}")

    def set_ui_scaler(self, ui_scaler):
        """Set the UI scaler for responsive design."""
        self.ui_scaler = ui_scaler
        self._calculate_layout()
        if ui_scaler and ui_scaler.debug_mode:
            logger.info(f"🎨 LoadingScreen: UIScaler set, scale_factor={ui_scaler.scale_factor:.2f}")

    def _calculate_layout(self):
        """Calculate responsive layout based on screen size and UIScaler; respect safe area when enabled."""
        if self.ui_scaler:
            if self.ui_scaler.safe_area_enabled:
                safe_rect = self.ui_scaler.get_safe_area_rect()
                self.content_center_x = safe_rect.centerx
                bar_margin = self.ui_scaler.margin("medium")
                self.bar_width = min(self.screen_width - bar_margin * 2, safe_rect.width - bar_margin * 2)
                self.bar_x = self.content_center_x - self.bar_width // 2
                self.title_y = safe_rect.top + self.ui_scaler.scale(30)
                self.status_y = safe_rect.top + self.ui_scaler.scale(70)
                self.bar_y = safe_rect.top + self.ui_scaler.scale(110)
            else:
                self.content_center_x = self.screen_width // 2
                bar_margin = self.ui_scaler.margin("medium")
                self.bar_width = self.screen_width - bar_margin * 2
                self.bar_x = bar_margin
                self.title_y = self.ui_scaler.scale(30)
                self.status_y = self.ui_scaler.scale(70)
                self.bar_y = self.ui_scaler.scale(110)
            
            self.bar_height = max(8, self.ui_scaler.scale(14))
            
            # Percentage text clearly below the bar (medium gap so it doesn't overlap)
            self.percent_y = self.bar_y + self.bar_height + self.ui_scaler.margin("medium") + self.ui_scaler.scale(4)
            self.detail_y = self.percent_y + self.ui_scaler.scale(getattr(self.config, 'FONT_SIZE_MEDIUM', 24)) + self.ui_scaler.margin("medium")
            
            # Responsive font sizes from config (single source of truth)
            self.title_font_size = self.ui_scaler.scale(getattr(self.config, 'FONT_SIZE_LARGE', 30))
            self.status_font_size = self.ui_scaler.scale(getattr(self.config, 'FONT_SIZE_MEDIUM', 24))
            self.percent_font_size = self.ui_scaler.scale(getattr(self.config, 'FONT_SIZE_MEDIUM', 24))
            self.detail_font_size = self.ui_scaler.scale(getattr(self.config, 'FONT_SIZE_SMALL', 20))
            
            # Debug logging for loading screen layout
            if self.ui_scaler.debug_mode:
                logger.info(f"🎨 LoadingScreen: screen={self.screen_width}x{self.screen_height}, bar={self.bar_width}x{self.bar_height}px, title_font={self.title_font_size}px")
        
        else:
            self.content_center_x = self.screen_width // 2
            # Fallback when ui_scaler not set: same base as UIScaler (320x240), scale proportionally
            scale = min(self.screen_width / 320, self.screen_height / 240)
            margin = max(4, int(8 * scale))
            self.title_y = max(20, int(30 * scale))
            self.status_y = max(40, int(70 * scale))
            self.bar_width = self.screen_width - margin * 2
            self.bar_height = max(8, int(14 * scale))
            self.bar_x = margin
            self.bar_y = max(60, int(110 * scale))
            self.percent_y = self.bar_y + self.bar_height + max(10, int(14 * scale))  # Clear gap below bar
            self.detail_y = self.percent_y + max(12, int(24 * scale)) + margin
            large = getattr(self.config, 'FONT_SIZE_LARGE', 30)
            medium = getattr(self.config, 'FONT_SIZE_MEDIUM', 24)
            small = getattr(self.config, 'FONT_SIZE_SMALL', 20)
            self.title_font_size = max(12, int(large * scale))
            self.status_font_size = max(10, int(medium * scale))
            self.percent_font_size = max(12, int(medium * scale))
            self.detail_font_size = max(10, int(small * scale))
    
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
        Draw the loading screen with responsive design.
        
        Args:
            screen (pygame.Surface): Surface to draw on
            fonts (dict): Dictionary of loaded fonts
        """
        # Clear screen
        screen.fill(self.config.Theme.BACKGROUND)
        content_center_x = getattr(self, 'content_center_x', self.screen_width // 2)
        
        # Draw title with responsive font size
        try:
            title_font = pygame.font.Font(None, self.title_font_size)
        except:
            title_font = fonts.get('large', fonts.get('medium'))
        
        title_text = "TRICORDER"
        title_surface = title_font.render(title_text, True, self.config.Theme.ACCENT)
        title_rect = title_surface.get_rect(center=(content_center_x, self.title_y))
        screen.blit(title_surface, title_rect)
        
        # Draw status text with responsive font size
        try:
            status_font = pygame.font.Font(None, self.status_font_size)
        except:
            status_font = fonts.get('medium', fonts.get('small'))
        
        # Truncate status text if too long for small screens
        display_status = self.status_text
        max_status_chars = 20 if self.screen_width <= 320 else 40
        if len(display_status) > max_status_chars:
            display_status = display_status[:max_status_chars-3] + "..."
        
        status_surface = status_font.render(display_status, True, self.config.Theme.FOREGROUND)
        status_rect = status_surface.get_rect(center=(content_center_x, self.status_y))
        screen.blit(status_surface, status_rect)
        
        # Draw progress bar (no text inside the bar)
        self._draw_progress_bar(screen)
        
        # Draw percentage below the bar so it's not on the yellow fill
        try:
            percent_font = pygame.font.Font(None, self.percent_font_size)
            percent_text = f"{int(self.progress * 100)}%"
            percent_surface = percent_font.render(percent_text, True, self.config.Theme.FOREGROUND)
            percent_y = getattr(self, 'percent_y', self.bar_y + self.bar_height + 8)
            percent_rect = percent_surface.get_rect(center=(content_center_x, percent_y))
            screen.blit(percent_surface, percent_rect)
        except Exception:
            pass
        
        # Draw detail text if provided and screen has room
        if self.detail_text and self.detail_y < self.screen_height - 30:
            try:
                detail_font = pygame.font.Font(None, self.detail_font_size)
            except:
                detail_font = fonts.get('small', fonts.get('medium'))
            
            # Truncate detail text for small screens
            display_detail = self.detail_text
            max_detail_chars = 25 if self.screen_width <= 320 else 50
            if len(display_detail) > max_detail_chars:
                display_detail = display_detail[:max_detail_chars-3] + "..."
            
            detail_surface = detail_font.render(display_detail, True, self.config.Theme.FOREGROUND)
            detail_rect = detail_surface.get_rect(center=(content_center_x, self.detail_y))
            screen.blit(detail_surface, detail_rect)
    
    def _draw_progress_bar(self, screen):
        """Draw the progress bar with responsive sizing (matches main loading screen style)."""
        # Outer border (green/foreground)
        border = 2
        if self.ui_scaler:
            border = max(1, self.ui_scaler.scale(2))
        bar_bg_rect = pygame.Rect(self.bar_x - border, self.bar_y - border,
                                  self.bar_width + border * 2, self.bar_height + border * 2)
        pygame.draw.rect(screen, self.config.Theme.FOREGROUND, bar_bg_rect)
        # Inner background (dark)
        bar_rect = pygame.Rect(self.bar_x, self.bar_y, self.bar_width, self.bar_height)
        pygame.draw.rect(screen, (20, 20, 20), bar_rect)
        # Progress fill
        if self.progress > 0:
            fill_width = int(self.bar_width * self.progress)
            fill_rect = pygame.Rect(self.bar_x, self.bar_y, fill_width, self.bar_height)
            pygame.draw.rect(screen, self.config.Theme.ACCENT, fill_rect)

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
    
    def update_status(self, status: str, detail: str = None):
        """Update the status text (method expected by wifi_manager)."""
        progress = self.current_step / self.total_steps if self.total_steps > 0 else 0.0
        self.loading_screen.update_progress(progress, status, detail)
    
    def complete(self):
        """Mark the operation as complete (method expected by wifi_manager)."""
        self.loading_screen.update_progress(1.0, "Complete!")
    
    def set_detail(self, detail: str):
        """Update the detail text without advancing step."""
        progress = self.current_step / self.total_steps if self.total_steps > 0 else 0.0
        current_status = f"{self.operation_name} ({self.current_step}/{self.total_steps})" if self.total_steps > 0 else self.operation_name
        self.loading_screen.update_progress(progress, current_status, detail) 