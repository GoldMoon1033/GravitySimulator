"""
Constants module for the gravity simulator.
Contains all global constants and configuration values.
"""

# Window dimensions (720p)
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

# Physics constants
G = 6.67430e-11  # Gravitational constant (scaled for simulation)
SIMULATION_SCALE = 1e9  # Scale factor for better visualization
TIME_STEP = 0.016  # 60 FPS equivalent
MAX_FORCE = 1e10  # Maximum force to prevent instabilities

# UI constants
PANEL_WIDTH = 300
PANEL_HEIGHT = WINDOW_HEIGHT

# Default values
DEFAULT_MASS = 1e24  # kg (Earth-like mass scaled)
DEFAULT_RADIUS = 20  # pixels
DEFAULT_DENSITY = 5515  # kg/m³ (Earth-like)
DEFAULT_VELOCITY = (0, 0)  # m/s

# Colors
DEFAULT_BG_COLOR = "#000000"  # Black
DEFAULT_BODY_COLOR = "#FFFFFF"  # White

# Limits
MIN_MASS = 1e20
MAX_MASS = 1e30
MIN_RADIUS = 5
MAX_RADIUS = 100
MIN_DENSITY = 100
MAX_DENSITY = 20000