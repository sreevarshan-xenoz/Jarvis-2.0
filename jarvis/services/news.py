#!/usr/bin/env python3
"""
Jarvis Voice Assistant - News Service Module

This module handles interactions with news APIs.
"""

import requests
from config.settings import NEWS_API_KEY

class NewsService:
    """
    Provides news information using NewsAPI.
    """
    
    def __init__(self):
        """
        Initialize the news service.
        """
        self.api_key = NEWS_API_KEY
        self.base_url = "https://newsapi.org/v2/top-headlines"
    
    def get_headlines(self, country='us', category=None, max_results=3):
        """
        Get top news headlines.
        
        Args:
            country (str): The country code to get news for
            category (str, optional): News category (business, entertainment, etc.)
            max_results (int): Maximum number of headlines to return
            
        Returns:
            str: News headlines as a formatted string
        """
        try:
            params = {
                'country': country,
                'apiKey': self.api_key
            }
            
            if category:
                params['category'] = category
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if response.status_code != 200:
                return f"Couldn't retrieve news: {data.get('message', 'Unknown error')}"
            
            articles = data['articles'][:max_results]
            
            if not articles:
                return "No news headlines available at the moment."
            
            headlines = "Here are today's top headlines. "
            for i, article in enumerate(articles, 1):
                headlines += f"{i}. {article['title']}. "
            
            return headlines
        
        except Exception as e:
            return f"Couldn't retrieve news: {str(e)}"