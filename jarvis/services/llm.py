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
            
            # Use conversation history for context if available
            context = self.conversation_history if self.conversation_history else None
            
            # Enhance the prompt to encourage friendly, conversational responses
            friendly_prompt = f"Please respond to this in a friendly, conversational way as if you're talking to a friend: {query}"
            
            # Generate response from Ollama with optimized parameters
            response = ollama.generate(
                model=self.model,
                prompt=friendly_prompt,
                context=context[-MAX_HISTORY_LENGTH:] if context else None,
                options={
                    "num_predict": 256,  # Limit token generation for faster responses
                    "temperature": 0.75,  # Slightly higher temperature for more personality
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
            friendly_errors = [
                f"Oops! I hit a snag: {str(e)}. Let me try again!",
                f"Well that's embarrassing! I ran into an error: {str(e)}. Sorry about that!",
                f"Even AI assistants make mistakes sometimes! Error: {str(e)}",
                f"Hmm, that didn't work as expected. Error: {str(e)}. Let's try something else!"
            ]
            import random
            return random.choice(friendly_errors)
    
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
            joke = pyjokes.get_joke()
            
            # Add occasional follow-up comments to jokes for personality
            import random
            if random.random() < 0.4:  # 40% chance to add a follow-up
                follow_ups = [
                    " I've been working on my comedy routine!",
                    " Did that make you laugh? I hope so!",
                    " I know, I know, I should stick to my day job!",
                    " That one always cracks me up!",
                    " Too cheesy? I have plenty more where that came from!"
                ]
                joke += random.choice(follow_ups)
                
            return joke
        except Exception as e:
            return "I seem to have forgotten all my jokes! Must be a case of artificial amnesia!"
    
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