# --- ui/views/settings/audio_test_screen.py ---
# Dedicated audio test screen with visual feedback and controls

import pygame
import logging
import time
from ui.components.text.text_display import render_footer, render_text
import config as app_config

logger = logging.getLogger(__name__)

class AudioTestScreen:
    """Manages the audio test screen state and display."""
    
    def __init__(self):
        self.test_start_time = None
        self.current_section = 0
        self.is_playing = False
        self.volume = 0.5  # Default volume
        self.test_sections = [
            {"name": "Low Frequency Sweep", "freq_range": "200Hz - 400Hz", "duration": 1.0, "color": (100, 150, 255)},
            {"name": "Mid Frequency Tones", "freq_range": "440Hz, 660Hz, 880Hz", "duration": 2.0, "color": (100, 255, 100)},
            {"name": "High Frequency Sweep", "freq_range": "1000Hz - 2000Hz", "duration": 1.0, "color": (255, 200, 100)},
            {"name": "C Major Chord", "freq_range": "261Hz, 330Hz, 392Hz", "duration": 2.0, "color": (255, 100, 255)},
        ]
        self.selected_option = 0  # 0: Play Test, 1: Volume Up, 2: Volume Down, 3: Stop, 4: Back
        
    def start_test(self):
        """Start the audio test."""
        self.test_start_time = time.time()
        self.current_section = 0
        self.is_playing = True
        logger.info("Audio test started")
        
    def stop_test(self):
        """Stop the audio test."""
        self.is_playing = False
        self.test_start_time = None
        self.current_section = 0
        logger.info("Audio test stopped")
        
    def update(self):
        """Update the test screen state."""
        if not self.is_playing or not self.test_start_time:
            return
            
        elapsed = time.time() - self.test_start_time
        total_duration = sum(section["duration"] for section in self.test_sections)
        
        # Check if test is complete
        if elapsed >= total_duration:
            self.stop_test()
            return
            
        # Update current section
        current_time = 0
        for i, section in enumerate(self.test_sections):
            if elapsed < current_time + section["duration"]:
                self.current_section = i
                break
            current_time += section["duration"]
    
    def get_current_section_info(self):
        """Get information about the current test section."""
        if not self.is_playing or self.current_section >= len(self.test_sections):
            return None
        return self.test_sections[self.current_section]
    
    def get_progress(self):
        """Get the progress of the current test (0.0 to 1.0)."""
        if not self.is_playing or not self.test_start_time:
            return 0.0
            
        elapsed = time.time() - self.test_start_time
        total_duration = sum(section["duration"] for section in self.test_sections)
        return min(elapsed / total_duration, 1.0)
    
    def get_section_progress(self):
        """Get the progress within the current section (0.0 to 1.0)."""
        if not self.is_playing or not self.test_start_time:
            return 0.0
            
        elapsed = time.time() - self.test_start_time
        current_time = 0
        for i, section in enumerate(self.test_sections):
            if i == self.current_section:
                section_elapsed = elapsed - current_time
                return min(section_elapsed / section["duration"], 1.0)
            current_time += section["duration"]
        return 0.0

