#!/usr/bin/env python3
"""
Jarvis Assistant - Main Assistant Class

This module provides the main JarvisAssistant class that integrates all components
and provides the core functionality of Jarvis.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("jarvis-assistant")

class JarvisAssistant:
    """
    The main Jarvis Assistant class that integrates all components and
    provides the core functionality of Jarvis.
    """
    
    def __init__(
        self,
        theme_manager=None,
        profile_manager=None,
        dataset_manager=None,
        display=None,
        ui_integrator=None,
        gesture_recognition=None,
        context_awareness=None
    ):
        """
        Initialize the Jarvis Assistant with the required components.
        
        Args:
            theme_manager: The theme manager component
            profile_manager: The profile manager component
            dataset_manager: The dataset manager component
            display: The display component
            ui_integrator: The UI integrator component
            gesture_recognition: The gesture recognition component
            context_awareness: The context awareness component
        """
        self._theme_manager = theme_manager
        self._profile_manager = profile_manager
        self._dataset_manager = dataset_manager
        self._display = display
        self._ui_integrator = ui_integrator
        self._gesture_recognition = gesture_recognition
        self._context_awareness = context_awareness
        
        self._is_running = False
        self._last_command = None
        self._last_response = None
        
        logger.info("JarvisAssistant initialized")
    
    def start(self, headless=False):
        """
        Start the Jarvis Assistant.
        
        Args:
            headless (bool): Whether to run in headless mode
        """
        if self._is_running:
            logger.warning("Jarvis Assistant is already running")
            return
        
        try:
            logger.info("Starting Jarvis Assistant" + (" (headless)" if headless else ""))
            
            # Initialize the display if available
            if self._display:
                self._display.initialize(headless=headless)
                self._display.show_message("Jarvis is starting...")
            
            # Start other components as needed
            # ...
            
            self._is_running = True
            
            if self._display:
                self._display.show_message("Jarvis is ready")
                
            logger.info("Jarvis Assistant started")
            
        except Exception as e:
            logger.error(f"Error starting Jarvis Assistant: {str(e)}")
            self.stop()
            raise
    
    def stop(self):
        """Stop the Jarvis Assistant."""
        if not self._is_running:
            logger.warning("Jarvis Assistant is not running")
            return
        
        try:
            logger.info("Stopping Jarvis Assistant")
            
            # Stop other components as needed
            # ...
            
            # Stop the display if available
            if self._display:
                self._display.show_message("Jarvis is shutting down...")
                self._display.stop()
            
            self._is_running = False
            
            logger.info("Jarvis Assistant stopped")
            
        except Exception as e:
            logger.error(f"Error stopping Jarvis Assistant: {str(e)}")
            self._is_running = False
            raise
    
    def process_command(self, command: str, web_mode=False) -> Dict[str, Any]:
        """
        Process a command and return the result.
        
        Args:
            command (str): The command to process
            web_mode (bool): Whether the command is coming from the web interface
            
        Returns:
            Dict[str, Any]: The result of processing the command
        """
        if not self._is_running:
            logger.warning("Jarvis Assistant is not running, can't process command")
            return {
                "success": False,
                "response": "Jarvis is not running. Please start Jarvis first.",
                "data": {}
            }
        
        try:
            logger.info(f"Processing command: {command}" + (" (web mode)" if web_mode else ""))
            
            self._last_command = command
            
            # Log the command to display if available and not in web mode
            if self._display and not web_mode:
                self._display.show_message(f"Command: {command}")
            
            # Process the command based on type/pattern
            if command.lower().startswith("hello") or command.lower().startswith("hi"):
                response = "Hello! I am Jarvis, your personal assistant. How can I help you today?"
            elif command.lower() == "status":
                response = "I'm operational and running normally. All systems are functioning properly."
            elif command.lower().startswith("time"):
                import datetime
                now = datetime.datetime.now()
                response = f"The current time is {now.strftime('%H:%M:%S')}."
            elif command.lower().startswith("date"):
                import datetime
                now = datetime.datetime.now()
                response = f"Today's date is {now.strftime('%A, %B %d, %Y')}."
            elif command.lower().startswith("weather"):
                response = "I'm sorry, weather functionality is not implemented yet."
            else:
                response = f"I received your command: '{command}'. However, I don't have specific functionality for that yet."
            
            self._last_response = response
            
            # Show the response in the display if available and not in web mode
            if self._display and not web_mode:
                self._display.show_message(f"Jarvis: {response}")
            
            logger.info(f"Processed command: {command}")
            
            return {
                "success": True,
                "response": response,
                "data": {
                    "command": command,
                    "timestamp": import_time().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
        except Exception as e:
            error_msg = f"Error processing command: {str(e)}"
            logger.error(error_msg)
            
            if self._display and not web_mode:
                self._display.show_message(f"Error: {error_msg}")
            
            return {
                "success": False,
                "response": error_msg,
                "data": {
                    "command": command,
                    "error": str(e)
                }
            }

# Helper function to import time module on demand
def import_time():
    """Import time module and return it."""
    import datetime
    return datetime.datetime.now()