#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Enhanced Animated Display Module

This module extends the original animated display with advanced features:
- Audio spectrum visualization using FFT
- Enhanced particle system with physics-based interactions
- 3D rendering with PyOpenGL
- Customizable themes and styles
"""

import tkinter as tk
from tkinter import Canvas, scrolledtext
import threading
import queue
import math
import random
import time
from PIL import Image, ImageTk, ImageDraw
import numpy as np
from tkinter import ttk

# Import original animated display
from core.animated_display import AnimatedDisplayWindow

# Import enhanced features
from core.ui_integrator import UIIntegrator

class EnhancedAnimatedDisplayWindow(AnimatedDisplayWindow):
    """
    Enhanced version of the AnimatedDisplayWindow with advanced visualization features.
    """
    
    def __init__(self):
        """
        Initialize the enhanced animated display window.
        """
        # Initialize enhanced features
        self.ui_integrator = None
        self.enhanced_objects = []
        self.using_enhanced_features = True
        
        # Initialize the parent class
        super().__init__()
        
        # Create window in the main thread
        self.root = tk.Tk()
        self.root.withdraw()  # Hide window initially
        self.root.after(100, self._delayed_window_creation)
    
    def _delayed_window_creation(self):
        """
        Create the window after a short delay to ensure proper initialization.
        """
        self.root.deiconify()  # Show window
        self._create_window()
        
        # Initialize UI integrator after window creation
        self.ui_integrator = UIIntegrator(self)
        self.ui_integrator.initialize()
    
    def _create_window(self):
        """
        Create the tkinter window with enhanced UI elements.
        """
        # Call the parent method to create the basic window
        super()._create_window()
        
        # Initialize UI integrator
        self.ui_integrator = UIIntegrator(self)
        
        # Add a toggle button for enhanced features
        self.enhanced_toggle_button = self._create_hover_button(self.root, "✨", "Toggle Enhanced UI")
        self.enhanced_toggle_button.place(x=10, y=10)
        self.enhanced_toggle_button.bind("<Button-1>", lambda e: self._toggle_enhanced_features())
    
    def _toggle_enhanced_features(self):
        """
        Toggle enhanced UI features on/off.
        """
        self.using_enhanced_features = not self.using_enhanced_features
        
        # Update button appearance
        if self.using_enhanced_features:
            self.enhanced_toggle_button.config(fg=self.color_scheme["accent"])
            # Initialize UI integrator if needed
            if not self.ui_integrator.initialized:
                self.ui_integrator.initialize()
        else:
            self.enhanced_toggle_button.config(fg=self.color_scheme["text_dim"])
            # Clear enhanced objects
            self._clear_enhanced_objects()
    
    def _clear_enhanced_objects(self):
        """
        Clear all enhanced visualization objects from the canvas.
        """
        if hasattr(self, 'canvas') and self.canvas:
            for obj_id in self.enhanced_objects:
                try:
                    self.canvas.delete(obj_id)
                except:
                    pass
            self.enhanced_objects = []
    
    def _init_animation(self):
        """
        Initialize the animation elements with enhanced features.
        """
        # Call the parent method to initialize basic animation
        super()._init_animation()
        
        # Initialize enhanced features
        if not self.ui_integrator:
            self.ui_integrator = UIIntegrator(self)
            self.ui_integrator.initialize()
    
    def _animate(self):
        """
        Update the animation frame with enhanced features.
        """
        if not self.is_running:
            return
        
        # Clear previous enhanced objects
        self._clear_enhanced_objects()
        
        # Call the parent method for basic animation
        super()._animate()
        
        # Add enhanced visualizations if enabled
        if self.using_enhanced_features and self.ui_integrator and self.ui_integrator.initialized:
            # Get canvas center
            center_x = self.canvas_width / 2
            center_y = self.canvas_height / 2
            
            # Integrate enhanced features
            enhanced_data = self.ui_integrator.integrate_with_animation(
                self.animation_state,
                self.animation_intensity,
                center_x,
                center_y
            )
            
            # Render audio spectrum if available
            if enhanced_data['audio_spectrum']:
                spectrum_ids = self.ui_integrator.render_audio_spectrum(
                    self.canvas,
                    enhanced_data['audio_spectrum'],
                    center_x,
                    center_y + 60,  # Position below center
                    80  # Height of visualization
                )
                self.enhanced_objects.extend(spectrum_ids)
            
            # Render enhanced particles if available
            if enhanced_data['particles']:
                particle_ids = self.ui_integrator.render_enhanced_particles(
                    self.canvas,
                    enhanced_data['particles']
                )
                self.enhanced_objects.extend(particle_ids)
            
            # Render 3D scene if available
            if enhanced_data['3d_rendering']:
                image_id = self.ui_integrator.render_3d_scene(
                    self.canvas,
                    enhanced_data['3d_rendering'],
                    center_x,
                    center_y
                )
                if image_id:
                    self.enhanced_objects.append(image_id)
        
        # Schedule next animation frame
        self.root.after(30, self._animate)
    
    def set_animation_state(self, state):
        """
        Set the animation state with enhanced features.
        
        Args:
            state (str): Animation state ('idle', 'listening', 'speaking', or 'conversation')
        """
        # Store previous state for transition effects
        self.previous_state = getattr(self, 'animation_state', 'idle')
        
        # Call parent method
        super().set_animation_state(state)
        
        # Apply state to enhanced features
        if self.using_enhanced_features and self.ui_integrator and self.ui_integrator.initialized:
            # Create keyword-based particle burst on state change
            if hasattr(self.ui_integrator, 'particle_system') and self.ui_integrator.particle_system:
                center_x = self.canvas_width / 2
                center_y = self.canvas_height / 2
                
                if state == 'listening' and self.previous_state != 'listening':
                    self.ui_integrator.particle_system.create_keyword_burst(
                        center_x, center_y, 'listening', self.color_scheme['success']
                    )
                elif state == 'speaking' and self.previous_state != 'speaking':
                    self.ui_integrator.particle_system.create_keyword_burst(
                        center_x, center_y, 'speaking', self.color_scheme['warning']
                    )
    
    def stop(self):
        """
        Stop the display window and clean up resources.
        """
        # Clean up enhanced features
        if self.ui_integrator:
            self.ui_integrator.cleanup()
        
        # Call parent method
        super().stop()