def draw_audio_test_screen(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the dedicated audio test screen with visual feedback.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module (config package)
        ui_scaler (UIScaler, optional): UI scaling system for responsive design
    """
    # Get or create audio test screen instance
    if not hasattr(app_state, 'audio_test_screen'):
        app_state.audio_test_screen = AudioTestScreen()
    
    audio_test = app_state.audio_test_screen
    audio_test.update()
    
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Clear screen
    screen.fill(config_module.Theme.BACKGROUND)
    
    # Title
    title_font = fonts['large']
    title_text = "Audio Test Screen"
    title_surface = title_font.render(title_text, True, config_module.Theme.FOREGROUND)
    title_x = (screen_width - title_surface.get_width()) // 2
    screen.blit(title_surface, (title_x, 20))
    
    # Audio status
    status_font = fonts['medium']
    if audio_test.is_playing:
        status_text = "🔊 PLAYING"
        status_color = config_module.Theme.ACCENT
    else:
        status_text = "🔇 STOPPED"
        status_color = config_module.Theme.WARNING
    
    status_surface = status_font.render(status_text, True, status_color)
    status_x = (screen_width - status_surface.get_width()) // 2
    screen.blit(status_surface, (status_x, 60))
    
    # Current section info
    if audio_test.is_playing:
        section_info = audio_test.get_current_section_info()
        if section_info:
            # Section name
            section_font = fonts['medium']
            section_text = f"Section {audio_test.current_section + 1}: {section_info['name']}"
            section_surface = section_font.render(section_text, True, section_info['color'])
            section_x = (screen_width - section_surface.get_width()) // 2
            screen.blit(section_surface, (section_x, 100))
            
            # Frequency range
            freq_text = f"Frequency: {section_info['freq_range']}"
            freq_surface = fonts['small'].render(freq_text, True, config_module.Theme.FOREGROUND)
            freq_x = (screen_width - freq_surface.get_width()) // 2
            screen.blit(freq_surface, (freq_x, 130))
            
            # Progress bar for current section
            progress = audio_test.get_section_progress()
            bar_width = screen_width - 100
            bar_height = 20
            bar_x = 50
            bar_y = 160
            
            # Background bar
            pygame.draw.rect(screen, config_module.Palette.DARK_GREY, 
                           (bar_x, bar_y, bar_width, bar_height))
            
            # Progress bar
            progress_width = int(bar_width * progress)
            pygame.draw.rect(screen, section_info['color'], 
                           (bar_x, bar_y, progress_width, bar_height))
            
            # Progress text
            progress_text = f"{int(progress * 100)}%"
            progress_surface = fonts['small'].render(progress_text, True, config_module.Theme.WHITE)
            progress_x = bar_x + (bar_width - progress_surface.get_width()) // 2
            progress_y = bar_y + (bar_height - progress_surface.get_height()) // 2
            screen.blit(progress_surface, (progress_x, progress_y))
    
    # Overall progress
    if audio_test.is_playing:
        overall_progress = audio_test.get_progress()
        overall_text = f"Overall Progress: {int(overall_progress * 100)}%"
        overall_surface = fonts['small'].render(overall_text, True, config_module.Theme.FOREGROUND)
        overall_x = (screen_width - overall_surface.get_width()) // 2
        screen.blit(overall_surface, (overall_x, 200))
    
    # Volume display
    volume_text = f"Volume: {int(audio_test.volume * 100)}%"
    volume_surface = fonts['small'].render(volume_text, True, config_module.Theme.FOREGROUND)
    volume_x = (screen_width - volume_surface.get_width()) // 2
    screen.blit(volume_surface, (volume_x, 230))
    
    # Volume bar
    vol_bar_width = screen_width - 100
    vol_bar_height = 15
    vol_bar_x = 50
    vol_bar_y = 250
    
    # Background volume bar
    pygame.draw.rect(screen, config_module.Palette.DARK_GREY, 
                   (vol_bar_x, vol_bar_y, vol_bar_width, vol_bar_height))
    
    # Volume level
    vol_width = int(vol_bar_width * audio_test.volume)
    pygame.draw.rect(screen, config_module.Theme.ACCENT, 
                   (vol_bar_x, vol_bar_y, vol_width, vol_bar_height))
    
    # Menu options
    menu_options = [
        "Play Test Sound" if not audio_test.is_playing else "Stop Test",
        "Volume Up",
        "Volume Down", 
        "Back to Settings"
    ]
    
    # Draw menu options
    menu_start_y = 300
    option_height = 30
    
    for i, option in enumerate(menu_options):
        y_pos = menu_start_y + i * option_height
        is_selected = (i == audio_test.selected_option)
        
        # Highlight selected option
        if is_selected:
            pygame.draw.rect(screen, config_module.Theme.MENU_SELECTED_BG, 
                           (20, y_pos - 5, screen_width - 40, option_height))
        
        # Option text
        color = config_module.Theme.MENU_SELECTED_TEXT if is_selected else config_module.Theme.FOREGROUND
        option_surface = fonts['medium'].render(option, True, color)
        screen.blit(option_surface, (30, y_pos))
    
    # Instructions
    instructions = [
        "Use A/D to navigate, Enter to select",
        "Test covers 200Hz - 2000Hz frequency range",
        "Listen for clarity across all sections"
    ]
    
    instruction_y = screen_height - 80
    for i, instruction in enumerate(instructions):
        inst_surface = fonts['small'].render(instruction, True, config_module.Palette.DARK_GREY)
        inst_x = (screen_width - inst_surface.get_width()) // 2
        screen.blit(inst_surface, (inst_x, instruction_y + i * 20))
