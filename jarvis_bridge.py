#!/usr/bin/env python3
"""
Jarvis Bridge - Connect Jarvis core functionality to AURA web interface

This module provides a bridge between the Jarvis core system and the AURA API server,
allowing the web interface to access Jarvis functionality.
"""

import os
import sys
import threading
import logging
import importlib.util
import time
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("jarvis-bridge")

# Add the core Jarvis directory to Python path if needed
jarvis_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'jarvis'))
if jarvis_path not in sys.path:
    sys.path.insert(0, jarvis_path)

class JarvisBridge:
    """Bridge between Jarvis core system and the AURA web interface"""
    
    def __init__(self):
        self._assistant = None
        self._theme_manager = None
        self._profile_manager = None
        self._dataset_manager = None
        self._display = None
        self._initialized = False
        self._lock = threading.Lock()
        self._last_response = ""
        self._is_running = False
        
    def initialize(self) -> bool:
        """Initialize the Jarvis core components"""
        with self._lock:
            if self._initialized:
                return True
                
            try:
                # Import the required Jarvis modules
                logger.info("Importing Jarvis core modules...")
                from core.assistant import JarvisAssistant
                from core.theme_manager import ThemeManager
                from core.user_profiles import ProfileManager
                from core.dataset_manager import DatasetManager
                from core.display_factory import create_display
                
                # Initialize core components
                logger.info("Initializing Jarvis theme manager...")
                self._theme_manager = ThemeManager()
                
                logger.info("Initializing Jarvis profile manager...")
                self._profile_manager = ProfileManager()
                
                logger.info("Initializing Jarvis dataset manager...")
                self._dataset_manager = DatasetManager()
                
                # Use headless display for web integration
                logger.info("Initializing Jarvis display (headless)...")
                self._display = create_display(use_animated=False, headless=True)
                
                # Initialize the main assistant
                logger.info("Initializing Jarvis assistant...")
                self._assistant = JarvisAssistant(
                    theme_manager=self._theme_manager,
                    profile_manager=self._profile_manager,
                    dataset_manager=self._dataset_manager,
                    display=self._display,
                    ui_integrator=None,
                    gesture_recognition=None,
                    context_awareness=None
                )
                
                self._initialized = True
                logger.info("Jarvis bridge initialization complete")
                return True
                
            except ImportError as e:
                logger.error(f"Failed to import Jarvis modules: {str(e)}")
                return False
            except Exception as e:
                logger.error(f"Failed to initialize Jarvis: {str(e)}")
                return False
    
    def start(self) -> bool:
        """Start the Jarvis assistant in a separate thread"""
        if not self._initialized and not self.initialize():
            return False
            
        if self._is_running:
            return True
            
        try:
            # Start in a non-blocking way for web integration
            threading.Thread(
                target=self._start_assistant_thread,
                daemon=True
            ).start()
            
            self._is_running = True
            return True
        except Exception as e:
            logger.error(f"Failed to start Jarvis: {str(e)}")
            return False
    
    def _start_assistant_thread(self):
        """Run the assistant in a separate thread"""
        try:
            if self._assistant:
                # Override standard input/output for web integration
                self._assistant.start(headless=True)
        except Exception as e:
            logger.error(f"Error in Jarvis thread: {str(e)}")
            self._is_running = False
    
    def stop(self) -> bool:
        """Stop the Jarvis assistant"""
        if not self._initialized or not self._is_running:
            return True
            
        try:
            if self._assistant:
                self._assistant.stop()
            self._is_running = False
            return True
        except Exception as e:
            logger.error(f"Failed to stop Jarvis: {str(e)}")
            return False
    
    def process_command(self, command: str) -> Dict[str, Any]:
        """Process a command through the Jarvis assistant"""
        if not self._initialized and not self.initialize():
            return {
                "success": False,
                "message": "Jarvis is not initialized",
                "command": command
            }
            
        if not self._is_running and not self.start():
            return {
                "success": False,
                "message": "Jarvis is not running",
                "command": command
            }
            
        try:
            # Send command to assistant
            if self._assistant:
                # Clear any previous response
                self._last_response = ""
                
                # Process command through Jarvis
                result = self._assistant.process_command(command, web_mode=True)
                
                # Store the response
                self._last_response = result.get("response", "")
                
                return {
                    "success": True,
                    "message": self._last_response,
                    "command": command,
                    "data": result.get("data", {})
                }
            else:
                return {
                    "success": False,
                    "message": "Jarvis assistant is not available",
                    "command": command
                }
        except Exception as e:
            logger.error(f"Error processing command: {str(e)}")
            return {
                "success": False,
                "message": f"Error: {str(e)}",
                "command": command
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the Jarvis system"""
        return {
            "initialized": self._initialized,
            "running": self._is_running,
            "components": {
                "theme_manager": self._theme_manager is not None,
                "profile_manager": self._profile_manager is not None,
                "dataset_manager": self._dataset_manager is not None,
                "display": self._display is not None,
                "assistant": self._assistant is not None
            }
        }

# Create a singleton instance
jarvis_bridge = JarvisBridge()

# Helper functions for API integration
def initialize_jarvis() -> bool:
    """Initialize the Jarvis bridge"""
    return jarvis_bridge.initialize()

def start_jarvis() -> bool:
    """Start the Jarvis assistant"""
    return jarvis_bridge.start()

def stop_jarvis() -> bool:
    """Stop the Jarvis assistant"""
    return jarvis_bridge.stop()

def process_jarvis_command(command: str) -> Dict[str, Any]:
    """Process a command through Jarvis"""
    return jarvis_bridge.process_command(command)

def get_jarvis_status() -> Dict[str, Any]:
    """Get Jarvis system status"""
    return jarvis_bridge.get_status() 