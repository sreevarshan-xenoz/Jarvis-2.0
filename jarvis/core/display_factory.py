#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Display Factory Module

This module provides a factory function to create the appropriate display window
based on configuration and available features.
"""

# Import display options
from core.display import DisplayWindow
from core.animated_display import AnimatedDisplayWindow

# Try to import enhanced display
try:
    from core.animated_display_enhanced import EnhancedAnimatedDisplayWindow
    ENHANCED_AVAILABLE = True
except ImportError:
    ENHANCED_AVAILABLE = False

def create_display(use_enhanced=True, use_animated=True):
    """
    Create the appropriate display window based on configuration and available features.
    
    Args:
        use_enhanced (bool): Whether to use enhanced animated display if available
        use_animated (bool): Whether to use animated display at all
        
    Returns:
        DisplayWindow: The created display window instance
    """
    if use_animated:
        if use_enhanced and ENHANCED_AVAILABLE:
            return EnhancedAnimatedDisplayWindow()
        else:
            return AnimatedDisplayWindow()
    else:
        return DisplayWindow()