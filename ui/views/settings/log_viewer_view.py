# --- ui/views/settings/log_viewer_view.py ---
# Handles rendering of the log viewer screen

import pygame
import logging
from ui.components.text.text_display import render_footer
import config as app_config

logger = logging.getLogger(__name__)

def draw_log_viewer_view(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the log viewer screen content.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
        ui_scaler (UIScaler, optional): UI scaling system for responsive design
    """
    screen.fill(config_module.Theme.BACKGROUND)
    
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Get or create log viewer
    if not hasattr(app_state, 'log_viewer'):
        from ui.components.log import LogViewer
        app_state.log_viewer = LogViewer()
    
    # Get scroll index
    scroll_index = getattr(app_state, 'log_viewer_scroll_index', 0)
    
    # Get log lines to display
    log_lines = app_state.log_viewer.get_display_lines(scroll_index)
    
    # Responsive sizing
    if screen_width <= 400:  # Small screen (Pi)
        title_font = fonts['small']
        content_font = fonts['tiny']
        line_height = 16  # Increased spacing
        start_y = 30
        margin = 8
        max_chars_per_line = 30  # Reduced for better fit
        max_lines = min(8, (screen_height - start_y - 40) // line_height)
    else:  # Large screen (Windows)
        title_font = fonts['medium']
        content_font = fonts['small']
        line_height = 20  # Increased spacing
        start_y = 50
        margin = 15
        max_chars_per_line = 60  # Reduced for better fit
        max_lines = min(15, (screen_height - start_y - 50) // line_height)
    
    # Title
    title_text = "Application Logs"
    title_surface = title_font.render(title_text, True, config_module.Theme.FOREGROUND)
    title_x = (screen_width - title_surface.get_width()) // 2
    screen.blit(title_surface, (title_x, 10))
    
    # Draw log lines with text wrapping
    y_offset = start_y
    lines_drawn = 0
    
    for line in log_lines:
        if lines_drawn >= max_lines:
            break
            
        # Color code by log level
        if "ERROR" in line or "CRITICAL" in line:
            color = config_module.Theme.ALERT
        elif "WARNING" in line:
            color = config_module.Theme.WARNING
        elif "INFO" in line:
            color = config_module.Theme.ACCENT
        else:
            color = config_module.Theme.FOREGROUND
        
        # Simple text wrapping - split by character count
        if len(line) <= max_chars_per_line:
            # Line fits, display as is
            if lines_drawn >= max_lines:
                break
            line_surface = content_font.render(line, True, color)
            screen.blit(line_surface, (margin, y_offset))
            y_offset += line_height
            lines_drawn += 1
        else:
            # Line is too long, split it
            words = line.split(' ')
            current_line = ""
            
            for word in words:
                test_line = current_line + (" " if current_line else "") + word
                
                if len(test_line) <= max_chars_per_line:
                    current_line = test_line
                else:
                    # Current line is full, display it
                    if current_line and lines_drawn < max_lines:
                        line_surface = content_font.render(current_line, True, color)
                        screen.blit(line_surface, (margin, y_offset))
                        y_offset += line_height
                        lines_drawn += 1
                    
                    # Start new line with current word
                    if len(word) <= max_chars_per_line:
                        current_line = word
                    else:
                        # Word is too long, break it
                        while len(word) > max_chars_per_line:
                            if lines_drawn >= max_lines:
                                break
                            chunk = word[:max_chars_per_line-3] + "..."
                            line_surface = content_font.render(chunk, True, color)
                            screen.blit(line_surface, (margin, y_offset))
                            y_offset += line_height
                            lines_drawn += 1
                            word = word[max_chars_per_line-3:]
                        current_line = word if word else ""
            
            # Display the last line
            if current_line and lines_drawn < max_lines:
                line_surface = content_font.render(current_line, True, color)
                screen.blit(line_surface, (margin, y_offset))
                y_offset += line_height
                lines_drawn += 1
    
    # Scroll indicator
    if len(log_lines) > max_lines:
        scroll_text = f"Scroll: {scroll_index + 1}-{min(scroll_index + max_lines, len(log_lines))}"
        scroll_surface = content_font.render(scroll_text, True, config_module.Theme.WARNING)
        screen.blit(scroll_surface, (margin, screen_height - 25))
    
    # Footer
    footer_text = "A/D: Scroll | Back: Return"
    render_footer(screen, footer_text, fonts, config_module.Theme.FOREGROUND, screen_width, screen_height)

