import pygame
import logging
import time
import threading

import config
from data import sensors
from utils.loc import count_python_lines

logger = logging.getLogger(__name__)

def draw_loading_screen(screen, fonts, logo_splash, logo_rect, progress, current_lines, total_lines, stage_text):
    """Draw the loading screen with splash logo, progress bar, and line count."""
    screen.fill(config.Theme.BACKGROUND)
    
    # Draw the splash logo
    screen.blit(logo_splash, logo_rect)
    
    # Loading bar dimensions
    bar_width = int(screen.get_width() * 0.6)
    bar_height = 20
    bar_x = (screen.get_width() - bar_width) // 2
    bar_y = logo_rect.bottom + 35  # Increased from 30 to 35
    
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
    try:
        progress_font = fonts.get('medium', pygame.font.Font(None, config.FONT_SIZE_MEDIUM))
    except:
        progress_font = pygame.font.Font(None, config.FONT_SIZE_MEDIUM)
    
    progress_text = f"{int(progress * 100)}%"
    progress_surface = progress_font.render(progress_text, True, config.Theme.FOREGROUND)
    progress_rect = progress_surface.get_rect(center=(screen.get_width() // 2, bar_y + bar_height + 25))  # Increased from 20 to 25
    screen.blit(progress_surface, progress_rect)
    
    # Draw current stage text
    stage_surface = progress_font.render(stage_text, True, config.Theme.FOREGROUND)
    stage_rect = stage_surface.get_rect(center=(screen.get_width() // 2, progress_rect.bottom + 18))  # Increased from 15 to 18
    screen.blit(stage_surface, stage_rect)
    
    # Draw line count if available
    if total_lines > 0:
        lines_text = f"Python Lines: {current_lines:,} / {total_lines:,}"
        lines_surface = progress_font.render(lines_text, True, config.Theme.ACCENT)
        lines_rect = lines_surface.get_rect(center=(screen.get_width() // 2, stage_rect.bottom + 15))  # Increased from 10 to 15
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