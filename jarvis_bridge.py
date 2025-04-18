#!/usr/bin/env python3
"""
AURA Core Bridge - Connect AURA core functionality to web interface

This module provides a bridge between the AURA core system and the API server,
allowing the web interface to access AURA AI functionality.
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
logger = logging.getLogger("aura-bridge")

# Add the core directory to Python path if needed
aura_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'jarvis'))
if aura_path not in sys.path:
    sys.path.insert(0, aura_path)

class AuraBridge:
    """Bridge between AURA core system and the web interface"""
    
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
        """Initialize the AURA core components"""
        with self._lock:
            if self._initialized:
                return True
                
            try:
                # Import the required core modules
                logger.info("Importing AURA core modules...")
                from core.assistant import JarvisAssistant
                from core.theme_manager import ThemeManager
                from core.user_profiles import ProfileManager
                from core.dataset_manager import DatasetManager
                from core.display_factory import create_display
                
                # Initialize core components
                logger.info("Initializing AURA theme manager...")
                self._theme_manager = ThemeManager()
                
                logger.info("Initializing AURA profile manager...")
                self._profile_manager = ProfileManager()
                
                logger.info("Initializing AURA dataset manager...")
                self._dataset_manager = DatasetManager()
                
                # Use headless display for web integration
                logger.info("Initializing AURA display (headless)...")
                self._display = create_display(use_animated=False, headless=True)
                
                # Initialize the main assistant
                logger.info("Initializing AURA assistant...")
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
                logger.info("AURA bridge initialization complete")
                return True
                
            except ImportError as e:
                logger.error(f"Failed to import AURA modules: {str(e)}")
                return False
            except Exception as e:
                logger.error(f"Failed to initialize AURA: {str(e)}")
                return False
    
    def start(self) -> bool:
        """Start the AURA assistant in a separate thread"""
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
            logger.error(f"Failed to start AURA: {str(e)}")
            return False
    
    def _start_assistant_thread(self):
        """Run the assistant in a separate thread"""
        try:
            if self._assistant:
                # Override standard input/output for web integration
                self._assistant.start(headless=True)
        except Exception as e:
            logger.error(f"Error in AURA thread: {str(e)}")
            self._is_running = False
    
    def stop(self) -> bool:
        """Stop the AURA assistant"""
        if not self._initialized or not self._is_running:
            return True
            
        try:
            if self._assistant:
                self._assistant.stop()
            self._is_running = False
            return True
        except Exception as e:
            logger.error(f"Failed to stop AURA: {str(e)}")
            return False
    
    def process_command(self, command: str) -> Dict[str, Any]:
        """Process a command through the AURA assistant"""
        if not self._initialized and not self.initialize():
            return {
                "success": False,
                "message": "AURA is not initialized",
                "command": command
            }
            
        if not self._is_running and not self.start():
            return {
                "success": False,
                "message": "AURA is not running",
                "command": command
            }
            
        try:
            # Send command to assistant
            if self._assistant:
                # Clear any previous response
                self._last_response = ""
                
                # Process command through AURA
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
                    "message": "AURA assistant is not available",
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
        """Get the current status of the AURA system"""
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
aura_bridge = AuraBridge()

def initialize_aura() -> bool:
    """Initialize the AURA core system"""
    return aura_bridge.initialize()
    
def start_aura() -> bool:
    """Start the AURA assistant"""
    return aura_bridge.start()
    
def stop_aura() -> bool:
    """Stop the AURA assistant"""
    return aura_bridge.stop()
    
def process_aura_command(command: str) -> Dict[str, Any]:
    """Process a command through the AURA assistant"""
    return aura_bridge.process_command(command)
    
def get_aura_status() -> Dict[str, Any]:
    """Get the current status of the AURA system"""
    return aura_bridge.get_status() 