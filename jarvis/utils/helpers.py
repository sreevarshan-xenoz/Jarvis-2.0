#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Helper Utilities

This module contains utility functions that can be used across the project.
"""

import datetime
import random
import string

def get_greeting():
    """
    Get a time-appropriate greeting.
    
    Returns:
        str: A greeting appropriate for the current time of day
    """
    hour = datetime.datetime.now().hour
    
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 18:
        return "Good afternoon"
    else:
        return "Good evening"

def generate_id(length=8):
    """
    Generate a random ID string.
    
    Args:
        length (int): Length of the ID to generate
        
    Returns:
        str: A random ID string
    """
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def extract_city_from_command(command):
    """
    Extract city name from a weather command.
    
    Args:
        command (str): The command containing a city name
        
    Returns:
        str: The extracted city name or empty string if not found
    """
    # Common weather command patterns
    patterns = [
        "weather in ",
        "weather for ",
        "weather at ",
        "what's the weather in ",
        "what is the weather in ",
        "how's the weather in ",
        "how is the weather in "
    ]
    
    for pattern in patterns:
        if pattern in command:
            return command.split(pattern)[1].strip()
    
    # If no pattern matches but 'weather' is in the command,
    # try to extract the city name after 'weather'
    if 'weather' in command:
        parts = command.split('weather', 1)
        if len(parts) > 1 and parts[1].strip():
            # Remove common prepositions
            city = parts[1].strip()
            for prep in ['in', 'for', 'at', 'of']:
                if city.startswith(prep + ' '):
                    city = city[len(prep) + 1:]
            return city.strip()
    
    return ""