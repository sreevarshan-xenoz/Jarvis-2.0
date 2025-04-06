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
        self.width = width
        self.height = height
        self.available = OPENGL_AVAILABLE
        self.initialized = False
        self.texture_ids = {}
        self.models = {}
        self.camera_position = [0.0, 0.0, 5.0]
        self.camera_rotation = [0.0, 0.0, 0.0]
        self.light_position = [0.0, 5.0, 5.0, 1.0]
        self.animation_time = 0.0
        
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
        # Create sphere model
        self.models['sphere'] = gluNewQuadric()
        gluQuadricNormals(self.models['sphere'], GLU_SMOOTH)
        gluQuadricTexture(self.models['sphere'], GL_TRUE)
        
        # Create torus model (will be created during rendering)
        
        # Create particle system
        self._init_particles()
    
    def _init_particles(self, num_particles=100):
        """
        Initialize particle system for 3D effects.
        
        Args:
            num_particles (int): Number of particles to create
        """
        self.particles = []
        for _ in range(num_particles):
            # Random position within a sphere
            theta = 2 * math.pi * np.random.random()
            phi = math.acos(2 * np.random.random() - 1)
            radius = 2.0 * np.random.random()
            
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.sin(phi) * math.sin(theta)
            z = radius * math.cos(phi)
            
            # Random velocity
            vx = (np.random.random() - 0.5) * 0.1
            vy = (np.random.random() - 0.5) * 0.1
            vz = (np.random.random() - 0.5) * 0.1
            
            # Random size and lifetime
            size = 0.05 + np.random.random() * 0.1
            lifetime = 1.0 + np.random.random() * 4.0
            
            # Random color (blue to cyan gradient)
            r = 0.0
            g = 0.4 + np.random.random() * 0.6
            b = 0.7 + np.random.random() * 0.3
            a = 0.7 + np.random.random() * 0.3
            
            self.particles.append({
                'position': [x, y, z],
                'velocity': [vx, vy, vz],
                'size': size,
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'color': [r, g, b, a]
            })
    
    def _update_particles(self, dt):
        """
        Update particle positions and properties.
        
        Args:
            dt (float): Time delta in seconds
        """
        particles_to_respawn = []
        
        for i, particle in enumerate(self.particles):
            # Update position
            particle['position'][0] += particle['velocity'][0] * dt
            particle['position'][1] += particle['velocity'][1] * dt
            particle['position'][2] += particle['velocity'][2] * dt
            
            # Update lifetime
            particle['lifetime'] -= dt
            
            # Check if particle needs to be respawned
            if particle['lifetime'] <= 0:
                particles_to_respawn.append(i)
        
        # Respawn dead particles
        for i in particles_to_respawn:
            # Random position on a sphere
            theta = 2 * math.pi * np.random.random()
            phi = math.acos(2 * np.random.random() - 1)
            radius = 2.0
            
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.sin(phi) * math.sin(theta)
            z = radius * math.cos(phi)
            
            # Random velocity (outward from center)
            speed = 0.05 + np.random.random() * 0.1
            vx = x * speed / radius
            vy = y * speed / radius
            vz = z * speed / radius
            
            # Reset properties
            self.particles[i]['position'] = [x, y, z]
            self.particles[i]['velocity'] = [vx, vy, vz]
            self.particles[i]['lifetime'] = self.particles[i]['max_lifetime']
    
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
            # Update animation time
            self.animation_time += dt * self.animation_speed
            
            # Update particles
            self._update_particles(dt)
            
            # Clear buffers
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
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
        Clean up OpenGL resources.
        """
        if not self.available or not self.initialized:
            return
            
        # Delete quadrics
        if 'sphere' in self.models:
            gluDeleteQuadric(self.models['sphere'])
            
        # Delete textures
        for texture_id in self.texture_ids.values():
            glDeleteTextures(texture_id)
            
        self.initialized = False