#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Media Service Module

This module handles media playback functionality.
"""

# Removed top-level import: import pywhatkit
from pywhatkit.core.exceptions import InternetException # Import specific exception

class MediaService:
    """
    Provides media playback functionality.
    """
    
    def __init__(self):
        """
        Initialize the media service.
        """
        pass
    
    def play_youtube(self, query):
        """
        Play a video on YouTube based on the search query.
        
        Args:
            query (str): The search query for YouTube
        """
        try:
            import pywhatkit # Import moved inside the function
            pywhatkit.playonyt(query)
            print(f"Playing '{query}' on YouTube.")
            return True
        except InternetException:
            print("Error: Cannot connect to YouTube. Please check your internet connection.")
            return False
        except Exception as e:
            print(f"Error playing YouTube video: {str(e)}")
            return False
    
    def play_music(self, song_name):
        """
        Play music from a local library or streaming service.
        This is a placeholder for future implementation.
        
        Args:
            song_name (str): The name of the song to play
        """
        # This could be implemented with a music streaming API or local music player
        # For now, we'll just use YouTube
        print(f"Attempting to play music: {song_name}")
        return self.play_youtube(song_name + " music")