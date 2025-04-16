#!/usr/bin/env python3
"""
Jarvis Voice Assistant - LLM Service Module

This module handles interactions with Ollama for AI responses.
"""

import ollama
import wikipedia
import pyjokes
import re
import sys
import os
from pathlib import Path
from config.settings import OLLAMA_MODEL, OLLAMA_CUSTOM_MODELS, MAX_HISTORY_LENGTH

# Add the root directory to sys.path to import rag_assistant
root_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(str(root_dir))

# Import the RAG assistant module
try:
    # Ensure the rag_assistant module is properly imported
    from rag_assistant import query_rag_model, setup_vector_db
    # Initialize the vector database when the service starts
    RAG_AVAILABLE = setup_vector_db()
    if RAG_AVAILABLE:
        print("RAG assistant initialized successfully for college queries.")
    else:
        print("Failed to initialize RAG assistant. College queries will use default model.")
except ImportError:
    print("RAG assistant module not available. College queries will use default model.")
    RAG_AVAILABLE = False

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
        
        # Default to the standard model
        return self.default_model
    
    def _is_college_related(self, query):
        """
        Determine if a query is related to college or admissions.
        
        Args:
            query (str): The user's query
            
        Returns:
            bool: True if college-related, False otherwise
        """
        query_lower = query.lower()
        
        # College-related keywords and patterns
        college_patterns = [
            r'\bcollege\b', r'\buniversity\b', r'\bcampus\b', r'\bschool\b',
            r'\badmission\b', r'\badmissions\b', r'\bapply\b', r'\bapplication\b',
            r'\bfee(s)?\b', r'\btuition\b', r'\bscholarship\b', r'\bfinancial aid\b',
            r'\benroll(ment)?\b', r'\bcourse(s)?\b', r'\bprogram(s)?\b',
            r'\bmajor(s)?\b', r'\bdegree(s)?\b', r'\bdorm\b', r'\bhousing\b',
            r'\bstudent(s)?\b', r'\bfaculty\b', r'\bprofessor(s)?\b', r'\bclass(es)?\b',
            r'\bsemester\b', r'\bquarter\b', r'\bacademic\b', r'\bstudy\b',
            r'\bdeadline\b', r'\brequirement(s)?\b',
            r'\btest(s)?\b', r'\bexam(s)?\b', r'\bsat\b', r'\bact\b', r'\bgpa\b', r'\bgrade(s)?\b'
        ]
        
        # Check if query matches any college-related pattern
        return any(re.search(pattern, query_lower) for pattern in college_patterns)
    
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
            
            # Check if query is college-related and RAG is available
            if RAG_AVAILABLE and self._is_college_related(query):
                print("Using RAG model for college-related query")
                rag_result = query_rag_model(query)
                
                if "error" not in rag_result:
                    model_response = rag_result["answer"]
                    
                    # Add source information if available
                    if rag_result["sources"] and len(rag_result["sources"]) > 0:
                        model_response += "\n\nThis information is based on my knowledge of college admissions."
                    
                    # Update conversation history and cache
                    self.conversation_history.append((query, model_response))
                    self.response_cache[cache_key] = model_response
                    return model_response
                else:
                    print(f"RAG error: {rag_result.get('error')}. Falling back to default model.")
            
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