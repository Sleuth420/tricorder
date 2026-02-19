import pygame
import logging
import time
import threading
import random
import math

import config
from data import sensors
from utils.loc import count_python_lines

logger = logging.getLogger(__name__)

def draw_tricorder_animations(screen, logo_rect, animation_time, progress, ui_scaler=None):
    """
    Draw subtle Star Trek tricorder-themed animations around the logo.
    
    Args:
        screen (pygame.Surface): The surface to draw on
        logo_rect (pygame.Rect): Rectangle of the logo for positioning
        animation_time (float): Time in seconds for animations
        progress (float): Loading progress (0.0 to 1.0)
        ui_scaler (UIScaler, optional): UI scaling system
    """
    # Calculate responsive sizing
    if ui_scaler:
        base_size = ui_scaler.scale(2)
        margin = ui_scaler.margin("medium")
    else:
        base_size = max(2, screen.get_height() // 120)  # Scale with screen size
        margin = max(15, screen.get_width() // 20)
    
    # Animation parameters
    pulse_speed = 2.0  # Pulses per second
    scan_speed = 1.5   # Scan cycles per second
    
    # Left side: Pulsing status indicators (like tricorder readouts)
    left_x = logo_rect.left - margin
    indicator_count = 4
    indicator_spacing = logo_rect.height // (indicator_count + 1)
    
    for i in range(indicator_count):
        y = logo_rect.top + indicator_spacing * (i + 1)
        
        # Staggered pulsing effect
        phase_offset = i * 0.3
        pulse_intensity = (1 + math.sin((animation_time * pulse_speed + phase_offset) * 2 * math.pi)) / 2
        
        # Color based on progress and pulse
        if progress > i * 0.25:  # Activate indicators as progress increases
            alpha = int(100 + 155 * pulse_intensity)
            color = (0, alpha, 0)  # Green pulse
        else:
            alpha = int(30 + 20 * pulse_intensity)
            color = (alpha, alpha, alpha)  # Dim grey pulse
        
        # Draw small rectangular indicator
        indicator_rect = pygame.Rect(left_x - base_size * 3, y - base_size, base_size * 6, base_size * 2)
        pygame.draw.rect(screen, color, indicator_rect)
        
        # Add a subtle border
        border_color = (min(255, color[1] + 50), min(255, color[1] + 50), min(255, color[1] + 50))
        pygame.draw.rect(screen, border_color, indicator_rect, 1)
    
    # Right side: Scanning beam effect (like tricorder sensor sweep)
    right_x = logo_rect.right + margin
    scan_height = logo_rect.height
    scan_width = base_size * 2
    
    # Vertical scanning beam that moves up and down
    scan_cycle = (animation_time * scan_speed) % 2.0  # 2-second cycle
    if scan_cycle < 1.0:
        # Moving down
        scan_progress_local = scan_cycle
    else:
        # Moving up
        scan_progress_local = 2.0 - scan_cycle
    
    scan_y = logo_rect.top + int(scan_height * scan_progress_local)
    
    # Draw scanning beam with gradient effect
    beam_length = base_size * 8
    for j in range(beam_length):
        beam_x = right_x + j
        # Fade out as we move away from the logo
        fade = max(0, 1.0 - (j / beam_length))
        intensity = int(255 * fade * (0.3 + 0.7 * progress))  # Brighter as loading progresses
        
        beam_color = (0, intensity, intensity // 2)  # Cyan-ish beam
        if intensity > 10:  # Only draw if visible
            pygame.draw.circle(screen, beam_color, (beam_x, scan_y), base_size)
    
    # Add subtle corner brackets (like tricorder display frame)
    bracket_size = base_size * 4
    bracket_thickness = max(1, base_size)
    bracket_color = (0, 100 + int(50 * progress), 50)  # Subtle green
    
    # Top-left bracket
    tl_x, tl_y = logo_rect.left - base_size * 2, logo_rect.top - base_size * 2
    pygame.draw.line(screen, bracket_color, (tl_x, tl_y), (tl_x + bracket_size, tl_y), bracket_thickness)
    pygame.draw.line(screen, bracket_color, (tl_x, tl_y), (tl_x, tl_y + bracket_size), bracket_thickness)
    
    # Top-right bracket
    tr_x, tr_y = logo_rect.right + base_size * 2, logo_rect.top - base_size * 2
    pygame.draw.line(screen, bracket_color, (tr_x, tr_y), (tr_x - bracket_size, tr_y), bracket_thickness)
    pygame.draw.line(screen, bracket_color, (tr_x, tr_y), (tr_x, tr_y + bracket_size), bracket_thickness)
    
    # Bottom-left bracket
    bl_x, bl_y = logo_rect.left - base_size * 2, logo_rect.bottom + base_size * 2
    pygame.draw.line(screen, bracket_color, (bl_x, bl_y), (bl_x + bracket_size, bl_y), bracket_thickness)
    pygame.draw.line(screen, bracket_color, (bl_x, bl_y), (bl_x, bl_y - bracket_size), bracket_thickness)
    
    # Bottom-right bracket
    br_x, br_y = logo_rect.right + base_size * 2, logo_rect.bottom + base_size * 2
    pygame.draw.line(screen, bracket_color, (br_x, br_y), (br_x - bracket_size, br_y), bracket_thickness)
    pygame.draw.line(screen, bracket_color, (br_x, br_y), (br_x, br_y - bracket_size), bracket_thickness)

def draw_loading_screen(screen, fonts, logo_splash, logo_rect, progress, current_lines, total_lines, stage_text, ui_scaler=None, scan_progress=0.0, animation_time=0.0):
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
        scan_progress (float): Progress of the scanning animation (0.0 to 1.0)
        animation_time (float): Time in seconds for animations
    """
    # Use UIScaler for all dimensions; respect safe area for curved bezel (before drawing so logo is centered)
    if ui_scaler:
        screen_w = ui_scaler.screen_width
        screen_h = ui_scaler.screen_height
        safe_rect = ui_scaler.get_safe_area_rect() if ui_scaler.safe_area_enabled else pygame.Rect(0, 0, screen_w, screen_h)
        center_x = safe_rect.centerx
        bar_width = min(ui_scaler.scale(192), safe_rect.width - ui_scaler.margin("medium") * 2)  # ~60% of base 320, within safe area
        bar_height = max(8, ui_scaler.scale(8))
        spacing_after_logo = ui_scaler.margin("large")
        progress_spacing = ui_scaler.margin("large")
        stage_spacing = ui_scaler.margin("large")
        lines_spacing = ui_scaler.margin("medium")  # Tighter under "matrices" so no blank gap
        bottom_margin = ui_scaler.margin("xlarge")
    else:
        screen_w = screen.get_width()
        screen_h = screen.get_height()
        safe_rect = pygame.Rect(0, 0, screen_w, screen_h)
        center_x = screen_w // 2
        bar_width = int(screen_w * 0.6)
        bar_height = max(8, screen_h // 30)
        spacing_after_logo = max(30, screen_h // 20)
        progress_spacing = max(25, screen_h // 24)
        stage_spacing = max(25, screen_h // 24)
        lines_spacing = max(8, screen_h // 40)  # Tighter under "matrices" so no blank gap
        bottom_margin = max(40, screen_h // 15)
    
    # Get font for text measurements (used for centering and drawing)
    try:
        progress_font = fonts.get('medium', pygame.font.Font(None, config.FONT_SIZE_MEDIUM))
    except Exception:
        progress_font = pygame.font.Font(None, config.FONT_SIZE_MEDIUM)
    
    # Pre-measure text to compute total content height (needed for vertical centering)
    progress_text = f"{int(progress * 100)}%"
    progress_surface = progress_font.render(progress_text, True, config.Theme.FOREGROUND)
    stage_surface = progress_font.render(stage_text, True, config.Theme.ACCENT)
    lines_surface = None
    if total_lines > 0:
        lines_text = f"Analyzing code matrices: {current_lines:,} / {total_lines:,}"
        lines_surface = progress_font.render(lines_text, True, config.Theme.FOREGROUND)
    
    content_below_logo = (bar_height + progress_spacing + progress_surface.get_height() +
                         stage_spacing + stage_surface.get_height())
    if lines_surface:
        content_below_logo += lines_spacing + lines_surface.get_height()
    total_content_height = logo_rect.height + spacing_after_logo + content_below_logo
    content_top = safe_rect.top + max(0, (safe_rect.height - total_content_height) // 2)
    logo_rect.midtop = (center_x, content_top)
    
    available_space_below_logo = (safe_rect.bottom if ui_scaler and ui_scaler.safe_area_enabled else screen_h) - logo_rect.bottom
    bar_x = center_x - bar_width // 2
    bar_y = logo_rect.bottom + spacing_after_logo
    
    content_height = content_below_logo
    bottom_ref = safe_rect.bottom if (ui_scaler and ui_scaler.safe_area_enabled) else screen_h
    # Adjust spacing if content would extend too close to bottom
    remaining_space = bottom_ref - (bar_y + content_height)
    if remaining_space < bottom_margin and content_height > 0:
        scale_factor = max(0.7, (available_space_below_logo - bottom_margin) / content_height)
        progress_spacing = int(progress_spacing * scale_factor)
        stage_spacing = int(stage_spacing * scale_factor)
        lines_spacing = int(lines_spacing * scale_factor)
        # Recompute actual content height and re-center so there's no black gap below matrices
        content_below_logo = (bar_height + progress_spacing + progress_surface.get_height() +
                             stage_spacing + stage_surface.get_height())
        if lines_surface:
            content_below_logo += lines_spacing + lines_surface.get_height()
        total_content_height = logo_rect.height + spacing_after_logo + content_below_logo
        content_top = safe_rect.top + max(0, (safe_rect.height - total_content_height) // 2)
        logo_rect.midtop = (center_x, content_top)
        bar_y = logo_rect.bottom + spacing_after_logo
        content_height = content_below_logo
    
    # Debug logging for loading screen layout - only log once at start
    if ui_scaler and ui_scaler.debug_mode and progress <= 0.01:
        total_height = bar_y + content_height
        bottom_space = screen_h - total_height
        logger.info(f"🎨 LoadingScreen: screen={screen_w}x{screen_h}, logo_rect={logo_rect}")
        logger.info(f"🎨 LoadingScreen: bar={bar_width}x{bar_height}px at ({bar_x}, {bar_y}), content_height={content_height}px, bottom_space={bottom_space}px")

    # Draw background, logo, and animations (after layout so logo is centered)
    screen.fill(config.Theme.BACKGROUND)
    screen.blit(logo_splash, logo_rect)
    draw_tricorder_animations(screen, logo_rect, animation_time, progress, ui_scaler)

    # Draw loading bar with improved design
    # Outer border (green)
    bar_bg_rect = pygame.Rect(bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4)
    pygame.draw.rect(screen, config.Theme.FOREGROUND, bar_bg_rect)
    
    # Inner background (dark grey instead of pure black for better contrast)
    bar_inner_rect = pygame.Rect(bar_x, bar_y, bar_width, bar_height)
    pygame.draw.rect(screen, (20, 20, 20), bar_inner_rect)
    
    # Progress fill with softer green tone
    fill_width = int(bar_width * progress)
    if fill_width > 0:
        fill_rect = pygame.Rect(bar_x, bar_y, fill_width, bar_height)
        # Use a softer green that complements the border
        progress_color = (0, 180, 50)  # Softer green instead of harsh yellow
        pygame.draw.rect(screen, progress_color, fill_rect)
        
        # More visible scanning effect
        if scan_progress > 0 and progress < 1.0 and fill_width > 8:
            scan_width = max(3, min(12, fill_width // 6))  # Wider scanning beam
            scan_x = bar_x + max(0, min(fill_width - scan_width, int(fill_width * scan_progress)))
            scan_rect = pygame.Rect(scan_x, bar_y, scan_width, bar_height)
            # Bright white scanning beam for visibility
            pygame.draw.rect(screen, (255, 255, 255), scan_rect)
            
            # Add a subtle glow effect around the scanning beam
            if scan_width >= 6:
                glow_rect = pygame.Rect(scan_x - 1, bar_y, scan_width + 2, bar_height)
                glow_color = (120, 255, 120)  # Light green glow
                pygame.draw.rect(screen, glow_color, glow_rect)
                # Draw the white beam on top
                pygame.draw.rect(screen, (255, 255, 255), scan_rect)
    
    # Draw progress percentage
    progress_rect = progress_surface.get_rect(center=(center_x, bar_y + bar_height + progress_spacing))
    screen.blit(progress_surface, progress_rect)
    
    # Draw current stage text
    stage_rect = stage_surface.get_rect(center=(center_x, progress_rect.bottom + stage_spacing))
    screen.blit(stage_surface, stage_rect)
    
    # Draw line count if available
    if lines_surface:
        lines_rect = lines_surface.get_rect(center=(center_x, stage_rect.bottom + lines_spacing))
        screen.blit(lines_surface, lines_rect)
    
    pygame.display.flip()

class LoadingProgress:
    """Thread-safe loading progress tracker."""
    def __init__(self):
        self.current_lines = 0
        self.total_lines = 0
        self.stage = "Initializing tricorder systems..."
        self.complete = False
        self.scan_progress = 0.0
        self.lock = threading.Lock()
    
    def update(self, current_lines=None, total_lines=None, stage=None, complete=None, scan_progress=None):
        with self.lock:
            if current_lines is not None:
                self.current_lines = current_lines
            if total_lines is not None:
                self.total_lines = total_lines
            if stage is not None:
                self.stage = stage
            if complete is not None:
                self.complete = complete
            if scan_progress is not None:
                self.scan_progress = scan_progress
    
    def get_status(self):
        with self.lock:
            return self.current_lines, self.total_lines, self.stage, self.complete, self.scan_progress

def loading_worker(progress_tracker):
    """Background worker that performs the actual loading tasks with Star Trek theming."""
    try:
        # Stage 1: Initialize tricorder systems
        progress_tracker.update(stage="Initializing tricorder systems...")
        time.sleep(0.8)
        
        # Stage 2: Scanning subroutines (progressive line counting)
        progress_tracker.update(stage="Scanning subroutines...")
        time.sleep(0.3)
        
        # Get total lines first (quickly)
        total_lines, python_files = count_python_lines()
        progress_tracker.update(total_lines=total_lines, current_lines=0)
        
        # Simulate progressive scanning with realistic timing
        scan_duration = 3.0  # Total time for scanning animation (slightly longer)
        scan_start_time = time.time()
        
        while True:
            elapsed = time.time() - scan_start_time
            if elapsed >= scan_duration:
                break
                
            # Calculate progress through the scan
            scan_progress = elapsed / scan_duration
            
            # Progressive line counting with some randomness for realism
            if scan_progress < 0.85:  # Don't reach 100% until near the end
                current_lines = int(total_lines * scan_progress * (0.7 + 0.3 * random.random()))
            else:
                current_lines = total_lines
            
            # Update with scanning beam animation (slower, more visible)
            beam_progress = (scan_progress * 2.5) % 1.0  # Slower beam for better visibility
            progress_tracker.update(
                current_lines=current_lines, 
                scan_progress=beam_progress,
                stage="Analyzing code matrices..."
            )
            
            time.sleep(0.08)  # Slightly faster updates for smoother animation
        
        # Ensure we end with full count
        progress_tracker.update(current_lines=total_lines, scan_progress=0.0)
        
        # Stage 3: Initialize sensors
        progress_tracker.update(stage="Calibrating sensor array...")
        time.sleep(0.7)
        
        # Stage 4: Check for updates and resolve location if WiFi available
        progress_tracker.update(stage="Checking for updates...")
        try:
            from data import system_info
            wifi_status, _ = system_info.get_wifi_info()
            if wifi_status in ["Connected", "Online"] and hasattr(progress_tracker, 'app_state') and progress_tracker.app_state:
                app = progress_tracker.app_state
                if app.update_manager._check_network_connectivity():
                    app.update_manager._check_for_updates()
                    app.update_available = app.update_manager.update_available
                    app.commits_behind = app.update_manager.remote_version.get('commits_behind', 0) if app.update_manager.remote_version else 0
                # Resolve location and public IP (once on boot)
                if app.location_from_ip is None:
                    progress_tracker.update(stage="Resolving location...")
                    loc, pub_ip = system_info.get_location_and_public_ip(timeout_sec=3.0)
                    app.location_from_ip = loc
                    app.public_ip = pub_ip
        except Exception as e:
            logger.debug(f"Update/location check failed: {e}")
        
        # Stage 5: Preparing system
        progress_tracker.update(stage="Establishing subspace link...")
        time.sleep(0.6)
        
        # Stage 5: Final preparation
        progress_tracker.update(stage="Tricorder ready. Scanning the Galaxy...")
        time.sleep(0.4)
        
        # Stage 6: Loading complete
        progress_tracker.update(stage="All systems operational. Engage!", complete=True)
        
    except Exception as e:
        logger.error(f"Error in loading worker: {e}", exc_info=True)
        progress_tracker.update(stage="System initialization completed with errors", complete=True) 