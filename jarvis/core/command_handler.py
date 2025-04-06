#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Command Handler Module

This module processes and executes different voice commands.
"""

import datetime
import re
import random

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
            friendly_time_responses = [
                f"It's currently {time}. Time flies when you're having fun! ⏰",
                f"The time is {time}. Carpe diem! ⌚",
                f"Look at that, it's already {time}! Where does the day go? 🕒",
                f"It's {time} right now. Always good to stay on schedule! 📅"
            ]
            self.speech_engine.speak(random.choice(friendly_time_responses))
        
        # Wikipedia commands
        elif 'who is' in command:
            person = command.replace('who is', '').strip()
            info = self.llm_service.search_wikipedia(person)
            self.speech_engine.speak(info)
        
        # Joke commands
        elif 'joke' in command:
            joke = self.llm_service.get_joke()
            joke_intros = [
                "Here's one that'll make you smile! 😄 ",
                "I've been saving this one! 😆 ",
                "This one cracks me up every time! 😂 ",
                "Let me brighten your day with this! 🤣 "
            ]
            self.speech_engine.speak(random.choice(joke_intros) + joke)
            
            # If using enhanced display, trigger joke reaction
            if hasattr(self.speech_engine.display_window, 'ui_integrator') and \
               hasattr(self.speech_engine.display_window.ui_integrator, 'particle_system'):
                try:
                    center_x = self.speech_engine.display_window.canvas_width / 2
                    center_y = self.speech_engine.display_window.canvas_height / 2
                    self.speech_engine.display_window.ui_integrator.particle_system.create_reaction(
                        center_x, center_y, 'joke'
                    )
                except Exception as e:
                    print(f"Error creating joke reaction: {e}")
        
        # Weather commands
        elif 'weather' in command:
            city = command.replace('weather', '').strip() or 'new york'
            weather_report = self.weather_service.get_weather(city)
            
            # Add friendly intros to weather reports
            weather_intros = [
                f"Let me check that for you! {weather_report} ☀️",
                f"Here's your forecast, friend! {weather_report} 🌤️",
                f"Weather update coming right up! {weather_report} 🌈",
                f"I hope you're dressed for this! {weather_report} 🌦️"
            ]
            self.speech_engine.speak(random.choice(weather_intros))
        
        # News commands
        elif 'news' in command:
            news = self.news_service.get_headlines()
            self.speech_engine.speak(news)
        
        # Volume commands
        elif 'volume up' in command:
            self.system_service.volume_up()
            volume_up_responses = [
                "Pumping up the volume for you! 🔊",
                "Turning it up! Rock on! 🎸",
                "Volume increased! Can you hear me better now? 👂",
                "Louder and clearer! How's that? 🔉→🔊"
            ]
            self.speech_engine.speak(random.choice(volume_up_responses))
        
        elif 'volume down' in command:
            self.system_service.volume_down()
            volume_down_responses = [
                "Lowering the volume for you. Getting too loud? 🔉",
                "Volume decreased! Going for that calm vibe! 😌",
                "Turning it down a notch! Better? 🔊→🔉",
                "Volume reduced! Let me know if you need it quieter! 🤫"
            ]
            self.speech_engine.speak(random.choice(volume_down_responses))
        
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
                friendly_responses = [
                    f"I'm on it! Searching{engine_text} for {query} right now! 🔍",
                    f"Let me find that for you! Searching{engine_text} for {query} 👀",
                    f"Detective Jarvis is on the case! Looking up {query}{engine_text} 🕵️",
                    f"Searching{engine_text} for {query}. This should be interesting! ✨"
                ]
                self.speech_engine.speak(random.choice(friendly_responses))
                self.web_search_service.search(query, engine)
            else:
                friendly_questions = [
                    "What would you like me to search for? I'm all ears! 👂",
                    "I'd be happy to search for something! What are you curious about? 🤔",
                    "Ready to search! Just tell me what you're looking for! 🔍"
                ]
                self.speech_engine.speak(random.choice(friendly_questions))
        
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
            farewell_messages = [
                "Goodbye, friend! Have a wonderful day! 👋",
                "See you later! I'll be here when you need me! 😊",
                "Farewell! It was great chatting with you! ✨",
                "Until next time! Take care of yourself! 🌟"
            ]
            self.speech_engine.speak(random.choice(farewell_messages))
            exit()
        
        # Default: Ask LLM
        else:
            response = self.llm_service.ask(command)
            
            # Add friendly intros occasionally to make responses more personable
            if random.random() < 0.3:  # 30% chance to add a friendly intro
                friendly_intros = [
                    "Happy to help! ",
                    "Great question! ",
                    "I'd love to answer that! ",
                    "Let me think about that... ",
                    "That's an interesting one! "
                ]
                response = random.choice(friendly_intros) + response
            
            self.speech_engine.speak(response)
            
            # If using enhanced display, trigger a thinking reaction
            if hasattr(self.speech_engine.display_window, 'ui_integrator') and \
               hasattr(self.speech_engine.display_window.ui_integrator, 'particle_system'):
                try:
                    center_x = self.speech_engine.display_window.canvas_width / 2
                    center_y = self.speech_engine.display_window.canvas_height / 2
                    self.speech_engine.display_window.ui_integrator.particle_system.create_reaction(
                        center_x, center_y, 'thinking'
                    )
                except Exception as e:
                    print(f"Error creating thinking reaction: {e}")