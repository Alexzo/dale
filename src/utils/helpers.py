"""
Helper utility functions for the game.
"""

import math
import random
from typing import Tuple, List

def distance(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate distance between two points."""
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

def normalize_vector(x: float, y: float) -> Tuple[float, float]:
    """Normalize a 2D vector."""
    length = math.sqrt(x**2 + y**2)
    if length > 0:
        return x / length, y / length
    return 0.0, 0.0

def angle_between_points(x1: float, y1: float, x2: float, y2: float) -> float:
    """Calculate angle between two points in radians."""
    return math.atan2(y2 - y1, x2 - x1)

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, value))

def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolation between two values."""
    return a + (b - a) * t

def random_point_in_circle(center_x: float, center_y: float, radius: float) -> Tuple[float, float]:
    """Generate a random point within a circle."""
    angle = random.uniform(0, 2 * math.pi)
    r = random.uniform(0, radius)
    x = center_x + r * math.cos(angle)
    y = center_y + r * math.sin(angle)
    return x, y

def point_in_rectangle(x: float, y: float, rect_x: float, rect_y: float, rect_width: float, rect_height: float) -> bool:
    """Check if a point is inside a rectangle."""
    return rect_x <= x <= rect_x + rect_width and rect_y <= y <= rect_y + rect_height

def circles_collide(x1: float, y1: float, r1: float, x2: float, y2: float, r2: float) -> bool:
    """Check if two circles collide."""
    return distance(x1, y1, x2, y2) <= (r1 + r2)

def format_time(seconds: float) -> str:
    """Format seconds into MM:SS format."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02d}:{seconds:02d}"

def format_number(number: int) -> str:
    """Format large numbers with commas."""
    return f"{number:,}" 