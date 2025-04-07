#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Main Entry Point

This module initializes and runs the Jarvis voice assistant with all core components.
"""

import os
from pathlib import Path
from core.assistant import JarvisAssistant
from core.theme_manager import ThemeManager
from core.user_profiles import ProfileManager
from core.dataset_manager import DatasetManager
from core.display_factory import create_display

def initialize_core_components():
    """
    Initialize all core components required by Jarvis.
    
    Returns:
        tuple: Initialized component instances
    """
    # Initialize managers
    theme_manager = ThemeManager()
    profile_manager = ProfileManager()
    dataset_manager = DatasetManager()
    
    # Initialize UI components
    display = create_display(use_animated=True)
    
    return (
        theme_manager,
        profile_manager,
        dataset_manager,
        display
    )

def main():
    """
    Initialize and run the Jarvis voice assistant with all components.
    """
    try:
        # Initialize all core components
        (
            theme_manager,
            profile_manager,
            dataset_manager,
            display
        ) = initialize_core_components()
        
        # Initialize the main assistant with all components
        assistant = JarvisAssistant(
            theme_manager=theme_manager,
            profile_manager=profile_manager,
            dataset_manager=dataset_manager,
            display=display,
            ui_integrator=None,
            gesture_recognition=None,
            context_awareness=None
        )
        
        # Start the assistant
        assistant.start()
        
    except Exception as e:
        print(f"Error initializing Jarvis: {e}")

if __name__ == "__main__":
    main()