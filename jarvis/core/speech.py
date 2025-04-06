#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Speech Module

This module handles speech recognition and text-to-speech functionality.
"""

import speech_recognition as sr
import pyttsx3
from core.animated_display import AnimatedDisplayWindow

class SpeechEngine:
    """
    Handles speech recognition and text-to-speech functionality.
    """
    
    def __init__(self):
        """
        Initialize speech recognition and text-to-speech engines.
        """
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        
        # Initialize text-to-speech engine
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[0].id)  # Default to male voice
        
        # Initialize animated display window
        self.display_window = AnimatedDisplayWindow()
        self.display_window.start()
    
    def speak(self, text):
        """
        Convert text to speech and display the text output.
        
        Args:
            text (str): The text to be spoken
        """
        # Display text output in console with formatting
        print("\n" + "="*50)
        print(f"🤖 JARVIS: {text}")
        print("="*50 + "\n")
        
        # Set animation state to speaking
        self.display_window.set_animation_state("speaking")
        
        # Display text in animated GUI window
        self.display_window.display(text)
        
        # Convert to speech
        self.engine.say(text)
        self.engine.runAndWait()
    
    def listen(self, timeout=5):
        """
        Listen for voice commands and convert to text.
        
        Args:
            timeout (int): Maximum time to listen for a command in seconds
            
        Returns:
            str: The recognized command as text, or empty string if nothing recognized
        """
        command = ""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print('Listening...')
                # Update animation state to listening
                # Don't change state if already in conversation mode
                current_state = getattr(self.display_window, 'animation_state', 'idle')
                if current_state != "conversation":
                    self.display_window.set_animation_state("listening")
                
                voice = self.recognizer.listen(source, timeout=timeout)
                command = self.recognizer.recognize_google(voice).lower()
                print(f"Recognized: {command}")
                
                # Only set back to idle if we're not in conversation mode
                if current_state != "conversation":
                    self.display_window.set_animation_state("idle")
        except (sr.UnknownValueError, sr.WaitTimeoutError):
            pass  # Nothing recognized or timeout
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
        
        return command
    
    def change_voice(self, voice_index):
        """
        Change the voice used for text-to-speech.
        
        Args:
            voice_index (int): Index of the voice to use
        """
        voices = self.engine.getProperty('voices')
        if 0 <= voice_index < len(voices):
            self.engine.setProperty('voice', voices[voice_index].id)
            return True
        return False