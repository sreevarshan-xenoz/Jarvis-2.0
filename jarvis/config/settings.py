#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Settings Module

This module contains configuration settings and constants for the voice assistant.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Wake word settings
WAKE_WORDS = ['jarvis', 'gervais', 'service']

# API Keys
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

# Ollama settings
OLLAMA_MODEL = 'gemma:2b'
OLLAMA_CUSTOM_MODELS = {
    'college-assistant': {
        'description': 'Specialized model for college admissions assistance',
        'default_for': ['college', 'admission', 'university', 'application']
    }
}

# RAG settings
USE_RAG_FOR_COLLEGE = True  # Set to False to disable RAG for college queries

# Website shortcuts
WEBSITES = {
    'youtube': 'https://youtube.com',
    'google': 'https://google.com',
    'gmail': 'https://mail.google.com',
    'chatgpt': 'https://chat.openai.com',
    'cults': 'https://cults3d.com',
    'kaggle': 'https://kaggle.com',
    'hianime': 'https://hianime.tv'
}

# System settings
VOLUME_STEP = 2000  # Volume change step for NirCmd

# Conversation settings
MAX_HISTORY_LENGTH = 5  # Maximum number of conversation turns to remember
CONVERSATION_TIMEOUT = 30  # Seconds to keep conversation active after last interaction
CONTINUOUS_MODE = True  # Enable continuous conversation mode without wake word