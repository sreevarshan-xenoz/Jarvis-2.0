#!/usr/bin/env python3
"""
Profile Manager for Jarvis

This module provides functionality for managing user profiles and preferences
for the Jarvis assistant.
"""

import os
import logging
import json
from typing import Dict, Any, Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("profile-manager")

class ProfileManager:
    """
    Manages user profiles and preferences for the Jarvis assistant.
    """
    
    def __init__(self, profiles_dir=None):
        """
        Initialize the profile manager.
        
        Args:
            profiles_dir (str, optional): Directory containing profile files
        """
        self._profiles = {}
        self._current_profile = "default"
        self._profiles_dir = profiles_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), "profiles")
        
        self._default_profile = {
            "name": "default",
            "display_name": "Default User",
            "created_at": "",
            "updated_at": "",
            "preferences": {
                "voice": {
                    "rate": 1.0,
                    "volume": 0.8,
                    "voice_id": "en-US-Standard-D"
                },
                "notifications": {
                    "enabled": True,
                    "sound": True,
                    "visual": True
                },
                "privacy": {
                    "save_conversation_history": True,
                    "data_collection": False
                },
                "ui": {
                    "theme": "default",
                    "animations": True,
                    "compact_mode": False
                }
            },
            "history": [],
            "reminders": []
        }
        
        # Load available profiles
        self._load_profiles()
        logger.info(f"ProfileManager initialized with {len(self._profiles)} profiles")
    
    def _load_profiles(self):
        """Load all available profiles from the profiles directory."""
        self._profiles = {"default": self._default_profile}
        
        if not os.path.exists(self._profiles_dir):
            os.makedirs(self._profiles_dir, exist_ok=True)
            logger.info(f"Created profiles directory: {self._profiles_dir}")
            
            # Save default profile
            self._save_profile(self._default_profile)
            
        try:
            for filename in os.listdir(self._profiles_dir):
                if filename.endswith(".json"):
                    profile_path = os.path.join(self._profiles_dir, filename)
                    with open(profile_path, 'r') as file:
                        profile = json.load(file)
                        if "name" in profile:
                            self._profiles[profile["name"]] = profile
                            logger.info(f"Loaded profile: {profile['name']}")
        except Exception as e:
            logger.error(f"Error loading profiles: {str(e)}")
    
    def _save_profile(self, profile: Dict[str, Any]):
        """
        Save a profile to disk.
        
        Args:
            profile (Dict[str, Any]): The profile to save
        """
        if "name" not in profile:
            logger.error("Cannot save profile without a name")
            return
            
        try:
            profile_path = os.path.join(self._profiles_dir, f"{profile['name']}.json")
            with open(profile_path, 'w') as file:
                json.dump(profile, file, indent=2)
            logger.info(f"Saved profile: {profile['name']}")
        except Exception as e:
            logger.error(f"Error saving profile: {str(e)}")
    
    def get_current_profile(self) -> Dict[str, Any]:
        """
        Get the current profile settings.
        
        Returns:
            Dict[str, Any]: The current profile
        """
        return self._profiles.get(self._current_profile, self._default_profile)
    
    def set_current_profile(self, profile_name: str) -> bool:
        """
        Set the current profile.
        
        Args:
            profile_name (str): Name of the profile to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        if profile_name in self._profiles:
            self._current_profile = profile_name
            logger.info(f"Set current profile to: {profile_name}")
            return True
        else:
            logger.warning(f"Profile not found: {profile_name}")
            return False
    
    def get_available_profiles(self) -> List[str]:
        """
        Get a list of available profiles.
        
        Returns:
            List[str]: List of profile names
        """
        return list(self._profiles.keys())
    
    def create_profile(self, profile: Dict[str, Any]) -> bool:
        """
        Create a new profile.
        
        Args:
            profile (Dict[str, Any]): The profile settings
            
        Returns:
            bool: True if successful, False otherwise
        """
        if "name" not in profile:
            logger.error("Cannot create profile without a name")
            return False
            
        profile_name = profile["name"]
        
        # Create a new profile based on default profile
        new_profile = self._default_profile.copy()
        
        # Update with provided profile data
        for key, value in profile.items():
            if key in new_profile:
                if isinstance(value, dict) and isinstance(new_profile[key], dict):
                    # Merge dictionaries for nested properties
                    new_profile[key].update(value)
                else:
                    new_profile[key] = value
            else:
                new_profile[key] = value
        
        self._profiles[profile_name] = new_profile
        self._save_profile(new_profile)
        logger.info(f"Created new profile: {profile_name}")
        return True
    
    def update_profile(self, profile_name: str, settings: Dict[str, Any]) -> bool:
        """
        Update an existing profile.
        
        Args:
            profile_name (str): Name of the profile to update
            settings (Dict[str, Any]): The settings to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        if profile_name not in self._profiles:
            logger.warning(f"Profile not found: {profile_name}")
            return False
            
        # Update profile settings
        profile = self._profiles[profile_name]
        
        # Handle nested updates
        def update_nested(target, source):
            for key, value in source.items():
                if key in target and isinstance(value, dict) and isinstance(target[key], dict):
                    update_nested(target[key], value)
                else:
                    target[key] = value
        
        update_nested(profile, settings)
        
        # Update timestamp
        import datetime
        profile["updated_at"] = datetime.datetime.now().isoformat()
            
        self._profiles[profile_name] = profile
        self._save_profile(profile)
        logger.info(f"Updated profile: {profile_name}")
        return True
    
    def delete_profile(self, profile_name: str) -> bool:
        """
        Delete a profile.
        
        Args:
            profile_name (str): Name of the profile to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if profile_name == "default":
            logger.warning("Cannot delete the default profile")
            return False
            
        if profile_name not in self._profiles:
            logger.warning(f"Profile not found: {profile_name}")
            return False
            
        # Delete profile file
        try:
            profile_path = os.path.join(self._profiles_dir, f"{profile_name}.json")
            if os.path.exists(profile_path):
                os.remove(profile_path)
                
            # Remove from profiles dictionary
            del self._profiles[profile_name]
            
            # If current profile was deleted, switch to default
            if self._current_profile == profile_name:
                self._current_profile = "default"
                
            logger.info(f"Deleted profile: {profile_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting profile: {str(e)}")
            return False
            
    def add_history_item(self, query: str, response: str) -> bool:
        """
        Add an item to the current profile's conversation history.
        
        Args:
            query (str): User's query
            response (str): System's response
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            profile = self.get_current_profile()
            
            # Ensure history list exists
            if "history" not in profile:
                profile["history"] = []
                
            # Add history item with timestamp
            import datetime
            history_item = {
                "timestamp": datetime.datetime.now().isoformat(),
                "query": query,
                "response": response
            }
            
            profile["history"].append(history_item)
            
            # Update profile
            return self.update_profile(self._current_profile, {"history": profile["history"]})
        except Exception as e:
            logger.error(f"Error adding history item: {str(e)}")
            return False
            
    def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the conversation history for the current profile.
        
        Args:
            limit (int): Maximum number of history items to return
            
        Returns:
            List[Dict[str, Any]]: List of history items
        """
        profile = self.get_current_profile()
        history = profile.get("history", [])
        
        # Return most recent items first
        return sorted(history, key=lambda x: x.get("timestamp", ""), reverse=True)[:limit]
            
    def add_reminder(self, title: str, description: str, due_date: str) -> bool:
        """
        Add a reminder to the current profile.
        
        Args:
            title (str): Reminder title
            description (str): Reminder description
            due_date (str): Due date in ISO format
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            profile = self.get_current_profile()
            
            # Ensure reminders list exists
            if "reminders" not in profile:
                profile["reminders"] = []
                
            # Add reminder with unique ID
            import uuid
            reminder = {
                "id": str(uuid.uuid4()),
                "title": title,
                "description": description,
                "due_date": due_date,
                "created_at": datetime.datetime.now().isoformat(),
                "completed": False
            }
            
            profile["reminders"].append(reminder)
            
            # Update profile
            return self.update_profile(self._current_profile, {"reminders": profile["reminders"]})
        except Exception as e:
            logger.error(f"Error adding reminder: {str(e)}")
            return False
            
    def get_reminders(self, include_completed: bool = False) -> List[Dict[str, Any]]:
        """
        Get reminders for the current profile.
        
        Args:
            include_completed (bool): Whether to include completed reminders
            
        Returns:
            List[Dict[str, Any]]: List of reminders
        """
        profile = self.get_current_profile()
        reminders = profile.get("reminders", [])
        
        if not include_completed:
            reminders = [r for r in reminders if not r.get("completed", False)]
            
        # Sort by due date
        return sorted(reminders, key=lambda x: x.get("due_date", ""))
            
    def update_reminder(self, reminder_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update a reminder.
        
        Args:
            reminder_id (str): ID of the reminder to update
            updates (Dict[str, Any]): The updates to apply
            
        Returns:
            bool: True if successful, False otherwise
        """
        profile = self.get_current_profile()
        reminders = profile.get("reminders", [])
        
        for i, reminder in enumerate(reminders):
            if reminder.get("id") == reminder_id:
                # Apply updates
                for key, value in updates.items():
                    reminders[i][key] = value
                
                # Update profile
                return self.update_profile(self._current_profile, {"reminders": reminders})
                
        logger.warning(f"Reminder not found: {reminder_id}")
        return False 