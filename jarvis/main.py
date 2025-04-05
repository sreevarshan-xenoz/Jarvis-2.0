#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Main Entry Point

This module initializes and runs the Jarvis voice assistant.
"""

from core.assistant import JarvisAssistant

def main():
    """
    Initialize and run the Jarvis voice assistant.
    """
    assistant = JarvisAssistant()
    assistant.start()

if __name__ == "__main__":
    main()