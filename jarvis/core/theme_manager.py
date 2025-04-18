#!/usr/bin/env python3
"""
Theme Manager for Jarvis

This module provides functionality for managing themes and appearance settings
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
logger = logging.getLogger("theme-manager")

class ThemeManager:
    """
    Manages themes and appearance settings for the Jarvis assistant.
    """
    
    def __init__(self, theme_dir=None):
        """
        Initialize the theme manager.
        
        Args:
            theme_dir (str, optional): Directory containing theme files
        """
        self._themes = {}
        self._current_theme = "default"
        self._theme_dir = theme_dir or os.path.join(os.path.dirname(os.path.dirname(__file__)), "themes")
        
        self._default_theme = {
            "name": "default",
            "primary_color": "#42dcdb",
            "secondary_color": "#a18fff",
            "background_color": "#121212",
            "text_color": "#e0e0e0",
            "accent_color": "#ff8a80",
            "font_family": "Roboto",
            "logo_path": "assets/jarvis-logo.png"
        }
        
        # Load available themes
        self._load_themes()
        logger.info(f"ThemeManager initialized with {len(self._themes)} themes")
    
    def _load_themes(self):
        """Load all available themes from the theme directory."""
        self._themes = {"default": self._default_theme}
        
        if not os.path.exists(self._theme_dir):
            os.makedirs(self._theme_dir, exist_ok=True)
            logger.info(f"Created theme directory: {self._theme_dir}")
            
            # Save default theme
            self._save_theme(self._default_theme)
            
        try:
            for filename in os.listdir(self._theme_dir):
                if filename.endswith(".json"):
                    theme_path = os.path.join(self._theme_dir, filename)
                    with open(theme_path, 'r') as file:
                        theme = json.load(file)
                        if "name" in theme:
                            self._themes[theme["name"]] = theme
                            logger.info(f"Loaded theme: {theme['name']}")
        except Exception as e:
            logger.error(f"Error loading themes: {str(e)}")
    
    def _save_theme(self, theme: Dict[str, Any]):
        """
        Save a theme to disk.
        
        Args:
            theme (Dict[str, Any]): The theme to save
        """
        if "name" not in theme:
            logger.error("Cannot save theme without a name")
            return
            
        try:
            theme_path = os.path.join(self._theme_dir, f"{theme['name']}.json")
            with open(theme_path, 'w') as file:
                json.dump(theme, file, indent=2)
            logger.info(f"Saved theme: {theme['name']}")
        except Exception as e:
            logger.error(f"Error saving theme: {str(e)}")
    
    def get_current_theme(self) -> Dict[str, Any]:
        """
        Get the current theme settings.
        
        Returns:
            Dict[str, Any]: The current theme
        """
        return self._themes.get(self._current_theme, self._default_theme)
    
    def set_current_theme(self, theme_name: str) -> bool:
        """
        Set the current theme.
        
        Args:
            theme_name (str): Name of the theme to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        if theme_name in self._themes:
            self._current_theme = theme_name
            logger.info(f"Set current theme to: {theme_name}")
            return True
        else:
            logger.warning(f"Theme not found: {theme_name}")
            return False
    
    def get_available_themes(self) -> List[str]:
        """
        Get a list of available themes.
        
        Returns:
            List[str]: List of theme names
        """
        return list(self._themes.keys())
    
    def create_theme(self, theme: Dict[str, Any]) -> bool:
        """
        Create a new theme.
        
        Args:
            theme (Dict[str, Any]): The theme settings
            
        Returns:
            bool: True if successful, False otherwise
        """
        if "name" not in theme:
            logger.error("Cannot create theme without a name")
            return False
            
        theme_name = theme["name"]
        self._themes[theme_name] = theme
        self._save_theme(theme)
        logger.info(f"Created new theme: {theme_name}")
        return True
    
    def update_theme(self, theme_name: str, settings: Dict[str, Any]) -> bool:
        """
        Update an existing theme.
        
        Args:
            theme_name (str): Name of the theme to update
            settings (Dict[str, Any]): The settings to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        if theme_name not in self._themes:
            logger.warning(f"Theme not found: {theme_name}")
            return False
            
        # Update theme settings
        theme = self._themes[theme_name].copy()
        for key, value in settings.items():
            theme[key] = value
            
        self._themes[theme_name] = theme
        self._save_theme(theme)
        logger.info(f"Updated theme: {theme_name}")
        return True
    
    def delete_theme(self, theme_name: str) -> bool:
        """
        Delete a theme.
        
        Args:
            theme_name (str): Name of the theme to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        if theme_name == "default":
            logger.warning("Cannot delete the default theme")
            return False
            
        if theme_name not in self._themes:
            logger.warning(f"Theme not found: {theme_name}")
            return False
            
        # Delete theme file
        try:
            theme_path = os.path.join(self._theme_dir, f"{theme_name}.json")
            if os.path.exists(theme_path):
                os.remove(theme_path)
                
            # Remove from themes dictionary
            del self._themes[theme_name]
            
            # If current theme was deleted, switch to default
            if self._current_theme == theme_name:
                self._current_theme = "default"
                
            logger.info(f"Deleted theme: {theme_name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting theme: {str(e)}")
            return False