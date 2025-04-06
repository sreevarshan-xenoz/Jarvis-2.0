#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Web Search Service Module

This module handles web search functionality.
"""

import webbrowser
import urllib.parse

class WebSearchService:
    """
    Provides web search functionality.
    """
    
    def __init__(self):
        """
        Initialize the web search service.
        """
        self.search_engines = {
            'google': 'https://www.google.com/search?q={}',
            'bing': 'https://www.bing.com/search?q={}',
            'duckduckgo': 'https://duckduckgo.com/?q={}',
            'youtube': 'https://www.youtube.com/results?search_query={}'
        }
        self.default_engine = 'google'
    
    def search(self, query, engine=None):
        """
        Search the web using the specified search engine.
        
        Args:
            query (str): The search query
            engine (str, optional): The search engine to use. Defaults to the default engine.
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not engine or engine.lower() not in self.search_engines:
            engine = self.default_engine
        else:
            engine = engine.lower()
        
        try:
            # URL encode the query
            encoded_query = urllib.parse.quote(query)
            
            # Format the search URL
            search_url = self.search_engines[engine].format(encoded_query)
            
            # Open the URL in the default browser
            webbrowser.open(search_url)
            return True
        except Exception as e:
            print(f"Error performing web search: {str(e)}")
            return False
    
    def get_available_engines(self):
        """
        Get a list of available search engines.
        
        Returns:
            list: List of available search engine names
        """
        return list(self.search_engines.keys())
    
    def set_default_engine(self, engine):
        """
        Set the default search engine.
        
        Args:
            engine (str): The search engine to set as default
            
        Returns:
            bool: True if successful, False if engine not available
        """
        if engine.lower() in self.search_engines:
            self.default_engine = engine.lower()
            return True
        else:
            return False