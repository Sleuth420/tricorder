# --- models/audio_manager.py ---
# Audio management for the tricorder application

import pygame
import logging
import os

logger = logging.getLogger(__name__)

class AudioManager:
    """Manages audio playback for the tricorder application."""
    
    def __init__(self, config):
        """
        Initialize the audio manager.
        
        Args:
            config: Configuration module containing audio settings
        """
        self.config = config
        self.enabled = config.AUDIO_ENABLED
        self.sounds = {}
        self.music_playing = False
        
        if self.enabled:
            self._init_audio()
            self._load_sounds()
    
    def _init_audio(self):
        """Initialize pygame audio subsystem."""
        try:
            pygame.mixer.init(
                frequency=self.config.AUDIO_FREQUENCY,
                size=-16,  # 16-bit signed
                channels=2,  # Stereo
                buffer=self.config.AUDIO_BUFFER_SIZE
            )
            logger.info("Pygame audio initialized successfully")
        except pygame.error as e:
            logger.error(f"Failed to initialize pygame audio: {e}")
            self.enabled = False
    
    def _load_sounds(self):
        """Load sound effects from the assets directory."""
        if not self.enabled:
            return
            
        sound_files = {
            'test_sound': 'test_sound.wav',
            'beep': 'beep.wav',
            'scan': 'scan.wav',
            'alert': 'alert.wav'
        }
        
        for sound_name, filename in sound_files.items():
            sound_path = os.path.join(self.config.SOUND_EFFECTS_PATH, filename)
            try:
                if os.path.exists(sound_path):
                    self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
                    logger.info(f"Loaded sound: {sound_name}")
                else:
                    logger.warning(f"Sound file not found: {sound_path}")
            except pygame.error as e:
                logger.error(f"Failed to load sound {sound_name}: {e}")
    
    def play_sound(self, sound_name):
        """
        Play a sound effect.
        
        Args:
            sound_name (str): Name of the sound to play
        """
        if not self.enabled:
            logger.debug("Audio disabled, skipping sound playback")
            return
            
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
                logger.debug(f"Playing sound: {sound_name}")
            except pygame.error as e:
                logger.error(f"Failed to play sound {sound_name}: {e}")
        else:
            logger.warning(f"Sound not found: {sound_name}")
    
    def play_music(self, music_file, loop=-1):
        """
        Play background music.
        
        Args:
            music_file (str): Path to music file
            loop (int): Number of times to loop (-1 for infinite)
        """
        if not self.enabled:
            logger.debug("Audio disabled, skipping music playback")
            return
            
        try:
            music_path = os.path.join(self.config.SOUND_EFFECTS_PATH, music_file)
            if os.path.exists(music_path):
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(loop)
                self.music_playing = True
                logger.info(f"Playing music: {music_file}")
            else:
                logger.warning(f"Music file not found: {music_path}")
        except pygame.error as e:
            logger.error(f"Failed to play music {music_file}: {e}")
    
    def stop_music(self):
        """Stop background music."""
        if self.enabled and self.music_playing:
            pygame.mixer.music.stop()
            self.music_playing = False
            logger.debug("Stopped music")
    
    def set_volume(self, volume):
        """
        Set master volume.
        
        Args:
            volume (float): Volume level (0.0 to 1.0)
        """
        if self.enabled:
            pygame.mixer.music.set_volume(volume)
            logger.debug(f"Set volume to: {volume}")
    
    def cleanup(self):
        """Clean up audio resources."""
        if self.enabled:
            pygame.mixer.quit()
            logger.info("Audio cleanup completed")
