#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Animated Display Module

This module provides a futuristic animated GUI for the Jarvis assistant,
similar to Apple's Siri with reactive visualizations.
"""

import tkinter as tk
from tkinter import Canvas, scrolledtext
import threading
import queue
import math
import random
import time
from PIL import Image, ImageTk
import numpy as np

class AnimatedDisplayWindow:
    """
    Provides a futuristic graphical user interface for displaying assistant responses
    with animated visualizations that react to voice input and output.
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
        self.particles = []
        self.wave_points = []
        self.animation_intensity = 0
        self.animation_fade_speed = 0.05
        self.animation_state = "idle"  # idle, listening, speaking
        self.color_scheme = {
            "bg_dark": "#0a0f18",
            "bg_medium": "#1a2634",
            "accent": "#0084ff",
            "accent_glow": "#00a2ff",
            "text": "#ffffff",
            "text_dim": "#a0a8b0"
        }
    
    def _create_window(self):
        """
        Create the tkinter window with futuristic UI elements and animation canvas.
        """
        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S.")
        self.root.geometry("800x600")
        self.root.configure(bg=self.color_scheme["bg_dark"])
        
        # Create main container
        main_container = tk.Frame(self.root, bg=self.color_scheme["bg_dark"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Create header with futuristic design
        header = tk.Frame(main_container, bg=self.color_scheme["bg_dark"], height=60)
        header.pack(fill=tk.X, pady=(0, 10))
        
        # Create animated logo/title
        title_frame = tk.Frame(header, bg=self.color_scheme["bg_dark"])
        title_frame.pack(side=tk.LEFT, padx=10)
        
        title = tk.Label(
            title_frame, 
            text="J.A.R.V.I.S.", 
            font=("Helvetica", 24, "bold"), 
            fg=self.color_scheme["accent"], 
            bg=self.color_scheme["bg_dark"]
        )
        title.pack(side=tk.TOP)
        
        subtitle = tk.Label(
            title_frame, 
            text="Just A Rather Very Intelligent System", 
            font=("Helvetica", 10), 
            fg=self.color_scheme["text_dim"], 
            bg=self.color_scheme["bg_dark"]
        )
        subtitle.pack(side=tk.TOP)
        
        # Status indicator
        self.status_indicator = tk.Label(
            header, 
            text="● IDLE", 
            font=("Helvetica", 10), 
            fg=self.color_scheme["text_dim"], 
            bg=self.color_scheme["bg_dark"]
        )
        self.status_indicator.pack(side=tk.RIGHT, padx=10)
        
        # Create animation canvas
        canvas_frame = tk.Frame(main_container, bg=self.color_scheme["bg_dark"], height=200)
        canvas_frame.pack(fill=tk.X, pady=10)
        
        self.canvas = Canvas(
            canvas_frame, 
            bg=self.color_scheme["bg_dark"], 
            height=180, 
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create response area with futuristic styling
        response_frame = tk.Frame(main_container, bg=self.color_scheme["bg_medium"])
        response_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Add a thin accent line above the response area
        accent_line = tk.Frame(response_frame, bg=self.color_scheme["accent"], height=2)
        accent_line.pack(fill=tk.X, side=tk.TOP)
        
        self.text_area = scrolledtext.ScrolledText(
            response_frame,
            wrap=tk.WORD,
            font=("Helvetica", 12),
            bg=self.color_scheme["bg_medium"],
            fg=self.color_scheme["text"],
            padx=15,
            pady=15,
            borderwidth=0,
            highlightthickness=0
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.config(state=tk.DISABLED)
        
        # Create footer with system info
        footer = tk.Frame(main_container, bg=self.color_scheme["bg_dark"], height=30)
        footer.pack(fill=tk.X, side=tk.BOTTOM, pady=(10, 0))
        
        footer_text = tk.Label(
            footer, 
            text="System Ready", 
            font=("Helvetica", 9), 
            fg=self.color_scheme["text_dim"], 
            bg=self.color_scheme["bg_dark"]
        )
        footer_text.pack(side=tk.LEFT, padx=10)
        
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
        # Get canvas dimensions
        self.canvas_width = self.canvas.winfo_reqwidth()
        self.canvas_height = self.canvas.winfo_reqheight()
        
        # Create wave points for the audio visualization
        num_points = 100
        self.wave_points = []
        for i in range(num_points):
            x = i * (self.canvas_width / (num_points - 1))
            y = self.canvas_height / 2
            point = {"x": x, "y": y, "amplitude": 0, "speed": 0.1 + random.random() * 0.1}
            self.wave_points.append(point)
        
        # Create the wave line
        self.wave_line = self.canvas.create_line(
            [p["x"] for p in self.wave_points], 
            [p["y"] for p in self.wave_points],
            fill=self.color_scheme["accent"],
            width=2,
            smooth=True
        )
        
        # Create central circle
        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2
        radius = 40
        self.center_circle = self.canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            outline=self.color_scheme["accent"],
            width=2,
            fill=""
        )
        
        # Create glow effect
        self.glow_circle = self.canvas.create_oval(
            center_x - radius - 10, center_y - radius - 10,
            center_x + radius + 10, center_y + radius + 10,
            outline=self.color_scheme["accent_glow"],
            width=1,
            fill="",
            stipple="gray50"
        )
    
    def _animate(self):
        """
        Update the animation frame.
        """
        if not self.is_running:
            return
        
        # Update animation intensity based on state
        if self.animation_state == "idle":
            target_intensity = 0.2
        elif self.animation_state == "listening":
            target_intensity = 0.6
        elif self.animation_state == "speaking":
            target_intensity = 1.0
        
        # Smoothly transition to target intensity
        if self.animation_intensity < target_intensity:
            self.animation_intensity += self.animation_fade_speed
        elif self.animation_intensity > target_intensity:
            self.animation_intensity -= self.animation_fade_speed
        
        self.animation_intensity = max(0.1, min(1.0, self.animation_intensity))
        
        # Update wave animation
        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2
        
        # Update wave points
        for i, point in enumerate(self.wave_points):
            # Calculate distance from center (normalized)
            dx = (point["x"] - center_x) / (self.canvas_width / 2)
            
            # Calculate new amplitude based on animation state
            time_factor = time.time() * point["speed"]
            wave = math.sin(time_factor + i * 0.2) * self.animation_intensity
            
            # Apply amplitude
            max_amplitude = 30 * self.animation_intensity
            point["amplitude"] = wave * max_amplitude
            
            # Update y position
            point["y"] = center_y + point["amplitude"]
        
        # Update wave line
        self.canvas.coords(
            self.wave_line,
            [p["x"] for p in self.wave_points],
            [p["y"] for p in self.wave_points]
        )
        
        # Update center circle pulse effect
        radius = 40 + 10 * math.sin(time.time() * 2) * self.animation_intensity
        self.canvas.coords(
            self.center_circle,
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius
        )
        
        # Update glow effect
        glow_radius = radius + 10 + 5 * math.sin(time.time() * 1.5) * self.animation_intensity
        self.canvas.coords(
            self.glow_circle,
            center_x - glow_radius, center_y - glow_radius,
            center_x + glow_radius, center_y + glow_radius
        )
        
        # Update colors based on state
        if self.animation_state == "idle":
            color = self.color_scheme["accent"]
            glow_color = self.color_scheme["accent_glow"]
        elif self.animation_state == "listening":
            color = "#00ff00"  # Green for listening
            glow_color = "#00cc00"
        elif self.animation_state == "speaking":
            color = "#ff9500"  # Orange for speaking
            glow_color = "#cc7a00"
        
        self.canvas.itemconfig(self.wave_line, fill=color)
        self.canvas.itemconfig(self.center_circle, outline=color)
        self.canvas.itemconfig(self.glow_circle, outline=glow_color)
        
        # Schedule next animation frame
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
        
        Args:
            text (str): The text to display
        """
        self.text_area.config(state=tk.NORMAL)
        
        # Add timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        self.text_area.insert(tk.END, f"\n[{timestamp}] 🤖 J.A.R.V.I.S.:\n")
        self.text_area.insert(tk.END, f"{text}\n")
        self.text_area.insert(tk.END, "\n" + "─"*50 + "\n")
        
        # Apply tag for timestamp
        self.text_area.tag_add("timestamp", f"end-{len(text)+len(timestamp)+20} linestart", f"end-{len(text)+len(timestamp)+10} lineend")
        self.text_area.tag_config("timestamp", foreground=self.color_scheme["text_dim"])
        
        # Apply tag for assistant name
        self.text_area.tag_add("assistant", f"end-{len(text)+10} linestart+{len(timestamp)+4}", f"end-{len(text)+10} linestart+{len(timestamp)+17}")
        self.text_area.tag_config("assistant", foreground=self.color_scheme["accent"], font=("Helvetica", 12, "bold"))
        
        # Auto-scroll to the bottom
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)
    
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
        Add a response to the display queue and trigger speaking animation.
        
        Args:
            text (str): The text to display
        """
        if self.is_running:
            self.response_queue.put(text)
            self.set_animation_state("speaking")
            # Schedule return to idle state after a delay
            if self.root:
                self.root.after(5000, lambda: self.set_animation_state("idle"))
    
    def set_animation_state(self, state):
        """
        Set the current animation state.
        
        Args:
            state (str): One of 'idle', 'listening', or 'speaking'
        """
        self.animation_state = state
        
        # Update status indicator
        if self.status_indicator:
            if state == "idle":
                self.status_indicator.config(text="● IDLE", fg=self.color_scheme["text_dim"])
            elif state == "listening":
                self.status_indicator.config(text="● LISTENING", fg="#00ff00")
            elif state == "speaking":
                self.status_indicator.config(text="● SPEAKING", fg="#ff9500")
    
    def stop(self):
        """
        Stop the display window.
        """
        self.is_running = False
        if self.root:
            self.root.quit()
            self.root.destroy()