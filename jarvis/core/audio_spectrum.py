#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Audio Spectrum Visualization Module

This module provides real-time FFT (Fast Fourier Transform) analysis of audio input
for visualization in the Jarvis animated UI.
"""

import numpy as np
import pygame
import math
from collections import deque

class AudioSpectrum:
    """
    Provides real-time audio spectrum analysis using FFT for visualization.
    """
    
    def __init__(self, sample_rate=44100, chunk_size=1024, history_size=5):
        """
        Initialize the audio spectrum analyzer.
        
        Args:
            sample_rate (int): Audio sample rate in Hz
            chunk_size (int): Size of audio chunks to process (must be power of 2 for FFT)
            history_size (int): Number of frames to keep in history for smoothing
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.history_size = history_size
        
        # Initialize pygame mixer for audio processing
        pygame.mixer.init(frequency=sample_rate, size=-16, channels=1)
        
        # Frequency bands for visualization
        self.bands = {
            'bass': (20, 250),      # Bass frequencies
            'mid': (250, 2000),     # Mid-range frequencies
            'treble': (2000, 10000) # Treble frequencies
        }
        
        # Color mapping for frequency bands
        self.band_colors = {
            'bass': "#FF5252",    # Red for bass
            'mid': "#FFFF00",     # Yellow for mid
            'treble': "#00E676"   # Green for treble
        }
        
        # Initialize spectrum data storage
        self.spectrum_history = deque(maxlen=history_size)
        self.current_spectrum = np.zeros(chunk_size // 2)
        self.band_energy = {band: 0.0 for band in self.bands}
        
        # For audio capture
        self.is_capturing = False
        self.audio_buffer = np.zeros(chunk_size, dtype=np.int16)
    
    def start_capture(self):
        """
        Start audio capture for spectrum analysis.
        """
        if not self.is_capturing:
            try:
                # Initialize pygame audio capture
                pygame.mixer.quit()  # Ensure clean state
                pygame.mixer.init(frequency=self.sample_rate, size=-16, channels=1)
                pygame.mixer.set_num_channels(1)
                
                # Start listening
                pygame.mixer.Channel(0).play(pygame.mixer.Sound(buffer=bytes(self.audio_buffer)))
                self.is_capturing = True
                return True
            except Exception as e:
                print(f"Error starting audio capture: {e}")
                return False
        return True
    
    def stop_capture(self):
        """
        Stop audio capture.
        """
        if self.is_capturing:
            try:
                pygame.mixer.quit()
                self.is_capturing = False
                return True
            except Exception as e:
                print(f"Error stopping audio capture: {e}")
                return False
        return True
    
    def update(self, audio_data=None):
        """
        Update spectrum analysis with new audio data.
        
        Args:
            audio_data (numpy.ndarray): Raw audio data to analyze. If None, will try to capture from mic.
            
        Returns:
            dict: Dictionary containing spectrum data and band energies
        """
        if audio_data is None and self.is_capturing:
            # Try to get audio data from pygame capture
            try:
                # This is a simplified approach - in a real implementation,
                # you would use pygame.mixer.get_raw() or similar
                # For now, we'll generate some test data
                audio_data = np.random.randint(-32768, 32767, self.chunk_size, dtype=np.int16)
            except Exception as e:
                print(f"Error capturing audio: {e}")
                audio_data = np.zeros(self.chunk_size, dtype=np.int16)
        elif audio_data is None:
            # No data provided and not capturing
            audio_data = np.zeros(self.chunk_size, dtype=np.int16)
        
        # Ensure audio_data is the right size
        if len(audio_data) != self.chunk_size:
            # Resize or pad data to match chunk_size
            if len(audio_data) > self.chunk_size:
                audio_data = audio_data[:self.chunk_size]
            else:
                padding = np.zeros(self.chunk_size - len(audio_data), dtype=audio_data.dtype)
                audio_data = np.concatenate([audio_data, padding])
        
        # Apply window function to reduce spectral leakage
        window = np.hanning(self.chunk_size)
        windowed_data = audio_data * window
        
        # Compute FFT
        fft_data = np.fft.rfft(windowed_data)
        
        # Convert to magnitude spectrum (absolute values)
        magnitude = np.abs(fft_data) / self.chunk_size
        
        # Convert to dB scale (log scale) with noise floor
        noise_floor_db = -120
        spectrum_db = 20 * np.log10(magnitude + 1e-10)  # Add small value to avoid log(0)
        spectrum_db = np.clip(spectrum_db, noise_floor_db, 0)
        
        # Normalize to 0-1 range for visualization
        normalized_spectrum = (spectrum_db - noise_floor_db) / -noise_floor_db
        
        # Store in history for smoothing
        self.spectrum_history.append(normalized_spectrum)
        
        # Apply smoothing by averaging the history
        if len(self.spectrum_history) > 0:
            self.current_spectrum = np.mean(self.spectrum_history, axis=0)
        else:
            self.current_spectrum = normalized_spectrum
        
        # Calculate energy in each frequency band
        freqs = np.fft.rfftfreq(self.chunk_size, 1.0/self.sample_rate)
        for band_name, (low_freq, high_freq) in self.bands.items():
            # Find indices corresponding to this frequency range
            band_indices = np.where((freqs >= low_freq) & (freqs <= high_freq))[0]
            if len(band_indices) > 0:
                # Calculate average energy in this band
                self.band_energy[band_name] = np.mean(self.current_spectrum[band_indices])
            else:
                self.band_energy[band_name] = 0.0
        
        return {
            'spectrum': self.current_spectrum,
            'band_energy': self.band_energy,
            'freqs': freqs
        }
    
    def get_visualization_data(self, num_points=64, smoothing=0.7):
        """
        Get processed data suitable for visualization.
        
        Args:
            num_points (int): Number of points to return (will resample the spectrum)
            smoothing (float): Smoothing factor between 0 and 1
            
        Returns:
            dict: Visualization-ready data including spectrum and band energies
        """
        # Resample spectrum to desired number of points
        if len(self.current_spectrum) > num_points:
            # Use logarithmic resampling to emphasize lower frequencies
            indices = np.logspace(
                np.log10(1), 
                np.log10(len(self.current_spectrum)), 
                num_points, 
                dtype=int
            ) - 1
            resampled_spectrum = self.current_spectrum[indices]
        else:
            # If we need more points than we have, interpolate
            indices = np.linspace(0, len(self.current_spectrum)-1, num_points)
            resampled_spectrum = np.interp(indices, np.arange(len(self.current_spectrum)), self.current_spectrum)
        
        # Apply additional smoothing if needed
        if hasattr(self, 'previous_resampled') and smoothing > 0:
            smoothed_spectrum = smoothing * self.previous_resampled + (1 - smoothing) * resampled_spectrum
            self.previous_resampled = smoothed_spectrum
        else:
            smoothed_spectrum = resampled_spectrum
            self.previous_resampled = resampled_spectrum
        
        # Apply some post-processing for better visualization
        # Boost the values a bit for more dramatic effect
        visualization_spectrum = np.power(smoothed_spectrum, 0.8) * 1.2
        
        # Clip to 0-1 range
        visualization_spectrum = np.clip(visualization_spectrum, 0, 1)
        
        return {
            'spectrum': visualization_spectrum,
            'band_energy': self.band_energy,
            'num_points': num_points
        }
    
    def get_band_colors(self):
        """
        Get the color mapping for frequency bands.
        
        Returns:
            dict: Mapping of band names to hex color codes
        """
        return self.band_colors
    
    def simulate_audio_input(self, intensity=0.5, complexity=0.7):
        """
        Generate simulated audio input for testing visualization.
        
        Args:
            intensity (float): Overall intensity of the simulated audio (0-1)
            complexity (float): Complexity of the waveform (0-1)
            
        Returns:
            dict: Simulated spectrum data
        """
        # Generate base frequencies with different amplitudes
        t = np.arange(self.chunk_size) / self.sample_rate
        
        # Create a complex waveform with multiple frequencies
        waveform = np.zeros(self.chunk_size)
        
        # Add bass frequencies (low)
        bass_freq = 80 + 40 * np.sin(time.time() * 0.5)
        waveform += 0.7 * intensity * np.sin(2 * np.pi * bass_freq * t)
        
        # Add mid frequencies
        if complexity > 0.3:
            mid_freq = 800 + 200 * np.sin(time.time() * 0.8)
            waveform += 0.5 * intensity * np.sin(2 * np.pi * mid_freq * t)
        
        # Add high frequencies
        if complexity > 0.6:
            high_freq = 4000 + 1000 * np.sin(time.time() * 1.2)
            waveform += 0.3 * intensity * np.sin(2 * np.pi * high_freq * t)
        
        # Add some noise
        noise_level = 0.1 * complexity
        waveform += noise_level * np.random.randn(self.chunk_size)
        
        # Convert to int16 audio format
        audio_data = (waveform * 32767).astype(np.int16)
        
        # Process this simulated audio
        return self.update(audio_data)