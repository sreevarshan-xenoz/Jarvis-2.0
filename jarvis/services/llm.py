#!/usr/bin/env python3
"""
Jarvis Voice Assistant - LLM Service Module

This module handles interactions with Ollama for AI responses.
"""

import ollama
import wikipedia
import pyjokes
from config.settings import OLLAMA_MODEL, MAX_HISTORY_LENGTH

class LLMService:
    """
    Provides AI response functionality using Ollama.
    """
    
    def __init__(self):
        """
        Initialize the LLM service.
        """
        self.model = OLLAMA_MODEL
        self.conversation_history = []
    
    def ask(self, query):
        """
        Ask a question to the Ollama model.
        
        Args:
            query (str): The question to ask
            
        Returns:
            str: The model's response
        """
        try:
            # Use conversation history for context if available
            context = self.conversation_history if self.conversation_history else None
            
            # Generate response from Ollama
            response = ollama.generate(
                model=self.model,
                prompt=query,
                context=context[-MAX_HISTORY_LENGTH:] if context else None
            )
            
            # Update conversation history
            self.conversation_history.append((query, response['response']))
            
            # Trim conversation history if needed
            if len(self.conversation_history) > MAX_HISTORY_LENGTH * 2:
                self.conversation_history = self.conversation_history[-MAX_HISTORY_LENGTH * 2:]
            
            return response['response']
        
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    def search_wikipedia(self, query, sentences=2):
        """
        Search Wikipedia for information.
        
        Args:
            query (str): The search query
            sentences (int): Number of sentences to return
            
        Returns:
            str: Wikipedia summary or error message
        """
        try:
            info = wikipedia.summary(query, sentences=sentences)
            return info
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Multiple results found. Please be more specific."
        except wikipedia.exceptions.PageError:
            return f"Sorry, I couldn't find information about {query}"
        except Exception as e:
            return f"An error occurred while searching Wikipedia: {str(e)}"
    
    def get_joke(self):
        """
        Get a random joke.
        
        Returns:
            str: A joke
        """
        try:
            return pyjokes.get_joke()
        except Exception as e:
            return f"Sorry, I couldn't think of a joke right now: {str(e)}"
    
    def clear_history(self):
        """
        Clear conversation history.
        """
        self.conversation_history = []
        return True