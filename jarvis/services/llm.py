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
        self.response_cache = {}  # Cache for common queries
        self.cache_size_limit = 50  # Maximum number of cached responses
    
    def ask(self, query):
        """
        Ask a question to the Ollama model.
        
        Args:
            query (str): The question to ask
            
        Returns:
            str: The model's response
        """
        try:
            # Check cache for exact query match
            cache_key = query.strip().lower()
            if cache_key in self.response_cache:
                print("Using cached response")
                return self.response_cache[cache_key]
            
            # Format conversation history for context
            context = None
            if self.conversation_history:
                # Convert history tuples to token integers for context
                context = [int(ord(c)) for pair in self.conversation_history[-MAX_HISTORY_LENGTH:] 
                          for c in pair[0] + pair[1]]
            
            # Generate response from Ollama with optimized parameters
            response = ollama.generate(
                model=self.model,
                prompt=query,
                context=context,
                options={
                    "num_predict": 256,  # Limit token generation for faster responses
                    "temperature": 0.7,  # Slightly lower temperature for more focused responses
                    "top_k": 40,        # Limit vocabulary search space
                    "top_p": 0.9,       # Nucleus sampling parameter
                    "num_gpu": 1,        # Use GPU acceleration if available
                    "num_thread": 4      # Use multiple threads for processing
                }
            )
            
            # Update conversation history
            self.conversation_history.append((query, response['response']))
            
            # Trim conversation history if needed
            if len(self.conversation_history) > MAX_HISTORY_LENGTH * 2:
                self.conversation_history = self.conversation_history[-MAX_HISTORY_LENGTH * 2:]
            
            # Cache the response
            if len(self.response_cache) >= self.cache_size_limit:
                # Remove oldest item if cache is full
                oldest_key = next(iter(self.response_cache))
                self.response_cache.pop(oldest_key)
            self.response_cache[cache_key] = response['response']
            
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
        
    def clear_cache(self):
        """
        Clear response cache.
        """
        self.response_cache = {}
        return True