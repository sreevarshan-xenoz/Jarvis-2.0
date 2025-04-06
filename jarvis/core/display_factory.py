#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Display Factory Module

This module provides a factory function to create the appropriate display window
based on configuration and available features.
"""

# Import display options
from core.display import DisplayWindow
from core.animated_display import AnimatedDisplayWindow as AnimatedDisplay


def create_display(use_animated=True):
    """
    Create the appropriate display window based on configuration.
    
    Args:
        use_animated (bool): Whether to use animated display
        
    Returns:
        DisplayWindow: The created display window instance
    """
    if use_animated:
        return AnimatedDisplay()
    else:
        return DisplayWindow()