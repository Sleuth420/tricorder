# --- ui/views/settings/audio_diagnostics_screen.py ---
# Audio diagnostics screen showing system-level audio information

import pygame
import logging
import platform
import subprocess
import os
from ui.components.text.text_display import render_footer, render_text

logger = logging.getLogger(__name__)

class AudioDiagnosticsScreen:
    """Manages the audio diagnostics screen state and display."""
    
    def __init__(self):
        self.diagnostics_data = {}
        self.refresh_needed = True
        
    def refresh_diagnostics(self, audio_manager):
        """Refresh audio diagnostics data."""
        self.diagnostics_data = {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'python_version': platform.python_version(),
            'pygame_version': pygame.version.ver,
            'audio_enabled': audio_manager.enabled if audio_manager else False,
            'sounds_loaded': len(audio_manager.sounds) if audio_manager else 0,
            'available_sounds': list(audio_manager.sounds.keys()) if audio_manager else [],
        }
        
        # Get audio status from audio manager
        if audio_manager:
            audio_status = audio_manager.get_audio_status()
            self.diagnostics_data['system_volume_percent'] = audio_status.get('system_volume_percent')
            self.diagnostics_data['system_volume'] = audio_status.get('system_volume')
        
        # Get system audio info
        if platform.system() == "Linux":
            self._get_linux_audio_info()
        
        self.refresh_needed = False
        
    def _get_linux_audio_info(self):
        """Get Linux-specific audio information."""
        try:
            # Check PulseAudio
            try:
                result = subprocess.run(['pulseaudio', '--check'], 
                                      capture_output=True, text=True, timeout=3)
                self.diagnostics_data['pulseaudio_running'] = result.returncode == 0
            except:
                self.diagnostics_data['pulseaudio_running'] = False
            
            # Check ALSA devices
            try:
                result = subprocess.run(['aplay', '-l'], 
                                      capture_output=True, text=True, timeout=3)
                if result.returncode == 0:
                    self.diagnostics_data['alsa_devices'] = [line.strip() for line in result.stdout.split('\n') 
                                                           if line.strip() and 'card' in line.lower()]
                else:
                    self.diagnostics_data['alsa_devices'] = []
            except:
                self.diagnostics_data['alsa_devices'] = []
            
            # Check 3.5mm jack config
            self._check_35mm_config()
            
        except Exception as e:
            logger.error(f"Error getting Linux audio info: {e}")
    
    def _check_35mm_config(self):
        """Check 3.5mm audio jack configuration."""
        config_paths = ['/boot/firmware/config.txt', '/boot/config.txt']
        self.diagnostics_data['35mm_enabled'] = False
        
        for config_path in config_paths:
            if os.path.exists(config_path):
                try:
                    with open(config_path, 'r') as f:
                        content = f.read()
                        if 'dtparam=audio=on' in content:
                            self.diagnostics_data['35mm_enabled'] = True
                            break
                except:
                    pass

