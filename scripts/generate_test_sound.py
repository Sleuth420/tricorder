#!/usr/bin/env python3
"""
Generate a comprehensive test sound file for the tricorder application.
This creates a frequency sweep and multiple tones to test audio across different ranges.
"""

import numpy as np
import wave
import os

def generate_test_sound():
    """Generate a comprehensive test sound file with frequency range."""
    # Audio parameters
    sample_rate = 22050  # Match pygame audio frequency
    duration = 6.0  # 6 seconds total
    
    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Create multiple test sections
    wave_data = np.zeros_like(t)
    
    # Section 1: Low frequency sweep (0-1s) - 200Hz to 400Hz
    sweep_start = 0.0
    sweep_end = 1.0
    sweep_mask = (t >= sweep_start) & (t < sweep_end)
    sweep_t = t[sweep_mask] - sweep_start
    sweep_duration = sweep_end - sweep_start
    sweep_freq_start = 200
    sweep_freq_end = 400
    sweep_freq = sweep_freq_start + (sweep_freq_end - sweep_freq_start) * (sweep_t / sweep_duration)
    wave_data[sweep_mask] = 0.3 * np.sin(2 * np.pi * sweep_freq * sweep_t)
    
    # Section 2: Mid frequency tones (1-3s) - 440Hz, 660Hz, 880Hz
    mid_start = 1.0
    mid_end = 3.0
    mid_mask = (t >= mid_start) & (t < mid_end)
    mid_t = t[mid_mask] - mid_start
    mid_duration = mid_end - mid_start
    tone_duration = mid_duration / 3
    
    # 440Hz (A4)
    tone1_mask = mid_t < tone_duration
    wave_data[mid_mask][tone1_mask] += 0.4 * np.sin(2 * np.pi * 440 * mid_t[tone1_mask])
    
    # 660Hz (E5)
    tone2_mask = (mid_t >= tone_duration) & (mid_t < 2 * tone_duration)
    wave_data[mid_mask][tone2_mask] += 0.4 * np.sin(2 * np.pi * 660 * (mid_t[tone2_mask] - tone_duration))
    
    # 880Hz (A5)
    tone3_mask = mid_t >= 2 * tone_duration
    wave_data[mid_mask][tone3_mask] += 0.4 * np.sin(2 * np.pi * 880 * (mid_t[tone3_mask] - 2 * tone_duration))
    
    # Section 3: High frequency sweep (3-4s) - 1000Hz to 2000Hz
    high_start = 3.0
    high_end = 4.0
    high_mask = (t >= high_start) & (t < high_end)
    high_t = t[high_mask] - high_start
    high_duration = high_end - high_start
    high_freq_start = 1000
    high_freq_end = 2000
    high_freq = high_freq_start + (high_freq_end - high_freq_start) * (high_t / high_duration)
    wave_data[high_mask] += 0.3 * np.sin(2 * np.pi * high_freq * high_t)
    
    # Section 4: Chord progression (4-6s) - Musical chord
    chord_start = 4.0
    chord_end = 6.0
    chord_mask = (t >= chord_start) & (t < chord_end)
    chord_t = t[chord_mask] - chord_start
    
    # C major chord: C4 (261.63Hz), E4 (329.63Hz), G4 (392.00Hz)
    wave_data[chord_mask] += 0.2 * np.sin(2 * np.pi * 261.63 * chord_t)  # C4
    wave_data[chord_mask] += 0.2 * np.sin(2 * np.pi * 329.63 * chord_t)  # E4
    wave_data[chord_mask] += 0.2 * np.sin(2 * np.pi * 392.00 * chord_t)  # G4
    
    # Add fade in/out to prevent clicks
    fade_samples = int(0.1 * sample_rate)  # 0.1 second fade
    if len(wave_data) > 2 * fade_samples:
        # Fade in
        fade_in = np.linspace(0, 1, fade_samples)
        wave_data[:fade_samples] *= fade_in
        # Fade out
        fade_out = np.linspace(1, 0, fade_samples)
        wave_data[-fade_samples:] *= fade_out
    
    # Normalize to prevent clipping
    max_val = np.max(np.abs(wave_data))
    if max_val > 0:
        wave_data = wave_data / max_val * 0.8  # 80% of max to prevent clipping
    
    # Convert to 16-bit integers
    wave_data = (wave_data * 32767).astype(np.int16)
    
    # Create stereo (duplicate for both channels)
    stereo_data = np.column_stack((wave_data, wave_data))
    
    # Save as WAV file
    output_path = "assets/sounds/test_sound.wav"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with wave.open(output_path, 'w') as wav_file:
        wav_file.setnchannels(2)  # Stereo
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(stereo_data.tobytes())
    
    print(f"Generated comprehensive test sound: {output_path}")
    print(f"Duration: {duration}s, Sample Rate: {sample_rate}Hz")
    print("Frequency range: 200Hz - 2000Hz")
    print("Sections:")
    print("  0-1s: Low frequency sweep (200Hz-400Hz)")
    print("  1-3s: Mid frequency tones (440Hz, 660Hz, 880Hz)")
    print("  3-4s: High frequency sweep (1000Hz-2000Hz)")
    print("  4-6s: C major chord (261Hz, 330Hz, 392Hz)")

if __name__ == "__main__":
    generate_test_sound()
