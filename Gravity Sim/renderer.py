"""
Renderer module for drawing the simulation.
Handles all visual output using Pygame.
"""

import pygame
import math
from utils import hex_to_rgb

class Renderer:
    """
    Handles all rendering for the gravity simulation.
    """
    
    def __init__(self, screen, width, height):
        """
        Initialize the renderer.
        
        Args:
            screen: Pygame screen surface
            width (int): Screen width
            height (int): Screen height
        """
        self.screen = screen
        self.width = width
        self.height = height
        self.background_color = (0, 0, 0)  # Black default
        self.show_trails = True
        self.show_vectors = False
        self.show_grid = False
        self.grid_size = 50
        
        # Font for text rendering
        pygame.font.init()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 16)
    
    def set_background_color(self, color):
        """
        Set the background color.
        
        Args:
            color: RGB tuple or hex string
        """
        if isinstance(color, str):
            self.background_color = hex_to_rgb(color)
        else:
            self.background_color = color
    
    def clear(self):
        """Clear the screen with background color."""
        self.screen.fill(self.background_color)
    
    def draw_grid(self):
        """Draw a grid overlay for reference."""
        if not self.show_grid:
            return
        
        grid_color = (40, 40, 40)  # Dark gray
        
        # Draw vertical lines
        for x in range(0, self.width, self.grid_size):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, self.height), 1)
        
        # Draw horizontal lines
        for y in range(0, self.height, self.grid_size):
            pygame.draw.line(self.screen, grid_color, (0, y), (self.width, y), 1)
    
    def draw_body(self, body):
        """
        Draw a celestial body.
        
        Args:
            body (CelestialBody): Body to draw
        """
        # Draw trail if enabled
        if self.show_trails and len(body.trail) > 1:
            for i in range(len(body.trail) - 1):
                alpha = int(255 * (i / len(body.trail)))
                trail_color = tuple(c * alpha // 255 for c in body.color)
                pygame.draw.line(self.screen, trail_color, 
                               body.trail[i], body.trail[i + 1], 1)
        
        # Draw the body
        pygame.draw.circle(self.screen, body.color, 
                         (int(body.x), int(body.y)), 
                         int(body.radius))
        
        # Draw a slightly darker border for better visibility
        border_color = tuple(c * 0.7 for c in body.color)
        pygame.draw.circle(self.screen, border_color, 
                         (int(body.x), int(body.y)), 
                         int(body.radius), 2)
    
    def draw_velocity_vector(self, body, scale=0.1):
        """
        Draw velocity vector for a body.
        
        Args:
            body (CelestialBody): Body whose velocity to draw
            scale (float): Scale factor for vector length
        """
        if not self.show_vectors:
            return
        
        # Calculate vector end point
        end_x = body.x + body.vx * scale
        end_y = body.y + body.vy * scale
        
        # Draw velocity vector in green
        pygame.draw.line(self.screen, (0, 255, 0), 
                        (body.x, body.y), (end_x, end_y), 2)
        
        # Draw arrowhead
        if body.vx != 0 or body.vy != 0:
            angle = math.atan2(body.vy, body.vx)
            arrow_length = 10
            arrow_angle = 0.5
            
            # Calculate arrowhead points
            x1 = end_x - arrow_length * math.cos(angle - arrow_angle)
            y1 = end_y - arrow_length * math.sin(angle - arrow_angle)
            x2 = end_x - arrow_length * math.cos(angle + arrow_angle)
            y2 = end_y - arrow_length * math.sin(angle + arrow_angle)
            
            pygame.draw.polygon(self.screen, (0, 255, 0), 
                              [(end_x, end_y), (x1, y1), (x2, y2)])
    
    def draw_acceleration_vector(self, body, scale=1e-20):
        """
        Draw acceleration vector for a body.
        
        Args:
            body (CelestialBody): Body whose acceleration to draw
            scale (float): Scale factor for vector length
        """
        if not self.show_vectors:
            return
        
        # Calculate vector end point
        end_x = body.x + body.ax * scale
        end_y = body.y + body.ay * scale
        
        # Draw acceleration vector in red
        pygame.draw.line(self.screen, (255, 0, 0), 
                        (body.x, body.y), (end_x, end_y), 2)
    
    def draw_info_text(self, bodies, physics_engine):
        """
        Draw information text on screen.
        
        Args:
            bodies (list): List of celestial bodies
            physics_engine (PhysicsEngine): Physics engine instance
        """
        info_texts = [
            f"Bodies: {len(bodies)}",
            f"Time Scale: {physics_engine.time_scale:.1f}x",
            f"Paused: {physics_engine.paused}",
        ]
        
        # Draw info in top-left corner
        y_offset = 10
        for text in info_texts:
            surface = self.font.render(text, True, (255, 255, 255))
            self.screen.blit(surface, (10, y_offset))
            y_offset += 30
    
    def draw_help_text(self):
        """Draw help text showing controls."""
        help_texts = [
            "Click: Place object",
            "Right-click: Delete object",
            "Space: Pause/Resume",
            "C: Clear all",
            "T: Toggle trails",
            "V: Toggle vectors",
            "G: Toggle grid",
            "+/-: Time scale",
        ]
        
        # Draw help in bottom-left corner
        y_offset = self.height - len(help_texts) * 20 - 10
        for text in help_texts:
            surface = self.small_font.render(text, True, (200, 200, 200))
            self.screen.blit(surface, (10, y_offset))
            y_offset += 20
    
    def render(self, bodies, physics_engine, show_help=True):
        """
        Render the complete frame.
        
        Args:
            bodies (list): List of celestial bodies
            physics_engine (PhysicsEngine): Physics engine instance
            show_help (bool): Whether to show help text
        """
        # Clear screen
        self.clear()
        
        # Draw grid if enabled
        self.draw_grid()
        
        # Draw all bodies
        for body in bodies:
            self.draw_body(body)
            self.draw_velocity_vector(body)
            self.draw_acceleration_vector(body)
        
        # Draw UI text
        self.draw_info_text(bodies, physics_engine)
        if show_help:
            self.draw_help_text()
        
        # Update display
        pygame.display.flip()