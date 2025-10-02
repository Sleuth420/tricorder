# --- ui/components/debug/debug_overlay.py ---
# Debug overlay component for displaying FPS and input information

import pygame
import time
import logging
from collections import deque

logger = logging.getLogger(__name__)

class FPSTracker:
    """Tracks and calculates FPS."""
    
    def __init__(self, sample_size=30):
        """
        Initialize FPS tracker.
        
        Args:
            sample_size (int): Number of frame times to average for FPS calculation
        """
        self.sample_size = sample_size
        self.frame_times = deque(maxlen=sample_size)
        self.last_time = time.time()
        self.fps = 0.0
        
    def update(self):
        """Update FPS calculation with current frame time."""
        current_time = time.time()
        frame_time = current_time - self.last_time
        self.frame_times.append(frame_time)
        self.last_time = current_time
        
        if len(self.frame_times) > 0:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            self.fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0
    
    def get_fps(self):
        """Get current FPS."""
        return self.fps
    
    def reset(self):
        """Reset FPS tracking."""
        self.frame_times.clear()
        self.last_time = time.time()
        self.fps = 0.0

class InputTracker:
    """Tracks recent input events for debug display."""
    
    def __init__(self, max_events=5):
        """
        Initialize input tracker.
        
        Args:
            max_events (int): Maximum number of recent events to track
        """
        self.max_events = max_events
        self.recent_events = deque(maxlen=max_events)
        
    def add_event(self, event_type, key=None):
        """
        Add an input event to the tracker.
        
        Args:
            event_type (str): Type of input event (KEYDOWN, KEYUP, etc.)
            key (str, optional): Key that was pressed/released
        """
        timestamp = time.time()
        event_info = {
            'type': event_type,
            'key': key,
            'time': timestamp
        }
        self.recent_events.append(event_info)
    
    def get_recent_events(self):
        """Get recent input events."""
        return list(self.recent_events)

class DebugOverlay:
    """Debug overlay component for displaying debug information."""
    
    def __init__(self, screen_width, screen_height):
        """
        Initialize debug overlay.
        
        Args:
            screen_width (int): Screen width
            screen_height (int): Screen height
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.fps_tracker = FPSTracker()
        self.input_tracker = InputTracker()
        self.enabled = False
        
        # Auto-hide functionality
        self.last_input_time = 0
        self.auto_hide_delay = 2.0  # Hide after 2 seconds of no input
        self.show_overlay = False
        
        # Responsive sizing based on screen size
        if screen_width <= 400:  # Small screen (Pi)
            self.overlay_width = 100
            self.overlay_x = screen_width - 105
            self.overlay_y = 5
            self.line_height = 12
            self.max_lines = 4
            self.font_size = 'tiny'
        else:  # Large screen (Windows dev)
            self.overlay_width = 150
            self.overlay_x = screen_width - 155
            self.overlay_y = 10
            self.line_height = 18
            self.max_lines = 6
            self.font_size = 'small'
        
    def set_enabled(self, enabled):
        """Enable or disable the debug overlay."""
        self.enabled = enabled
        
    def update(self):
        """Update debug information."""
        if self.enabled:
            self.fps_tracker.update()
            
            # Auto-hide logic
            current_time = time.time()
            if self.show_overlay and current_time - self.last_input_time > self.auto_hide_delay:
                self.show_overlay = False
    
    def add_input_event(self, event_type, key=None):
        """Add an input event to the tracker."""
        if self.enabled:
            self.input_tracker.add_event(event_type, key)
            self.last_input_time = time.time()
            self.show_overlay = True  # Show overlay when input occurs
    
    def draw(self, screen, fonts, config_module):
        """
        Draw the debug overlay on screen.
        
        Args:
            screen (pygame.Surface): Screen to draw on
            fonts (dict): Font dictionary
            config_module: Configuration module for colors
        """
        if not self.enabled or not self.show_overlay:
            return
            
        # Get appropriate font
        font = fonts.get(self.font_size, fonts.get('small', fonts.get('default')))
        
        # Background rectangle for better readability
        overlay_height = min(self.max_lines * self.line_height + 8, self.screen_height - 20)
        bg_rect = pygame.Rect(self.overlay_x - 4, self.overlay_y - 4, self.overlay_width, overlay_height)
        
        # Semi-transparent background
        overlay_surface = pygame.Surface((self.overlay_width, overlay_height))
        overlay_surface.set_alpha(200)  # Semi-transparent
        overlay_surface.fill(config_module.Theme.BACKGROUND)
        screen.blit(overlay_surface, (self.overlay_x - 4, self.overlay_y - 4))
        
        # Border
        pygame.draw.rect(screen, config_module.Theme.ACCENT, bg_rect, 1)
        
        # Draw debug information (minimal for small screen)
        y_offset = self.overlay_y
        line_spacing = self.line_height
        
        # FPS (most important)
        fps_text = f"FPS: {self.fps_tracker.get_fps():.0f}"
        fps_surface = font.render(fps_text, True, config_module.Theme.ACCENT)
        screen.blit(fps_surface, (self.overlay_x, y_offset))
        y_offset += line_spacing
        
        # Show input data on both screens (you need this on Pi too)
        recent_events = self.input_tracker.get_recent_events()
        if recent_events:
            last_event = recent_events[-1]
            if last_event['key']:
                # Convert key code to readable name
                key_name = self._get_key_name(last_event['key'])
                event_text = f"Key: {key_name}"
            else:
                event_text = f"Input: {last_event['type']}"
            
            # Truncate if too long for small screen
            max_len = 8 if self.screen_width <= 400 else 12
            if len(event_text) > max_len:
                event_text = event_text[:max_len] + "..."
            
            event_surface = font.render(event_text, True, config_module.Theme.WARNING)
            screen.blit(event_surface, (self.overlay_x, y_offset))
    
    def _get_key_name(self, key_code):
        """Convert pygame key code to readable name."""
        # Common key mappings
        key_map = {
            97: 'A', 98: 'B', 99: 'C', 100: 'D', 101: 'E', 102: 'F', 103: 'G', 104: 'H',
            105: 'I', 106: 'J', 107: 'K', 108: 'L', 109: 'M', 110: 'N', 111: 'O', 112: 'P',
            113: 'Q', 114: 'R', 115: 'S', 116: 'T', 117: 'U', 118: 'V', 119: 'W', 120: 'X',
            121: 'Y', 122: 'Z',
            13: 'Enter', 27: 'Esc', 32: 'Space', 8: 'Backspace', 9: 'Tab',
            273: 'Up', 274: 'Down', 275: 'Right', 276: 'Left'
        }
        return key_map.get(key_code, f"Key{key_code}")
