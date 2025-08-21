# GravitySimulator
A rather simple 2D gravity simulator with interactable objects and variables.

# Features
 - Physics Properties:

   - Mass, Velocity, Size, Density - All interconnected with the relationship: Mass = Density × Volume
   - Gravitational Force - Calculated using Newton's law of universal gravitation
   - Acceleration - Derived from forces using F = ma
   - Property Locking - Lock any property to manually control it while others auto-calculate

 - Interactive UI:

   - Left Click + Drag - Place objects with initial velocity
   - Right Click - Delete objects
   - Property Panel - Edit all object properties in real-time
   - Color Picker - Change object and background colors with HEX input
   - Presets - Binary systems, solar system, galaxy collision, random bodies

- Visual Features:

   - 720p Resolution (1280×720)
   - Circular Objects with random initial colors
   - Object Trails - Visual paths showing movement
   - Velocity/Acceleration Vectors - Green and red arrows
   - Grid Overlay - For spatial reference
   - Black Background - Changeable via HEX color picker

# Requirement
 - Python
 - pygame (Install by running "pip install pygame" in bash)
