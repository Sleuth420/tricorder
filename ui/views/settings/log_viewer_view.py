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
    if ui_scaler:
        screen_width = ui_scaler.screen_width
        screen_height = ui_scaler.screen_height
    else:
        screen_width = screen.get_width()
        screen_height = screen.get_height()
    margin_sm = ui_scaler.margin("small") if ui_scaler else 8
    margin_md = ui_scaler.margin("medium") if ui_scaler else 15
    # Get or create log viewer
    if not hasattr(app_state, 'log_viewer'):
        from ui.components.log import LogViewer
        app_state.log_viewer = LogViewer()
    
    # Get scroll index
    scroll_index = getattr(app_state, 'log_viewer_scroll_index', 0)
    
    # Get log lines to display
    log_lines = app_state.log_viewer.get_display_lines(scroll_index)
    
    footer_space = ui_scaler.scale(40) if ui_scaler else 40
    is_small = screen_width <= 400 if not ui_scaler else ui_scaler.is_small_screen()
    if is_small:
        title_font = fonts['small']
        content_font = fonts['tiny']
        line_height = ui_scaler.scale(16) if ui_scaler else 16
        start_y = ui_scaler.margin("large") if ui_scaler else 30
        margin = margin_sm
        max_chars_per_line = 30
        max_lines = max(1, min(8, (screen_height - start_y - footer_space) // line_height))
    else:
        title_font = fonts['medium']
        content_font = fonts['small']
        line_height = ui_scaler.scale(20) if ui_scaler else 20
        start_y = ui_scaler.scale(50) if ui_scaler else 50
        margin = margin_md
        max_chars_per_line = 60
        max_lines = max(1, min(15, (screen_height - start_y - footer_space) // line_height))
    title_text = "Application Logs"
    title_surface = title_font.render(title_text, True, config_module.Theme.FOREGROUND)
    title_x = (screen_width - title_surface.get_width()) // 2
    title_top = ui_scaler.margin("small") if ui_scaler else 10
    screen.blit(title_surface, (title_x, title_top))
    
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
        scroll_bottom = screen_height - (ui_scaler.scale(25) if ui_scaler else 25)
        screen.blit(scroll_surface, (margin, scroll_bottom))
    labels = config_module.get_control_labels()
    footer_text = f"{labels['prev']}/{labels['next']}: Scroll | {labels['back']}: Return"
    render_footer(screen, footer_text, fonts, config_module.Theme.FOREGROUND, screen_width, screen_height, ui_scaler=ui_scaler)

