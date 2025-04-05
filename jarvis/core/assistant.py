#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Core Assistant Module

This module contains the main JarvisAssistant class that coordinates
all the voice assistant's functionality.
"""

from core.speech import SpeechEngine
from core.command_handler import CommandHandler
from config.settings import WAKE_WORDS

class JarvisAssistant:
    """
    Main assistant class that coordinates speech recognition,
    command processing, and response generation.
    """
    
    def __init__(self):
        """
        Initialize the Jarvis assistant with speech engine and command handler.
        """
        self.speech_engine = SpeechEngine()
        self.command_handler = CommandHandler(self.speech_engine)
        self.is_active = False
        
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
            command = self.speech_engine.listen()
            
            if not command:
                continue
                
            if self.detect_wake_word(command):
                # Extract the actual command after the wake word
                actual_command = command.split(' ', 1)[1] if ' ' in command else ""
                
                if actual_command:
                    self.command_handler.process_command(actual_command)
                else:
                    self.speech_engine.speak("Yes? I'm listening...")
                    follow_up_command = self.speech_engine.listen()
                    if follow_up_command:
                        self.command_handler.process_command(follow_up_command)
    
    def stop(self):
        """
        Stop the voice assistant.
        """
        self.is_active = False
        self.speech_engine.speak("Goodbye!")