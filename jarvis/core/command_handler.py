#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Command Handler Module

This module processes and executes different voice commands.
"""

import datetime
import re

from services.weather import WeatherService
from services.news import NewsService
from services.media import MediaService
from services.browser import BrowserService
from services.system import SystemService
from services.llm import LLMService
from services.web_search import WebSearchService

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
        self.web_search_service = WebSearchService()
    
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
        
        # Web search commands
        elif re.search(r'search (for|on)\s+', command) or command.startswith('search '):
            # Extract search query and optional engine
            search_pattern = re.search(r'search (for|on)?\s+(.*?)( on| using| with)? ?(google|bing|duckduckgo|youtube)?$', command)
            
            if search_pattern:
                query = search_pattern.group(2).strip()
                engine = search_pattern.group(4) if search_pattern.group(4) else None
            else:
                query = command.replace('search', '', 1).strip()
                engine = None
            
            if query:
                engine_text = f" on {engine}" if engine else ""
                self.speech_engine.speak(f"Searching{engine_text} for {query}")
                self.web_search_service.search(query, engine)
            else:
                self.speech_engine.speak("What would you like me to search for?")
        
        # Close application commands
        elif re.search(r'close|exit|quit', command) and not (command == 'exit' or command == 'quit' or 'goodbye' in command):
            # First remove close/exit/quit keywords
            app_name = re.sub(r'(close|exit|quit)\s+', '', command).strip()
            
            # Then remove any wake words that might be in the command
            from config.settings import WAKE_WORDS
            for wake_word in WAKE_WORDS:
                if app_name.lower().startswith(wake_word.lower()):
                    app_name = app_name[len(wake_word):].strip()
            
            if app_name:
                # Provide better feedback for browser tabs
                if app_name.lower() in ['youtube', 'facebook', 'twitter', 'instagram', 'gmail']:
                    self.speech_engine.speak(f"Trying to close {app_name}...")
                    if self.system_service.close_application(app_name):
                        self.speech_engine.speak(f"Successfully closed {app_name}")
                    else:
                        self.speech_engine.speak(f"I couldn't find an open {app_name} tab")
                # Regular applications
                else:
                    if self.system_service.close_application(app_name):
                        self.speech_engine.speak(f"Closed {app_name}")
                    else:
                        self.speech_engine.speak(f"Could not find {app_name} running")
            else:
                self.speech_engine.speak("Which application would you like me to close?")
        
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