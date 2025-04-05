#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Weather Service Module

This module handles interactions with weather APIs.
"""

import requests
from config.settings import WEATHER_API_KEY

class WeatherService:
    """
    Provides weather information using OpenWeatherMap API.
    """
    
    def __init__(self):
        """
        Initialize the weather service.
        """
        self.api_key = WEATHER_API_KEY
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, city):
        """
        Get current weather for a city.
        
        Args:
            city (str): The city to get weather for
            
        Returns:
            str: Weather information as a formatted string
        """
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(self.base_url, params=params)
            data = response.json()
            
            if response.status_code != 200:
                return f"Couldn't retrieve weather: {data.get('message', 'Unknown error')}"
            
            weather = data['weather'][0]['description']
            temp = data['main']['temp']
            feels_like = data['main']['feels_like']
            humidity = data['main']['humidity']
            
            return f"Weather in {city}: {weather}, Temperature: {temp}°C, Feels like: {feels_like}°C, Humidity: {humidity}%"
        
        except Exception as e:
            return f"Couldn't retrieve weather: {str(e)}"