def draw_audio_diagnostics_screen(screen, app_state, fonts, config_module, ui_scaler=None):
    """
    Draw the audio diagnostics screen with system information.

    Args:
        screen (pygame.Surface): The surface to draw on
        app_state (AppState): The current application state
        fonts (dict): Dictionary of loaded fonts
        config_module (module): Configuration module
        ui_scaler (UIScaler, optional): UI scaling system
    """
    # Get or create diagnostics screen instance
    if not hasattr(app_state, 'audio_diagnostics_screen'):
        app_state.audio_diagnostics_screen = AudioDiagnosticsScreen()
    
    diagnostics = app_state.audio_diagnostics_screen
    
    # Refresh diagnostics if needed
    if diagnostics.refresh_needed:
        diagnostics.refresh_diagnostics(app_state.audio_manager)
    
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    # Clear screen
    screen.fill(config_module.Theme.BACKGROUND)
    
    # Title
    title_font = fonts['large']
    title_text = "Audio Diagnostics"
    title_surface = title_font.render(title_text, True, config_module.Theme.FOREGROUND)
    title_x = (screen_width - title_surface.get_width()) // 2
    screen.blit(title_surface, (title_x, 20))
    
    # System Information
    y_offset = 70
    line_height = 25
    small_font = fonts['small']
    medium_font = fonts['medium']
    
    # Platform info
    platform_text = f"Platform: {diagnostics.diagnostics_data.get('platform', 'Unknown')} {diagnostics.diagnostics_data.get('platform_release', '')}"
    platform_surface = medium_font.render(platform_text, True, config_module.Theme.FOREGROUND)
    screen.blit(platform_surface, (20, y_offset))
    y_offset += line_height
    
    # Python/Pygame versions
    python_text = f"Python: {diagnostics.diagnostics_data.get('python_version', 'Unknown')}"
    pygame_text = f"Pygame: {diagnostics.diagnostics_data.get('pygame_version', 'Unknown')}"
    
    python_surface = small_font.render(python_text, True, config_module.Theme.FOREGROUND)
    pygame_surface = small_font.render(pygame_text, True, config_module.Theme.FOREGROUND)
    screen.blit(python_surface, (20, y_offset))
    screen.blit(pygame_surface, (screen_width - 200, y_offset))
    y_offset += line_height + 10
    
    # Audio status
    audio_enabled = diagnostics.diagnostics_data.get('audio_enabled', False)
    audio_status = "✓ ENABLED" if audio_enabled else "✗ DISABLED"
    audio_color = config_module.Theme.ACCENT if audio_enabled else config_module.Theme.ALERT
    
    status_surface = medium_font.render(f"Audio Status: {audio_status}", True, audio_color)
    screen.blit(status_surface, (20, y_offset))
    y_offset += line_height
    
    # Sounds loaded
    sounds_count = diagnostics.diagnostics_data.get('sounds_loaded', 0)
    sounds_text = f"Sounds Loaded: {sounds_count}"
    sounds_surface = small_font.render(sounds_text, True, config_module.Theme.FOREGROUND)
    screen.blit(sounds_surface, (20, y_offset))
    y_offset += line_height
    
    # Available sounds
    available_sounds = diagnostics.diagnostics_data.get('available_sounds', [])
    if available_sounds:
        sounds_list = ", ".join(available_sounds)
        if len(sounds_list) > 60:  # Truncate if too long
            sounds_list = sounds_list[:60] + "..."
        sounds_list_surface = small_font.render(f"Available: {sounds_list}", True, config_module.Theme.FOREGROUND)
        screen.blit(sounds_list_surface, (20, y_offset))
        y_offset += line_height
    
    # Linux-specific info
    if diagnostics.diagnostics_data.get('platform') == 'Linux':
        y_offset += 10
        
        # PulseAudio status
        pulse_running = diagnostics.diagnostics_data.get('pulseaudio_running', False)
        pulse_status = "✓ Running" if pulse_running else "✗ Not Running"
        pulse_color = config_module.Theme.ACCENT if pulse_running else config_module.Theme.WARNING
        
        pulse_surface = medium_font.render(f"PulseAudio: {pulse_status}", True, pulse_color)
        screen.blit(pulse_surface, (20, y_offset))
        y_offset += line_height
        
        # System volume
        system_vol = diagnostics.diagnostics_data.get('system_volume_percent')
        if system_vol is not None:
            vol_status = f"{system_vol}%"
            if system_vol < 50:
                vol_color = config_module.Theme.ALERT
                vol_status += " (LOW!)"
            elif system_vol < 75:
                vol_color = config_module.Theme.WARNING
            else:
                vol_color = config_module.Theme.ACCENT
        else:
            vol_status = "Unknown"
            vol_color = config_module.Theme.WARNING
        
        vol_surface = medium_font.render(f"System Volume: {vol_status}", True, vol_color)
        screen.blit(vol_surface, (20, y_offset))
        y_offset += line_height
        
        # 3.5mm jack status
        jack_enabled = diagnostics.diagnostics_data.get('35mm_enabled', False)
        jack_status = "✓ Enabled" if jack_enabled else "⚠ Check config.txt"
        jack_color = config_module.Theme.ACCENT if jack_enabled else config_module.Theme.WARNING
        
        jack_surface = medium_font.render(f"3.5mm Jack: {jack_status}", True, jack_color)
        screen.blit(jack_surface, (20, y_offset))
        y_offset += line_height
        
        # ALSA devices
        alsa_devices = diagnostics.diagnostics_data.get('alsa_devices', [])
        if alsa_devices:
            alsa_text = f"ALSA Devices: {len(alsa_devices)} found"
            alsa_surface = small_font.render(alsa_text, True, config_module.Theme.FOREGROUND)
            screen.blit(alsa_surface, (20, y_offset))
            y_offset += line_height
            
            # Show first few devices
            for i, device in enumerate(alsa_devices[:3]):
                device_surface = small_font.render(f"  {device}", True, config_module.Theme.FOREGROUND)
                screen.blit(device_surface, (40, y_offset))
                y_offset += line_height - 5
    
    # Footer
    render_footer(screen, "Press Back to return", fonts, config_module.Theme.FOREGROUND, screen_width, screen_height)
