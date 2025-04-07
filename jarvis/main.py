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
from core.gesture_recognition import GestureRecognizer
from core.context_awareness import ContextManager
from core.animated_display_enhanced import EnhancedAnimatedDisplayWindow
from core.ui_integrator import UIIntegrator

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
    display = EnhancedAnimatedDisplayWindow()
    ui_integrator = UIIntegrator(display)
    
    # Initialize recognition systems
    gesture_recognition = GestureRecognizer()
    context_awareness = ContextManager()
    
    return (
        theme_manager,
        profile_manager,
        dataset_manager,
        display,
        ui_integrator,
        gesture_recognition,
        context_awareness
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
            display,
            ui_integrator,
            gesture_recognition,
            context_awareness
        ) = initialize_core_components()
        
        # Initialize the main assistant with all components
        assistant = JarvisAssistant(
            theme_manager=theme_manager,
            profile_manager=profile_manager,
            dataset_manager=dataset_manager,
            display=display,
            ui_integrator=ui_integrator,
            gesture_recognition=gesture_recognition,
            context_awareness=context_awareness
        )
        
        # Start the assistant
        assistant.start()
        
    except Exception as e:
        print(f"Error initializing Jarvis: {e}")

if __name__ == "__main__":
    main()