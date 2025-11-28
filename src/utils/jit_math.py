import math
from numba import jit

@jit(nopython=True)
def distance_sq(x1, y1, x2, y2):
    """Calculate squared distance between two points."""
    dx = x1 - x2
    dy = y1 - y2
    return dx*dx + dy*dy

@jit(nopython=True)
def distance(x1, y1, x2, y2):
    """Calculate distance between two points."""
    return math.sqrt(distance_sq(x1, y1, x2, y2))

@jit(nopython=True)
def calculate_separation_force_fast(x1, y1, x2, y2, r1, r2, strength):
    """
    Calculate separation force vector components.
    Returns (force_x, force_y)
    """
    dist_sq = distance_sq(x1, y1, x2, y2)
    min_dist = r1 + r2
    
    # Avoid division by zero and unnecessary calculations
    if dist_sq < 0.0001 or dist_sq >= min_dist * min_dist:
        return 0.0, 0.0
        
    dist = math.sqrt(dist_sq)
    
    # Normalized direction vector (x1-x2, y1-y2) / dist
    dir_x = (x1 - x2) / dist
    dir_y = (y1 - y2) / dist
    
    # Force magnitude
    overlap = min_dist - dist
    force_mag = (overlap / min_dist) * strength
    
    return dir_x * force_mag, dir_y * force_mag

@jit(nopython=True)
def clamp_value(val, min_val, max_val):
    """Clamp a value between min and max."""
    if val < min_val:
        return min_val
    if val > max_val:
        return max_val
    return val
