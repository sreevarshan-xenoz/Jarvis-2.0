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
from PIL import Image, ImageTk, ImageDraw
import numpy as np
from tkinter import ttk  # For modern themed widgets

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
        # Modern color scheme with gradients
        self.color_scheme = {
            "bg_dark": "#0a1622",
            "bg_medium": "#162231",
            "bg_gradient_top": "#0d1a29",
            "bg_gradient_bottom": "#1e2b3a",
            "accent": "#00a8ff",
            "accent_glow": "#00d2ff",
            "accent_secondary": "#7b42ff",
            "text": "#ffffff",
            "text_dim": "#a0b8d0",
            "success": "#00e676",
            "warning": "#ff9100",
            "error": "#ff5252"
        }
        # Particle settings
        self.max_particles = 50
        self.particle_fade_speed = 0.02
        self.particle_size_range = (2, 6)
        self.particle_speed_range = (0.5, 2.0)
    
    def _create_window(self):
        """
        Create the tkinter window with futuristic UI elements and animation canvas.
        """
        self.root = tk.Tk()
        self.root.title("J.A.R.V.I.S.")
        self.root.geometry("900x650")
        self.root.configure(bg=self.color_scheme["bg_dark"])
        self.root.minsize(800, 600)  # Set minimum window size
        
        # Create gradient background image
        self._create_gradient_background()
        
        # Create main container with padding
        main_container = tk.Frame(self.root, bg=self.color_scheme["bg_dark"])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create header with modern design
        header = tk.Frame(main_container, bg=self.color_scheme["bg_dark"], height=70)
        header.pack(fill=tk.X, pady=(0, 15))
        
        # Create animated logo/title with glow effect
        title_frame = tk.Frame(header, bg=self.color_scheme["bg_dark"])
        title_frame.pack(side=tk.LEFT, padx=10)
        
        # Main title with custom font and glow effect
        title = tk.Label(
            title_frame, 
            text="J.A.R.V.I.S.", 
            font=("Segoe UI", 28, "bold"), 
            fg=self.color_scheme["accent"], 
            bg=self.color_scheme["bg_dark"]
        )
        title.pack(side=tk.TOP)
        
        # Add subtitle with modern font
        subtitle = tk.Label(
            title_frame, 
            text="Just A Rather Very Intelligent System", 
            font=("Segoe UI", 11), 
            fg=self.color_scheme["text_dim"], 
            bg=self.color_scheme["bg_dark"]
        )
        subtitle.pack(side=tk.TOP)
        
        # Create interactive buttons frame
        buttons_frame = tk.Frame(header, bg=self.color_scheme["bg_dark"])
        buttons_frame.pack(side=tk.RIGHT, padx=10)
        
        # Add interactive buttons with hover effects
        self.settings_button = self._create_hover_button(buttons_frame, "⚙️", "Settings")
        self.settings_button.pack(side=tk.RIGHT, padx=5)
        
        self.info_button = self._create_hover_button(buttons_frame, "ℹ️", "Info")
        self.info_button.pack(side=tk.RIGHT, padx=5)
        
        # Status indicator with modern styling
        status_frame = tk.Frame(header, bg=self.color_scheme["bg_dark"])
        status_frame.pack(side=tk.RIGHT, padx=15)
        
        self.status_indicator = tk.Label(
            status_frame, 
            text="● IDLE", 
            font=("Segoe UI", 11, "bold"), 
            fg=self.color_scheme["text_dim"], 
            bg=self.color_scheme["bg_dark"]
        )
        self.status_indicator.pack(side=tk.RIGHT)
        
        # Create animation canvas with increased height
        canvas_frame = tk.Frame(main_container, bg=self.color_scheme["bg_dark"])
        canvas_frame.pack(fill=tk.X, pady=10)
        
        # Create canvas with rounded corners effect
        self.canvas = Canvas(
            canvas_frame, 
            bg=self.color_scheme["bg_dark"], 
            height=220,  # Increased height for more visual impact
            highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Create response area with modern styling and rounded corners
        response_container = tk.Frame(main_container, bg=self.color_scheme["bg_dark"])
        response_container.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create a frame for the response area with a gradient border effect
        response_frame = tk.Frame(
            response_container, 
            bg=self.color_scheme["bg_medium"],
            highlightbackground=self.color_scheme["accent"],
            highlightthickness=1,
            bd=0
        )
        response_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Add a gradient accent line above the response area
        accent_frame = tk.Frame(response_frame, height=3, bg=self.color_scheme["bg_medium"])
        accent_frame.pack(fill=tk.X, side=tk.TOP)
        
        # Create gradient accent line
        accent_canvas = tk.Canvas(accent_frame, height=3, bg=self.color_scheme["bg_medium"], highlightthickness=0)
        accent_canvas.pack(fill=tk.X)
        
        # Draw gradient on accent line
        for i in range(100):
            x_ratio = i / 100
            # Create gradient from accent to accent_secondary
            r1, g1, b1 = self._hex_to_rgb(self.color_scheme["accent"])
            r2, g2, b2 = self._hex_to_rgb(self.color_scheme["accent_secondary"])
            r = int(r1 + (r2 - r1) * x_ratio)
            g = int(g1 + (g2 - g1) * x_ratio)
            b = int(b1 + (b2 - b1) * x_ratio)
            color = f"#{r:02x}{g:02x}{b:02x}"
            accent_canvas.create_line(i * 10, 0, i * 10 + 10, 0, fill=color, width=3)
        
        # Modern scrolled text area with custom styling
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
        
        # Customize scrollbar
        scrollbar = ttk.Style()
        scrollbar.configure("TScrollbar", background=self.color_scheme["bg_medium"], 
                          troughcolor=self.color_scheme["bg_dark"], 
                          borderwidth=0, 
                          arrowcolor=self.color_scheme["accent"])
        
        # Create interactive footer with system info and time
        footer = tk.Frame(main_container, bg=self.color_scheme["bg_dark"], height=35)
        footer.pack(fill=tk.X, side=tk.BOTTOM, pady=(15, 0))
        
        # System status with icon
        footer_text = tk.Label(
            footer, 
            text="⚡ System Ready", 
            font=("Segoe UI", 10), 
            fg=self.color_scheme["text_dim"], 
            bg=self.color_scheme["bg_dark"]
        )
        footer_text.pack(side=tk.LEFT, padx=10)
        
        # Add time display to footer
        self.time_display = tk.Label(
            footer,
            text=time.strftime("%H:%M:%S"),
            font=("Segoe UI", 10),
            fg=self.color_scheme["text_dim"],
            bg=self.color_scheme["bg_dark"]
        )
        self.time_display.pack(side=tk.RIGHT, padx=10)
        self.root.after(1000, self._update_time)
        
        # Set up window close event
        self.root.protocol("WM_DELETE_WINDOW", self.stop)
        
        # Initialize animation
        self._init_animation()
        
        # Start checking for new responses
        self.root.after(100, self._check_queue)
        
        # Start animation loop
        self.root.after(30, self._animate)
    
    def _create_gradient_background(self):
        """
        Create a gradient background image for the window.
        """
        width, height = 900, 650
        gradient_img = Image.new('RGBA', (width, height), color=0)
        draw = ImageDraw.Draw(gradient_img)
        
        # Create gradient from top to bottom
        for y in range(height):
            # Calculate gradient color
            r1, g1, b1 = self._hex_to_rgb(self.color_scheme["bg_gradient_top"])
            r2, g2, b2 = self._hex_to_rgb(self.color_scheme["bg_gradient_bottom"])
            ratio = y / height
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            color = (r, g, b, 255)
            draw.line([(0, y), (width, y)], fill=color)
        
        # Add subtle noise texture for more modern look
        for _ in range(5000):
            x = random.randint(0, width-1)
            y = random.randint(0, height-1)
            brightness = random.randint(-10, 10)
            r, g, b, a = gradient_img.getpixel((x, y))
            r = max(0, min(255, r + brightness))
            g = max(0, min(255, g + brightness))
            b = max(0, min(255, b + brightness))
            gradient_img.putpixel((x, y), (r, g, b, a))
        
        # Convert to PhotoImage for tkinter
        self.bg_image = ImageTk.PhotoImage(gradient_img)
        
        # Create a label to hold the background image
        bg_label = tk.Label(self.root, image=self.bg_image)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        bg_label.lower()  # Put it behind all other widgets
    
    def _hex_to_rgb(self, hex_color):
        """
        Convert hex color to RGB tuple.
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _create_hover_button(self, parent, text, tooltip_text):
        """
        Create a button with hover effect and tooltip.
        """
        button = tk.Label(
            parent,
            text=text,
            font=("Segoe UI", 14),
            fg=self.color_scheme["text_dim"],
            bg=self.color_scheme["bg_dark"],
            padx=8,
            pady=4
        )
        
        # Create tooltip
        tooltip = tk.Label(
            parent,
            text=tooltip_text,
            font=("Segoe UI", 9),
            fg=self.color_scheme["text"],
            bg=self.color_scheme["bg_medium"],
            padx=6,
            pady=2,
            relief="solid",
            bd=0
        )
        tooltip.place_forget()
        
        # Add hover effects
        def on_enter(e):
            button.config(fg=self.color_scheme["accent"])
            x, y, _, _ = button.bbox("all")
            x += button.winfo_rootx() + 20
            y += button.winfo_rooty() + 20
            tooltip.place(x=x, y=y)
            
        def on_leave(e):
            button.config(fg=self.color_scheme["text_dim"])
            tooltip.place_forget()
            
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        
        return button
    
    def _update_time(self):
        """
        Update the time display in the footer.
        """
        if hasattr(self, 'time_display') and self.time_display:
            self.time_display.config(text=time.strftime("%H:%M:%S"))
            if self.is_running:
                self.root.after(1000, self._update_time)
    
    def _init_animation(self):
        """
        Initialize the animation elements.
        """
        # Get canvas dimensions
        self.canvas_width = self.canvas.winfo_reqwidth()
        self.canvas_height = self.canvas.winfo_reqheight()
        
        # Create wave points for the audio visualization with more points for smoother animation
        num_points = 150
        self.wave_points = []
        for i in range(num_points):
            x = i * (self.canvas_width / (num_points - 1))
            y = self.canvas_height / 2
            # Add more randomness to wave properties for more natural look
            point = {
                "x": x, 
                "y": y, 
                "amplitude": 0, 
                "speed": 0.05 + random.random() * 0.15,
                "phase": random.random() * math.pi * 2,  # Random phase offset
                "frequency": 0.8 + random.random() * 0.4  # Random frequency
            }
            self.wave_points.append(point)
        
        # Create multiple wave lines for layered effect
        self.wave_lines = []
        
        # Main wave line
        self.wave_line = self.canvas.create_line(
            [p["x"] for p in self.wave_points], 
            [p["y"] for p in self.wave_points],
            fill=self.color_scheme["accent"],
            width=2.5,
            smooth=True,
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND
        )
        self.wave_lines.append(self.wave_line)
        
        # Secondary wave lines with different colors and opacity
        secondary_line = self.canvas.create_line(
            [p["x"] for p in self.wave_points], 
            [p["y"] for p in self.wave_points],
            fill=self.color_scheme["accent_secondary"],
            width=1.5,
            smooth=True,
            capstyle=tk.ROUND,
            joinstyle=tk.ROUND
        )
        self.wave_lines.append(secondary_line)
        
        # Create central circle with gradient fill
        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2
        radius = 45
        
        # Create inner circle with gradient effect
        self.inner_circle = self.canvas.create_oval(
            center_x - radius * 0.7, center_y - radius * 0.7,
            center_x + radius * 0.7, center_y + radius * 0.7,
            outline="",
            fill=self.color_scheme["accent_secondary"],
            stipple="gray25"
        )
        
        # Main circle with thicker outline
        self.center_circle = self.canvas.create_oval(
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius,
            outline=self.color_scheme["accent"],
            width=2.5,
            fill=""
        )
        
        # Create multiple glow effects for depth
        self.glow_circles = []
        
        # Primary glow
        self.glow_circle = self.canvas.create_oval(
            center_x - radius - 10, center_y - radius - 10,
            center_x + radius + 10, center_y + radius + 10,
            outline=self.color_scheme["accent_glow"],
            width=1.5,
            fill="",
            stipple="gray50"
        )
        self.glow_circles.append(self.glow_circle)
        
        # Secondary glow
        secondary_glow = self.canvas.create_oval(
            center_x - radius - 20, center_y - radius - 20,
            center_x + radius + 20, center_y + radius + 20,
            outline=self.color_scheme["accent_secondary"],
            width=1,
            fill="",
            stipple="gray25"
        )
        self.glow_circles.append(secondary_glow)
        
        # Initialize particles
        self.particles = []
        self._init_particles()
        
        # Create radial lines for additional visual effect
        self.radial_lines = []
        self._create_radial_lines(center_x, center_y, radius)
    
    def _init_particles(self):
        """
        Initialize particle system for dynamic effects.
        """
        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2
        
        # Create initial particles
        for _ in range(self.max_particles // 2):  # Start with half the particles
            self._create_particle(center_x, center_y)
    
    def _create_particle(self, x, y):
        """
        Create a new particle at the specified position.
        """
        # Random angle and speed
        angle = random.random() * math.pi * 2
        speed = random.uniform(*self.particle_speed_range)
        size = random.uniform(*self.particle_size_range)
        
        # Calculate velocity based on angle and speed
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed
        
        # Random lifetime and opacity
        lifetime = random.uniform(0.7, 1.0)
        opacity = random.uniform(0.6, 1.0)
        
        # Create particle object
        particle = {
            "x": x,
            "y": y,
            "vx": vx,
            "vy": vy,
            "size": size,
            "lifetime": lifetime,
            "max_lifetime": lifetime,
            "opacity": opacity,
            "color": self.color_scheme["accent"],
            "id": None  # Will be set when drawn
        }
        
        # Draw particle on canvas
        particle_id = self.canvas.create_oval(
            x - size, y - size,
            x + size, y + size,
            fill=particle["color"],
            outline="",
            stipple="gray75"
        )
        particle["id"] = particle_id
        
        # Add to particles list
        self.particles.append(particle)
    
    def _create_radial_lines(self, center_x, center_y, radius):
        """
        Create radial lines emanating from the center circle.
        """
        num_lines = 12
        line_length = radius * 0.7  # Length of lines relative to circle radius
        
        for i in range(num_lines):
            angle = (i / num_lines) * math.pi * 2
            x1 = center_x + math.cos(angle) * radius
            y1 = center_y + math.sin(angle) * radius
            x2 = center_x + math.cos(angle) * (radius + line_length)
            y2 = center_y + math.sin(angle) * (radius + line_length)
            
            line = self.canvas.create_line(
                x1, y1, x2, y2,
                fill=self.color_scheme["accent"],
                width=1,
                dash=(3, 3),  # Dashed line
                state=tk.HIDDEN  # Initially hidden
            )
            self.radial_lines.append(line)
    
    def _animate(self):
        """
        Update the animation frame with modern effects.
        """
        if not self.is_running:
            return
        
        # Update animation intensity based on state with smoother transitions
        if self.animation_state == "idle":
            target_intensity = 0.2
            target_color = self.color_scheme["accent"]
            target_glow = self.color_scheme["accent_glow"]
            target_secondary = self.color_scheme["accent_secondary"]
            particle_spawn_rate = 1  # Particles per frame
        elif self.animation_state == "listening":
            target_intensity = 0.7  # Increased from 0.6 for more activity
            target_color = self.color_scheme["success"]
            target_glow = "#00e060"  # Slightly darker green
            target_secondary = "#80ffbb"  # Light green
            particle_spawn_rate = 3  # More particles when listening
        elif self.animation_state == "speaking":
            target_intensity = 1.0
            target_color = self.color_scheme["warning"]
            target_glow = "#ff8000"  # Slightly darker orange
            target_secondary = "#ffb366"  # Light orange
            particle_spawn_rate = 5  # Most particles when speaking
        
        # Smoothly transition to target intensity with easing
        if self.animation_intensity < target_intensity:
            self.animation_intensity += self.animation_fade_speed * (1 + (target_intensity - self.animation_intensity) * 2)
        elif self.animation_intensity > target_intensity:
            self.animation_intensity -= self.animation_fade_speed * (1 + (self.animation_intensity - target_intensity) * 2)
        
        self.animation_intensity = max(0.1, min(1.0, self.animation_intensity))
        
        # Get canvas center
        center_x = self.canvas_width / 2
        center_y = self.canvas_height / 2
        
        # Update wave points with more complex wave patterns
        current_time = time.time()
        for i, point in enumerate(self.wave_points):
            # Calculate distance from center (normalized)
            dx = (point["x"] - center_x) / (self.canvas_width / 2)
            
            # Create more complex wave pattern with multiple frequencies
            time_factor = current_time * point["speed"]
            phase = point["phase"]
            freq = point["frequency"]
            
            # Primary wave
            wave1 = math.sin(time_factor + phase) * self.animation_intensity
            # Secondary wave with different frequency
            wave2 = math.sin(time_factor * 1.5 + phase * 2) * self.animation_intensity * 0.3
            # Add distance factor for more interesting pattern
            wave3 = math.sin(dx * 3 + time_factor) * self.animation_intensity * 0.2
            
            # Combine waves
            combined_wave = (wave1 + wave2 + wave3) * freq
            
            # Apply amplitude with distance falloff for natural look
            distance_factor = 1 - min(1, abs(dx) * 0.7)  # Falloff from center
            max_amplitude = 35 * self.animation_intensity * distance_factor
            point["amplitude"] = combined_wave * max_amplitude
            
            # Update y position
            point["y"] = center_y + point["amplitude"]
        
        # Update all wave lines with different offsets for layered effect
        for i, line_id in enumerate(self.wave_lines):
            offset = i * 5  # Vertical offset between lines
            y_offset = offset * self.animation_intensity
            
            self.canvas.coords(
                line_id,
                [p["x"] for p in self.wave_points],
                [p["y"] + (i * y_offset) for p in self.wave_points]
            )
        
        # Update center circle with pulse effect and breathing animation
        base_radius = 45
        pulse_factor = math.sin(current_time * 2) * self.animation_intensity
        breath_factor = math.sin(current_time * 0.8) * self.animation_intensity * 0.3
        radius = base_radius + (8 * pulse_factor) + (5 * breath_factor)
        
        # Update inner circle
        inner_radius = radius * 0.7
        self.canvas.coords(
            self.inner_circle,
            center_x - inner_radius, center_y - inner_radius,
            center_x + inner_radius, center_y + inner_radius
        )
        
        # Update main circle
        self.canvas.coords(
            self.center_circle,
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius
        )
        
        # Update all glow circles with different pulse rates
        for i, glow_id in enumerate(self.glow_circles):
            # Different timing for each glow circle
            glow_pulse = math.sin(current_time * (1.5 - i * 0.3)) * self.animation_intensity
            glow_radius = radius + 10 + (i * 10) + (5 * glow_pulse)
            
            self.canvas.coords(
                glow_id,
                center_x - glow_radius, center_y - glow_radius,
                center_x + glow_radius, center_y + glow_radius
            )
        
        # Update radial lines visibility and length based on intensity
        for i, line_id in enumerate(self.radial_lines):
            angle = (i / len(self.radial_lines)) * math.pi * 2
            
            # Only show lines when intensity is high enough
            if self.animation_intensity > 0.4:
                self.canvas.itemconfig(line_id, state=tk.NORMAL)
                
                # Calculate line endpoints
                x1 = center_x + math.cos(angle) * radius
                y1 = center_y + math.sin(angle) * radius
                
                # Line length varies with intensity and time
                line_pulse = math.sin(current_time * 3 + i * 0.5) * 0.3 + 0.7
                line_length = radius * 0.7 * self.animation_intensity * line_pulse
                
                x2 = center_x + math.cos(angle) * (radius + line_length)
                y2 = center_y + math.sin(angle) * (radius + line_length)
                
                self.canvas.coords(line_id, x1, y1, x2, y2)
            else:
                self.canvas.itemconfig(line_id, state=tk.HIDDEN)
        
        # Update particles
        self._update_particles(center_x, center_y, particle_spawn_rate)
        
        # Update colors based on state with smooth transitions
        # For each wave line
        for i, line_id in enumerate(self.wave_lines):
            if i == 0:  # Main line
                self.canvas.itemconfig(line_id, fill=target_color)
            else:  # Secondary lines
                self.canvas.itemconfig(line_id, fill=target_secondary)
        
        # Update circle colors
        self.canvas.itemconfig(self.center_circle, outline=target_color)
        self.canvas.itemconfig(self.inner_circle, fill=target_secondary)
        
        # Update glow colors
        for i, glow_id in enumerate(self.glow_circles):
            if i == 0:  # Main glow
                self.canvas.itemconfig(glow_id, outline=target_glow)
            else:  # Secondary glow
                self.canvas.itemconfig(glow_id, outline=target_secondary)
        
        # Update radial lines
        for line_id in self.radial_lines:
            self.canvas.itemconfig(line_id, fill=target_color)
        
        # Schedule next animation frame
        self.root.after(30, self._animate)
    
    def _update_particles(self, center_x, center_y, spawn_rate):
        """
        Update particle positions and properties, and spawn new particles.
        """
        # Spawn new particles based on animation state
        for _ in range(spawn_rate):
            if len(self.particles) < self.max_particles and random.random() < self.animation_intensity:
                self._create_particle(center_x, center_y)
        
        # Update existing particles
        particles_to_remove = []
        for particle in self.particles:
            # Update position
            particle["x"] += particle["vx"]
            particle["y"] += particle["vy"]
            
            # Apply slight gravity effect
            particle["vy"] += 0.01
            
            # Slow down over time
            particle["vx"] *= 0.99
            particle["vy"] *= 0.99
            
            # Decrease lifetime
            particle["lifetime"] -= self.particle_fade_speed
            
            # Calculate opacity based on lifetime
            opacity_ratio = particle["lifetime"] / particle["max_lifetime"]
            current_size = particle["size"] * opacity_ratio
            
            # Update particle on canvas
            if particle["lifetime"] > 0 and particle["id"] is not None:
                # Update particle position and size
                self.canvas.coords(
                    particle["id"],
                    particle["x"] - current_size, particle["y"] - current_size,
                    particle["x"] + current_size, particle["y"] + current_size
                )
                
                # Update color based on animation state
                if self.animation_state == "idle":
                    color = self.color_scheme["accent"]
                elif self.animation_state == "listening":
                    color = self.color_scheme["success"]
                elif self.animation_state == "speaking":
                    color = self.color_scheme["warning"]
                
                self.canvas.itemconfig(particle["id"], fill=color)
                
                # Apply stipple pattern based on opacity for fade effect
                if opacity_ratio < 0.3:
                    self.canvas.itemconfig(particle["id"], stipple="gray25")
                elif opacity_ratio < 0.6:
                    self.canvas.itemconfig(particle["id"], stipple="gray50")
                else:
                    self.canvas.itemconfig(particle["id"], stipple="gray75")
            else:
                # Mark for removal if lifetime ended
                particles_to_remove.append(particle)
        
        # Remove dead particles
        for particle in particles_to_remove:
            if particle["id"] is not None:
                self.canvas.delete(particle["id"])
            self.particles.remove(particle)
    
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
        Update the text area with a new response using modern styling and animations.
        
        Args:
            text (str): The text to display
        """
        self.text_area.config(state=tk.NORMAL)
        
        # Add timestamp with modern format
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        # Insert message container with padding
        self.text_area.insert(tk.END, "\n\n")
        message_start = self.text_area.index(tk.END)
        
        # Insert header with icon and timestamp
        self.text_area.insert(tk.END, f"🤖 J.A.R.V.I.S. • {timestamp}\n\n")
        
        # Insert the actual message text
        self.text_area.insert(tk.END, f"{text}\n")
        
        # Insert separator with modern style
        self.text_area.insert(tk.END, "\n")
        
        # Apply modern styling with tags
        
        # Create message container tag
        message_end = self.text_area.index(tk.END)
        self.text_area.tag_add("message_container", message_start, message_end)
        self.text_area.tag_config("message_container", lmargin1=10, lmargin2=10, rmargin=10)
        
        # Style the header with gradient-like effect
        header_end = f"{message_start}+1l"
        self.text_area.tag_add("header", message_start, header_end)
        self.text_area.tag_config("header", foreground=self.color_scheme["accent"], 
                                font=("Segoe UI", 12, "bold"), spacing1=5, spacing3=5)
        
        # Style the timestamp portion
        timestamp_start = f"{message_start}+4c+11c"
        timestamp_end = f"{message_start}+1l"
        self.text_area.tag_add("timestamp", timestamp_start, timestamp_end)
        self.text_area.tag_config("timestamp", foreground=self.color_scheme["text_dim"], 
                                font=("Segoe UI", 10))
        
        # Style the message text
        text_start = f"{message_start}+1l"
        text_end = f"{message_end}-1l"
        self.text_area.tag_add("message_text", text_start, text_end)
        self.text_area.tag_config("message_text", foreground=self.color_scheme["text"], 
                                font=("Segoe UI", 12), spacing1=3, spacing2=2)
        
        # Add a subtle background for the entire message
        self.text_area.tag_add("message_bg", message_start, message_end)
        self.text_area.tag_config("message_bg", background=self.color_scheme["bg_gradient_bottom"])
        
        # Add a left border to indicate message source
        self.text_area.tag_add("message_border", message_start, message_end)
        self.text_area.tag_config("message_border", borderwidth=2, 
                                relief="flat", border=self.color_scheme["accent"])
        
        # Auto-scroll to the bottom with a slight delay for animation effect
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)
        
        # Simulate typing animation by temporarily showing a cursor
        self.root.after(100, lambda: self._flash_cursor(message_end))
    
    def _flash_cursor(self, position):
        """
        Create a typing cursor animation effect at the end of a message.
        """
        if not self.is_running:
            return
            
        self.text_area.config(state=tk.NORMAL)
        cursor_tag = "typing_cursor"
        
        # Check if cursor already exists and remove it
        if self.text_area.tag_ranges(cursor_tag):
            self.text_area.tag_remove(cursor_tag, "1.0", tk.END)
        
        # Add cursor
        self.text_area.tag_add(cursor_tag, position+"-1c", position)
        self.text_area.tag_config(cursor_tag, background=self.color_scheme["accent"])
        self.text_area.config(state=tk.DISABLED)
        
        # Schedule cursor removal
        self.root.after(500, lambda: self._remove_cursor(cursor_tag))
    
    def _remove_cursor(self, cursor_tag):
        """
        Remove the typing cursor effect.
        """
        if not self.is_running:
            return
            
        self.text_area.config(state=tk.NORMAL)
        if self.text_area.tag_ranges(cursor_tag):
            self.text_area.tag_remove(cursor_tag, "1.0", tk.END)
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
        Set the current animation state with visual feedback.
        
        Args:
            state (str): One of 'idle', 'listening', or 'speaking'
        """
        # Store previous state for transition effects
        previous_state = self.animation_state
        self.animation_state = state
        
        # Update status indicator with enhanced visual feedback
        if hasattr(self, 'status_indicator') and self.status_indicator:
            # Define status colors and text based on state
            if state == "idle":
                status_text = "● IDLE"
                status_color = self.color_scheme["text_dim"]
                status_font = ("Segoe UI", 11, "bold")
            elif state == "listening":
                status_text = "● LISTENING"
                status_color = self.color_scheme["success"]
                status_font = ("Segoe UI", 11, "bold")
            elif state == "speaking":
                status_text = "● SPEAKING"
                status_color = self.color_scheme["warning"]
                status_font = ("Segoe UI", 11, "bold")
            
            # Apply the new status with a brief highlight effect
            self.status_indicator.config(text=status_text, fg=status_color, font=status_font)
            
            # Create a flash effect when changing states
            if previous_state != state and self.root:
                # Flash effect - briefly highlight with brighter color
                original_bg = self.status_indicator.cget("background")
                self.status_indicator.config(background=status_color)
                
                # Schedule return to normal background
                self.root.after(150, lambda: self.status_indicator.config(background=original_bg))
                
                # Create particles burst effect on state change
                if hasattr(self, 'canvas') and self.canvas:
                    # Get canvas center
                    center_x = self.canvas_width / 2
                    center_y = self.canvas_height / 2
                    
                    # Create a burst of particles
                    for _ in range(15):
                        self._create_particle(center_x, center_y)
                        
            # Update footer text based on state
            if hasattr(self, 'footer_text') and self.footer_text:
                if state == "idle":
                    self.footer_text.config(text="⚡ System Ready")
                elif state == "listening":
                    self.footer_text.config(text="🎤 Listening...")
                elif state == "speaking":
                    self.footer_text.config(text="💬 Speaking...")

    
    def stop(self):
        """
        Stop the display window.
        """
        self.is_running = False
        if self.root:
            self.root.quit()
            self.root.destroy()