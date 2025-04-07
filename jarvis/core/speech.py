#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Speech Module

This module handles speech recognition and text-to-speech functionality.
"""

import speech_recognition as sr
import pyttsx3
import threading
import queue
import time
from config.settings import WAKE_WORDS
from core.display_factory import create_display

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
        
        # Initialize display window with enhanced features
        self.display_window = create_display(use_animated=True)
        self.display_window.start()
        
        # Interruption handling
        self.speaking = False
        self.should_interrupt = False
        self.interrupt_event = threading.Event()
        self.background_listener_active = False
        self.background_listener_thread = None
        self.audio_queue = queue.Queue()
    
    def _background_listener(self):
        """
        Background thread that listens for wake words while speaking.
        """
        self.background_listener_active = True
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                while self.speaking and not self.should_interrupt:
                    try:
                        audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=2)
                        self.audio_queue.put(audio)
                    except (sr.WaitTimeoutError, sr.UnknownValueError):
                        continue
                    except Exception as e:
                        print(f"Background listener error: {e}")
                        break
        except Exception as e:
            print(f"Background listener setup error: {e}")
        finally:
            self.background_listener_active = False
    
    def _process_audio_queue(self):
        """
        Process audio queue to detect wake words.
        """
        while self.speaking and not self.should_interrupt:
            try:
                if not self.audio_queue.empty():
                    audio = self.audio_queue.get(block=False)
                    try:
                        command = self.recognizer.recognize_google(audio).lower()
                        print(f"Background recognized: {command}")
                        
                        # Check if command contains wake word
                        if any(word in command for word in WAKE_WORDS):
                            # Don't interrupt if already in conversation mode
                            current_state = getattr(self.display_window, 'animation_state', 'idle')
                            if current_state != "conversation":
                                print("Wake word detected while speaking - interrupting")
                                self.should_interrupt = True
                                self.interrupt_event.set()
                    except sr.UnknownValueError:
                        pass
                    except Exception as e:
                        print(f"Audio processing error: {e}")
            except queue.Empty:
                pass
            time.sleep(0.1)
    
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
        
        # Reset interruption flags
        self.speaking = True
        self.should_interrupt = False
        self.interrupt_event.clear()
        
        # Start background listener if not already running
        if not self.background_listener_active:
            self.background_listener_thread = threading.Thread(target=self._background_listener)
            self.background_listener_thread.daemon = True
            self.background_listener_thread.start()
            
            # Start audio processing thread
            audio_processor = threading.Thread(target=self._process_audio_queue)
            audio_processor.daemon = True
            audio_processor.start()
        
        # Convert to speech with interruption support
        def on_word(name, location, length):
            if self.should_interrupt:
                return False  # Stop speech
            return True
        
        # Store the connection token for proper disconnection
        connection_token = self.engine.connect('started-word', on_word)
        
        # Say the text
        self.engine.say(text)
        self.engine.runAndWait()
        
        # Clean up
        self.speaking = False
        # Properly disconnect using the connection token
        try:
            self.engine.disconnect(connection_token)
        except Exception as e:
            print(f"Warning: Could not disconnect event handler: {e}")
            # Fallback: Create a new engine instance if needed
            # self.engine = pyttsx3.init()
        
        # If interrupted, return to listening state
        if self.should_interrupt:
            print("Speech interrupted - returning to listening state")
            self.display_window.set_animation_state("listening")
    
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