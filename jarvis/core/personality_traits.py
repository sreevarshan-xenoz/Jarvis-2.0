#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Personality Traits Module

This module adds personality traits to Jarvis, making it more friendly and personable
through animated reactions, casual conversational responses, and playful visual effects.
"""

import random
import time

class PersonalityTraits:
    """
    Provides personality traits and reactions for Jarvis to make it more friendly and personable.
    """
    
    def __init__(self, particle_system=None):
        """
        Initialize the personality traits module.
        
        Args:
            particle_system: Reference to the enhanced particle system for visual effects
        """
        self.particle_system = particle_system
        self.last_reaction_time = 0
        self.reaction_cooldown = 3.0  # Seconds between automatic reactions
        
        # Personality trait settings
        self.friendliness = 0.8  # 0.0 to 1.0 (higher = more friendly reactions)
        self.humor = 0.7  # 0.0 to 1.0 (higher = more humorous reactions)
        self.expressiveness = 0.8  # 0.0 to 1.0 (higher = more expressive animations)
        
        # Define reaction types and their associated emojis and animations
        self.reactions = {
            'greeting': {
                'emojis': ['👋', '😊', '🤗', '✨'],
                'messages': [
                    "Hello there!",
                    "Great to see you!",
                    "How can I help today?",
                    "Hey friend!"
                ],
                'animation': 'wave'
            },
            'joke': {
                'emojis': ['😂', '🤣', '😆', '😄'],
                'messages': [
                    "That's a good one!",
                    "Haha! I love your sense of humor!",
                    "That made my circuits laugh!",
                    "Good joke! I'm still learning humor though!"
                ],
                'animation': 'laugh'
            },
            'thinking': {
                'emojis': ['🤔', '💭', '⏳', '🧠'],
                'messages': [
                    "Hmm, let me think about that...",
                    "Processing...",
                    "Interesting question!",
                    "Let me figure this out..."
                ],
                'animation': 'pulse'
            },
            'success': {
                'emojis': ['✅', '👍', '🎉', '😊'],
                'messages': [
                    "Got it!",
                    "Task complete!",
                    "All done!",
                    "Success!"
                ],
                'animation': 'celebrate'
            },
            'error': {
                'emojis': ['❌', '😕', '🤷', '⚠️'],
                'messages': [
                    "Oops, something went wrong.",
                    "I couldn't do that, sorry!",
                    "That didn't work as expected.",
                    "Let's try something else."
                ],
                'animation': 'shake'
            },
            'casual': {
                'emojis': ['😎', '👌', '💯', '🙌'],
                'messages': [
                    "Cool!",
                    "Sounds good!",
                    "Awesome!",
                    "You got it!"
                ],
                'animation': 'bounce'
            },
            'surprise': {
                'emojis': ['😮', '😲', '🤯', '😱'],
                'messages': [
                    "Wow!",
                    "That's surprising!",
                    "I didn't expect that!",
                    "Amazing!"
                ],
                'animation': 'burst'
            }
        }
        
        # Casual conversation patterns to make responses more friendly
        self.casual_prefixes = [
            "I think ",
            "Looks like ",
            "It seems ",
            "From what I can tell, "
        ]
        
        self.casual_suffixes = [
            " if that helps!",
            " Hope that's what you were looking for!",
            " Let me know if you need anything else!",
            " That was fun to figure out!"
        ]
        
        # Jokes and fun facts for random insertion
        self.jokes = [
            "Why did the AI go to art school? To learn how to draw conclusions!",
            "I'm reading a book on anti-gravity. It's impossible to put down!",
            "What do you call an AI that sings? Artificial Harmonies!",
            "I told my computer I needed a break, and now it won't stop sending me vacation ads."
        ]
        
        self.fun_facts = [
            "Did you know? The first computer bug was an actual real-life moth!",
            "Fun fact: The word 'robot' comes from the Czech word 'robota' meaning forced labor.",
            "Interesting tidbit: The first computer programmer was a woman named Ada Lovelace.",
            "Random fact: The average person spends 6 months of their life waiting at traffic lights."
        ]
    
    def get_reaction(self, reaction_type):
        """
        Get a reaction based on the specified type.
        
        Args:
            reaction_type (str): Type of reaction ('greeting', 'joke', 'thinking', etc.)
            
        Returns:
            dict: Reaction data including emoji, message, and animation type
        """
        if reaction_type not in self.reactions:
            reaction_type = 'casual'  # Default to casual reaction
            
        reaction = self.reactions[reaction_type]
        
        return {
            'emoji': random.choice(reaction['emojis']),
            'message': random.choice(reaction['messages']),
            'animation': reaction['animation']
        }
    
    def apply_casual_style(self, message):
        """
        Apply casual conversational style to a message.
        
        Args:
            message (str): Original message
            
        Returns:
            str: Message with casual style applied
        """
        # Only apply casual style sometimes based on friendliness setting
        if random.random() > self.friendliness:
            return message
            
        # Apply casual prefix (30% chance)
        if random.random() < 0.3:
            message = random.choice(self.casual_prefixes) + message.lower()
            
        # Apply casual suffix (20% chance)
        if random.random() < 0.2:
            message = message + random.choice(self.casual_suffixes)
            
        return message
    
    def maybe_add_joke(self, message):
        """
        Maybe add a joke to the message based on humor setting.
        
        Args:
            message (str): Original message
            
        Returns:
            str: Message possibly with a joke added
        """
        # Only add jokes sometimes based on humor setting
        if random.random() > self.humor * 0.3:  # Reduced frequency to avoid being annoying
            return message
            
        joke = random.choice(self.jokes)
        return f"{message}\n\nOh, and here's something fun: {joke}"
    
    def maybe_add_fun_fact(self, message):
        """
        Maybe add a fun fact to the message.
        
        Args:
            message (str): Original message
            
        Returns:
            str: Message possibly with a fun fact added
        """
        # Only add fun facts sometimes based on friendliness setting
        if random.random() > self.friendliness * 0.2:  # Reduced frequency
            return message
            
        fun_fact = random.choice(self.fun_facts)
        return f"{message}\n\n{fun_fact}"
    
    def create_visual_reaction(self, x, y, reaction_type):
        """
        Create a visual reaction using the particle system.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
            reaction_type (str): Type of reaction
        """
        if not self.particle_system:
            return
            
        # Get reaction data
        reaction = self.get_reaction(reaction_type)
        
        # Create emoji reaction
        if hasattr(self.particle_system, 'create_reaction'):
            self.particle_system.create_reaction(x, y, reaction_type)
        
        # Create animation based on reaction type
        animation_type = reaction['animation']
        
        if animation_type == 'wave':
            self._create_wave_animation(x, y)
        elif animation_type == 'laugh':
            self._create_laugh_animation(x, y)
        elif animation_type == 'pulse':
            self._create_pulse_animation(x, y)
        elif animation_type == 'celebrate':
            self._create_celebrate_animation(x, y)
        elif animation_type == 'shake':
            self._create_shake_animation(x, y)
        elif animation_type == 'bounce':
            self._create_bounce_animation(x, y)
        elif animation_type == 'burst':
            self._create_burst_animation(x, y)
    
    def _create_wave_animation(self, x, y):
        """Create a friendly waving animation."""
        if not self.particle_system:
            return
            
        # Create particles that move in a wave pattern
        for i in range(10):
            angle = random.uniform(0, math.pi)  # Upward arc
            speed = random.uniform(1.0, 2.0)
            self.particle_system.create_particle(
                x, y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                particle_type='bubble',
                color='#00E676'  # Friendly green
            )
    
    def _create_laugh_animation(self, x, y):
        """Create a laughing animation with bouncy particles."""
        if not self.particle_system:
            return
            
        # Create bouncy particles that move outward
        for i in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.5, 3.0)
            self.particle_system.create_particle(
                x, y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                particle_type='bounce',
                color='#FFFF00'  # Happy yellow
            )
    
    def _create_pulse_animation(self, x, y):
        """Create a thinking pulse animation."""
        if not self.particle_system:
            return
            
        # Create pulsing particles
        for i in range(8):
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(20, 40)
            self.particle_system.create_particle(
                x + math.cos(angle) * distance, 
                y + math.sin(angle) * distance,
                vx=math.cos(angle) * 0.2,
                vy=math.sin(angle) * 0.2,
                particle_type='pulse',
                color='#7B42FF'  # Purple for thinking
            )
    
    def _create_celebrate_animation(self, x, y):
        """Create a celebration animation with sparks."""
        if not self.particle_system:
            return
            
        # Create spark particles that shoot upward
        for i in range(20):
            angle = random.uniform(-math.pi * 0.8, -math.pi * 0.2)  # Upward arc
            speed = random.uniform(3.0, 6.0)
            self.particle_system.create_particle(
                x, y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                particle_type='spark',
                color='#FF9100'  # Celebratory orange
            )
    
    def _create_shake_animation(self, x, y):
        """Create a shaking animation for errors."""
        if not self.particle_system:
            return
            
        # Create particles that move in a zigzag pattern
        for i in range(12):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1.0, 2.0)
            self.particle_system.create_particle(
                x, y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                particle_type='physics',
                color='#FF5252'  # Error red
            )
    
    def _create_bounce_animation(self, x, y):
        """Create a casual bouncy animation."""
        if not self.particle_system:
            return
            
        # Create bouncy particles
        for i in range(10):
            angle = random.uniform(-math.pi, 0)  # Downward arc
            speed = random.uniform(1.0, 3.0)
            self.particle_system.create_particle(
                x, y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                particle_type='bounce',
                color='#00A8FF'  # Cool blue
            )
    
    def _create_burst_animation(self, x, y):
        """Create a surprise burst animation."""
        if not self.particle_system:
            return
            
        # Create particles that burst outward
        for i in range(25):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2.0, 5.0)
            self.particle_system.create_particle(
                x, y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                particle_type='spark',
                color='#00D2FF'  # Bright cyan
            )
    
    def update(self, dt, animation_state, x, y):
        """
        Update personality traits and possibly trigger automatic reactions.
        
        Args:
            dt (float): Time delta in seconds
            animation_state (str): Current animation state
            x (float): X coordinate for visual effects
            y (float): Y coordinate for visual effects
        """
        current_time = time.time()
        
        # Check if enough time has passed since last reaction
        if current_time - self.last_reaction_time > self.reaction_cooldown:
            # Chance to create a random reaction based on expressiveness
            if random.random() < self.expressiveness * 0.1:  # Low chance for automatic reactions
                # Choose a reaction type based on current state
                if animation_state == 'idle':
                    reaction_types = ['casual', 'thinking']
                elif animation_state == 'listening':
                    reaction_types = ['thinking', 'surprise']
                elif animation_state == 'speaking':
                    reaction_types = ['casual', 'success']
                else:
                    reaction_types = list(self.reactions.keys())
                    
                reaction_type = random.choice(reaction_types)
                self.create_visual_reaction(x, y, reaction_type)
                self.last_reaction_time = current_time