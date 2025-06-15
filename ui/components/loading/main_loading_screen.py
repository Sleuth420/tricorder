import pygame
import logging
import time
import threading

import config
from data import sensors
from utils.loc import count_python_lines

logger = logging.getLogger(__name__)

def draw_loading_screen(screen, fonts, logo_splash, logo_rect, progress, current_lines, total_lines, stage_text, ui_scaler=None):
    """
    Draw the loading screen with splash logo, progress bar, and line count using responsive design.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        fonts (dict): Dictionary of loaded fonts
        logo_splash (pygame.Surface): The logo surface
        logo_rect (pygame.Rect): Rectangle for logo positioning
        progress (float): Progress value from 0.0 to 1.0
        current_lines (int): Current line count
        total_lines (int): Total line count
        stage_text (str): Current stage description
        ui_scaler (UIScaler, optional): UI scaling system for responsive design
    """
    screen.fill(config.Theme.BACKGROUND)
    
    # Draw the splash logo
    screen.blit(logo_splash, logo_rect)
    
    # Calculate available space below logo for balanced layout
    available_space_below_logo = screen.get_height() - logo_rect.bottom
    
    # Use UIScaler for responsive dimensions if available
    if ui_scaler:
        bar_width = int(screen.get_width() * 0.6)
        bar_height = max(8, screen.get_height() // 30)  # ~3.3% of screen height, minimum 8px
        
        # Improved spacing calculations for better balance
        spacing_after_logo = ui_scaler.margin("large")  # Space between logo and progress bar
        progress_spacing = ui_scaler.margin("large")    # Space between bar and percentage
        stage_spacing = ui_scaler.margin("large")       # Space between percentage and stage
        lines_spacing = ui_scaler.margin("large")       # Space between stage and line count
        bottom_margin = ui_scaler.margin("xlarge")      # Bottom margin to balance top
    else:
        # Fallback to improved proportional calculations
        bar_width = int(screen.get_width() * 0.6)
        bar_height = max(8, screen.get_height() // 30)
        
        # Improved spacing for better visual balance
        spacing_after_logo = max(30, screen.get_height() // 20)  # ~5% of screen height
        progress_spacing = max(25, screen.get_height() // 24)    # ~4% of screen height
        stage_spacing = max(25, screen.get_height() // 24)       # ~4% of screen height  
        lines_spacing = max(20, screen.get_height() // 30)       # ~3% of screen height
        bottom_margin = max(40, screen.get_height() // 15)       # ~7% of screen height
    
    # Calculate positions for all elements
    bar_x = (screen.get_width() - bar_width) // 2
    bar_y = logo_rect.bottom + spacing_after_logo
    
    # Get font for text measurements
    try:
        progress_font = fonts.get('medium', pygame.font.Font(None, config.FONT_SIZE_MEDIUM))
    except:
        progress_font = pygame.font.Font(None, config.FONT_SIZE_MEDIUM)
    
    # Pre-calculate text elements to determine total height needed
    progress_text = f"{int(progress * 100)}%"
    progress_surface = progress_font.render(progress_text, True, config.Theme.FOREGROUND)
    
    stage_surface = progress_font.render(stage_text, True, config.Theme.FOREGROUND)
    
    lines_surface = None
    if total_lines > 0:
        lines_text = f"Python Lines: {current_lines:,} / {total_lines:,}"
        lines_surface = progress_font.render(lines_text, True, config.Theme.ACCENT)
    
    # Calculate total content height to check if it fits well
    content_height = (bar_height + progress_spacing + progress_surface.get_height() + 
                     stage_spacing + stage_surface.get_height())
    if lines_surface:
        content_height += lines_spacing + lines_surface.get_height()
    
    # Adjust spacing if content would extend too close to bottom
    remaining_space = screen.get_height() - (bar_y + content_height)
    if remaining_space < bottom_margin:
        # Reduce spacing proportionally to fit better
        scale_factor = max(0.7, (available_space_below_logo - bottom_margin) / content_height)
        progress_spacing = int(progress_spacing * scale_factor)
        stage_spacing = int(stage_spacing * scale_factor)
        lines_spacing = int(lines_spacing * scale_factor)
    
    # Debug logging for loading screen layout - only log once at start
    if ui_scaler and ui_scaler.debug_mode and progress <= 0.01:  # Only log at very beginning
        total_height = bar_y + content_height
        bottom_space = screen.get_height() - total_height
        logger.info(f"🎨 LoadingScreen: screen={screen.get_width()}x{screen.get_height()}, logo_rect={logo_rect}")
        logger.info(f"🎨 LoadingScreen: bar={bar_width}x{bar_height}px at ({bar_x}, {bar_y}), content_height={content_height}px, bottom_space={bottom_space}px")

    # Draw loading bar background
    bar_bg_rect = pygame.Rect(bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4)
    pygame.draw.rect(screen, config.Theme.FOREGROUND, bar_bg_rect)
    pygame.draw.rect(screen, config.Theme.BACKGROUND, pygame.Rect(bar_x, bar_y, bar_width, bar_height))
    
    # Draw loading bar fill
    fill_width = int(bar_width * progress)
    if fill_width > 0:
        fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
        pygame.draw.rect(screen, config.Theme.ACCENT, fill_rect)
    
    # Draw progress percentage
    progress_rect = progress_surface.get_rect(center=(screen.get_width() // 2, bar_y + bar_height + progress_spacing))
    screen.blit(progress_surface, progress_rect)
    
    # Draw current stage text
    stage_rect = stage_surface.get_rect(center=(screen.get_width() // 2, progress_rect.bottom + stage_spacing))
    screen.blit(stage_surface, stage_rect)
    
    # Draw line count if available
    if lines_surface:
        lines_rect = lines_surface.get_rect(center=(screen.get_width() // 2, stage_rect.bottom + lines_spacing))
        screen.blit(lines_surface, lines_rect)
    
    pygame.display.flip()

class LoadingProgress:
    """Thread-safe loading progress tracker."""
    def __init__(self):
        self.current_lines = 0
        self.total_lines = 0
        self.stage = "Initializing..."
        self.complete = False
        self.lock = threading.Lock()
    
    def update(self, current_lines=None, total_lines=None, stage=None, complete=None):
        with self.lock:
            if current_lines is not None:
                self.current_lines = current_lines
            if total_lines is not None:
                self.total_lines = total_lines
            if stage is not None:
                self.stage = stage
            if complete is not None:
                self.complete = complete
    
    def get_status(self):
        with self.lock:
            return self.current_lines, self.total_lines, self.stage, self.complete

def loading_worker(progress_tracker):
    """Background worker that performs the actual loading tasks."""
    try:
        # Stage 1: Count Python lines
        progress_tracker.update(stage="Counting Python files...")
        time.sleep(0.5)  # Small delay to show the stage
        
        total_lines, python_files = count_python_lines()
        progress_tracker.update(total_lines=total_lines, current_lines=total_lines)
        
        # Stage 2: Initialize sensors (if not already done)
        progress_tracker.update(stage="Initializing sensors...")
        time.sleep(0.5)
        
        # Stage 3: Preparing system
        progress_tracker.update(stage="Preparing system...")
        time.sleep(0.5)
        
        # Stage 4: Loading complete
        progress_tracker.update(stage="Loading complete! Scanning the Galaxy...", complete=True)
        
    except Exception as e:
        logger.error(f"Error in loading worker: {e}", exc_info=True)
        progress_tracker.update(stage="Loading completed with errors", complete=True) 