#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Context Awareness Module

This module provides contextual awareness capabilities to Jarvis,
allowing it to understand user patterns and provide proactive assistance.
"""

import datetime
import time
import json
import os
from pathlib import Path
import threading

class ContextManager:
    """
    Manages contextual information about the user's environment and activities.
    Enables proactive assistance based on patterns and contextual information.
    """
    
    def __init__(self, profile_manager=None):
        """
        Initialize the context manager.
        
        Args:
            profile_manager: Optional profile manager for personalized context
        """
        self.profile_manager = profile_manager
        self.current_context = {
            "time_of_day": None,
            "day_of_week": None,
            "location": "home",  # Default assumption
            "active_applications": [],
            "recent_commands": [],
            "system_status": {},
            "last_updated": None
        }
        self.patterns = {
            "morning_routine": [],
            "evening_routine": [],
            "frequent_commands": {},
            "time_based_commands": {}
        }
        self.context_dir = Path(os.path.dirname(os.path.dirname(__file__))) / "data" / "context"
        self.context_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing patterns
        self._load_patterns()
        
        # Start background context updater
        self.update_thread = threading.Thread(target=self._background_updater, daemon=True)
        self.update_thread.start()
    
    def _load_patterns(self):
        """
        Load learned patterns from disk.
        """
        patterns_file = self.context_dir / "patterns.json"
        if patterns_file.exists():
            try:
                with open(patterns_file, "r") as f:
                    self.patterns = json.load(f)
            except Exception as e:
                print(f"Error loading patterns: {e}")
    
    def _save_patterns(self):
        """
        Save learned patterns to disk.
        """
        patterns_file = self.context_dir / "patterns.json"
        try:
            with open(patterns_file, "w") as f:
                json.dump(self.patterns, f, indent=2)
        except Exception as e:
            print(f"Error saving patterns: {e}")
    
    def _background_updater(self):
        """
        Background thread that periodically updates contextual information.
        """
        while True:
            self.update_context()
            time.sleep(60)  # Update every minute
    
    def update_context(self):
        """
        Update the current context with fresh information.
        """
        now = datetime.datetime.now()
        
        # Update time context
        self.current_context["time_of_day"] = self._get_time_of_day(now.hour)
        self.current_context["day_of_week"] = now.strftime("%A")
        
        # Update system status (could include battery level, network status, etc.)
        self.current_context["system_status"] = self._get_system_status()
        
        # Update timestamp
        self.current_context["last_updated"] = now.isoformat()
    
    def _get_time_of_day(self, hour):
        """
        Get the time of day category based on the hour.
        
        Args:
            hour (int): The current hour (0-23)
            
        Returns:
            str: The time of day category
        """
        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 22:
            return "evening"
        else:
            return "night"
    
    def _get_system_status(self):
        """
        Get the current system status.
        
        Returns:
            dict: System status information
        """
        # This could be expanded to include more system information
        status = {
            "battery_level": None,  # Could be implemented with psutil
            "connected_devices": [],
            "network_status": "connected"
        }
        return status
    
    def add_command_to_context(self, command, response):
        """
        Add a command to the recent commands list and update patterns.
        
        Args:
            command (str): The command given by the user
            response (str): The response from Jarvis
        """
        timestamp = datetime.datetime.now().isoformat()
        
        # Add to recent commands
        self.current_context["recent_commands"].append({
            "timestamp": timestamp,
            "command": command,
            "context": self.current_context.copy()
        })
        
        # Limit recent commands list
        if len(self.current_context["recent_commands"]) > 20:
            self.current_context["recent_commands"] = self.current_context["recent_commands"][-20:]
        
        # Update command frequency patterns
        command_key = command.lower()
        self.patterns["frequent_commands"][command_key] = self.patterns["frequent_commands"].get(command_key, 0) + 1
        
        # Update time-based patterns
        time_key = self.current_context["time_of_day"]
        if time_key not in self.patterns["time_based_commands"]:
            self.patterns["time_based_commands"][time_key] = {}
        
        self.patterns["time_based_commands"][time_key][command_key] = \
            self.patterns["time_based_commands"][time_key].get(command_key, 0) + 1
        
        # Save updated patterns
        self._save_patterns()
    
    def get_suggestions(self, limit=3):
        """
        Get command suggestions based on current context.
        
        Args:
            limit (int): Maximum number of suggestions to return
            
        Returns:
            list: List of suggested commands
        """
        suggestions = []
        
        # Get time-based suggestions
        time_key = self.current_context["time_of_day"]
        if time_key in self.patterns["time_based_commands"]:
            time_commands = self.patterns["time_based_commands"][time_key]
            time_suggestions = sorted(time_commands.items(), key=lambda x: x[1], reverse=True)[:limit]
            suggestions.extend([cmd for cmd, _ in time_suggestions])
        
        # Add overall frequent commands if needed
        if len(suggestions) < limit:
            freq_commands = sorted(self.patterns["frequent_commands"].items(), key=lambda x: x[1], reverse=True)
            for cmd, _ in freq_commands:
                if cmd not in suggestions and len(suggestions) < limit:
                    suggestions.append(cmd)
        
        return suggestions[:limit]
    
    def detect_routine(self):
        """
        Detect if the user is in a known routine based on time and recent commands.
        
        Returns:
            tuple: (routine_name, confidence) or (None, 0) if no routine detected
        """
        time_key = self.current_context["time_of_day"]
        day_key = self.current_context["day_of_week"]
        
        # Check morning routine
        if time_key == "morning" and self.patterns["morning_routine"]:
            return ("morning_routine", 0.8)  # Simplified confidence score
        
        # Check evening routine
        if time_key == "evening" and self.patterns["evening_routine"]:
            return ("evening_routine", 0.8)  # Simplified confidence score
        
        return (None, 0)
    
    def learn_routine(self, routine_name, commands):
        """
        Learn a new routine from a sequence of commands.
        
        Args:
            routine_name (str): The name of the routine
            commands (list): List of commands in the routine
        """
        if routine_name == "morning_routine":
            self.patterns["morning_routine"] = commands
        elif routine_name == "evening_routine":
            self.patterns["evening_routine"] = commands
        
        self._save_patterns()
    
    def get_proactive_suggestion(self):
        """
        Get a proactive suggestion based on current context.
        
        Returns:
            str: A proactive suggestion or None if no suggestion
        """
        now = datetime.datetime.now()
        hour = now.hour
        day = now.strftime("%A")
        
        # Morning weather check suggestion
        if 7 <= hour <= 9 and day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]:
            return "Would you like to hear today's weather forecast?"
        
        # Evening news suggestion
        if 18 <= hour <= 20:
            return "Would you like to hear the latest news headlines?"
        
        # Check for routine-based suggestions
        routine, confidence = self.detect_routine()
        if routine and confidence > 0.7:
            if routine == "morning_routine":
                return "Good morning! Would you like me to start your morning routine?"
            elif routine == "evening_routine":
                return "Good evening! Would you like me to start your evening routine?"
        
        return None