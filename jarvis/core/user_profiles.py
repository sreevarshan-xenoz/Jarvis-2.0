#!/usr/bin/env python3
"""
Jarvis Voice Assistant - User Profiles Module

This module manages user profiles for personalized interactions.
"""

import os
import json
import datetime
from pathlib import Path

class UserProfile:
    """
    Represents a user profile with personalized settings and interaction history.
    """
    
    def __init__(self, name, voice_id=0):
        """
        Initialize a user profile.
        
        Args:
            name (str): The user's name
            voice_id (int): The preferred voice ID for this user
        """
        self.name = name
        self.voice_id = voice_id
        self.preferences = {
            "wake_word": "jarvis",
            "theme": "dark",
            "volume": 75,
            "speaking_rate": 180,
            "favorite_sites": [],
            "favorite_apps": []
        }
        self.interaction_history = []
        self.frequent_commands = {}
        self.created_at = datetime.datetime.now().isoformat()
        self.last_interaction = None
    
    def add_interaction(self, command, response):
        """
        Add an interaction to the user's history.
        
        Args:
            command (str): The command given by the user
            response (str): The response from Jarvis
        """
        timestamp = datetime.datetime.now().isoformat()
        self.interaction_history.append({
            "timestamp": timestamp,
            "command": command,
            "response": response
        })
        
        # Limit history size
        if len(self.interaction_history) > 100:
            self.interaction_history = self.interaction_history[-100:]
        
        # Update frequent commands
        command_key = command.lower()
        self.frequent_commands[command_key] = self.frequent_commands.get(command_key, 0) + 1
        
        # Update last interaction time
        self.last_interaction = timestamp
    
    def update_preference(self, key, value):
        """
        Update a user preference.
        
        Args:
            key (str): The preference key
            value: The preference value
        """
        if key in self.preferences:
            self.preferences[key] = value
    
    def get_greeting(self):
        """
        Get a personalized greeting based on time of day and user history.
        
        Returns:
            str: A personalized greeting
        """
        hour = datetime.datetime.now().hour
        
        if hour < 12:
            time_greeting = "Good morning"
        elif hour < 18:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"
        
        return f"{time_greeting}, {self.name}. How can I assist you today?"
    
    def to_dict(self):
        """
        Convert the profile to a dictionary for serialization.
        
        Returns:
            dict: The profile as a dictionary
        """
        return {
            "name": self.name,
            "voice_id": self.voice_id,
            "preferences": self.preferences,
            "interaction_history": self.interaction_history,
            "frequent_commands": self.frequent_commands,
            "created_at": self.created_at,
            "last_interaction": self.last_interaction
        }

class ProfileManager:
    """
    Manages user profiles, including loading, saving, and switching between profiles.
    """
    
    def __init__(self):
        """
        Initialize the profile manager.
        """
        self.profiles_dir = Path(os.path.dirname(os.path.dirname(__file__))) / "data" / "profiles"
        self.profiles = {}
        self.active_profile = None
        
        # Create profiles directory if it doesn't exist
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing profiles
        self._load_profiles()
        
        # Create default profile if no profiles exist
        if not self.profiles:
            self.create_profile("User")
        
        # Set the first profile as active if none is active
        if not self.active_profile and self.profiles:
            self.active_profile = list(self.profiles.values())[0]
    
    def _load_profiles(self):
        """
        Load profiles from disk.
        """
        for profile_file in self.profiles_dir.glob("*.json"):
            try:
                with open(profile_file, "r") as f:
                    profile_data = json.load(f)
                    
                profile = UserProfile(profile_data["name"], profile_data["voice_id"])
                profile.preferences = profile_data["preferences"]
                profile.interaction_history = profile_data["interaction_history"]
                profile.frequent_commands = profile_data["frequent_commands"]
                profile.created_at = profile_data["created_at"]
                profile.last_interaction = profile_data["last_interaction"]
                
                self.profiles[profile.name.lower()] = profile
            except Exception as e:
                print(f"Error loading profile {profile_file}: {e}")
    
    def save_profile(self, profile):
        """
        Save a profile to disk.
        
        Args:
            profile (UserProfile): The profile to save
        """
        profile_path = self.profiles_dir / f"{profile.name.lower()}.json"
        
        try:
            with open(profile_path, "w") as f:
                json.dump(profile.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Error saving profile {profile.name}: {e}")
    
    def create_profile(self, name, voice_id=0):
        """
        Create a new user profile.
        
        Args:
            name (str): The user's name
            voice_id (int): The preferred voice ID for this user
            
        Returns:
            UserProfile: The created profile
        """
        profile = UserProfile(name, voice_id)
        self.profiles[name.lower()] = profile
        self.save_profile(profile)
        
        # Set as active if it's the first profile
        if len(self.profiles) == 1:
            self.active_profile = profile
        
        return profile
    
    def get_profile(self, name):
        """
        Get a profile by name.
        
        Args:
            name (str): The profile name
            
        Returns:
            UserProfile: The profile, or None if not found
        """
        return self.profiles.get(name.lower())
    
    def set_active_profile(self, name):
        """
        Set the active profile by name.
        
        Args:
            name (str): The profile name
            
        Returns:
            bool: True if successful, False otherwise
        """
        profile = self.get_profile(name.lower())
        if profile:
            self.active_profile = profile
            return True
        return False
    
    def delete_profile(self, name):
        """
        Delete a profile.
        
        Args:
            name (str): The profile name
            
        Returns:
            bool: True if successful, False otherwise
        """
        profile = self.get_profile(name.lower())
        if not profile:
            return False
        
        # Remove from memory
        del self.profiles[name.lower()]
        
        # Remove from disk
        profile_path = self.profiles_dir / f"{name.lower()}.json"
        try:
            if profile_path.exists():
                profile_path.unlink()
        except Exception as e:
            print(f"Error deleting profile file {name}: {e}")
            return False
        
        # If the active profile was deleted, set a new active profile
        if self.active_profile and self.active_profile.name.lower() == name.lower():
            if self.profiles:
                self.active_profile = list(self.profiles.values())[0]
            else:
                self.active_profile = None
        
        return True
    
    def get_all_profiles(self):
        """
        Get all profiles.
        
        Returns:
            list: List of all profiles
        """
        return list(self.profiles.values())
    
    def save_all_profiles(self):
        """
        Save all profiles to disk.
        """
        for profile in self.profiles.values():
            self.save_profile(profile)