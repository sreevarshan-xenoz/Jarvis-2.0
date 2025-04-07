#!/usr/bin/env python3
"""
Jarvis Voice Assistant - UI Integrator Module

This module integrates all the enhanced UI features (audio spectrum visualization,
3D rendering, enhanced particles, and theme management) with the main animated display.
"""

import time
import threading
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk

# Import enhanced modules
from core.audio_spectrum import AudioSpectrum
from core.enhanced_particles import ParticleSystem
from core.theme_manager import ThemeManager

# Import OpenGL renderer (with fallback if not available)
try:
    from core.opengl_renderer import OpenGLRenderer
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("PyOpenGL not available. 3D rendering will be disabled.")

class UIIntegrator:
    """
    Integrates all enhanced UI features with the main animated display.
    """
    
    def __init__(self, animated_display):
        """
        Initialize the UI integrator.
        
        Args:
            animated_display: The main AnimatedDisplayWindow instance
        """
        self.display = animated_display
        self.initialized = False
        self.active_features = {
            'audio_spectrum': False,
            '3d_rendering': False,
            'enhanced_particles': False,
            'themes': True  # Themes are always enabled
        }
        
        # Initialize components
        self.audio_spectrum = None
        self.particle_system = None
        self.opengl_renderer = None
        self.theme_manager = ThemeManager()
        
        # Apply initial theme
        self._apply_theme(self.theme_manager.get_theme())
        
        # Setup UI controls for feature toggling
        self.ui_controls = {}
        
        # Create basic UI frame for controls
        self._setup_control_frame()
    
    def _setup_control_frame(self):
        """
        Setup the basic UI frame for controls.
        """
        if not hasattr(self.display, 'root') or not self.display.root:
            return
            
        # Create main control frame
        control_frame = tk.Frame(self.display.root)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        # Store the control frame
        self.ui_controls['settings_frame'] = control_frame
        
    def initialize(self):
        """
        Initialize all enhanced UI features.
        """
        if self.initialized:
            return
            
        # Get canvas dimensions
        if not hasattr(self.display, 'canvas') or not self.display.canvas:
            print("Canvas not available. Cannot initialize enhanced UI features.")
            return False
            
        canvas_width = self.display.canvas.winfo_width() or 900
        canvas_height = self.display.canvas.winfo_height() or 220
        
        # Initialize audio spectrum analyzer
        try:
            self.audio_spectrum = AudioSpectrum()
            self.active_features['audio_spectrum'] = True
        except Exception as e:
            print(f"Error initializing audio spectrum: {e}")
            self.active_features['audio_spectrum'] = False
        
        # Initialize enhanced particle system
        try:
            self.particle_system = ParticleSystem(canvas_width, canvas_height)
            self.active_features['enhanced_particles'] = True
        except Exception as e:
            print(f"Error initializing enhanced particles: {e}")
            self.active_features['enhanced_particles'] = False
        
        # Initialize 3D renderer if OpenGL is available
        if OPENGL_AVAILABLE:
            try:
                self.opengl_renderer = OpenGLRenderer(400, 300)  # Smaller size for overlay
                if self.opengl_renderer.initialize():
                    self.active_features['3d_rendering'] = True
                else:
                    print("Failed to initialize OpenGL renderer.")
                    self.active_features['3d_rendering'] = False
            except Exception as e:
                print(f"Error initializing OpenGL renderer: {e}")
                self.active_features['3d_rendering'] = False
        else:
            self.active_features['3d_rendering'] = False
        
        # Add UI controls for feature toggling
        self._setup_ui_controls()
        
        self.initialized = True
        return True
    
    def _setup_ui_controls(self):
        """
        Set up UI controls for toggling features and changing themes.
        """
        if not hasattr(self.display, 'root') or not self.display.root:
            return
            
        # Create a settings panel (initially hidden)
        settings_frame = tk.Frame(
            self.display.root,
            bg=self.display.color_scheme["bg_medium"],
            padx=15,
            pady=15,
            highlightbackground=self.display.color_scheme["accent"],
            highlightthickness=1
        )
        
        # Add title
        title = tk.Label(
            settings_frame,
            text="Jarvis UI Settings",
            font=("Segoe UI", 14, "bold"),
            fg=self.display.color_scheme["text"],
            bg=self.display.color_scheme["bg_medium"]
        )
        title.pack(pady=(0, 10))
        
        # Add feature toggles
        features_frame = tk.Frame(settings_frame, bg=self.display.color_scheme["bg_medium"])
        features_frame.pack(fill=tk.X, pady=5)
        
        # Audio spectrum toggle
        audio_var = tk.BooleanVar(value=self.active_features['audio_spectrum'])
        audio_check = tk.Checkbutton(
            features_frame,
            text="Audio Spectrum Visualization",
            variable=audio_var,
            command=lambda: self.toggle_feature('audio_spectrum', audio_var.get()),
            fg=self.display.color_scheme["text"],
            bg=self.display.color_scheme["bg_medium"],
            selectcolor=self.display.color_scheme["bg_dark"],
            activebackground=self.display.color_scheme["bg_medium"],
            activeforeground=self.display.color_scheme["accent"]
        )
        audio_check.pack(anchor=tk.W, pady=2)
        
        # 3D rendering toggle
        render_var = tk.BooleanVar(value=self.active_features['3d_rendering'])
        render_check = tk.Checkbutton(
            features_frame,
            text="3D Rendering",
            variable=render_var,
            command=lambda: self.toggle_feature('3d_rendering', render_var.get()),
            fg=self.display.color_scheme["text"],
            bg=self.display.color_scheme["bg_medium"],
            selectcolor=self.display.color_scheme["bg_dark"],
            activebackground=self.display.color_scheme["bg_medium"],
            activeforeground=self.display.color_scheme["accent"]
        )
        render_check.pack(anchor=tk.W, pady=2)
        
        # Enhanced particles toggle
        particles_var = tk.BooleanVar(value=self.active_features['enhanced_particles'])
        particles_check = tk.Checkbutton(
            features_frame,
            text="Enhanced Particle Effects",
            variable=particles_var,
            command=lambda: self.toggle_feature('enhanced_particles', particles_var.get()),
            fg=self.display.color_scheme["text"],
            bg=self.display.color_scheme["bg_medium"],
            selectcolor=self.display.color_scheme["bg_dark"],
            activebackground=self.display.color_scheme["bg_medium"],
            activeforeground=self.display.color_scheme["accent"]
        )
        particles_check.pack(anchor=tk.W, pady=2)
        
        # Theme selector
        theme_frame = tk.Frame(settings_frame, bg=self.display.color_scheme["bg_medium"])
        theme_frame.pack(fill=tk.X, pady=(15, 5))
        
        theme_label = tk.Label(
            theme_frame,
            text="Theme:",
            font=("Segoe UI", 11),
            fg=self.display.color_scheme["text"],
            bg=self.display.color_scheme["bg_medium"]
        )
        theme_label.pack(side=tk.LEFT, padx=(0, 10))
        
        # Get available themes
        themes = self.theme_manager.get_available_themes()
        theme_names = [theme['name'] for theme in themes]
        theme_ids = [theme['id'] for theme in themes]
        
        # Create dropdown for theme selection
        theme_var = tk.StringVar()
        theme_var.set(theme_names[theme_ids.index(self.theme_manager.current_theme)])
        
        theme_dropdown = tk.OptionMenu(
            theme_frame,
            theme_var,
            *theme_names,
            command=lambda name: self.change_theme(theme_ids[theme_names.index(name)])
        )
        theme_dropdown.config(
            fg=self.display.color_scheme["text"],
            bg=self.display.color_scheme["bg_dark"],
            activebackground=self.display.color_scheme["bg_medium"],
            activeforeground=self.display.color_scheme["accent"],
            highlightbackground=self.display.color_scheme["accent"],
            highlightthickness=1
        )
        theme_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Close button
        close_button = tk.Button(
            settings_frame,
            text="Close",
            command=lambda: settings_frame.place_forget(),
            fg=self.display.color_scheme["text"],
            bg=self.display.color_scheme["bg_dark"],
            activebackground=self.display.color_scheme["accent"],
            activeforeground=self.display.color_scheme["text"],
            bd=0,
            padx=10,
            pady=5
        )
        close_button.pack(pady=(15, 0))
        
        # Store references
        self.ui_controls['settings_frame'] = settings_frame
        self.ui_controls['audio_var'] = audio_var
        self.ui_controls['render_var'] = render_var
        self.ui_controls['particles_var'] = particles_var
        self.ui_controls['theme_var'] = theme_var
        
        # Connect settings button to show panel
        if hasattr(self.display, 'settings_button'):
            self.display.settings_button.bind("<Button-1>", lambda e: self._toggle_settings_panel())
    
    def _toggle_settings_panel(self):
        """
        Toggle the visibility of the settings panel.
        """
        settings_frame = self.ui_controls.get('settings_frame')
        if not settings_frame:
            return
            
        if settings_frame.winfo_ismapped():
            settings_frame.place_forget()
        else:
            # Position in the center of the window
            settings_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    
    def toggle_feature(self, feature_name, enabled):
        """
        Toggle a UI feature on or off.
        
        Args:
            feature_name (str): Name of the feature to toggle
            enabled (bool): Whether to enable or disable the feature
        """
        if feature_name not in self.active_features:
            return
            
        self.active_features[feature_name] = enabled
        
        # Initialize components if needed
        if enabled and not self.initialized:
            self.initialize()
    
    def change_theme(self, theme_id):
        """
        Change the current theme.
        
        Args:
            theme_id (str): ID of the theme to apply
        """
        if self.theme_manager.set_theme(theme_id):
            theme_data = self.theme_manager.get_theme()
            self._apply_theme(theme_data)
    
    def _apply_theme(self, theme_data):
        """
        Apply a theme to the UI.
        
        Args:
            theme_data (dict): Theme data to apply
        """
        if not theme_data or not hasattr(self.display, 'color_scheme'):
            return
            
        # Update color scheme
        self.display.color_scheme.update(theme_data['colors'])
        
        # Update animation parameters if available
        if hasattr(self.display, 'max_particles') and 'animation' in theme_data:
            self.display.max_particles = theme_data['animation'].get('particle_count', 50)
            self.display.animation_fade_speed = 0.05 * theme_data['animation'].get('intensity', 1.0)
        
        # Update fonts if available
        if 'fonts' in theme_data and hasattr(self.display, 'root') and self.display.root:
            # Update title font
            if hasattr(self.display, 'title') and self.display.title:
                font_data = theme_data['fonts'].get('title', {})
                self.display.title.config(
                    font=(font_data.get('family', 'Segoe UI'), 
                          font_data.get('size', 28), 
                          font_data.get('weight', 'bold'))
                )
            
            # Update subtitle font
            if hasattr(self.display, 'subtitle') and self.display.subtitle:
                font_data = theme_data['fonts'].get('subtitle', {})
                self.display.subtitle.config(
                    font=(font_data.get('family', 'Segoe UI'), 
                          font_data.get('size', 11), 
                          font_data.get('weight', 'normal'))
                )
            
            # Update text area font
            if hasattr(self.display, 'text_area') and self.display.text_area:
                font_data = theme_data['fonts'].get('text', {})
                self.display.text_area.config(
                    font=(font_data.get('family', 'Segoe UI'), 
                          font_data.get('size', 12), 
                          font_data.get('weight', 'normal'))
                )
        
        # Refresh UI
        self._refresh_ui()
    
    def _refresh_ui(self):
        """
        Refresh the UI after theme changes.
        """
        if not hasattr(self.display, 'root') or not self.display.root:
            return
            
        # Update background
        if hasattr(self.display, '_create_gradient_background'):
            self.display._create_gradient_background()
        
        # Update settings panel if visible
        if 'settings_frame' in self.ui_controls and self.ui_controls['settings_frame'].winfo_ismapped():
            settings_frame = self.ui_controls['settings_frame']
            settings_frame.config(bg=self.display.color_scheme["bg_medium"])
            
            # Update all children recursively
            for child in settings_frame.winfo_children():
                if isinstance(child, (tk.Label, tk.Frame)):
                    child.config(bg=self.display.color_scheme["bg_medium"])
                    if isinstance(child, tk.Label):
                        child.config(fg=self.display.color_scheme["text"])
                        
                # Update grandchildren
                if isinstance(child, tk.Frame):
                    for grandchild in child.winfo_children():
                        if isinstance(grandchild, tk.Checkbutton):
                            grandchild.config(
                                fg=self.display.color_scheme["text"],
                                bg=self.display.color_scheme["bg_medium"],
                                selectcolor=self.display.color_scheme["bg_dark"],
                                activebackground=self.display.color_scheme["bg_medium"],
                                activeforeground=self.display.color_scheme["accent"]
                            )
                        elif isinstance(grandchild, (tk.Label, tk.Frame)):
                            grandchild.config(bg=self.display.color_scheme["bg_medium"])
                            if isinstance(grandchild, tk.Label):
                                grandchild.config(fg=self.display.color_scheme["text"])
    
    def integrate_with_animation(self, animation_state, intensity, center_x, center_y):
        """
        Integrate enhanced features with the main animation loop.
        
        Args:
            animation_state (str): Current animation state ('idle', 'listening', or 'speaking')
            intensity (float): Animation intensity from 0.0 to 1.0
            center_x (float): X coordinate of the center point
            center_y (float): Y coordinate of the center point
            
        Returns:
            dict: Enhanced visualization data for rendering
        """
        if not self.initialized:
            self.initialize()
        
        result = {
            'audio_spectrum': None,
            'particles': None,
            '3d_rendering': None
        }
        
        # Update audio spectrum if enabled
        if self.active_features['audio_spectrum'] and self.audio_spectrum:
            # For real implementation, this would use actual audio data
            # For now, simulate audio input based on animation state
            audio_intensity = intensity
            audio_complexity = 0.5
            
            if animation_state == 'listening':
                audio_intensity = intensity * 0.8
                audio_complexity = 0.8
            elif animation_state == 'speaking':
                audio_intensity = intensity * 1.2
                audio_complexity = 1.0
            
            # Get simulated spectrum data
            self.audio_spectrum.simulate_audio_input(audio_intensity, audio_complexity)
            result['audio_spectrum'] = self.audio_spectrum.get_visualization_data(64, 0.7)
        
        # Update enhanced particles if enabled
        if self.active_features['enhanced_particles'] and self.particle_system:
            # Update particles with current state
            result['particles'] = self.particle_system.update(
                0.033,  # Assume ~30fps
                center_x,
                center_y,
                animation_state,
                intensity
            )
            
            # Create keyword-based particle effects for state changes
            if hasattr(self.display, 'previous_state') and self.display.previous_state != animation_state:
                if animation_state == 'listening':
                    self.particle_system.create_keyword_burst(
                        center_x, center_y, 'listening', self.display.color_scheme['success']
                    )
                elif animation_state == 'speaking':
                    self.particle_system.create_keyword_burst(
                        center_x, center_y, 'speaking', self.display.color_scheme['warning']
                    )
        
        # Update 3D rendering if enabled
        if self.active_features['3d_rendering'] and self.opengl_renderer:
            # Set animation state for 3D renderer
            self.opengl_renderer.set_animation_state(animation_state, intensity)
            
            # Render 3D scene
            result['3d_rendering'] = self.opengl_renderer.get_tkinter_image()
        
        return result
    
    def render_audio_spectrum(self, canvas, spectrum_data, center_x, center_y, height=100):
        """
        Render audio spectrum visualization on the canvas.
        
        Args:
            canvas: Tkinter canvas to draw on
            spectrum_data (dict): Spectrum data from audio_spectrum.get_visualization_data()
            center_x (float): X coordinate of the center point
            center_y (float): Y coordinate of the center point
            height (float): Height of the visualization
            
        Returns:
            list: IDs of created canvas objects
        """
        if not spectrum_data or 'spectrum' not in spectrum_data:
            return []
            
        # Get spectrum and number of points
        spectrum = spectrum_data['spectrum']
        num_points = len(spectrum)
        band_energy = spectrum_data.get('band_energy', {})
        
        # Calculate bar width and spacing
        total_width = 600  # Total width of visualization
        bar_width = total_width / (num_points * 1.5)  # Leave some space between bars
        spacing = bar_width * 0.5
        
        # Get band colors from audio spectrum
        if hasattr(self.audio_spectrum, 'get_band_colors'):
            band_colors = self.audio_spectrum.get_band_colors()
        else:
            # Default colors if not available
            band_colors = {
                'bass': "#FF5252",    # Red for bass
                'mid': "#FFFF00",     # Yellow for mid
                'treble': "#00E676"   # Green for treble
            }
        
        # Create bars
        bar_ids = []
        start_x = center_x - (total_width / 2)
        
        for i, value in enumerate(spectrum):
            # Calculate bar position and size
            x = start_x + (i * (bar_width + spacing))
            bar_height = value * height
            
            # Determine color based on frequency band
            if i < num_points * 0.2:  # First 20% = bass
                color = band_colors.get('bass', "#FF5252")
                # Add glow effect for bass
                glow_factor = band_energy.get('bass', 0.5)
                if glow_factor > 0.6 and i % 2 == 0:  # Only add glow to every other bar
                    glow = canvas.create_rectangle(
                        x - bar_width * 0.5, center_y - bar_height * 1.2,
                        x + bar_width * 1.5, center_y + bar_height * 0.2,
                        fill=color,
                        outline="",
                        stipple="gray25"  # Transparent effect
                    )
                    bar_ids.append(glow)
            elif i < num_points * 0.6:  # Next 40% = mid
                color = band_colors.get('mid', "#FFFF00")
            else:  # Last 40% = treble
                color = band_colors.get('treble', "#00E676")
            
            # Create bar
            bar = canvas.create_rectangle(
                x, center_y - bar_height,
                x + bar_width, center_y,
                fill=color,
                outline=""
            )
            bar_ids.append(bar)
        
        return bar_ids
    
    def render_enhanced_particles(self, canvas, particle_data):
        """
        Render enhanced particles on the canvas.
        
        Args:
            canvas: Tkinter canvas to draw on
            particle_data (dict): Particle data from particle_system.update()
            
        Returns:
            list: IDs of created canvas objects
        """
        if not particle_data:
            return []
            
        particle_ids = []
        
        # Render trails first (so they appear behind particles)
        if 'trails' in particle_data:
            for trail in particle_data['trails']:
                # Calculate opacity
                opacity_hex = self._opacity_to_stipple(trail['opacity'])
                
                # Create trail
                trail_id = canvas.create_oval(
                    trail['x'] - trail['size'], trail['y'] - trail['size'],
                    trail['x'] + trail['size'], trail['y'] + trail['size'],
                    fill=trail['color'],
                    outline="",
                    stipple=opacity_hex
                )
                particle_ids.append(trail_id)
                
                # Store canvas ID in trail object for future updates
                trail['id'] = trail_id
        
        # Render particles
        if 'particles' in particle_data:
            for particle in particle_data['particles']:
                # Get particle properties
                x = particle['x']
                y = particle['y']
                size = particle['size']
                color = particle['color']
                opacity = particle.get('opacity', 1.0)
                shape = particle.get('shape', 'oval')
                
                # Calculate opacity
                opacity_hex = self._opacity_to_stipple(opacity)
                
                # Create particle based on shape
                if shape == 'oval':
                    particle_id = canvas.create_oval(
                        x - size, y - size,
                        x + size, y + size,
                        fill=color,
                        outline="",
                        stipple=opacity_hex
                    )
                elif shape == 'rect':
                    particle_id = canvas.create_rectangle(
                        x - size, y - size,
                        x + size, y + size,
                        fill=color,
                        outline="",
                        stipple=opacity_hex
                    )
                else:  # Default to oval
                    particle_id = canvas.create_oval(
                        x - size, y - size,
                        x + size, y + size,
                        fill=color,
                        outline="",
                        stipple=opacity_hex
                    )
                
                particle_ids.append(particle_id)
                
                # Store canvas ID in particle object for future updates
                particle['id'] = particle_id
        
        return particle_ids
    
    def render_3d_scene(self, canvas, image, x, y):
        """
        Render 3D scene on the canvas.
        
        Args:
            canvas: Tkinter canvas to draw on
            image: Tkinter PhotoImage from opengl_renderer.get_tkinter_image()
            x (float): X coordinate to place the image
            y (float): Y coordinate to place the image
            
        Returns:
            int: ID of created canvas object
        """
        if not image:
            return None
            
        # Create image on canvas
        image_id = canvas.create_image(x, y, image=image, anchor=tk.CENTER)
        
        # Store reference to prevent garbage collection
        if not hasattr(self, '_image_refs'):
            self._image_refs = []
        self._image_refs.append(image)
        
        return image_id
    
    def _opacity_to_stipple(self, opacity):
        """
        Convert opacity value to appropriate stipple pattern.
        
        Args:
            opacity (float): Opacity value from 0.0 to 1.0
            
        Returns:
            str: Stipple pattern name
        """
        if opacity >= 0.9:
            return ""
        elif opacity >= 0.7:
            return "gray75"
        elif opacity >= 0.4:
            return "gray50"
        elif opacity >= 0.2:
            return "gray25"
        else:
            return "gray12"
    
    def cleanup(self):
        """
        Clean up resources used by enhanced features.
        """
        # Stop audio spectrum analyzer
        if self.audio_spectrum:
            self.audio_spectrum.stop_capture()
        
        # Clean up OpenGL renderer
        if self.opengl_renderer:
            self.opengl_renderer.cleanup()
        
        # Clear image references
        if hasattr(self, '_image_refs'):
            self._image_refs.clear()