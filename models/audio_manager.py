# --- models/audio_manager.py ---
# Audio management for the tricorder application

import pygame
import logging
import os
import platform
import subprocess
import sys

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
        self.audio_system_info = {}
        self.audio_devices = []
        
        # Log system information first
        self._log_system_audio_info()
        
        if self.enabled:
            self._init_audio()
            self._load_sounds()
    
    def _log_system_audio_info(self):
        """Log comprehensive system audio information for debugging."""
        logger.info("=== AUDIO SYSTEM DIAGNOSTICS ===")
        
        # Platform information
        logger.info(f"Platform: {platform.system()} {platform.release()}")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Pygame version: {pygame.version.ver}")
        
        # Audio configuration
        logger.info(f"Audio enabled: {self.enabled}")
        logger.info(f"Audio frequency: {self.config.AUDIO_FREQUENCY} Hz")
        logger.info(f"Audio buffer size: {self.config.AUDIO_BUFFER_SIZE}")
        logger.info(f"Audio channels: 2 (stereo)")
        logger.info(f"Audio bit depth: 16-bit signed")
        
        # System audio devices (Linux/Raspberry Pi specific)
        if platform.system() == "Linux":
            self._log_linux_audio_info()
        else:
            logger.info("Non-Linux platform - skipping advanced audio diagnostics")
        
        logger.info("=== END AUDIO SYSTEM DIAGNOSTICS ===")
    
    def _log_linux_audio_info(self):
        """Log Linux-specific audio information for Raspberry Pi debugging."""
        try:
            # Check for PulseAudio
            try:
                result = subprocess.run(['pulseaudio', '--check'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    logger.info("✓ PulseAudio is running")
                    self._log_pulseaudio_info()
                else:
                    logger.warning("⚠ PulseAudio not running or not available")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logger.warning("⚠ PulseAudio command not found or timed out")
            
            # Check for ALSA
            try:
                result = subprocess.run(['aplay', '-l'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    logger.info("✓ ALSA devices found:")
                    for line in result.stdout.split('\n'):
                        if line.strip() and 'card' in line.lower():
                            logger.info(f"  {line.strip()}")
                else:
                    logger.warning("⚠ No ALSA devices found")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                logger.warning("⚠ ALSA aplay command not found")
            
            # Check for 3.5mm jack specifically
            self._check_35mm_audio_jack()
            
        except Exception as e:
            logger.error(f"Error gathering Linux audio info: {e}")
    
    def _log_pulseaudio_info(self):
        """Log PulseAudio specific information."""
        try:
            # Get PulseAudio sink information
            result = subprocess.run(['pactl', 'list', 'sinks', 'short'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("PulseAudio sinks:")
                for line in result.stdout.split('\n'):
                    if line.strip():
                        logger.info(f"  {line.strip()}")
            
            # Get default sink
            result = subprocess.run(['pactl', 'get-default-sink'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info(f"Default audio sink: {result.stdout.strip()}")
                
        except Exception as e:
            logger.warning(f"Could not get PulseAudio info: {e}")
    
    def _check_35mm_audio_jack(self):
        """Check specifically for 3.5mm audio jack configuration."""
        try:
            # Check if 3.5mm jack is enabled in config
            config_paths = [
                '/boot/firmware/config.txt',
                '/boot/config.txt'
            ]
            
            for config_path in config_paths:
                if os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        content = f.read()
                        if 'dtparam=audio=on' in content:
                            logger.info("✓ 3.5mm audio jack enabled in config.txt")
                        else:
                            logger.warning("⚠ 3.5mm audio jack not explicitly enabled in config.txt")
                        break
            else:
                logger.warning("⚠ Could not find config.txt to check 3.5mm audio settings")
                
        except Exception as e:
            logger.warning(f"Could not check 3.5mm audio configuration: {e}")
    
    def _init_audio(self):
        """Initialize pygame audio subsystem with enhanced logging."""
        logger.info("Initializing pygame audio subsystem...")
        
        try:
            # Log SDL audio driver info
            sdl_audio_driver = os.environ.get('SDL_AUDIODRIVER', 'default')
            logger.info(f"SDL audio driver: {sdl_audio_driver}")
            
            pygame.mixer.init(
                frequency=self.config.AUDIO_FREQUENCY,
                size=-16,  # 16-bit signed
                channels=2,  # Stereo
                buffer=self.config.AUDIO_BUFFER_SIZE
            )
            
            # Log successful initialization details
            logger.info("✓ Pygame audio initialized successfully")
            logger.info(f"  - Frequency: {self.config.AUDIO_FREQUENCY} Hz")
            logger.info(f"  - Channels: 2 (stereo)")
            logger.info(f"  - Bit depth: 16-bit signed")
            logger.info(f"  - Buffer size: {self.config.AUDIO_BUFFER_SIZE}")
            
            # Test audio system
            self._test_audio_system()
            
        except pygame.error as e:
            logger.error(f"✗ Failed to initialize pygame audio: {e}")
            logger.error("This may indicate:")
            logger.error("  - No audio device available")
            logger.error("  - Audio device in use by another application")
            logger.error("  - Incorrect audio configuration")
            logger.error("  - Missing audio drivers")
            self.enabled = False
        except Exception as e:
            logger.error(f"✗ Unexpected error during audio initialization: {e}")
            self.enabled = False
    
    def _test_audio_system(self):
        """Test the audio system with a brief sound to verify it's working."""
        try:
            # Create a brief test tone
            import numpy as np
            sample_rate = self.config.AUDIO_FREQUENCY
            duration = 0.1  # 100ms test
            frequency = 440  # A4 note
            
            # Generate test tone
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            test_tone = (0.1 * np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)
            
            # Convert to stereo and ensure C-contiguous array
            stereo_tone = np.array([test_tone, test_tone]).T
            stereo_tone = np.ascontiguousarray(stereo_tone)
            
            # Create pygame sound from numpy array
            test_sound = pygame.sndarray.make_sound(stereo_tone)
            
            # Play test sound
            test_sound.play()
            logger.info("✓ Audio system test completed - test tone played")
            
        except Exception as e:
            logger.warning(f"Audio system test failed: {e}")
            logger.warning("Audio may still work, but test verification failed")
    
    def _load_sounds(self):
        """Load sound effects from the assets directory with enhanced logging."""
        if not self.enabled:
            logger.info("Audio disabled - skipping sound loading")
            return
        
        logger.info("Loading sound effects...")
        sound_files = {
            'test_sound': 'test_sound.wav',
            'beep': 'beep.wav',
            'scan': 'scan.wav',
            'alert': 'alert.wav'
        }
        
        loaded_count = 0
        for sound_name, filename in sound_files.items():
            sound_path = os.path.join(self.config.SOUND_EFFECTS_PATH, filename)
            try:
                if os.path.exists(sound_path):
                    # Get file size for logging
                    file_size = os.path.getsize(sound_path)
                    
                    # Load the sound
                    sound = pygame.mixer.Sound(sound_path)
                    self.sounds[sound_name] = sound
                    
                    # Get sound properties
                    length = sound.get_length()
                    volume = sound.get_volume()
                    
                    logger.info(f"✓ Loaded sound: {sound_name}")
                    logger.info(f"  - File: {filename} ({file_size} bytes)")
                    logger.info(f"  - Duration: {length:.2f} seconds")
                    logger.info(f"  - Volume: {volume}")
                    
                    loaded_count += 1
                else:
                    logger.warning(f"⚠ Sound file not found: {sound_path}")
            except pygame.error as e:
                logger.error(f"✗ Failed to load sound {sound_name}: {e}")
            except Exception as e:
                logger.error(f"✗ Unexpected error loading {sound_name}: {e}")
        
        logger.info(f"Sound loading complete: {loaded_count}/{len(sound_files)} sounds loaded")
    
    def play_sound(self, sound_name):
        """
        Play a sound effect with enhanced logging for debugging.
        
        Args:
            sound_name (str): Name of the sound to play
        """
        if not self.enabled:
            logger.warning("Audio disabled - cannot play sound")
            return
            
        if sound_name in self.sounds:
            try:
                sound = self.sounds[sound_name]
                
                # Log sound properties before playing
                length = sound.get_length()
                volume = sound.get_volume()
                logger.info(f"🔊 Playing sound: {sound_name}")
                logger.info(f"  - Duration: {length:.2f} seconds")
                logger.info(f"  - Volume: {volume}")
                
                # Play the sound
                sound.play()
                
                # Log successful playback
                logger.info(f"✓ Sound '{sound_name}' playback initiated successfully")
                
            except pygame.error as e:
                logger.error(f"✗ Failed to play sound {sound_name}: {e}")
                logger.error("This may indicate:")
                logger.error("  - Audio device disconnected")
                logger.error("  - Audio system error")
                logger.error("  - Sound file corruption")
            except Exception as e:
                logger.error(f"✗ Unexpected error playing {sound_name}: {e}")
        else:
            logger.warning(f"⚠ Sound not found: {sound_name}")
            logger.warning("Available sounds:")
            for available_sound in self.sounds.keys():
                logger.warning(f"  - {available_sound}")
    
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
    
    def get_audio_status(self):
        """Get comprehensive audio system status for debugging."""
        status = {
            'enabled': self.enabled,
            'sounds_loaded': len(self.sounds),
            'music_playing': self.music_playing,
            'available_sounds': list(self.sounds.keys()),
            'platform': platform.system(),
            'pygame_version': pygame.version.ver
        }
        
        if self.enabled:
            try:
                status['mixer_initialized'] = pygame.mixer.get_init() is not None
                if status['mixer_initialized']:
                    init_info = pygame.mixer.get_init()
                    status['frequency'] = init_info[0]
                    status['format'] = init_info[1]
                    status['channels'] = init_info[2]
            except:
                status['mixer_initialized'] = False
        
        return status
    
    def log_audio_status(self):
        """Log current audio system status for debugging."""
        status = self.get_audio_status()
        logger.info("=== CURRENT AUDIO STATUS ===")
        logger.info(f"Audio enabled: {status['enabled']}")
        logger.info(f"Mixer initialized: {status.get('mixer_initialized', 'Unknown')}")
        logger.info(f"Music playing: {status['music_playing']}")
        logger.info(f"Sounds loaded: {status['sounds_loaded']}")
        logger.info(f"Available sounds: {', '.join(status['available_sounds'])}")
        
        if status.get('mixer_initialized'):
            logger.info(f"Frequency: {status.get('frequency', 'Unknown')} Hz")
            logger.info(f"Format: {status.get('format', 'Unknown')}")
            logger.info(f"Channels: {status.get('channels', 'Unknown')}")
        
        logger.info("=== END AUDIO STATUS ===")
    
    def cleanup(self):
        """Clean up audio resources with enhanced logging."""
        logger.info("Cleaning up audio resources...")
        
        if self.enabled:
            try:
                # Stop any playing music
                if self.music_playing:
                    pygame.mixer.music.stop()
                    logger.info("Stopped background music")
                
                # Quit mixer
                pygame.mixer.quit()
                logger.info("✓ Pygame mixer quit successfully")
                
            except Exception as e:
                logger.error(f"Error during audio cleanup: {e}")
            finally:
                self.enabled = False
                logger.info("Audio cleanup completed")
        else:
            logger.info("Audio was not enabled - no cleanup needed")
