"""
Main module for the 2D Gravity Simulator.
This is the entry point that initializes and runs the application.
"""

import pygame
import sys
import threading
import math
from physics_engine import PhysicsEngine
from renderer import Renderer
from ui_manager import UIManager
from celestial_body import CelestialBody
from constants import WINDOW_WIDTH, WINDOW_HEIGHT
from utils import generate_random_color

class GravitySimulator:
    """
    Main application class for the gravity simulator.
    Manages the overall application flow and event handling.
    """
    
    def __init__(self):
        """Initialize the gravity simulator."""
        # Initialize Pygame
        pygame.init()
        
        # Create display
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("2D Gravity Simulator")
        
        # Create clock for FPS control
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Initialize components
        self.physics_engine = PhysicsEngine()
        self.renderer = Renderer(self.screen, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.ui_manager = UIManager(self.physics_engine, self.renderer)
        
        # State variables
        self.running = True
        self.placing_body = False
        self.placement_start = None
        self.show_help = True
        
        # Create UI in separate thread
        self.ui_thread = threading.Thread(target=self.run_ui, daemon=True)
        self.ui_thread.start()
    
    def run_ui(self):
        """Run the UI manager in a separate thread."""
        self.ui_manager.create_panel()
        self.ui_manager.run()
    
    def handle_events(self):
        """Handle all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.handle_left_click(event.pos)
                elif event.button == 3:  # Right click
                    self.handle_right_click(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.placing_body:
                    self.finish_placing_body(event.pos)
            
            elif event.type == pygame.KEYDOWN:
                self.handle_key_press(event.key)
    
    def handle_left_click(self, pos):
        """
        Handle left mouse click.
        
        Args:
            pos (tuple): Mouse position (x, y)
        """
        # Check if clicking on existing body
        body = self.physics_engine.get_body_at_position(*pos)
        if body:
            self.ui_manager.select_body(body)
        else:
            # Start placing new body
            self.placing_body = True
            self.placement_start = pos
    
    def handle_right_click(self, pos):
        """
        Handle right mouse click.
        
        Args:
            pos (tuple): Mouse position (x, y)
        """
        # Delete body at position
        body = self.physics_engine.get_body_at_position(*pos)
        if body:
            self.physics_engine.remove_body(body)
            if self.ui_manager.selected_body == body:
                self.ui_manager.select_body(None)
    
    def finish_placing_body(self, end_pos):
        """
        Finish placing a new body with initial velocity.
        
        Args:
            end_pos (tuple): Mouse release position
        """
        if not self.placing_body or not self.placement_start:
            return
        
        # Calculate initial velocity from drag
        vx = (end_pos[0] - self.placement_start[0]) * 0.5
        vy = (end_pos[1] - self.placement_start[1]) * 0.5
        
        # Create new body
        body = CelestialBody(
            self.placement_start[0], 
            self.placement_start[1],
            mass=self.ui_manager.default_mass,
            radius=self.ui_manager.default_radius,
            density=self.ui_manager.default_density,
            velocity=(vx, vy),
            color=generate_random_color()
        )
        
        self.physics_engine.add_body(body)
        self.ui_manager.select_body(body)
        
        # Reset placement state
        self.placing_body = False
        self.placement_start = None
    
    def handle_key_press(self, key):
        """
        Handle keyboard input.
        
        Args:
            key: Pygame key constant
        """
        if key == pygame.K_SPACE:
            self.physics_engine.toggle_pause()
        
        elif key == pygame.K_c:
            self.physics_engine.clear_all_bodies()
            self.ui_manager.select_body(None)
        
        elif key == pygame.K_t:
            self.renderer.show_trails = not self.renderer.show_trails
        
        elif key == pygame.K_v:
            self.renderer.show_vectors = not self.renderer.show_vectors
        
        elif key == pygame.K_g:
            self.renderer.show_grid = not self.renderer.show_grid
        
        elif key == pygame.K_h:
            self.show_help = not self.show_help
        
        elif key == pygame.K_PLUS or key == pygame.K_EQUALS:
            current = self.physics_engine.time_scale
            self.physics_engine.set_time_scale(min(10.0, current + 0.5))
        
        elif key == pygame.K_MINUS:
            current = self.physics_engine.time_scale
            self.physics_engine.set_time_scale(max(0.1, current - 0.5))
        
        elif key == pygame.K_ESCAPE:
            self.running = False
    
    def draw_placement_preview(self):
        """Draw preview while placing a new body."""
        if not self.placing_body or not self.placement_start:
            return
        
        # Get current mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw body preview
        pygame.draw.circle(self.screen, (255, 255, 255), 
                         self.placement_start, 
                         self.ui_manager.default_radius, 2)
        
        # Draw velocity vector
        pygame.draw.line(self.screen, (0, 255, 0), 
                        self.placement_start, mouse_pos, 2)
        
        # Draw velocity text
        vx = (mouse_pos[0] - self.placement_start[0]) * 0.5
        vy = (mouse_pos[1] - self.placement_start[1]) * 0.5
        velocity = math.sqrt(vx*vx + vy*vy)
        
        font = pygame.font.Font(None, 24)
        text = font.render(f"v = {velocity:.1f} m/s", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.placement_start[0], 
                                         self.placement_start[1] - self.ui_manager.default_radius - 20))
        self.screen.blit(text, text_rect)
    
    def run(self):
        """Main application loop."""
        print("=" * 50)
        print("2D GRAVITY SIMULATOR")
        print("=" * 50)
        print("\nControls:")
        print("  Left Click + Drag: Place object with velocity")
        print("  Right Click: Delete object")
        print("  Space: Pause/Resume simulation")
        print("  C: Clear all objects")
        print("  T: Toggle trails")
        print("  V: Toggle velocity/acceleration vectors")
        print("  G: Toggle grid")
        print("  H: Toggle help text")
        print("  +/-: Adjust time scale")
        print("  ESC: Exit")
        print("\nUI Panel should open in a separate window.")
        print("=" * 50)
        
        while self.running:
            # Handle events
            self.handle_events()
            
            # Update physics
            self.physics_engine.update()
            
            # Update UI info
            self.ui_manager.update_info()
            
            # Render frame
            self.renderer.render(self.physics_engine.bodies, 
                                self.physics_engine, 
                                self.show_help)
            
            # Draw placement preview if placing
            self.draw_placement_preview()
            
            # Update display
            pygame.display.flip()
            
            # Control frame rate
            self.clock.tick(self.fps)
        
        # Cleanup
        self.ui_manager.destroy()
        pygame.quit()
        sys.exit()

def main():
    """Entry point for the application."""
    simulator = GravitySimulator()
    simulator.run()

if __name__ == "__main__":
    main()