"""
Utility module containing helper functions for the simulator.
"""

import random
import math
import re

def hex_to_rgb(hex_color):
    """
    Convert hex color string to RGB tuple.
    
    Args:
        hex_color (str): Hex color string (e.g., "#FF0000")
    
    Returns:
        tuple: RGB values (r, g, b)
    """
    # Remove '#' if present
    hex_color = hex_color.lstrip('#')
    
    # Validate hex color
    if not re.match(r'^[0-9A-Fa-f]{6}$', hex_color):
        return (255, 255, 255)  # Return white if invalid
    
    # Convert to RGB
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    """
    Convert RGB tuple to hex color string.
    
    Args:
        rgb (tuple): RGB values (r, g, b)
    
    Returns:
        str: Hex color string
    """
    return '#{:02x}{:02x}{:02x}'.format(int(rgb[0]), int(rgb[1]), int(rgb[2]))

def generate_random_color():
    """
    Generate a random bright color.
    
    Returns:
        tuple: RGB color tuple
    """
    # Generate bright colors by ensuring at least one component is high
    r = random.randint(100, 255)
    g = random.randint(100, 255)
    b = random.randint(100, 255)
    return (r, g, b)

def calculate_distance(pos1, pos2):
    """
    Calculate Euclidean distance between two positions.
    
    Args:
        pos1 (tuple): First position (x, y)
        pos2 (tuple): Second position (x, y)
    
    Returns:
        float: Distance between positions
    """
    dx = pos2[0] - pos1[0]
    dy = pos2[1] - pos1[1]
    return math.sqrt(dx*dx + dy*dy)

def normalize_vector(vector):
    """
    Normalize a 2D vector.
    
    Args:
        vector (tuple): 2D vector (x, y)
    
    Returns:
        tuple: Normalized vector
    """
    magnitude = math.sqrt(vector[0]**2 + vector[1]**2)
    if magnitude == 0:
        return (0, 0)
    return (vector[0]/magnitude, vector[1]/magnitude)
