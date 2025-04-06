#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Theme Manager Module

This module provides customizable themes and styles for the Jarvis animated UI.
"""

import json
import os
from pathlib import Path

class ThemeManager:
    """
    Manages customizable themes and styles for the Jarvis animated UI.
    """
    
    def __init__(self, themes_dir=None):
        """
        Initialize the theme manager.
        
        Args:
            themes_dir (str): Directory containing theme files
        """
        # Default themes directory
        if themes_dir is None:
            # Get the directory of the current file
            current_dir = Path(__file__).parent.absolute()
            # Go up one level to the jarvis directory and then to themes
            self.themes_dir = os.path.join(current_dir.parent, 'themes')
        else:
            self.themes_dir = themes_dir
            
        # Create themes directory if it doesn't exist
        os.makedirs(self.themes_dir, exist_ok=True)
        
        # Initialize themes
        self.themes = {}
        self.current_theme = 'dark'  # Default theme
        
        # Load built-in themes
        self._init_default_themes()
        
        # Load custom themes from directory
        self._load_themes()
    
    def _init_default_themes(self):
        """
        Initialize default built-in themes.
        """
        # Dark theme (default)
        self.themes['dark'] = {
            "name": "Dark",
            "description": "Default dark theme with blue accents",
            "colors": {
                "bg_dark": "#0a1622",
                "bg_medium": "#162231",
                "bg_gradient_top": "#0d1a29",
                "bg_gradient_bottom": "#1e2b3a",
                "accent": "#00a8ff",
                "accent_glow": "#00d2ff",
                "accent_secondary": "#7b42ff",
                "text": "#ffffff",
                "text_dim": "#a0b8d0",
                "success": "#00e676",
                "warning": "#ff9100",
                "error": "#ff5252"
            },
            "animation": {
                "intensity": 1.0,
                "complexity": 1.0,
                "particle_count": 50,
                "wave_complexity": 1.0
            },
            "fonts": {
                "title": {"family": "Segoe UI", "size": 28, "weight": "bold"},
                "subtitle": {"family": "Segoe UI", "size": 11, "weight": "normal"},
                "text": {"family": "Segoe UI", "size": 12, "weight": "normal"},
                "status": {"family": "Segoe UI", "size": 11, "weight": "bold"},
                "footer": {"family": "Segoe UI", "size": 10, "weight": "normal"}
            }
        }
        
        # Light theme
        self.themes['light'] = {
            "name": "Light",
            "description": "Light theme with blue accents",
            "colors": {
                "bg_dark": "#f0f4f8",
                "bg_medium": "#e1e8f0",
                "bg_gradient_top": "#f5f9ff",
                "bg_gradient_bottom": "#e1e8f0",
                "accent": "#0078d4",
                "accent_glow": "#00a2ff",
                "accent_secondary": "#6b2ebb",
                "text": "#1a1a1a",
                "text_dim": "#555555",
                "success": "#00b248",
                "warning": "#d06a00",
                "error": "#d32f2f"
            },
            "animation": {
                "intensity": 0.8,
                "complexity": 0.9,
                "particle_count": 40,
                "wave_complexity": 0.9
            },
            "fonts": {
                "title": {"family": "Segoe UI", "size": 28, "weight": "bold"},
                "subtitle": {"family": "Segoe UI", "size": 11, "weight": "normal"},
                "text": {"family": "Segoe UI", "size": 12, "weight": "normal"},
                "status": {"family": "Segoe UI", "size": 11, "weight": "bold"},
                "footer": {"family": "Segoe UI", "size": 10, "weight": "normal"}
            }
        }
        
        # High Contrast theme
        self.themes['high_contrast'] = {
            "name": "High Contrast",
            "description": "High contrast theme for accessibility",
            "colors": {
                "bg_dark": "#000000",
                "bg_medium": "#0a0a0a",
                "bg_gradient_top": "#000000",
                "bg_gradient_bottom": "#0a0a0a",
                "accent": "#ffff00",
                "accent_glow": "#ffff00",
                "accent_secondary": "#ffffff",
                "text": "#ffffff",
                "text_dim": "#cccccc",
                "success": "#00ff00",
                "warning": "#ffaa00",
                "error": "#ff0000"
            },
            "animation": {
                "intensity": 0.7,
                "complexity": 0.6,
                "particle_count": 30,
                "wave_complexity": 0.7
            },
            "fonts": {
                "title": {"family": "Segoe UI", "size": 30, "weight": "bold"},
                "subtitle": {"family": "Segoe UI", "size": 12, "weight": "bold"},
                "text": {"family": "Segoe UI", "size": 14, "weight": "normal"},
                "status": {"family": "Segoe UI", "size": 12, "weight": "bold"},
                "footer": {"family": "Segoe UI", "size": 11, "weight": "normal"}
            }
        }
        
        # Cyberpunk theme
        self.themes['cyberpunk'] = {
            "name": "Cyberpunk",
            "description": "Futuristic cyberpunk theme with neon colors",
            "colors": {
                "bg_dark": "#0a001a",
                "bg_medium": "#16002a",
                "bg_gradient_top": "#0a001a",
                "bg_gradient_bottom": "#16002a",
                "accent": "#00ffaa",
                "accent_glow": "#00ffcc",
                "accent_secondary": "#ff00aa",
                "text": "#ffffff",
                "text_dim": "#aa99cc",
                "success": "#00ff99",
                "warning": "#ff9900",
                "error": "#ff0066"
            },
            "animation": {
                "intensity": 1.2,
                "complexity": 1.3,
                "particle_count": 70,
                "wave_complexity": 1.4
            },
            "fonts": {
                "title": {"family": "Segoe UI", "size": 28, "weight": "bold"},
                "subtitle": {"family": "Segoe UI", "size": 11, "weight": "normal"},
                "text": {"family": "Segoe UI", "size": 12, "weight": "normal"},
                "status": {"family": "Segoe UI", "size": 11, "weight": "bold"},
                "footer": {"family": "Segoe UI", "size": 10, "weight": "normal"}
            }
        }
        
        # Minimal theme
        self.themes['minimal'] = {
            "name": "Minimal",
            "description": "Clean, minimalist theme with reduced animations",
            "colors": {
                "bg_dark": "#1a1a1a",
                "bg_medium": "#2a2a2a",
                "bg_gradient_top": "#1a1a1a",
                "bg_gradient_bottom": "#2a2a2a",
                "accent": "#999999",
                "accent_glow": "#aaaaaa",
                "accent_secondary": "#777777",
                "text": "#ffffff",
                "text_dim": "#aaaaaa",
                "success": "#aaffaa",
                "warning": "#ffddaa",
                "error": "#ffaaaa"
            },
            "animation": {
                "intensity": 0.5,
                "complexity": 0.4,
                "particle_count": 20,
                "wave_complexity": 0.5
            },
            "fonts": {
                "title": {"family": "Segoe UI", "size": 24, "weight": "normal"},
                "subtitle": {"family": "Segoe UI", "size": 10, "weight": "normal"},
                "text": {"family": "Segoe UI", "size": 12, "weight": "normal"},
                "status": {"family": "Segoe UI", "size": 10, "weight": "normal"},
                "footer": {"family": "Segoe UI", "size": 9, "weight": "normal"}
            }
        }
        
        # Save default themes to files
        for theme_id, theme_data in self.themes.items():
            self._save_theme(theme_id, theme_data)
    
    def _load_themes(self):
        """
        Load themes from the themes directory.
        """
        try:
            # Get all .json files in the themes directory
            theme_files = [f for f in os.listdir(self.themes_dir) if f.endswith('.json')]
            
            for theme_file in theme_files:
                theme_id = os.path.splitext(theme_file)[0]  # Remove .json extension
                theme_path = os.path.join(self.themes_dir, theme_file)
                
                try:
                    with open(theme_path, 'r') as f:
                        theme_data = json.load(f)
                        
                    # Validate theme data (basic validation)
                    if self._validate_theme(theme_data):
                        self.themes[theme_id] = theme_data
                except Exception as e:
                    print(f"Error loading theme {theme_file}: {e}")
        except Exception as e:
            print(f"Error loading themes: {e}")
    
    def _validate_theme(self, theme_data):
        """
        Validate theme data structure.
        
        Args:
            theme_data (dict): Theme data to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        # Check required keys
        required_keys = ['name', 'colors', 'animation', 'fonts']
        if not all(key in theme_data for key in required_keys):
            return False
            
        # Check required color keys
        required_colors = ['bg_dark', 'bg_medium', 'accent', 'text']
        if not all(key in theme_data['colors'] for key in required_colors):
            return False
            
        return True
    
    def _save_theme(self, theme_id, theme_data):
        """
        Save theme to a file.
        
        Args:
            theme_id (str): Theme identifier
            theme_data (dict): Theme data to save
        """
        try:
            theme_path = os.path.join(self.themes_dir, f"{theme_id}.json")
            with open(theme_path, 'w') as f:
                json.dump(theme_data, f, indent=2)
        except Exception as e:
            print(f"Error saving theme {theme_id}: {e}")
    
    def get_theme(self, theme_id=None):
        """
        Get theme data by ID.
        
        Args:
            theme_id (str): Theme identifier, or None for current theme
            
        Returns:
            dict: Theme data or None if not found
        """
        if theme_id is None:
            theme_id = self.current_theme
            
        return self.themes.get(theme_id)
    
    def set_theme(self, theme_id):
        """
        Set the current theme.
        
        Args:
            theme_id (str): Theme identifier
            
        Returns:
            bool: True if theme was set, False if theme not found
        """
        if theme_id in self.themes:
            self.current_theme = theme_id
            return True
        return False
    
    def get_available_themes(self):
        """
        Get a list of available themes.
        
        Returns:
            list: List of theme IDs and names
        """
        return [
            {'id': theme_id, 'name': theme_data.get('name', theme_id)}
            for theme_id, theme_data in self.themes.items()
        ]
    
    def create_theme(self, theme_id, theme_data):
        """
        Create a new theme.
        
        Args:
            theme_id (str): Theme identifier
            theme_data (dict): Theme data
            
        Returns:
            bool: True if theme was created, False if theme already exists or is invalid
        """
        if theme_id in self.themes:
            return False
            
        if not self._validate_theme(theme_data):
            return False
            
        self.themes[theme_id] = theme_data
        self._save_theme(theme_id, theme_data)
        return True
    
    def update_theme(self, theme_id, theme_data):
        """
        Update an existing theme.
        
        Args:
            theme_id (str): Theme identifier
            theme_data (dict): Theme data
            
        Returns:
            bool: True if theme was updated, False if theme not found or is invalid
        """
        if theme_id not in self.themes:
            return False
            
        if not self._validate_theme(theme_data):
            return False
            
        self.themes[theme_id] = theme_data
        self._save_theme(theme_id, theme_data)
        return True
    
    def delete_theme(self, theme_id):
        """
        Delete a theme.
        
        Args:
            theme_id (str): Theme identifier
            
        Returns:
            bool: True if theme was deleted, False if theme not found or is a built-in theme
        """
        # Don't allow deleting built-in themes
        if theme_id in ['dark', 'light', 'high_contrast', 'cyberpunk', 'minimal']:
            return False
            
        if theme_id not in self.themes:
            return False
            
        # Remove from memory
        del self.themes[theme_id]
        
        # Remove file
        try:
            theme_path = os.path.join(self.themes_dir, f"{theme_id}.json")
            if os.path.exists(theme_path):
                os.remove(theme_path)
        except Exception as e:
            print(f"Error deleting theme file {theme_id}: {e}")
            return False
            
        # Reset current theme if it was deleted
        if self.current_theme == theme_id:
            self.current_theme = 'dark'
            
        return True