#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Browser Service Module

This module handles web browser functionality.
"""

import webbrowser
from config.settings import WEBSITES

class BrowserService:
    """
    Provides web browser functionality.
    """
    
    def __init__(self):
        """
        Initialize the browser service.
        """
        self.websites = WEBSITES
    
    def open_website(self, site_name):
        """
        Open a website in the default web browser.
        
        Args:
            site_name (str): The name of the website to open
            
        Returns:
            bool: True if successful, False otherwise
        """
        site_name = site_name.lower()
        
        if site_name in self.websites:
            try:
                webbrowser.open(self.websites[site_name])
                return True
            except Exception as e:
                print(f"Error opening website: {str(e)}")
                return False
        else:
            return False
    
    def get_available_sites(self):
        """
        Get a list of available website shortcuts.
        
        Returns:
            list: List of available website names
        """
        return list(self.websites.keys())
    
    def add_website(self, site_name, url):
        """
        Add a new website shortcut.
        
        Args:
            site_name (str): The name of the website
            url (str): The URL of the website
            
        Returns:
            bool: True if successful, False if site already exists
        """
        site_name = site_name.lower()
        
        if site_name not in self.websites:
            self.websites[site_name] = url
            return True
        else:
            return False