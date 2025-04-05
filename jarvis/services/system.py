#!/usr/bin/env python3
"""
Jarvis Voice Assistant - System Service Module

This module handles system control functionality like volume control.
"""

import os
import platform
from config.settings import VOLUME_STEP

class SystemService:
    """
    Provides system control functionality.
    """
    
    def __init__(self):
        """
        Initialize the system service.
        """
        self.system = platform.system()
    
    def volume_up(self):
        """
        Increase system volume.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.system == "Windows":
                os.system(f"nircmd.exe changesysvolume {VOLUME_STEP}")
            elif self.system == "Darwin":  # macOS
                os.system("osascript -e 'set volume output volume (output volume of (get volume settings) + 10)'")
            elif self.system == "Linux":
                os.system("amixer -D pulse sset Master 10%+")
            return True
        except Exception as e:
            print(f"Error adjusting volume: {str(e)}")
            return False
    
    def volume_down(self):
        """
        Decrease system volume.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.system == "Windows":
                os.system(f"nircmd.exe changesysvolume -{VOLUME_STEP}")
            elif self.system == "Darwin":  # macOS
                os.system("osascript -e 'set volume output volume (output volume of (get volume settings) - 10)'")
            elif self.system == "Linux":
                os.system("amixer -D pulse sset Master 10%-")
            return True
        except Exception as e:
            print(f"Error adjusting volume: {str(e)}")
            return False
    
    def mute(self):
        """
        Mute system volume.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.system == "Windows":
                os.system("nircmd.exe mutesysvolume 1")
            elif self.system == "Darwin":  # macOS
                os.system("osascript -e 'set volume output muted true'")
            elif self.system == "Linux":
                os.system("amixer -D pulse set Master mute")
            return True
        except Exception as e:
            print(f"Error muting volume: {str(e)}")
            return False
    
    def unmute(self):
        """
        Unmute system volume.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.system == "Windows":
                os.system("nircmd.exe mutesysvolume 0")
            elif self.system == "Darwin":  # macOS
                os.system("osascript -e 'set volume output muted false'")
            elif self.system == "Linux":
                os.system("amixer -D pulse set Master unmute")
            return True
        except Exception as e:
            print(f"Error unmuting volume: {str(e)}")
            return False