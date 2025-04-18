#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Main Entry Point

This module initializes and runs the Jarvis voice assistant with all core components.
"""

import os
import sys
import signal
import logging
import argparse
from pathlib import Path
from core.assistant import JarvisAssistant
from core.theme_manager import ThemeManager
from core.user_profiles import ProfileManager
from core.dataset_manager import DatasetManager
from core.display_factory import create_display

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def initialize_core_components(headless=False, basic_display=False):
    """
    Initialize all core components required by Jarvis.
    
    Args:
        headless (bool): Whether to run in headless mode (no GUI)
        basic_display (bool): Whether to use basic display instead of animated
    
    Returns:
        tuple: Initialized component instances
    
    Raises:
        RuntimeError: If any component fails to initialize
    """
    components = {}
    try:
        # Initialize managers in order of dependency
        logger.info("Initializing theme manager...")
        components['theme_manager'] = ThemeManager()
        
        logger.info("Initializing profile manager...")
        components['profile_manager'] = ProfileManager()
        
        logger.info("Initializing dataset manager...")
        components['dataset_manager'] = DatasetManager()
        
        # Initialize UI components last
        logger.info(f"Initializing display (headless={headless}, basic_display={basic_display})...")
        components['display'] = create_display(use_animated=not (headless or basic_display), headless=headless)
        
        return (
            components['theme_manager'],
            components['profile_manager'],
            components['dataset_manager'],
            components['display']
        )
        
    except Exception as e:
        # Clean up any initialized components
        for component in components.values():
            try:
                if hasattr(component, 'stop'):
                    component.stop()
            except Exception as cleanup_error:
                logger.error(f"Error during cleanup: {cleanup_error}")
        
        raise RuntimeError(f"Failed to initialize components: {str(e)}") from e

def signal_handler(signum, frame):
    """
    Handle system signals for graceful shutdown.
    """
    logger.info(f"Received signal {signum}. Initiating shutdown...")
    sys.exit(0)

def main():
    """
    Initialize and run the Jarvis voice assistant with all components.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run Jarvis Voice Assistant')
    parser.add_argument('--headless', action='store_true', 
                        help='Run in headless mode without GUI (for web deployments)')
    parser.add_argument('--basic-display', action='store_true',
                        help='Use basic display instead of animated display')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    args = parser.parse_args()
    
    # Set up debug logging if requested
    if args.debug or os.environ.get('JARVIS_DEBUG') == '1':
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('PIL').setLevel(logging.INFO)  # Keep PIL logs less verbose
        logger.debug("Debug logging enabled")
    
    headless_mode = args.headless
    basic_display = args.basic_display
    
    if headless_mode:
        logger.info("Running in headless mode")
    elif basic_display:
        logger.info("Running with basic display")
    else:
        logger.info("Running with animated display")
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    assistant = None
    try:
        logger.info("Starting Jarvis initialization...")
        # Initialize all core components
        (
            theme_manager,
            profile_manager,
            dataset_manager,
            display
        ) = initialize_core_components(headless=headless_mode, basic_display=basic_display)
        
        # Initialize the main assistant with all components
        logger.info("Initializing main assistant...")
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
        logger.info("Starting Jarvis...")
        assistant.start(headless=headless_mode)
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt. Shutting down...")
    except Exception as e:
        logger.error(f"Error running Jarvis: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Ensure proper cleanup
        if assistant:
            try:
                assistant.stop()
                logger.info("Jarvis shutdown complete.")
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")

if __name__ == "__main__":
    main()