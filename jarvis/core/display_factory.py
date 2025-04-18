#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Display Factory Module

This module provides a factory function to create the appropriate display window
based on configuration and available features.
"""

import logging

# Set up logger
logger = logging.getLogger("display-factory")

# Import display options
from core.display import DisplayWindow

# Try to import animated display, but fall back if dependencies are missing
try:
    from core.animated_display import AnimatedDisplayWindow as AnimatedDisplay
    ANIMATED_DISPLAY_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Could not import AnimatedDisplayWindow: {e}")
    logger.warning("Animated display unavailable - reverting to basic display")
    ANIMATED_DISPLAY_AVAILABLE = False

from core.headless_display import HeadlessDisplay


def create_display(use_animated=True, headless=False):
    """
    Create the appropriate display window based on configuration.
    
    Args:
        use_animated (bool): Whether to use animated display
        headless (bool): Whether to use headless display (no GUI)
        
    Returns:
        Display: The created display instance
    """
    if headless:
        logger.info("Creating headless display")
        return HeadlessDisplay()
    elif use_animated and ANIMATED_DISPLAY_AVAILABLE:
        try:
            logger.info("Creating animated display")
            return AnimatedDisplay()
        except Exception as e:
            logger.error(f"Failed to create animated display: {e}")
            logger.warning("Falling back to basic display")
            return DisplayWindow()
    else:
        logger.info("Creating basic display")
        return DisplayWindow()