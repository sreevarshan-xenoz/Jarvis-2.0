#!/usr/bin/env python3
"""
Jarvis Voice Assistant - 3D OpenGL Renderer Module

This module provides 3D rendering capabilities using PyOpenGL for the Jarvis animated UI.
"""

import numpy as np
import math
import time
from PIL import Image, ImageTk
import tkinter as tk

# Import PyOpenGL - will need to be added to requirements.txt
try:
    from OpenGL.GL import *
    from OpenGL.GLU import *
    from OpenGL.GLUT import *
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("PyOpenGL not available. 3D rendering will be disabled.")

class OpenGLRenderer:
    """
    Provides 3D rendering capabilities using PyOpenGL for the Jarvis animated UI.
    """
    
    def __init__(self, width=400, height=300):
        """
        Initialize the OpenGL renderer.
        
        Args:
            width (int): Width of the rendering area
            height (int): Height of the rendering area
        """
        # Add destructor to ensure proper cleanup
        import atexit
        atexit.register(self.cleanup)
        self.width = width
        self.height = height
        self.available = OPENGL_AVAILABLE
        self.initialized = False
        
        # Optimize texture and model management
        self._texture_cache = {}
        self._model_cache = {}
        self._vertex_buffers = {}
        self._index_buffers = {}
        self._batch_size = 1000  # Increased batch size for better performance
        
        # Use NumPy arrays for better performance
        self.camera_position = np.array([0.0, 0.0, 5.0], dtype=np.float32)
        self.camera_rotation = np.array([0.0, 0.0, 0.0], dtype=np.float32)
        self.light_position = np.array([0.0, 5.0, 5.0, 1.0], dtype=np.float32)
        self.animation_time = 0.0
        
        # Pre-allocate transformation matrices
        self.model_matrix = np.eye(4, dtype=np.float32)
        self.view_matrix = np.eye(4, dtype=np.float32)
        self.projection_matrix = np.eye(4, dtype=np.float32)
        
        self._cleanup_required = False
        
        # Animation parameters
        self.animation_speed = 1.0
        self.pulse_frequency = 0.5
        self.rotation_speed = 15.0  # degrees per second
        
        # Rendering settings
        self.wireframe_mode = False
        self.use_lighting = True
        self.use_textures = True
        self.use_blending = True
        
        # Material properties
        self.materials = {
            'default': {
                'ambient': [0.2, 0.2, 0.2, 1.0],
                'diffuse': [0.8, 0.8, 0.8, 1.0],
                'specular': [1.0, 1.0, 1.0, 1.0],
                'shininess': 50.0
            },
            'blue_glow': {
                'ambient': [0.0, 0.1, 0.2, 1.0],
                'diffuse': [0.0, 0.4, 0.8, 1.0],
                'specular': [0.0, 0.8, 1.0, 1.0],
                'shininess': 75.0
            },
            'green_glow': {
                'ambient': [0.0, 0.2, 0.1, 1.0],
                'diffuse': [0.0, 0.8, 0.4, 1.0],
                'specular': [0.0, 1.0, 0.8, 1.0],
                'shininess': 75.0
            },
            'orange_glow': {
                'ambient': [0.2, 0.1, 0.0, 1.0],
                'diffuse': [0.8, 0.4, 0.0, 1.0],
                'specular': [1.0, 0.8, 0.0, 1.0],
                'shininess': 75.0
            }
        }
        
        # Current material
        self.current_material = 'blue_glow'
        
        # Initialize offscreen rendering
        self.fbo = None
        self.render_texture = None
        self.depth_buffer = None
    
    def cleanup(self):
        """
        Clean up OpenGL resources to prevent memory leaks.
        """
        if not self.initialized:
            return
            
        try:
            # Batch delete textures
            if self._texture_cache:
                texture_ids = list(self._texture_cache.values())
                glDeleteTextures(len(texture_ids), texture_ids)
                self._texture_cache.clear()
            
            # Batch delete models/quadrics
            for model in self._model_cache.values():
                if model:
                    try:
                        gluDeleteQuadric(model)
                    except Exception as e:
                        print(f"Error deleting quadric: {e}")
            self._model_cache.clear()
            
            # Batch delete vertex and index buffers
            if self._vertex_buffers:
                vbos = list(self._vertex_buffers.values())
                glDeleteBuffers(len(vbos), vbos)
                self._vertex_buffers.clear()
            
            if self._index_buffers:
                ibos = list(self._index_buffers.values())
                glDeleteBuffers(len(ibos), ibos)
                self._index_buffers.clear()
            
            # Delete FBO and associated resources
            if self.fbo:
                glDeleteFramebuffers(1, [self.fbo])
            if self.render_texture:
                glDeleteTextures([self.render_texture])
            if self.depth_buffer:
                glDeleteRenderbuffers(1, [self.depth_buffer])
                
            self.initialized = False
            
        except Exception as e:
            print(f"Error during OpenGL cleanup: {e}")
    
    def initialize(self):
        """
        Initialize OpenGL context and settings.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        if not self.available:
            return False
            
        try:
            # Initialize GLUT for offscreen rendering
            glutInit()
            glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
            glutInitWindowSize(self.width, self.height)
            glutCreateWindow("Jarvis 3D Renderer")
            
            # Set up OpenGL state
            glClearColor(0.0, 0.0, 0.0, 0.0)  # Transparent background
            glEnable(GL_DEPTH_TEST)
            glDepthFunc(GL_LEQUAL)
            
            # Set up lighting
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glLightfv(GL_LIGHT0, GL_POSITION, self.light_position)
            glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
            glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
            glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
            
            # Enable blending for transparency
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            # Set up perspective projection
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(45.0, self.width / self.height, 0.1, 100.0)
            
            # Initialize models
            self._init_models()
            
            self.initialized = True
            return True
        except Exception as e:
            print(f"Error initializing OpenGL: {e}")
            self.available = False
            return False
    
    def _init_models(self):
        """
        Initialize 3D models for rendering.
        """
        # Create sphere model with error handling
        try:
            self.models['sphere'] = gluNewQuadric()
            if self.models['sphere']:
                gluQuadricNormals(self.models['sphere'], GLU_SMOOTH)
                gluQuadricTexture(self.models['sphere'], GL_TRUE)
        except Exception as e:
            print(f"Error creating sphere model: {e}")
            return False
        # Create hologram model with error handling
        try:
            self.models['hologram'] = gluNewQuadric()
            if self.models['hologram']:
                gluQuadricNormals(self.models['hologram'], GLU_SMOOTH)
                gluQuadricTexture(self.models['hologram'], GL_TRUE)
        except Exception as e:
            print(f"Error creating hologram model: {e}")
        
        # Create energy field model with error handling
        try:
            self.models['energy_field'] = gluNewQuadric()
            if self.models['energy_field']:
                gluQuadricNormals(self.models['energy_field'], GLU_SMOOTH)
                gluQuadricTexture(self.models['energy_field'], GL_TRUE)
        except Exception as e:
            print(f"Error creating energy field model: {e}")
        
        # Create particle system with error handling
        try:
            self._init_particles()
        except Exception as e:
            print(f"Error initializing particle system: {e}")
            self.particles = []
        
        # Initialize holographic effects
        self.holo_rotation = 0.0
        self.holo_scale = 1.0
        self.holo_alpha = 0.7
        self.holo_layers = 3
        
        # Energy field parameters
        self.field_rotation = 0.0
        self.field_scale = 1.2
        self.field_intensity = 0.8
        self.field_pulse = 0.0
    
    def _init_particles(self, num_particles=100):
        """
        Initialize particle system for 3D effects using numpy arrays for better performance.
        
        Args:
            num_particles (int): Number of particles to create
        """
        # Generate random spherical coordinates
        theta = 2 * math.pi * np.random.random(num_particles)
        phi = np.arccos(2 * np.random.random(num_particles) - 1)
        radius = 2.0 * np.random.random(num_particles)
        
        # Convert to Cartesian coordinates
        positions = np.zeros((num_particles, 3), dtype=np.float32)
        positions[:, 0] = radius * np.sin(phi) * np.cos(theta)
        positions[:, 1] = radius * np.sin(phi) * np.sin(theta)
        positions[:, 2] = radius * np.cos(phi)
        
        # Generate velocities
        velocities = (np.random.random((num_particles, 3)) - 0.5) * 0.1
        
        # Generate sizes and lifetimes
        sizes = (0.05 + np.random.random(num_particles) * 0.1).astype(np.float32)
        lifetimes = (1.0 + np.random.random(num_particles) * 4.0).astype(np.float32)
        
        # Generate colors (blue to cyan gradient)
        colors = np.zeros((num_particles, 4), dtype=np.float32)
        colors[:, 1] = 0.4 + np.random.random(num_particles) * 0.6  # Green
        colors[:, 2] = 0.7 + np.random.random(num_particles) * 0.3  # Blue
        colors[:, 3] = 0.7 + np.random.random(num_particles) * 0.3  # Alpha
        
        self.particles = {
            'position': positions,
            'velocity': velocities,
            'size': sizes,
            'lifetime': lifetimes.copy(),
            'max_lifetime': lifetimes,
            'color': colors
        }
    
    def _update_particles(self, dt):
        """
        Update particle positions and properties using vectorized operations.
        
        Args:
            dt (float): Time delta since last update
        """
        if not isinstance(self.particles, dict) or not self.particles:
            return
            
        try:
            # Update positions using vectorized operations
            new_positions = self.particles['position'] + self.particles['velocity'] * dt
            self.particles['position'] = np.clip(new_positions, -10.0, 10.0)
            
            # Apply center force using vectorized operations
            center_force = 0.1
            dist_to_center = -self.particles['position']
            new_velocities = self.particles['velocity'] + dist_to_center * center_force * dt
            self.particles['velocity'] = np.clip(new_velocities, -1.0, 1.0)
            
            # Update lifetimes and colors
            self.particles['lifetime'] = np.maximum(0.0, self.particles['lifetime'] - dt)
            life_ratios = self.particles['lifetime'] / np.maximum(self.particles['max_lifetime'], 0.001)
            self.particles['color'][:, 3] = np.clip(life_ratios, 0.0, 1.0)
            
            # Find and reset dead particles
            dead_particles = self.particles['lifetime'] <= 0
            if np.any(dead_particles):
                self._reset_dead_particles(dead_particles)
                
        except Exception as e:
            print(f"Error in particle system update: {e}")
            self._init_particles()  # Reinitialize particle system on critical error
    
    def _reset_dead_particles(self, dead_mask):
        """
        Reset dead particles using vectorized operations.
        
        Args:
            dead_mask (np.ndarray): Boolean mask of dead particles
        """
        num_dead = np.sum(dead_mask)
        if num_dead == 0:
            return
            
        try:
            # Generate new random values for dead particles
            theta = 2 * math.pi * np.random.random(num_dead)
            phi = np.arccos(2 * np.random.random(num_dead) - 1)
            radius = 2.0 * np.random.random(num_dead)
            
            # Update positions
            self.particles['position'][dead_mask, 0] = radius * np.sin(phi) * np.cos(theta)
            self.particles['position'][dead_mask, 1] = radius * np.sin(phi) * np.sin(theta)
            self.particles['position'][dead_mask, 2] = radius * np.cos(phi)
            
            # Update velocities
            self.particles['velocity'][dead_mask] = (np.random.random((num_dead, 3)) - 0.5) * 0.1
            
            # Update sizes and lifetimes
            self.particles['size'][dead_mask] = 0.05 + np.random.random(num_dead) * 0.1
            new_lifetimes = 1.0 + np.random.random(num_dead) * 4.0
            self.particles['lifetime'][dead_mask] = new_lifetimes
            self.particles['max_lifetime'][dead_mask] = new_lifetimes
            
            # Update colors
            self.particles['color'][dead_mask, 1] = 0.4 + np.random.random(num_dead) * 0.6
            self.particles['color'][dead_mask, 2] = 0.7 + np.random.random(num_dead) * 0.3
            self.particles['color'][dead_mask, 3] = 0.7 + np.random.random(num_dead) * 0.3
            
        except Exception as e:
            print(f"Error resetting dead particles: {e}")

    
    def _reset_particle(self, particle):
        """
        Reset a particle to its initial state with new random values and error handling.
        
        Args:
            particle (dict): Particle to reset
        
        Returns:
            bool: True if reset successful, False otherwise
        """
        try:
            # Validate input
            if not isinstance(particle, dict):
                print("Invalid particle object")
                return False
                
            # Random position on sphere surface with bounds checking
            try:
                theta = 2 * math.pi * max(0.0, min(np.random.random(), 1.0))
                phi = math.acos(2 * max(0.0, min(np.random.random(), 1.0)) - 1)
                radius = max(0.1, min(2.0, 2.0 * np.random.random()))
                
                particle['position'] = [
                    radius * math.sin(phi) * math.cos(theta),
                    radius * math.sin(phi) * math.sin(theta),
                    radius * math.cos(phi)
                ]
            except Exception as e:
                print(f"Error setting particle position: {e}")
                return False
            
            # Random velocity with safety limits
            try:
                speed = max(0.05, min(0.3, 0.1 + np.random.random() * 0.2))
                particle['velocity'] = [
                    max(-0.5, min(0.5, -particle['position'][0] * speed * 0.1)),
                    max(-0.5, min(0.5, -particle['position'][1] * speed * 0.1)),
                    max(-0.5, min(0.5, -particle['position'][2] * speed * 0.1))
                ]
            except Exception as e:
                print(f"Error setting particle velocity: {e}")
                return False
            
            # Reset lifetime and color with validation
            try:
                particle['lifetime'] = max(0.1, particle.get('max_lifetime', 1.0))
                particle['color'][3] = max(0.1, min(1.0, 0.7 + np.random.random() * 0.3))
            except Exception as e:
                print(f"Error resetting particle properties: {e}")
                return False
                
            return True
            
        except Exception as e:
            print(f"Critical error in particle reset: {e}")
            return False
    
    def render_hologram(self, intensity=1.0):
        """
        Render a holographic effect with multiple layers and glow.
        
        Args:
            intensity (float): Animation intensity
        """
        glPushMatrix()
        
        # Update hologram animation
        self.holo_rotation += self.rotation_speed * 0.5
        self.holo_scale = 1.0 + math.sin(time.time() * 2.0) * 0.1
        self.holo_alpha = 0.5 + math.sin(time.time() * 3.0) * 0.2
        
        # Set material properties for hologram
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.0, 0.2, 0.3, self.holo_alpha])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.0, 0.5, 0.8, self.holo_alpha])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.0, 1.0, 1.0, self.holo_alpha])
        glMaterialf(GL_FRONT, GL_SHININESS, 50.0)
        
        # Render multiple layers with different rotations and scales
        for layer in range(self.holo_layers):
            layer_scale = self.holo_scale * (1.0 + layer * 0.1)
            layer_alpha = self.holo_alpha * (1.0 - layer * 0.2)
            
            glPushMatrix()
            glRotatef(self.holo_rotation + layer * 30, 0, 1, 0)
            glScalef(layer_scale, layer_scale, layer_scale)
            
            # Draw holographic sphere
            glColor4f(0.0, 0.6, 1.0, layer_alpha)
            gluSphere(self.models['hologram'], 1.0, 32, 32)
            
            glPopMatrix()
        
        glPopMatrix()
    
    def render_energy_field(self, intensity=1.0):
        """
        Render an energy field effect around the hologram.
        
        Args:
            intensity (float): Animation intensity
        """
        glPushMatrix()
        
        # Update energy field animation
        self.field_rotation += self.rotation_speed * 0.3
        self.field_pulse = (math.sin(time.time() * 4.0) + 1.0) * 0.5
        field_scale = self.field_scale + self.field_pulse * 0.2
        
        # Set material properties for energy field
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.1, 0.2, 0.3, 0.3])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.2, 0.5, 0.8, 0.3])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.5, 0.8, 1.0, 0.3])
        glMaterialf(GL_FRONT, GL_SHININESS, 30.0)
        
        # Draw energy field
        glPushMatrix()
        glRotatef(self.field_rotation, 0, 1, 0)
        glScalef(field_scale, field_scale, field_scale)
        
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE)
        
        # Draw multiple layers with different rotations
        for i in range(2):
            glRotatef(90 * i, 1, 0, 0)
            glColor4f(0.2, 0.6, 1.0, 0.15 * intensity)
            gluDisk(self.models['energy_field'], 0, 1.5, 32, 1)
        
        glDisable(GL_BLEND)
        glPopMatrix()
        
        glPopMatrix()
    

    
    def set_material(self, material_name):
        """
        Set the current material for rendering.
        
        Args:
            material_name (str): Name of the material to use
        """
        if material_name in self.materials:
            self.current_material = material_name
    
    def _apply_material(self, material_name=None):
        """
        Apply the specified material properties to OpenGL.
        
        Args:
            material_name (str): Name of the material to apply, or None for current material
        """
        if not material_name:
            material_name = self.current_material
            
        material = self.materials.get(material_name, self.materials['default'])
        
        glMaterialfv(GL_FRONT, GL_AMBIENT, material['ambient'])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, material['diffuse'])
        glMaterialfv(GL_FRONT, GL_SPECULAR, material['specular'])
        glMaterialf(GL_FRONT, GL_SHININESS, material['shininess'])
    
    def set_animation_state(self, state, intensity=1.0):
        """
        Set the animation state and parameters.
        
        Args:
            state (str): Animation state ('idle', 'listening', or 'speaking')
            intensity (float): Animation intensity from 0.0 to 1.0
        """
        # Set material based on state
        if state == 'idle':
            self.set_material('blue_glow')
            self.animation_speed = 0.5 * intensity
            self.pulse_frequency = 0.3 * intensity
        elif state == 'listening':
            self.set_material('green_glow')
            self.animation_speed = 1.0 * intensity
            self.pulse_frequency = 0.8 * intensity
        elif state == 'speaking':
            self.set_material('orange_glow')
            self.animation_speed = 1.5 * intensity
            self.pulse_frequency = 1.2 * intensity
        
        # Scale rotation speed with intensity
        self.rotation_speed = 15.0 * intensity
    
    def render(self, dt=0.033):
        """
        Render the current scene to an offscreen buffer and return as image.
        
        Args:
            dt (float): Time delta in seconds
            
        Returns:
            PIL.Image: Rendered image or None if rendering failed
        """
        if not self.available or not self.initialized:
            return None
            
        try:
            # Update animation time safely
            try:
                self.animation_time += dt * self.animation_speed
            except Exception as e:
                print(f"Error updating animation time: {e}")
                self.animation_time = 0.0
            
            # Update particles with error handling
            try:
                self._update_particles(dt)
            except Exception as e:
                print(f"Error updating particles: {e}")
            
            # Clear buffers with error checking
            try:
                glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            except Exception as e:
                print(f"Error clearing buffers: {e}")
                return None
            
            # Set up modelview matrix
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            
            # Position camera
            gluLookAt(
                self.camera_position[0], self.camera_position[1], self.camera_position[2],
                0.0, 0.0, 0.0,  # Look at origin
                0.0, 1.0, 0.0   # Up vector
            )
            
            # Apply camera rotation
            glRotatef(self.camera_rotation[0], 1.0, 0.0, 0.0)
            glRotatef(self.camera_rotation[1], 0.0, 1.0, 0.0)
            glRotatef(self.camera_rotation[2], 0.0, 0.0, 1.0)
            
            # Update camera rotation for animation
            self.camera_rotation[1] += self.rotation_speed * dt
            
            # Enable/disable features based on settings
            if self.use_lighting:
                glEnable(GL_LIGHTING)
            else:
                glDisable(GL_LIGHTING)
                
            if self.wireframe_mode:
                glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            else:
                glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
                
            if self.use_blending:
                glEnable(GL_BLEND)
            else:
                glDisable(GL_BLEND)
            
            # Render central sphere
            glPushMatrix()
            
            # Apply pulsing effect
            pulse = 0.8 + 0.2 * math.sin(self.animation_time * self.pulse_frequency * math.pi)
            glScalef(pulse, pulse, pulse)
            
            # Apply material
            self._apply_material()
            
            # Draw sphere
            gluSphere(self.models['sphere'], 1.0, 32, 32)
            
            glPopMatrix()
            
            # Render particles
            glDisable(GL_LIGHTING)  # Disable lighting for particles
            
            for particle in self.particles:
                # Calculate opacity based on lifetime
                opacity = particle['lifetime'] / particle['max_lifetime']
                color = particle['color'].copy()
                color[3] = color[3] * opacity
                
                glPushMatrix()
                
                # Position particle
                glTranslatef(
                    particle['position'][0],
                    particle['position'][1],
                    particle['position'][2]
                )
                
                # Make particles always face camera (billboarding)
                glRotatef(-self.camera_rotation[1], 0.0, 1.0, 0.0)
                glRotatef(-self.camera_rotation[0], 1.0, 0.0, 0.0)
                
                # Set color with transparency
                glColor4f(color[0], color[1], color[2], color[3])
                
                # Draw particle as point sprite
                glPointSize(particle['size'] * 20)  # Scale for visibility
                glBegin(GL_POINTS)
                glVertex3f(0.0, 0.0, 0.0)
                glEnd()
                
                glPopMatrix()
            
            # Re-enable lighting if it was enabled
            if self.use_lighting:
                glEnable(GL_LIGHTING)
            
            # Read pixels from framebuffer
            glPixelStorei(GL_PACK_ALIGNMENT, 1)
            data = glReadPixels(0, 0, self.width, self.height, GL_RGBA, GL_UNSIGNED_BYTE)
            
            # Convert to PIL Image
            image = Image.frombytes("RGBA", (self.width, self.height), data)
            
            # OpenGL returns image flipped vertically
            image = image.transpose(Image.FLIP_TOP_BOTTOM)
            
            return image
            
        except Exception as e:
            print(f"Error rendering OpenGL scene: {e}")
            return None
    
    def get_tkinter_image(self):
        """
        Render the current scene and return as a Tkinter-compatible PhotoImage.
        
        Returns:
            ImageTk.PhotoImage: Rendered image for Tkinter or None if rendering failed
        """
        image = self.render()
        if image:
            return ImageTk.PhotoImage(image)
        return None
    
    def resize(self, width, height):
        """
        Resize the rendering viewport.
        
        Args:
            width (int): New width
            height (int): New height
        """
        if not self.available or not self.initialized:
            return
            
        self.width = width
        self.height = height
        
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, width / height, 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
    
    def cleanup(self):
        """
        Clean up OpenGL resources safely with error handling.
        """
        if not self.available:
            return
            
        try:
            # Delete all quadric objects safely
            for model in list(self.models.values()):
                try:
                    if model:
                        gluDeleteQuadric(model)
                except Exception as e:
                    print(f"Error deleting quadric: {e}")
            self.models.clear()
            
            # Delete textures safely
            for texture_id in list(self.texture_ids.values()):
                try:
                    if texture_id:
                        glDeleteTextures([texture_id])
                except Exception as e:
                    print(f"Error deleting texture: {e}")
            self.texture_ids.clear()
            
            # Delete framebuffer objects safely
            if self.fbo is not None:
                try:
                    glDeleteFramebuffers(1, [self.fbo])
                except Exception as e:
                    print(f"Error deleting framebuffer: {e}")
                self.fbo = None
            
            if self.render_texture is not None:
                try:
                    glDeleteTextures([self.render_texture])
                except Exception as e:
                    print(f"Error deleting render texture: {e}")
                self.render_texture = None
            
            if self.depth_buffer is not None:
                try:
                    glDeleteRenderbuffers(1, [self.depth_buffer])
                except Exception as e:
                    print(f"Error deleting depth buffer: {e}")
                self.depth_buffer = None
                
            # Disable states that were enabled
            try:
                glDisable(GL_LIGHTING)
                glDisable(GL_LIGHT0)
                glDisable(GL_DEPTH_TEST)
                glDisable(GL_BLEND)
            except Exception as e:
                print(f"Error disabling GL states: {e}")
                
        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            # Always reset state even if cleanup fails
            self.initialized = False
            self.particles = []
            self.animation_time = 0.0
            self.available = False  # Mark as unavailable after cleanup