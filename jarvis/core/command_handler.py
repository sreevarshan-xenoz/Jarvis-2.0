#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Command Handler Module

This module processes and executes different voice commands.
"""

import datetime

from services.weather import WeatherService
from services.news import NewsService
from services.media import MediaService
from services.browser import BrowserService
from services.system import SystemService
from services.llm import LLMService

class CommandHandler:
    """
    Processes and executes different voice commands.
    """
    
    def __init__(self, speech_engine):
        """
        Initialize the command handler with required services.
        
        Args:
            speech_engine: The speech engine for text-to-speech output
        """
        self.speech_engine = speech_engine
        
        # Initialize services
        self.weather_service = WeatherService()
        self.news_service = NewsService()
        self.media_service = MediaService()
        self.browser_service = BrowserService()
        self.system_service = SystemService()
        self.llm_service = LLMService()
    
    def process_command(self, command):
        """
        Process and execute a voice command.
        
        Args:
            command (str): The command to process
        """
        print(f"Processing command: {command}")
        
        # Media commands
        if 'play' in command:
            song = command.replace('play', '').strip()
            self.speech_engine.speak(f'Playing {song}')
            self.media_service.play_youtube(song)
        
        # Time commands
        elif 'time' in command:
            time = datetime.datetime.now().strftime('%I:%M %p')
            self.speech_engine.speak(f'Current time is {time}')
        
        # Wikipedia commands
        elif 'who is' in command:
            person = command.replace('who is', '').strip()
            info = self.llm_service.search_wikipedia(person)
            self.speech_engine.speak(info)
        
        # Joke commands
        elif 'joke' in command:
            joke = self.llm_service.get_joke()
            self.speech_engine.speak(joke)
        
        # Weather commands
        elif 'weather' in command:
            city = command.replace('weather', '').strip() or 'new york'
            weather_report = self.weather_service.get_weather(city)
            self.speech_engine.speak(weather_report)
        
        # News commands
        elif 'news' in command:
            news = self.news_service.get_headlines()
            self.speech_engine.speak(news)
        
        # Volume commands
        elif 'volume up' in command:
            self.system_service.volume_up()
            self.speech_engine.speak('Increasing volume')
        
        elif 'volume down' in command:
            self.system_service.volume_down()
            self.speech_engine.speak('Decreasing volume')
        
        # Browser commands
        elif 'open' in command:
            for site in self.browser_service.get_available_sites():
                if site in command:
                    self.speech_engine.speak(f'Opening {site}')
                    self.browser_service.open_website(site)
                    return
            self.speech_engine.speak("Website not in my database")
        
        # Exit commands
        elif 'exit' in command or 'goodbye' in command:
            self.speech_engine.speak("Goodbye!")
            exit()
        
        # Default: Ask LLM
        else:
            response = self.llm_service.ask(command)
            self.speech_engine.speak(response)