#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Core Assistant Module

This module contains the main JarvisAssistant class that coordinates
all the voice assistant's functionality.
"""

from core.speech import SpeechEngine
from core.command_handler import CommandHandler
from config.settings import WAKE_WORDS, CONVERSATION_TIMEOUT, CONTINUOUS_MODE
import time

class JarvisAssistant:
    """
    Main assistant class that coordinates speech recognition,
    command processing, and response generation.
    """
    
    def __init__(self, theme_manager=None, profile_manager=None, dataset_manager=None,
                 display=None, ui_integrator=None, gesture_recognition=None, context_awareness=None):
        """
        Initialize the Jarvis assistant with all core components.

        Args:
            theme_manager: Theme management component
            profile_manager: User profile management component
            dataset_manager: Dataset management component
            display: Display interface component
            ui_integrator: UI integration component
            gesture_recognition: Gesture recognition component
            context_awareness: Context awareness component
        """
        self.theme_manager = theme_manager
        self.profile_manager = profile_manager
        self.dataset_manager = dataset_manager
        self.display = display
        self.ui_integrator = ui_integrator
        self.gesture_recognition = gesture_recognition
        self.context_awareness = context_awareness

        self.speech_engine = SpeechEngine()
        self.command_handler = CommandHandler(self.speech_engine)
        self.is_active = False
        self.conversation_active = False
        self.last_interaction_time = 0
        
    def detect_wake_word(self, command):
        """
        Check if the command starts with one of the wake words.
        
        Args:
            command (str): The command to check
            
        Returns:
            bool: True if a wake word is detected, False otherwise
        """
        return any(command.startswith(word) for word in WAKE_WORDS)
    
    def start(self):
        """
        Start the voice assistant and listen for commands.
        """
        self.is_active = True
        self.speech_engine.speak("Jarvis activated. How can I assist you?")
        
        while self.is_active:
            # Check if conversation has timed out
            if self.conversation_active and time.time() - self.last_interaction_time > CONVERSATION_TIMEOUT:
                self.conversation_active = False
                self.speech_engine.display_window.set_animation_state("idle")
            
            # Adjust listen timeout based on conversation state
            listen_timeout = 3 if self.conversation_active else 5
            command = self.speech_engine.listen(timeout=listen_timeout)
            
            if not command:
                continue
            
            # Process command based on conversation state
            if self.detect_wake_word(command) or self.conversation_active:
                # Update conversation state
                self.conversation_active = True
                self.last_interaction_time = time.time()
                
                # Set animation state to conversation active
                self.speech_engine.display_window.set_animation_state("conversation")
                
                # Extract the actual command after the wake word if needed
                if self.detect_wake_word(command) and not CONTINUOUS_MODE:
                    actual_command = command.split(' ', 1)[1] if ' ' in command else ""
                else:
                    actual_command = command
                
                if actual_command:
                    # Set animation state to speaking before processing command
                    self.speech_engine.display_window.set_animation_state("speaking")
                    self.command_handler.process_command(actual_command)
                    # Keep conversation active after command processing
                    self.last_interaction_time = time.time()
                else:
                    self.speech_engine.speak("Yes? I'm listening...")
                    follow_up_command = self.speech_engine.listen()
                    if follow_up_command:
                        self.command_handler.process_command(follow_up_command)
                        # Keep conversation active after command processing
                        self.last_interaction_time = time.time()
    
    def stop(self):
        """
        Stop the voice assistant.
        """
        self.is_active = False
        self.speech_engine.speak("Goodbye!")
        # Stop the display window
        self.speech_engine.display_window.stop()