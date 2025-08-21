"""
Physics engine module handling all physics calculations.
Manages gravitational interactions and object updates.
"""

import math
from constants import TIME_STEP, MAX_FORCE

class PhysicsEngine:
    """
    Handles physics calculations for the gravity simulation.
    """
    
    def __init__(self):
        """Initialize the physics engine."""
        self.bodies = []
        self.paused = False
        self.time_scale = 1.0
        self.show_forces = False
        self.show_trails = True
    
    def add_body(self, body):
        """
        Add a celestial body to the simulation.
        
        Args:
            body (CelestialBody): Body to add
        """
        self.bodies.append(body)
    
    def remove_body(self, body):
        """
        Remove a celestial body from the simulation.
        
        Args:
            body (CelestialBody): Body to remove
        """
        if body in self.bodies:
            self.bodies.remove(body)
    
    def clear_all_bodies(self):
        """Remove all bodies from the simulation."""
        self.bodies.clear()
    
    def calculate_forces(self):
        """
        Calculate gravitational forces between all body pairs.
        Uses Newton's law of universal gravitation.
        """
        # Reset all forces
        for body in self.bodies:
            body.force_x = 0
            body.force_y = 0
        
        # Calculate pairwise gravitational forces
        for i in range(len(self.bodies)):
            for j in range(i + 1, len(self.bodies)):
                body1 = self.bodies[i]
                body2 = self.bodies[j]
                
                # Get gravitational force
                fx, fy = body1.get_gravitational_force(body2)
                
                # Apply Newton's third law (equal and opposite forces)
                body1.apply_force(fx, fy)
                body2.apply_force(-fx, -fy)
    
    def update(self, dt=None):
        """
        Update the physics simulation for one time step.
        
        Args:
            dt (float): Time step (uses default if None)
        """
        if self.paused:
            return
        
        # Use provided dt or default with time scale
        actual_dt = (dt if dt else TIME_STEP) * self.time_scale
        
        # Calculate all forces
        self.calculate_forces()
        
        # Update accelerations and positions
        for body in self.bodies:
            body.update_acceleration()
            body.update_position(actual_dt)
    
    def toggle_pause(self):
        """Toggle simulation pause state."""
        self.paused = not self.paused
    
    def set_time_scale(self, scale):
        """
        Set the time scale for the simulation.
        
        Args:
            scale (float): Time scale multiplier
        """
        self.time_scale = max(0.1, min(10.0, scale))
    
    def get_body_at_position(self, x, y):
        """
        Get the body at a specific position.
        
        Args:
            x (float): X coordinate
            y (float): Y coordinate
        
        Returns:
            CelestialBody or None: Body at position
        """
        for body in self.bodies:
            distance = math.sqrt((x - body.x)**2 + (y - body.y)**2)
            if distance <= body.radius:
                return body
        return None
    
    def get_system_energy(self):
        """
        Calculate total system energy (kinetic + potential).
        
        Returns:
            dict: Energy components
        """
        kinetic_energy = 0
        potential_energy = 0
        
        # Calculate kinetic energy
        for body in self.bodies:
            velocity_squared = body.vx**2 + body.vy**2
            kinetic_energy += 0.5 * body.mass * velocity_squared
        
        # Calculate potential energy
        for i in range(len(self.bodies)):
            for j in range(i + 1, len(self.bodies)):
                body1 = self.bodies[i]
                body2 = self.bodies[j]
                
                dx = body2.x - body1.x
                dy = body2.y - body1.y
                distance = math.sqrt(dx*dx + dy*dy)
                
                if distance > 0:
                    potential_energy -= (6.67430e-11 * body1.mass * body2.mass) / distance
        
        return {
            'kinetic': kinetic_energy,
            'potential': potential_energy,
            'total': kinetic_energy + potential_energy
        }
