#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Enhanced Particle System Module

This module provides an advanced particle system with physics-based interactions,
particle trails, and reactive effects for the Jarvis animated UI.
"""

import numpy as np
import math
import random
import time

class ParticleSystem:
    """
    Advanced particle system with physics-based interactions and reactive effects.
    """
    
    def __init__(self, width=900, height=220, max_particles=200):
        """
        Initialize the particle system.
        
        Args:
            width (int): Width of the canvas
            height (int): Height of the canvas
            max_particles (int): Maximum number of particles
        """
        self.width = width
        self.height = height
        self.max_particles = max_particles
        self.particles = []
        self.trails = []
        self.flow_field = None
        self.collision_grid = {}
        self.grid_cell_size = 20  # Size of collision grid cells
        self.friendly_mode = True  # Enable friendly animations by default
        self.emoji_particles = []  # Store emoji particles separately
        self.last_emoji_time = 0  # Track when the last emoji was created
        
        # Friendly animation settings
        self.emoji_set = ['😊', '👍', '✨', '🎵', '💡', '🚀', '🔍', '👋', '😄', '🎉']
        self.reaction_emojis = {
            'listening': ['👂', '🎧', '🔊', '👀'],
            'speaking': ['💬', '🗣️', '📢', '🎵'],
            'success': ['✅', '👍', '🎉', '😊'],
            'thinking': ['🤔', '💭', '⏳', '🧠'],
            'error': ['❌', '😕', '🤷', '⚠️'],
            'joke': ['😂', '🤣', '😆', '😄']
        }
        self.emoji_lifetime = 3.0  # Seconds
        self.emoji_spawn_chance = 0.02  # Chance per update
        self.emoji_min_interval = 2.0  # Minimum seconds between emoji spawns
        
        # Particle types and their properties
        self.particle_types = {
            'normal': {
                'size_range': (2, 6),
                'speed_range': (0.5, 2.0),
                'lifetime_range': (0.7, 1.5),
                'opacity_range': (0.6, 1.0),
                'trail_chance': 0.0,
                'collision_radius': 0.0,  # No collision
                'color_shift': 0.0,  # No color shift
                'mass': 1.0
            },
            'pulse': {
                'size_range': (3, 8),
                'speed_range': (0.3, 1.0),
                'lifetime_range': (0.8, 2.0),
                'opacity_range': (0.7, 0.9),
                'trail_chance': 0.1,
                'collision_radius': 0.0,  # No collision
                'color_shift': 0.1,  # Slight color shift
                'mass': 1.5
            },
            'trail': {
                'size_range': (1.5, 4),
                'speed_range': (0.8, 3.0),
                'lifetime_range': (0.5, 1.2),
                'opacity_range': (0.4, 0.7),
                'trail_chance': 0.8,
                'collision_radius': 0.0,  # No collision
                'color_shift': 0.2,  # Moderate color shift
                'mass': 0.7
            },
            'spark': {
                'size_range': (1, 3),
                'speed_range': (2.0, 5.0),
                'lifetime_range': (0.3, 0.8),
                'opacity_range': (0.8, 1.0),
                'trail_chance': 0.6,
                'collision_radius': 0.0,  # No collision
                'color_shift': 0.3,  # Significant color shift
                'mass': 0.5
            },
            'physics': {
                'size_range': (3, 7),
                'speed_range': (0.5, 2.5),
                'lifetime_range': (1.0, 3.0),
                'opacity_range': (0.7, 1.0),
                'trail_chance': 0.4,
                'collision_radius': 5.0,  # Enable collision
                'color_shift': 0.1,  # Slight color shift
                'mass': 2.0
            },
            'attractor': {
                'size_range': (5, 10),
                'speed_range': (0.2, 0.8),
                'lifetime_range': (2.0, 5.0),
                'opacity_range': (0.6, 0.9),
                'trail_chance': 0.2,
                'collision_radius': 30.0,  # Large influence radius
                'color_shift': 0.0,  # No color shift
                'mass': 10.0,
                'attraction_strength': 0.05
            },
            # Friendly particle types
            'bubble': {
                'size_range': (5, 12),
                'speed_range': (0.3, 1.2),
                'lifetime_range': (1.5, 3.0),
                'opacity_range': (0.4, 0.8),
                'trail_chance': 0.0,
                'collision_radius': 8.0,  # Soft collision
                'color_shift': 0.2,  # Moderate color shift
                'mass': 0.8,
                'is_bubble': True  # Special flag for bubble behavior
            },
            'bounce': {
                'size_range': (4, 8),
                'speed_range': (1.0, 3.0),
                'lifetime_range': (1.0, 2.5),
                'opacity_range': (0.7, 1.0),
                'trail_chance': 0.3,
                'collision_radius': 6.0,  # Enable bouncy collision
                'color_shift': 0.15,  # Slight color shift
                'mass': 1.2,
                'bounce_factor': 0.8  # How bouncy the particle is
            }
        }
        
        # Initialize flow field
        self._init_flow_field()
    
    def _init_flow_field(self, resolution=20):
        """
        Initialize a flow field for particle movement.
        
        Args:
            resolution (int): Resolution of the flow field grid
        """
        # Calculate grid dimensions
        cols = int(self.width / resolution) + 1
        rows = int(self.height / resolution) + 1
        
        # Create flow field as a 2D grid of angles
        self.flow_field = np.zeros((rows, cols))
        
        # Generate Perlin noise-like flow field (simplified)
        for y in range(rows):
            for x in range(cols):
                # Create a flowing pattern that changes over time
                angle = (x * 0.1) + (y * 0.1) + (math.sin(x * 0.05) * math.cos(y * 0.05) * 2)
                self.flow_field[y, x] = angle
        
        # Store flow field metadata
        self.flow_field_meta = {
            'resolution': resolution,
            'cols': cols,
            'rows': rows,
            'last_update': time.time()
        }
    
    def update_flow_field(self, time_factor=0.1):
        """
        Update the flow field to create dynamic movement patterns.
        
        Args:
            time_factor (float): Time factor for animation speed
        """
        current_time = time.time()
        time_delta = current_time - self.flow_field_meta['last_update']
        
        # Only update periodically for performance
        if time_delta < 0.2:  # Update every 200ms
            return
            
        cols = self.flow_field_meta['cols']
        rows = self.flow_field_meta['rows']
        
        # Update flow field angles with time-based variation
        time_offset = current_time * time_factor
        for y in range(rows):
            for x in range(cols):
                # Create a flowing pattern that changes over time
                angle = (x * 0.1) + (y * 0.1) + time_offset + \
                        (math.sin(x * 0.05 + time_offset) * math.cos(y * 0.05 + time_offset) * 2)
                self.flow_field[y, x] = angle
        
        self.flow_field_meta['last_update'] = current_time
    
    def get_flow_field_force(self, x, y):
        """
        Get the force vector from the flow field at the given position.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
            
        Returns:
            tuple: (force_x, force_y) normalized force vector
        """
        # Get flow field cell
        resolution = self.flow_field_meta['resolution']
        col = int(x / resolution)
        row = int(y / resolution)
        
        # Clamp to grid bounds
        col = max(0, min(col, self.flow_field_meta['cols'] - 1))
        row = max(0, min(row, self.flow_field_meta['rows'] - 1))
        
        # Get angle from flow field
        angle = self.flow_field[row, col]
        
        # Convert angle to force vector
        force_x = math.cos(angle) * 0.2  # Scale force
        force_y = math.sin(angle) * 0.2
        
        return (force_x, force_y)
    
    def create_emoji_particle(self, x, y, state='idle'):
        """
        Create an emoji particle at the specified position based on the current state.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
            state (str): Current animation state
        """
        # Select appropriate emoji based on state
        if state in self.reaction_emojis:
            emoji = random.choice(self.reaction_emojis[state])
        else:
            emoji = random.choice(self.emoji_set)
        
        # Create emoji particle with random movement
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.5, 1.5)
        vx = math.cos(angle) * speed
        vy = math.sin(angle) * speed - 0.5  # Slight upward bias
        
        # Add emoji particle
        self.emoji_particles.append({
            'emoji': emoji,
            'x': x,
            'y': y,
            'vx': vx,
            'vy': vy,
            'size': random.uniform(20, 30),
            'opacity': 1.0,
            'lifetime': self.emoji_lifetime,
            'age': 0.0,
            'rotation': random.uniform(-15, 15),
            'rotation_speed': random.uniform(-5, 5)
        })
    
    def create_reaction(self, x, y, reaction_type):
        """
        Create a reaction emoji burst for specific events.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
            reaction_type (str): Type of reaction ('success', 'error', 'joke', etc.)
        """
        if not self.friendly_mode:
            return
            
        # Create multiple emojis for the reaction
        count = random.randint(3, 6)
        for _ in range(count):
            # Select emoji based on reaction type
            if reaction_type in self.reaction_emojis:
                emoji = random.choice(self.reaction_emojis[reaction_type])
            else:
                emoji = random.choice(self.emoji_set)
            
            # Create with burst pattern
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(10, 40)
            pos_x = x + math.cos(angle) * distance
            pos_y = y + math.sin(angle) * distance
            
            # Add emoji with random movement
            speed = random.uniform(1.0, 2.0)
            vx = math.cos(angle) * speed * 0.5
            vy = math.sin(angle) * speed * 0.5 - 1.0  # Stronger upward bias
            
            self.emoji_particles.append({
                'emoji': emoji,
                'x': pos_x,
                'y': pos_y,
                'vx': vx,
                'vy': vy,
                'size': random.uniform(25, 35),
                'opacity': 1.0,
                'lifetime': self.emoji_lifetime * 1.5,
                'age': 0.0,
                'rotation': random.uniform(-20, 20),
                'rotation_speed': random.uniform(-8, 8)
            })
    
    def update_emoji_particles(self, dt):
        """
        Update emoji particles with physics and aging.
        
        Args:
            dt (float): Time delta in seconds
        """
        # Update existing emoji particles
        i = 0
        while i < len(self.emoji_particles):
            emoji = self.emoji_particles[i]
            
            # Update age
            emoji['age'] += dt
            if emoji['age'] >= emoji['lifetime']:
                # Remove expired emoji
                self.emoji_particles.pop(i)
                continue
            
            # Update position with physics
            emoji['x'] += emoji['vx'] * dt * 60
            emoji['y'] += emoji['vy'] * dt * 60
            
            # Add gravity and friction
            emoji['vy'] += 0.05 * dt  # Gravity
            emoji['vx'] *= 0.98  # Horizontal friction
            
            # Update rotation
            emoji['rotation'] += emoji['rotation_speed'] * dt
            
            # Update opacity (fade out near end of life)
            life_ratio = emoji['age'] / emoji['lifetime']
            if life_ratio > 0.7:
                emoji['opacity'] = 1.0 - ((life_ratio - 0.7) / 0.3)
            
            i += 1
    
    def _update_collision_grid(self):
        """
        Update the spatial partitioning grid for efficient collision detection.
        """
        # Clear the grid
        self.collision_grid = {}
        
        # Add particles to grid cells
        for i, particle in enumerate(self.particles):
            # Skip particles without collision
            if particle.get('collision_radius', 0) <= 0:
                continue
                
            # Get grid cell coordinates
            cell_x = int(particle['x'] / self.grid_cell_size)
            cell_y = int(particle['y'] / self.grid_cell_size)
            cell_key = f"{cell_x},{cell_y}"
            
            # Add particle index to this cell
            if cell_key not in self.collision_grid:
                self.collision_grid[cell_key] = []
            self.collision_grid[cell_key].append(i)
            
            # Also add to neighboring cells if near the boundary
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                        
                    # Check if particle is close to this neighboring cell
                    neighbor_x = cell_x + dx
                    neighbor_y = cell_y + dy
                    neighbor_key = f"{neighbor_x},{neighbor_y}"
                    
                    # Calculate distance to cell boundary
                    boundary_x = (cell_x + (1 if dx > 0 else 0)) * self.grid_cell_size
                    boundary_y = (cell_y + (1 if dy > 0 else 0)) * self.grid_cell_size
                    
                    dist_x = abs(particle['x'] - boundary_x)
                    dist_y = abs(particle['y'] - boundary_y)
                    
                    # If close to boundary, add to neighboring cell
                    if dist_x < particle['collision_radius'] or dist_y < particle['collision_radius']:
                        if neighbor_key not in self.collision_grid:
                            self.collision_grid[neighbor_key] = []
                        self.collision_grid[neighbor_key].append(i)
    
    def _check_collisions(self):
        """
        Check for collisions between particles and resolve them.
        """
        # Update collision grid
        self._update_collision_grid()
        
        # Process each grid cell
        for cell_key, particle_indices in self.collision_grid.items():
            # Skip cells with less than 2 particles
            if len(particle_indices) < 2:
                continue
                
            # Check all pairs in this cell
            for i in range(len(particle_indices)):
                for j in range(i + 1, len(particle_indices)):
                    p1_idx = particle_indices[i]
                    p2_idx = particle_indices[j]
                    
                    # Get particles
                    p1 = self.particles[p1_idx]
                    p2 = self.particles[p2_idx]
                    
                    # Calculate distance
                    dx = p2['x'] - p1['x']
                    dy = p2['y'] - p1['y']
                    distance = math.sqrt(dx*dx + dy*dy)
                    
                    # Check for collision
                    min_distance = p1['collision_radius'] + p2['collision_radius']
                    if distance < min_distance and distance > 0:
                        # Handle collision based on particle types
                        if p1.get('type') == 'attractor' or p2.get('type') == 'attractor':
                            # Handle attractor-based interaction
                            self._handle_attraction(p1, p2, dx, dy, distance)
                        else:
                            # Handle physical collision
                            self._handle_collision(p1, p2, dx, dy, distance, min_distance)
    
    def _handle_collision(self, p1, p2, dx, dy, distance, min_distance):
        """
        Handle physical collision between two particles.
        
        Args:
            p1 (dict): First particle
            p2 (dict): Second particle
            dx (float): X distance between particles
            dy (float): Y distance between particles
            distance (float): Total distance between particles
            min_distance (float): Minimum distance before collision
        """
        # Calculate collision normal
        nx = dx / distance
        ny = dy / distance
        
        # Calculate relative velocity
        dvx = p2['vx'] - p1['vx']
        dvy = p2['vy'] - p1['vy']
        
        # Calculate velocity along normal
        normal_vel = dvx * nx + dvy * ny
        
        # If particles are moving away from each other, skip collision response
        if normal_vel > 0:
            return
            
        # Calculate impulse scalar
        restitution = 0.8  # Bounciness factor
        
        # Get particle masses
        m1 = p1.get('mass', 1.0)
        m2 = p2.get('mass', 1.0)
        
        # Calculate impulse scalar
        impulse = -(1 + restitution) * normal_vel / (1/m1 + 1/m2)
        
        # Apply impulse
        p1['vx'] -= impulse * nx / m1
        p1['vy'] -= impulse * ny / m1
        p2['vx'] += impulse * nx / m2
        p2['vy'] += impulse * ny / m2
        
        # Separate particles to prevent sticking
        overlap = min_distance - distance
        separation_x = nx * overlap * 0.5
        separation_y = ny * overlap * 0.5
        
        p1['x'] -= separation_x
        p1['y'] -= separation_y
        p2['x'] += separation_x
        p2['y'] += separation_y
        
        # Create spark particles on collision
        if random.random() < 0.3:  # 30% chance
            collision_x = p1['x'] + dx * 0.5
            collision_y = p1['y'] + dy * 0.5
            self.create_particle_burst('spark', collision_x, collision_y, 3, p1['color'])
    
    def _handle_attraction(self, p1, p2, dx, dy, distance):
        """
        Handle attraction/repulsion between particles.
        
        Args:
            p1 (dict): First particle
            p2 (dict): Second particle
            dx (float): X distance between particles
            dy (float): Y distance between particles
            distance (float): Total distance between particles
        """
        # Determine which particle is the attractor
        attractor, affected = (p1, p2) if p1.get('type') == 'attractor' else (p2, p1)
        
        # Calculate attraction direction
        nx = dx / distance
        ny = dy / distance
        
        # Get attraction strength
        strength = attractor.get('attraction_strength', 0.05)
        
        # Apply attraction force (inverse square law)
        force = strength / max(0.1, distance * 0.1)  # Prevent division by zero
        
        # Apply force to affected particle
        affected['vx'] += nx * force
        affected['vy'] += ny * force
        
        # Create trail effect for attracted particles
        if random.random() < 0.1:  # 10% chance
            self.add_trail(affected['x'], affected['y'], affected['size'] * 0.5, affected['color'])
    
    def create_particle(self, x, y, particle_type='normal', color=None, velocity=None):
        """
        Create a new particle at the specified position.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
            particle_type (str): Type of particle to create
            color (str): Hex color code or None for default
            velocity (tuple): Initial velocity (vx, vy) or None for random
            
        Returns:
            dict: The created particle
        """
        # Get particle type properties
        type_props = self.particle_types.get(particle_type, self.particle_types['normal'])
        
        # Random properties based on type
        size = random.uniform(*type_props['size_range'])
        lifetime = random.uniform(*type_props['lifetime_range'])
        opacity = random.uniform(*type_props['opacity_range'])
        
        # Set velocity
        if velocity:
            vx, vy = velocity
        else:
            # Random angle and speed
            angle = random.random() * math.pi * 2
            speed = random.uniform(*type_props['speed_range'])
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
        
        # Create particle
        particle = {
            'x': x,
            'y': y,
            'vx': vx,
            'vy': vy,
            'ax': 0,  # Acceleration x
            'ay': 0,  # Acceleration y
            'size': size,
            'original_size': size,
            'lifetime': lifetime,
            'max_lifetime': lifetime,
            'opacity': opacity,
            'color': color if color else "#00a8ff",  # Default blue
            'type': particle_type,
            'pulse_phase': random.random() * math.pi * 2,  # For pulsing particles
            'trail_chance': type_props['trail_chance'],
            'collision_radius': type_props['collision_radius'],
            'mass': type_props['mass'],
            'id': None  # Will be set when drawn
        }
        
        # Add special properties for specific types
        if particle_type == 'attractor':
            particle['attraction_strength'] = type_props.get('attraction_strength', 0.05)
        
        # Add to particles list if not full
        if len(self.particles) < self.max_particles:
            self.particles.append(particle)
            return particle
        else:
            # Replace oldest particle
            oldest_idx = 0
            oldest_lifetime_ratio = 1.0
            
            for i, p in enumerate(self.particles):
                lifetime_ratio = p['lifetime'] / p['max_lifetime']
                if lifetime_ratio < oldest_lifetime_ratio:
                    oldest_lifetime_ratio = lifetime_ratio
                    oldest_idx = i
            
            self.particles[oldest_idx] = particle
            return particle
    
    def create_particle_burst(self, particle_type, x, y, count, color=None, speed_range=(0.5, 2.0)):
        """
        Create a burst of particles at the specified position.
        
        Args:
            particle_type (str): Type of particles to create
            x (float): X coordinate
            y (float): Y coordinate
            count (int): Number of particles to create
            color (str): Hex color code or None for default
            speed_range (tuple): Range of speeds for particles
        """
        for _ in range(count):
            # Random angle and speed
            angle = random.random() * math.pi * 2
            speed = random.uniform(*speed_range)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            
            # Create particle with specified velocity
            self.create_particle(x, y, particle_type, color, (vx, vy))
    
    def add_trail(self, x, y, size, color, lifetime_factor=0.5):
        """
        Add a trail particle that fades out over time.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
            size (float): Size of the trail particle
            color (str): Color of the trail particle
            lifetime_factor (float): Lifetime relative to normal particles
        """
        # Create a simple trail particle with no movement
        trail = {
            'x': x,
            'y': y,
            'size': size,
            'lifetime': 0.5 * lifetime_factor,  # Short lifetime
            'max_lifetime': 0.5 * lifetime_factor,
            'color': color,
            'opacity': 0.7,
            'id': None  # Will be set when drawn
        }
        
        # Add to trails list
        self.trails.append(trail)
        
        # Limit number of trails
        if len(self.trails) > self.max_particles * 2:
            self.trails.pop(0)  # Remove oldest trail
    
    def update(self, dt, center_x, center_y, animation_state='idle', intensity=0.5):
        """
        Update all particles and trails.
        
        Args:
            dt (float): Time delta in seconds
            center_x (float): X coordinate of the center point
            center_y (float): Y coordinate of the center point
            animation_state (str): Current animation state
            intensity (float): Animation intensity from 0.0 to 1.0
            
        Returns:
            dict: Updated particles and trails
        """
        # Update flow field
        self.update_flow_field()
        
        # Determine spawn rate based on animation state and intensity
        spawn_rate = 0
        if animation_state == 'idle':
            spawn_rate = 1 * intensity
        elif animation_state == 'listening':
            spawn_rate = 3 * intensity
        elif animation_state == 'speaking':
            spawn_rate = 5 * intensity
        
        # Spawn new particles
        for _ in range(int(spawn_rate)):
            if len(self.particles) < self.max_particles and random.random() < intensity:
                # Determine particle type based on animation state and friendly mode
                if self.friendly_mode:
                    if animation_state == 'idle':
                        particle_type = random.choice(['normal', 'pulse', 'bubble'])
                    elif animation_state == 'listening':
                        particle_type = random.choice(['normal', 'pulse', 'trail', 'bounce'])
                    elif animation_state == 'speaking':
                        particle_type = random.choice(['normal', 'pulse', 'trail', 'bounce', 'bubble'])
                    else:
                        particle_type = 'normal'
                else:
                    if animation_state == 'idle':
                        particle_type = random.choice(['normal', 'pulse'])
                    elif animation_state == 'listening':
                        particle_type = random.choice(['normal', 'pulse', 'trail', 'physics'])
                    elif animation_state == 'speaking':
                        particle_type = random.choice(['normal', 'pulse', 'trail', 'spark', 'physics', 'attractor'])
                    else:
                        particle_type = 'normal'
                    
                # Create particle at center
                self.create_particle(center_x, center_y, particle_type)
                
        # Spawn emoji particles in friendly mode
        current_time = time.time()
        if self.friendly_mode and current_time - self.last_emoji_time > self.emoji_min_interval:
            if random.random() < self.emoji_spawn_chance * intensity:
                self.last_emoji_time = current_time
                self.create_emoji_particle(center_x, center_y, animation_state)
        
        # Check for collisions
        self._check_collisions()
        
        # Update existing particles
        particles_to_remove = []
        for i, particle in enumerate(self.particles):
            # Get particle type
            particle_type = particle.get('type', 'normal')
            
            # Apply flow field forces
            flow_x, flow_y = self.get_flow_field_force(particle['x'], particle['y'])
            particle['vx'] += flow_x * dt
            particle['vy'] += flow_y * dt
            
            # Apply acceleration
            particle['vx'] += particle['ax'] * dt
            particle['vy'] += particle['ay'] * dt
            
            # Reset acceleration
            particle['ax'] = 0
            particle['ay'] = 0
            
            # Update position with type-specific behavior
            if particle_type == 'normal':
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
            elif particle_type == 'pulse':
                # Pulsing particles move slower
                particle['x'] += particle['vx'] * 0.8
                particle['y'] += particle['vy'] * 0.8
                # Add pulsing effect
                particle['pulse_phase'] += 0.1
                # Adjust size based on pulse
                pulse_factor = 0.3 * math.sin(particle['pulse_phase'])
                particle['size'] = particle['original_size'] * (1 + pulse_factor)
            elif particle_type == 'trail':
                # Trail particles accelerate
                particle['vx'] *= 1.01
                particle['vy'] *= 1.01
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                # Create trail effect
                if random.random() < particle['trail_chance']:
                    self.add_trail(particle['x'], particle['y'], particle['size'] * 0.5, particle['color'])
            elif particle_type == 'spark':
                # Spark particles move erratically
                particle['vx'] += (random.random() - 0.5) * 0.2
                particle['vy'] += (random.random() - 0.5) * 0.2
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                # Create occasional trail
                if random.random() < particle['trail_chance']:
                    self.add_trail(particle['x'], particle['y'], particle['size'] * 0.3, particle['color'])
            elif particle_type == 'physics' or particle_type == 'attractor':
                # Physics-based particles follow normal movement
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                # Apply slight drag
                particle['vx'] *= 0.99
                particle['vy'] *= 0.99
            
            # Update lifetime
            particle['lifetime'] -= dt
            
            # Check if particle is dead or out of bounds
            if particle['lifetime'] <= 0 or \
               particle['x'] < -50 or particle['x'] > self.width + 50 or \
               particle['y'] < -50 or particle['y'] > self.height + 50:
                particles_to_remove.append(i)
        
        # Remove dead particles (in reverse order to avoid index issues)
        for i in sorted(particles_to_remove, reverse=True):
            if i < len(self.particles):
                self.particles.pop(i)
        
        # Update trails
        trails_to_remove = []
        for i, trail in enumerate(self.trails):
            # Update lifetime
            trail['lifetime'] -= dt
            
            # Update opacity based on lifetime
            trail['opacity'] = trail['lifetime'] / trail['max_lifetime'] * 0.7
            
            # Check if trail is dead
            if trail['lifetime'] <= 0:
                trails_to_remove.append(i)
        
        # Remove dead trails (in reverse order)
        for i in sorted(trails_to_remove, reverse=True):
            if i < len(self.trails):
                self.trails.pop(i)
        
        return {
            'particles': self.particles,
            'trails': self.trails
        }
    
    def create_keyword_burst(self, x, y, keyword, color=None):
        """
        Create a special particle burst based on a keyword.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
            keyword (str): Keyword to determine burst type
            color (str): Color override or None for default
        """
        # Default settings
        burst_type = 'normal'
        count = 5
        speed_range = (0.5, 2.0)
        
        # Adjust based on keyword
        keyword = keyword.lower()
        
        if 'error' in keyword or 'warning' in keyword or 'alert' in keyword:
            burst_type = 'spark'
            count = 10
            speed_range = (1.0, 3.0)
            if not color:
                color = "#ff5252"  # Red
                
        elif 'success' in keyword or 'complete' in keyword or 'done' in keyword:
            burst_type = 'pulse'
            count = 8
            if not color:
                color = "#00e676"  # Green
                
        elif 'processing' in keyword or 'computing' in keyword or 'thinking' in keyword:
            burst_type = 'physics'
            count = 12
            if not color:
                color = "#7b42ff"  # Purple
                
        elif 'listening' in keyword or 'heard' in keyword or 'audio' in keyword:
            burst_type = 'trail'
            count = 15
            speed_range = (0.8, 2.5)
            if not color:
                color = "#00a8ff"  # Blue
                
        elif 'speaking' in keyword or 'saying' in keyword or 'voice' in keyword:
            burst_type = 'attractor'
            count = 1  # Just one attractor
            # And some particles to be attracted
            self.create_particle_burst('normal', x, y, 10, color, (0.2, 1.0))
            if not color:
                color = "#ff9100"  # Orange
        
        # Create the burst
        self.create_particle_burst(burst_type, x, y, count, color, speed_range)