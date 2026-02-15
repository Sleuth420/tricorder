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
    
    if ui_scaler:
        screen_width = ui_scaler.screen_width
        screen_height = ui_scaler.screen_height
        safe_rect = ui_scaler.get_safe_area_rect() if ui_scaler.safe_area_enabled else pygame.Rect(0, 0, screen_width, screen_height)
    else:
        screen_width = screen.get_width()
        screen_height = screen.get_height()
        safe_rect = pygame.Rect(0, 0, screen_width, screen_height)
    title_top = safe_rect.top + (ui_scaler.margin("small") if ui_scaler else 20)
    status_y = safe_rect.top + (ui_scaler.scale(60) if ui_scaler else 60)
    section_y = safe_rect.top + (ui_scaler.scale(100) if ui_scaler else 100)
    freq_y = safe_rect.top + (ui_scaler.scale(130) if ui_scaler else 130)
    bar_inset = safe_rect.left + (ui_scaler.scale(50) if ui_scaler else 50)
    bar_y = safe_rect.top + (ui_scaler.scale(160) if ui_scaler else 160)
    bar_h = ui_scaler.scale(20) if ui_scaler else 20
    bar_width_max = safe_rect.width - 2 * (ui_scaler.scale(50) if ui_scaler else 50)
    overall_y = safe_rect.top + (ui_scaler.scale(200) if ui_scaler else 200)
    volume_y = safe_rect.top + (ui_scaler.scale(230) if ui_scaler else 230)
    vol_bar_y = safe_rect.top + (ui_scaler.scale(250) if ui_scaler else 250)
    vol_bar_h = ui_scaler.scale(15) if ui_scaler else 15
    menu_start_y = safe_rect.top + (ui_scaler.scale(300) if ui_scaler else 300)
    option_height = ui_scaler.scale(30) if ui_scaler else 30
    option_inset = safe_rect.left + (ui_scaler.margin("small") if ui_scaler else 30)
    instruction_bottom = ui_scaler.scale(80) if ui_scaler else 80
    instruction_line = ui_scaler.scale(20) if ui_scaler else 20
    screen.fill(config_module.Theme.BACKGROUND)
    title_font = fonts['large']
    title_text = "Audio Test Screen"
    title_surface = title_font.render(title_text, True, config_module.Theme.FOREGROUND)
    title_rect = title_surface.get_rect(centerx=safe_rect.centerx)
    screen.blit(title_surface, (title_rect.x, title_top))
    status_font = fonts['medium']
    if audio_test.is_playing:
        status_text = "🔊 PLAYING"
        status_color = config_module.Theme.ACCENT
    else:
        status_text = "🔇 STOPPED"
        status_color = config_module.Theme.WARNING
    status_surface = status_font.render(status_text, True, status_color)
    status_rect = status_surface.get_rect(centerx=safe_rect.centerx)
    screen.blit(status_surface, (status_rect.x, status_y))
    
    # Current section info
    if audio_test.is_playing:
        section_info = audio_test.get_current_section_info()
        if section_info:
            # Section name
            section_font = fonts['medium']
            section_text = f"Section {audio_test.current_section + 1}: {section_info['name']}"
            section_surface = section_font.render(section_text, True, section_info['color'])
            section_rect = section_surface.get_rect(centerx=safe_rect.centerx)
            screen.blit(section_surface, (section_rect.x, section_y))
            freq_text = f"Frequency: {section_info['freq_range']}"
            freq_surface = fonts['small'].render(freq_text, True, config_module.Theme.FOREGROUND)
            freq_rect = freq_surface.get_rect(centerx=safe_rect.centerx)
            screen.blit(freq_surface, (freq_rect.x, freq_y))
            
            progress = audio_test.get_section_progress()
            bar_width = bar_width_max
            pygame.draw.rect(screen, config_module.Palette.DARK_GREY, (bar_inset, bar_y, bar_width, bar_h))
            progress_width = int(bar_width * progress)
            pygame.draw.rect(screen, section_info['color'], (bar_inset, bar_y, progress_width, bar_h))
            progress_text = f"{int(progress * 100)}%"
            progress_surface = fonts['small'].render(progress_text, True, config_module.Theme.WHITE)
            progress_x = bar_inset + (bar_width - progress_surface.get_width()) // 2
            progress_y_off = bar_y + (bar_h - progress_surface.get_height()) // 2
            screen.blit(progress_surface, (progress_x, progress_y_off))
    
    # Overall progress
    if audio_test.is_playing:
        overall_progress = audio_test.get_progress()
        overall_text = f"Overall Progress: {int(overall_progress * 100)}%"
        overall_surface = fonts['small'].render(overall_text, True, config_module.Theme.FOREGROUND)
        overall_rect = overall_surface.get_rect(centerx=safe_rect.centerx)
        screen.blit(overall_surface, (overall_rect.x, overall_y))
    volume_text = f"Volume: {int(audio_test.volume * 100)}%"
    volume_surface = fonts['small'].render(volume_text, True, config_module.Theme.FOREGROUND)
    volume_rect = volume_surface.get_rect(centerx=safe_rect.centerx)
    screen.blit(volume_surface, (volume_rect.x, volume_y))
    vol_bar_width = bar_width_max
    pygame.draw.rect(screen, config_module.Palette.DARK_GREY, (bar_inset, vol_bar_y, vol_bar_width, vol_bar_h))
    vol_width = int(vol_bar_width * audio_test.volume)
    pygame.draw.rect(screen, config_module.Theme.ACCENT, (bar_inset, vol_bar_y, vol_width, vol_bar_h))
    
    # Menu options
    menu_options = [
        "Play Test Sound" if not audio_test.is_playing else "Stop Test",
        "Volume Up",
        "Volume Down", 
        "Back to Settings"
    ]
    
    menu_inset = ui_scaler.margin("small") if ui_scaler else 20
    for i, option in enumerate(menu_options):
        y_pos = menu_start_y + i * option_height
        is_selected = (i == audio_test.selected_option)
        menu_inset_val = ui_scaler.margin("small") if ui_scaler else 20
        if is_selected:
            sel_pad = ui_scaler.scale(5) if ui_scaler else 5
            pygame.draw.rect(screen, config_module.Theme.MENU_SELECTED_BG,
                             (safe_rect.left + menu_inset_val, y_pos - sel_pad, safe_rect.width - 2 * menu_inset_val, option_height))
        color = config_module.Theme.MENU_SELECTED_TEXT if is_selected else config_module.Theme.FOREGROUND
        option_surface = fonts['medium'].render(option, True, color)
        screen.blit(option_surface, (option_inset, y_pos))
    
    # Instructions (OS-adaptive: Left/Right/Middle on Pi, A/D/Enter on dev)
    labels = config_module.get_control_labels()
    instructions = [
        f"Use {labels['prev']}/{labels['next']} to navigate, {labels['select']} to select",
        "Test covers 200Hz - 2000Hz frequency range",
        "Listen for clarity across all sections"
    ]
    
    instruction_y = safe_rect.bottom - instruction_bottom
    for i, instruction in enumerate(instructions):
        inst_surface = fonts['small'].render(instruction, True, config_module.Palette.DARK_GREY)
        inst_rect = inst_surface.get_rect(centerx=safe_rect.centerx)
        screen.blit(inst_surface, (inst_rect.x, instruction_y + i * instruction_line))
