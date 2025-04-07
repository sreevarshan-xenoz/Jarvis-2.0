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
        
        # Animation state properties - simplified
        self.state_properties = {
            "idle": {
                "intensity": 0.3,
                "color": "accent",
                "wave_amplitude": 10
            },
            "active": {
                "intensity": 0.8,
                "color": "accent",
                "wave_amplitude": 15
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
            
            # Create central circle
            center_x = self.canvas_width / 2
            center_y = self.canvas_height / 2
            radius = 45
            
            # Main circle
            self.center_circle = self.canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                outline=self.color_scheme["accent"],
                width=2.5,
                fill=""
            )
            
            # Glow effect
            self.glow_circle = self.canvas.create_oval(
                center_x - radius - 10, center_y - radius - 10,
                center_x + radius + 10, center_y + radius + 10,
                outline=self.color_scheme["accent_glow"],
                width=1.5,
                fill="",
                stipple="gray50"
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
            # Update animation intensity
            target_intensity = self.state_properties[self.animation_state]["intensity"]
            if self.animation_intensity < target_intensity:
                self.animation_intensity = min(target_intensity, self.animation_intensity + self.animation_fade_speed)
            elif self.animation_intensity > target_intensity:
                self.animation_intensity = max(target_intensity, self.animation_intensity - self.animation_fade_speed)
            
            # Update wave points
            t = time.time()
            points = []
            for point in self.wave_points:
                x = point["x"]
                base_y = point["y"]
                amplitude = self.state_properties[self.animation_state]["wave_amplitude"] * self.animation_intensity
                y = base_y + math.sin(t * point["speed"] + point["phase"]) * amplitude
                points.append(x)
                points.append(y)
            
            # Draw wave
            if hasattr(self, "wave"):
                self.canvas.delete("wave")
            if len(points) >= 4:
                self.wave = self.canvas.create_line(
                    points,
                    fill=self.color_scheme[self.state_properties[self.animation_state]["color"]],
                    width=2,
                    smooth=True,
                    tags="wave"
                )
            
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
    
    def set_animation_state(self, state):
        """
        Set the animation state.
        
        Args:
            state (str): Animation state ('idle' or 'active')
        """
        mapped_state = "active" if state in ["listening", "speaking"] else "idle"
        if mapped_state in self.state_properties:
            self.animation_state = mapped_state
            status_text = f"● {state.upper()}"
            self.status_indicator.config(text=status_text, fg=self.color_scheme["accent"])
    
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