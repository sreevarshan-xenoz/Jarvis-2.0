#!/usr/bin/env python3
"""
Jarvis Voice Assistant - LLM Service Module

This module handles interactions with Ollama for AI responses.
"""

import ollama
import wikipedia
import pyjokes
import re
from config.settings import OLLAMA_MODEL, OLLAMA_CUSTOM_MODELS, MAX_HISTORY_LENGTH

class LLMService:
    """
    Provides AI response functionality using Ollama.
    """
    
    def __init__(self):
        """
        Initialize the LLM service.
        """
        self.default_model = OLLAMA_MODEL
        self.model = self.default_model
        self.custom_models = OLLAMA_CUSTOM_MODELS
        self.conversation_history = []
        self.response_cache = {}  # Cache for common queries
        self.cache_size_limit = 50  # Maximum number of cached responses
        
        # Check if custom models are available
        self.available_models = self._get_available_models()
    
    def _get_available_models(self):
        """
        Get a list of available models from Ollama.
        
        Returns:
            list: List of available model names
        """
        try:
            models = ollama.list()
            return [model['name'] for model in models.get('models', [])]
        except Exception as e:
            print(f"Error getting available models: {e}")
            return []
    
    def _select_model_for_query(self, query):
        """
        Select the appropriate model based on the query content.
        
        Args:
            query (str): The user's query
            
        Returns:
            str: The model name to use
        """
        query_lower = query.lower()
        
        # Check if any custom model should be used based on keywords
        for model_name, model_info in self.custom_models.items():
            # Skip if model is not available in Ollama
            if model_name not in self.available_models:
                continue
                
            # Check if query contains any of the default keywords for this model
            default_keywords = model_info.get('default_for', [])
            if any(keyword in query_lower for keyword in default_keywords):
                return model_name
            
            # Enhanced detection for college-related queries
            if model_name == 'college-assistant':
                # Check for common college-related terms and questions
                college_patterns = [
                    r'fee(s)?', r'tuition', r'scholarship', r'financial aid',
                    r'admission', r'enroll(ment)?', r'course(s)?', r'program(s)?',
                    r'major(s)?', r'degree(s)?', r'campus', r'dorm', r'housing',
                    r'student(s)?', r'faculty', r'professor(s)?', r'class(es)?',
                    r'semester', r'quarter', r'academic', r'study', r'college',
                    r'university', r'school', r'education', r'learn(ing)?',
                    r'apply(ing)?', r'application', r'deadline', r'requirement(s)?',
                    r'test(s)?', r'exam(s)?', r'sat', r'act', r'gpa', r'grade(s)?'
                ]
                
                # Check if query matches any college-related pattern
                if any(re.search(pattern, query_lower) for pattern in college_patterns):
                    return model_name
        
        # Default to the standard model
        return self.default_model
    
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
            
            # Select the appropriate model for this query
            selected_model = self._select_model_for_query(query)
            
            # Format the query to ensure we get a proper response from the local model
            formatted_query = f"Please provide a direct and informative answer to this question: {query}"
            
            # Generate response from Ollama with optimized parameters
            response = ollama.generate(
                model=selected_model,
                prompt=formatted_query,
                context=context,
                options={
                    "num_predict": 512,  # Increased token limit for more complete answers
                    "temperature": 0.5,  # Lower temperature for more factual responses
                    "top_k": 40,        # Limit vocabulary search space
                    "top_p": 0.9,       # Nucleus sampling parameter
                    "num_gpu": 1,        # Use GPU acceleration if available
                    "num_thread": 4      # Use multiple threads for processing
                }
            )
            
            # Process the response to ensure it's relevant and concise
            model_response = response['response'].strip()
            
            # Update conversation history
            self.conversation_history.append((query, model_response))
            
            # Trim conversation history if needed
            if len(self.conversation_history) > MAX_HISTORY_LENGTH * 2:
                self.conversation_history = self.conversation_history[-MAX_HISTORY_LENGTH * 2:]
            
            # Cache the response
            if len(self.response_cache) >= self.cache_size_limit:
                # Remove oldest item if cache is full
                oldest_key = next(iter(self.response_cache))
                self.response_cache.pop(oldest_key)
            self.response_cache[cache_key] = model_response
            
            return model_response
        
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