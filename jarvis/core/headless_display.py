#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Headless Display Module

This module provides a simple headless implementation for use with web interfaces.
"""

import logging

logger = logging.getLogger("headless-display")

class HeadlessDisplay:
    """
    Provides a headless interface for displaying assistant responses.
    """
    
    def __init__(self):
        """
        Initialize the headless display.
        """
        self.is_running = False
        self.messages = []
        logger.info("HeadlessDisplay initialized")
    
    def initialize(self, headless=True):
        """
        Initialize the display (no-op for headless display).
        
        Args:
            headless (bool): Whether to run in headless mode (ignored)
        """
        logger.info("HeadlessDisplay initialized in headless mode")
        self.is_running = True
    
    def start(self):
        """
        Start the display (no-op for headless display).
        """
        logger.info("HeadlessDisplay started")
        self.is_running = True
    
    def show_message(self, text):
        """
        Log a message (does not display graphically).
        
        Args:
            text (str): The text to log
        """
        logger.info(f"Message: {text}")
        self.messages.append(text)
    
    def display(self, text):
        """
        Display a response (alias for show_message).
        
        Args:
            text (str): The text to display
        """
        self.show_message(text)
    
    def stop(self):
        """
        Stop the display.
        """
        logger.info("HeadlessDisplay stopped")
        self.is_running = False
            
    def set_animation_state(self, state):
        """
        Set the animation state (no-op for headless display).
        
        Args:
            state (str): Animation state ('idle', 'listening', 'speaking', or 'conversation')
        """
        # No animation state changes in headless display
        pass
    
    def get_messages(self):
        """
        Get all messages that have been displayed.
        
        Returns:
            list: List of messages
        """
        return self.messages 