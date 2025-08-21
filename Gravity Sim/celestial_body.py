"""
CelestialBody module defining the physics objects in the simulation.
Each body has mass, position, velocity, and visual properties.
"""

import math
from utils import generate_random_color, calculate_distance

class CelestialBody:
    """
    Represents a celestial body in the gravity simulation.
    """
    
    def __init__(self, x, y, mass=None, radius=None, velocity=(0, 0), 
                 color=None, density=None, locked_properties=None):
        """
        Initialize a celestial body.
        
        Args:
            x (float): X position
            y (float): Y position
            mass (float): Mass of the body
            radius (float): Visual radius in pixels
            velocity (tuple): Initial velocity (vx, vy)
            color (tuple): RGB color
            density (float): Density of the body
            locked_properties (set): Set of locked property names
        """
        self.x = x
        self.y = y
        self.vx, self.vy = velocity
        self.ax = 0  # Acceleration x
        self.ay = 0  # Acceleration y
        
        # Physical properties
        self.mass = mass if mass else 1e24
        self.radius = radius if radius else 20
        self.density = density if density else 5515
        
        # Visual properties
        self.color = color if color else generate_random_color()
        self.trail = []  # Position trail for visual effect
        self.max_trail_length = 50
        
        # Property locks
        self.locked_properties = locked_properties if locked_properties else set()
        
        # Force tracking
        self.force_x = 0
        self.force_y = 0
        
        # Update dependent properties
        self.update_dependent_properties()
    
    def update_dependent_properties(self):
        """
        Update properties based on locked/unlocked relationships.
        Mass = Density × Volume
        Volume = (4/3) × π × r³
        """
        # If density and radius are set, calculate mass
        if 'mass' not in self.locked_properties:
            volume = (4/3) * math.pi * (self.radius ** 3)
            self.mass = self.density * volume * 1e15  # Scale factor
        
        # If mass and radius are set, calculate density
        elif 'density' not in self.locked_properties:
            volume = (4/3) * math.pi * (self.radius ** 3)
            if volume > 0:
                self.density = self.mass / (volume * 1e15)
        
        # If mass and density are set, calculate radius
        elif 'radius' not in self.locked_properties:
            volume = self.mass / (self.density * 1e15)
            self.radius = ((3 * volume) / (4 * math.pi)) ** (1/3)
            self.radius = max(5, min(100, self.radius))  # Clamp radius
    
    def apply_force(self, fx, fy):
        """
        Apply force to the body.
        
        Args:
            fx (float): Force in x direction
            fy (float): Force in y direction
        """
        self.force_x += fx
        self.force_y += fy
    
    def update_acceleration(self):
        """
        Update acceleration based on accumulated forces.
        F = ma, therefore a = F/m
        """
        if self.mass > 0:
            self.ax = self.force_x / self.mass
            self.ay = self.force_y / self.mass
        else:
            self.ax = 0
            self.ay = 0
        
        # Reset forces for next frame
        self.force_x = 0
        self.force_y = 0
    
    def update_position(self, dt):
        """
        Update position and velocity using Euler integration.
        
        Args:
            dt (float): Time step
        """
        # Update velocity
        self.vx += self.ax * dt
        self.vy += self.ay * dt
        
        # Update position
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Add to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)
    
    def get_gravitational_force(self, other):
        """
        Calculate gravitational force between this body and another.
        F = G * (m1 * m2) / r²
        
        Args:
            other (CelestialBody): Another celestial body
        
        Returns:
            tuple: Force components (fx, fy)
        """
        # Calculate distance
        dx = other.x - self.x
        dy = other.y - self.y
        distance = math.sqrt(dx*dx + dy*dy)
        
        # Prevent division by zero and collision instability
        if distance < (self.radius + other.radius):
            distance = self.radius + other.radius
        
        # Calculate force magnitude
        force_magnitude = (6.67430e-11 * self.mass * other.mass) / (distance ** 2)
        
        # Limit maximum force to prevent instabilities
        force_magnitude = min(force_magnitude, 1e10)
        
        # Calculate force components
        fx = force_magnitude * (dx / distance)
        fy = force_magnitude * (dy / distance)
        
        return fx, fy
    
    def set_property(self, property_name, value):
        """
        Set a property value and update dependent properties.
        
        Args:
            property_name (str): Name of the property
            value: New value for the property
        """
        if property_name == 'mass':
            self.mass = value
        elif property_name == 'radius':
            self.radius = value
        elif property_name == 'density':
            self.density = value
        elif property_name == 'vx':
            self.vx = value
        elif property_name == 'vy':
            self.vy = value
        elif property_name == 'color':
            self.color = value
        
        # Update dependent properties
        if property_name in ['mass', 'radius', 'density']:
            self.update_dependent_properties()
    
    def lock_property(self, property_name):
        """Lock a property from automatic updates."""
        self.locked_properties.add(property_name)
    
    def unlock_property(self, property_name):
        """Unlock a property for automatic updates."""
        self.locked_properties.discard(property_name)
    
    def is_locked(self, property_name):
        """Check if a property is locked."""
        return property_name in self.locked_properties
