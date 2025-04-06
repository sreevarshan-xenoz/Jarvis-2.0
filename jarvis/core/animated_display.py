#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Animated Display Module

This module provides a simple animated GUI for the Jarvis assistant.
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

class AnimatedDisplayWindow:
    """
    Provides a graphical user interface for displaying assistant responses
    with simple animated visualizations.
    """
    
    def __init__(self):
        """
        Initialize the animated display window.
        """
        self.root = None
        self.text_area = None
        self.canvas = None
        self.response_queue = queue.Queue()
        self.is_running = False
        self.window_thread = None
        self.animation_active = False
        self.wave_points = []
        self.animation_intensity = 0
        self.animation_fade_speed = 0.05
        self.animation_state = "idle"  # idle, listening, speaking
        self.status_indicator = None  # Initialize status_indicator attribute
        
        # Animation state properties with enhanced dynamics
        self.state_properties = {
            "idle": {
                "intensity": 0.4,
                "color": "#3498db",
                "wave_amplitude": 12,
                "pulse_speed": 0.015,
                "glow_radius": 8,
                "wave_frequency": 0.8,
                "ripple_intensity": 0.3,
                "color_shift": 0.15
            },
            "listening": {
                "intensity": 0.7,
                "color": "#2ecc71",
                "wave_amplitude": 18,
                "pulse_speed": 0.03,
                "glow_radius": 10,
                "wave_frequency": 1.2,
                "ripple_intensity": 0.5,
                "color_shift": 0.35
            },
            "speaking": {
                "intensity": 0.9,
                "color": "#e74c3c",
                "wave_amplitude": 25,
                "pulse_speed": 0.045,
                "glow_radius": 15,
                "wave_frequency": 1.6,
                "ripple_intensity": 0.7,
                "color_shift": 0.6
            },
            "conversation": {
                "intensity": 0.8,
                "color": "#9b59b6",
                "wave_amplitude": 22,
                "pulse_speed": 0.035,
                "glow_radius": 12,
                "wave_frequency": 1.4,
                "ripple_intensity": 0.6,
                "color_shift": 0.45
            }
        }
        
        # Simplified color scheme
        self.color_scheme = {
            "bg_dark": "#1c2833",
            "bg_medium": "#2c3e50",
            "accent": "#3498db",
            "accent_glow": "#2980b9",
            "text": "#ecf0f1",
            "text_dim": "#bdc3c7"
        }
    
    def _create_window(self):
        """
        Create the tkinter window with UI elements.
        """
        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S.")
        self.root.geometry("900x650")
        self.root.configure(bg=self.color_scheme["bg_dark"])
        self.root.minsize(800, 600)
        
        # Create header
        header = tk.Frame(self.root, bg=self.color_scheme["bg_dark"])
        header.pack(fill=tk.X, padx=10, pady=10)
        
        # Title
        title = tk.Label(
            header, 
            text="JARVIS", 
            font=("Arial", 18, "bold"), 
            fg=self.color_scheme["accent"], 
            bg=self.color_scheme["bg_dark"]
        )
        title.pack(side=tk.LEFT, padx=10)
        
        # Status indicator
        self.status_indicator = tk.Label(
            header, 
            text="● IDLE", 
            font=("Arial", 11), 
            fg=self.color_scheme["text_dim"], 
            bg=self.color_scheme["bg_dark"]
        )
        self.status_indicator.pack(side=tk.RIGHT, padx=10)
        
        # Create animation canvas
        self.canvas = Canvas(
            self.root, 
            bg=self.color_scheme["bg_dark"], 
            height=150,
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.X, padx=10, pady=5)
        
        # Create response area
        response_frame = tk.Frame(
            self.root, 
            bg=self.color_scheme["bg_medium"]
        )
        response_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Text area
        self.text_area = scrolledtext.ScrolledText(
            response_frame,
            wrap=tk.WORD,
            font=("Segoe UI", 12),
            bg=self.color_scheme["bg_medium"],
            fg=self.color_scheme["text"],
            padx=18,
            pady=18,
            borderwidth=0,
            highlightthickness=0
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.config(state=tk.DISABLED)
        
        # Set up window close event
        self.root.protocol("WM_DELETE_WINDOW", self.stop)
        
        # Initialize animation
        self._init_animation()
        
        # Start checking for new responses
        self.root.after(100, self._check_queue)
        
        # Start animation loop
        self.root.after(30, self._animate)
    
    def _init_animation(self):
        """
        Initialize the animation elements.
        """
        try:
            # Get canvas dimensions
            self.canvas_width = self.canvas.winfo_reqwidth() or 900
            self.canvas_height = self.canvas.winfo_reqheight() or 220
            
            # Create wave points - optimized
            num_points = 120
            self.wave_points = [{
                "x": i * (self.canvas_width / (num_points - 1)),
                "y": self.canvas_height / 2,
                "speed": 0.1,
                "phase": random.random() * math.pi * 2
            } for i in range(num_points)]
            
            # Create central orb
            center_x = self.canvas_width / 2
            center_y = self.canvas_height / 2
            self.base_radius = 45
            self.pulse_phase = 0
            
            # Main orb
            self.center_circle = self.canvas.create_oval(
                center_x - self.base_radius, center_y - self.base_radius,
                center_x + self.base_radius, center_y + self.base_radius,
                outline=self.state_properties["idle"]["color"],
                width=2.5,
                fill=""
            )
            
            # Inner glow
            self.inner_glow = self.canvas.create_oval(
                center_x - self.base_radius + 10, center_y - self.base_radius + 10,
                center_x + self.base_radius - 10, center_y + self.base_radius - 10,
                outline=self.state_properties["idle"]["color"],
                width=1.5,
                fill=""
            )
            
            # Outer glow
            self.outer_glow = self.canvas.create_oval(
                center_x - self.base_radius - 15, center_y - self.base_radius - 15,
                center_x + self.base_radius + 15, center_y + self.base_radius + 15,
                outline=self.state_properties["idle"]["color"],
                width=1,
                fill=""
            )
            
        except Exception as e:
            print(f"Error initializing animation: {e}")
    
    def _animate(self):
        """
        Update the animation frame.
        """
        if not self.is_running:
            return
        
        try:
            # Get current state properties
            state = self.animation_state if self.animation_state in self.state_properties else "idle"
            state_props = self.state_properties[state]
            
            # Update animation intensity with smooth transition
            target_intensity = state_props["intensity"]
            if self.animation_intensity < target_intensity:
                self.animation_intensity = min(target_intensity, self.animation_intensity + self.animation_fade_speed)
            elif self.animation_intensity > target_intensity:
                self.animation_intensity = max(target_intensity, self.animation_intensity - self.animation_fade_speed)
            
            # Update pulse effect
            self.pulse_phase += state_props["pulse_speed"]
            pulse_scale = 1 + math.sin(self.pulse_phase) * 0.1 * self.animation_intensity
            
            # Calculate orb dimensions
            center_x = self.canvas_width / 2
            center_y = self.canvas_height / 2
            current_radius = self.base_radius * pulse_scale
            
            # Update orb and glows
            self.canvas.coords(self.center_circle,
                center_x - current_radius, center_y - current_radius,
                center_x + current_radius, center_y + current_radius)
            
            # Update inner glow
            inner_radius = current_radius * 0.8
            self.canvas.coords(self.inner_glow,
                center_x - inner_radius, center_y - inner_radius,
                center_x + inner_radius, center_y + inner_radius)
            
            # Update outer glow
            outer_radius = current_radius * 1.3 + state_props["glow_radius"]
            self.canvas.coords(self.outer_glow,
                center_x - outer_radius, center_y - outer_radius,
                center_x + outer_radius, center_y + outer_radius)
            
            # Update colors with dynamic transitions
            color = state_props["color"]
            color_shift = state_props["color_shift"]
            
            # Apply color shift based on pulse phase
            pulse_color_mod = abs(math.sin(self.pulse_phase * 2)) * color_shift
            
            # Create dynamic color effect
            base_color = color
            glow_color = self._adjust_color_brightness(color, 1 + pulse_color_mod)
            outer_color = self._adjust_color_brightness(color, 1 - pulse_color_mod)
            
            self.canvas.itemconfig(self.center_circle, outline=base_color)
            self.canvas.itemconfig(self.inner_glow, outline=glow_color)
            self.canvas.itemconfig(self.outer_glow, outline=outer_color)
            
            # Update wave points
            t = time.time()
            
            # Clear previous wave
            self.canvas.delete("wave")
            
            # Get current state properties
            state = self.animation_state if self.animation_state in self.state_properties else "idle"
            state_props = self.state_properties[state]
            
            # Draw wave
            points = []
            for point in self.wave_points:
                # Calculate y position with enhanced sinusoidal components
                wave_freq = state_props["wave_frequency"]
                ripple_intensity = state_props["ripple_intensity"]
                
                # Primary sinusoidal wave with dynamic phase
                base_wave = math.sin(t * point["speed"] * wave_freq + point["phase"])
                
                # Secondary waves with varying frequencies and phases
                wave2 = math.sin(t * 1.5 * point["speed"] * wave_freq + point["phase"] * 0.5) * 0.7
                wave3 = math.sin(t * 0.75 * point["speed"] * wave_freq - point["phase"] * 0.3) * 0.5
                
                # Smooth ripple effect
                ripple = math.sin(t * 2 * point["speed"] * wave_freq + point["phase"] * 2) * ripple_intensity * 0.8
                
                # Subtle harmonic motion
                harmonic = math.cos(t * 3 * point["speed"] * wave_freq - point["phase"]) * (ripple_intensity * 0.3)
                
                # High-frequency flutter for organic movement
                flutter = math.sin(t * 4 * point["speed"] + point["phase"] * 1.5) * (ripple_intensity * 0.15)
                
                # Combine all wave components with weighted influence
                wave_height = (base_wave * 1.2 + wave2 + wave3 + ripple + harmonic + flutter) * \
                    state_props["wave_amplitude"] * \
                    self.animation_intensity
                
                y = point["y"] + wave_height
                points.extend([point["x"], y])
            
            # Draw main wave
            if len(points) >= 4:
                # Create gradient effect with multiple lines
                alpha = 0.8
                for i in range(3):
                    offset = i * 2
                    width = 3 - i * 0.8
                    
                    # Adjust points for parallel waves
                    wave_points = points.copy()
                    for j in range(1, len(wave_points), 2):
                        wave_points[j] += offset
                    
                    # Convert color to RGBA format for transparency
                    color = state_props["color"]
                    r = int(color[1:3], 16)
                    g = int(color[3:5], 16)
                    b = int(color[5:7], 16)
                    alpha_hex = int(alpha * 255)
                    rgba_color = f"#{r:02x}{g:02x}{b:02x}{alpha_hex:02x}"
                    
                    self.canvas.create_line(
                        wave_points,
                        smooth=True,
                        fill=rgba_color,
                        width=width,
                        tags="wave"
                    )
                    alpha *= 0.6
            
            # Update circle glow
            if hasattr(self, "center_circle") and hasattr(self, "glow_circle"):
                glow_color = self.color_scheme[self.state_properties[self.animation_state]["color"]]
                self.canvas.itemconfig(self.center_circle, outline=glow_color)
                self.canvas.itemconfig(self.glow_circle, outline=glow_color)
            
        except Exception as e:
            print(f"Error in animation: {e}")
        
        # Schedule next frame
        self.root.after(30, self._animate)
    
    def _check_queue(self):
        """
        Check for new responses in the queue and update the display.
        """
        try:
            while True:
                response = self.response_queue.get_nowait()
                self._update_display(response)
                self.response_queue.task_done()
        except queue.Empty:
            pass
        
        if self.is_running:
            self.root.after(100, self._check_queue)
    
    def _update_display(self, text):
        """
        Update the text area with a new response.
        """
        self.text_area.config(state=tk.NORMAL)
        
        # Add timestamp
        timestamp = time.strftime("%H:%M:%S")
        self.text_area.insert(tk.END, f"\n[{timestamp}] 🤖 JARVIS:\n")
        self.text_area.insert(tk.END, f"{text}\n")
        self.text_area.insert(tk.END, "\n" + "-"*50 + "\n")
        
        # Auto-scroll to the bottom
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)
    
    def _adjust_color_brightness(self, color, factor):
        """Adjust the brightness of a color."""
        # Remove the '#' and convert to RGB
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        # Adjust brightness
        r = min(255, max(0, int(r * factor)))
        g = min(255, max(0, int(g * factor)))
        b = min(255, max(0, int(b * factor)))
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def set_animation_state(self, state):
        """
        Set the animation state.
        
        Args:
            state (str): Animation state ('idle', 'listening', 'speaking', or 'conversation')
        """
        if state in self.state_properties:
            self.animation_state = state
            status_text = f"● {state.upper()}"
            # Only update status indicator if it exists
            if self.status_indicator is not None:
                status_color = self.state_properties[state]["color"]
                self.status_indicator.config(text=status_text, fg=status_color)
    
    def start(self):
        """
        Start the display window in a separate thread.
        """
        if not self.is_running:
            self.is_running = True
            self.window_thread = threading.Thread(target=self._run_window)
            self.window_thread.daemon = True
            self.window_thread.start()
    
    def _run_window(self):
        """
        Run the tkinter main loop in a separate thread.
        """
        self._create_window()
        self.root.mainloop()
        self.is_running = False
    
    def display(self, text):
        """
        Add a response to the display queue.
        
        Args:
            text (str): The text to display
        """
        if self.is_running:
            self.response_queue.put(text)
    
    def stop(self):
        """
        Stop the display window.
        """
        self.is_running = False
        if self.root:
            self.root.quit()
            self.root.destroy()