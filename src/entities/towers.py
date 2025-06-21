"""
Tower classes and tower management.
"""

import pygame
import math
from typing import List, Optional

from ..game.settings import *
from .projectiles import Arrow

class ArrowTower:
    """Arrow tower that shoots arrows at enemies."""
    
    def __init__(self, grid_x: int, grid_y: int, sprite_manager):
        """Initialize arrow tower."""
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = grid_x * TILE_SIZE + TILE_SIZE // 2
        self.y = grid_y * TILE_SIZE + TILE_SIZE // 2
        self.sprite_manager = sprite_manager
        
        # Tower stats
        self.damage = ARROW_TOWER_DAMAGE
        self.range = ARROW_TOWER_RANGE
        self.fire_rate = ARROW_TOWER_FIRE_RATE
        self.size = TOWER_SIZE
        
        # Firing state
        self.last_fire_time = 0.0
        self.target = None
        
        # Sprite
        self.sprite = sprite_manager.get_sprite('arrow_tower')
        if not self.sprite:
            # Fallback sprite
            self.sprite = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.rect(self.sprite, BROWN, (0, 0, self.size, self.size))
            pygame.draw.rect(self.sprite, BLACK, (0, 0, self.size, self.size), 2)
            
        # Collision rect
        self.rect = pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)
        
    def find_target(self, enemies: List) -> Optional[object]:
        """Find the closest enemy within range."""
        closest_enemy = None
        closest_distance = float('inf')
        
        for enemy in enemies:
            distance = self.get_distance_to(enemy.x, enemy.y)
            if distance <= self.range and distance < closest_distance:
                closest_enemy = enemy
                closest_distance = distance
                
        return closest_enemy
        
    def can_fire(self) -> bool:
        """Check if tower can fire."""
        import time
        current_time = time.time()
        return (current_time - self.last_fire_time) >= (1.0 / self.fire_rate)
        
    def fire_at(self, target) -> Optional['Arrow']:
        """Fire an arrow at the target."""
        if self.can_fire() and target:
            import time
            self.last_fire_time = time.time()
            
            # Calculate direction to target
            dx = target.x - self.x
            dy = target.y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                # Create arrow projectile
                arrow = Arrow(
                    self.x, self.y,
                    dx / distance, dy / distance,
                    self.damage,
                    self.sprite_manager
                )
                return arrow
                
        return None
        
    def get_distance_to(self, x: float, y: float) -> float:
        """Get distance to a point."""
        return math.sqrt((self.x - x)**2 + (self.y - y)**2)
        
    def update(self, dt: float):
        """Update tower state."""
        # Arrow towers don't need much updating
        pass
        
    def render(self, screen: pygame.Surface):
        """Render the tower."""
        # Draw tower sprite
        sprite_rect = self.sprite.get_rect()
        sprite_rect.centerx = self.x
        sprite_rect.centery = self.y
        screen.blit(self.sprite, sprite_rect)
        
        # Draw range indicator when debugging
        if False:  # Set to True for debugging
            pygame.draw.circle(screen, (255, 255, 255, 50), (int(self.x), int(self.y)), int(self.range), 1)

class TowerManager:
    """Manages tower building and updates."""
    
    def __init__(self, sprite_manager, state_manager):
        """Initialize tower manager."""
        self.sprite_manager = sprite_manager
        self.state_manager = state_manager
        
        # Track occupied grid positions
        self.occupied_positions = set()
        
    def try_build_tower(self, grid_x: int, grid_y: int) -> bool:
        """Try to build a tower at the specified grid position."""
        # Check if position is valid
        if not self._is_valid_position(grid_x, grid_y):
            return False
            
        # Check if position is already occupied
        if (grid_x, grid_y) in self.occupied_positions:
            return False
            
        # Check if player has enough essence
        if not self.state_manager.spend_essence(ARROW_TOWER_COST):
            return False
            
        # Build the tower
        tower = ArrowTower(grid_x, grid_y, self.sprite_manager)
        self.state_manager.entities['towers'].append(tower)
        self.occupied_positions.add((grid_x, grid_y))
        
        return True
        
    def _is_valid_position(self, grid_x: int, grid_y: int) -> bool:
        """Check if the grid position is valid for building."""
        # Check bounds
        if grid_x < 0 or grid_x >= GRID_WIDTH:
            return False
        if grid_y < 0 or grid_y >= (GRID_HEIGHT - HUD_HEIGHT // TILE_SIZE):
            return False
            
        # Convert tower position to world coordinates
        tower_x = grid_x * TILE_SIZE + TILE_SIZE // 2
        tower_y = grid_y * TILE_SIZE + TILE_SIZE // 2
        
        # Check if too close to enemy path
        if self._is_too_close_to_path(tower_x, tower_y):
            return False
            
        # Check if too close to castle (updated for new castle size)
        castle_data = self.state_manager.castle_data
        castle_left = castle_data['x'] - CASTLE_WIDTH//2
        castle_right = castle_data['x'] + CASTLE_WIDTH//2
        castle_top = castle_data['y'] - CASTLE_HEIGHT//2
        castle_bottom = castle_data['y'] + CASTLE_HEIGHT//2
        
        # Add buffer zone around castle
        buffer = TILE_SIZE * 2  # 2 tile buffer
        if (tower_x >= castle_left - buffer and tower_x <= castle_right + buffer and
            tower_y >= castle_top - buffer and tower_y <= castle_bottom + buffer):
            return False
            
        return True
        
    def _is_too_close_to_path(self, tower_x: float, tower_y: float) -> bool:
        """Check if tower position is too close to the enemy path."""
        # Define minimum distance from path (path width + tower size + buffer)
        min_distance = PATH_WIDTH // 2 + TOWER_SIZE // 2 + 10  # 10 pixel buffer
        
        # Check distance to each path segment
        for i in range(len(ENEMY_PATH) - 1):
            start_point = ENEMY_PATH[i]
            end_point = ENEMY_PATH[i + 1]
            
            # Calculate distance from tower position to this path segment
            distance = self._point_to_line_segment_distance(
                tower_x, tower_y,
                start_point[0], start_point[1],
                end_point[0], end_point[1]
            )
            
            if distance < min_distance:
                return True  # Too close to path
                
        return False  # Safe distance from all path segments
        
    def _point_to_line_segment_distance(self, px: float, py: float, 
                                      x1: float, y1: float, x2: float, y2: float) -> float:
        """Calculate the shortest distance from a point to a line segment."""
        # Vector from start to end of line segment
        dx = x2 - x1
        dy = y2 - y1
        
        # If the segment has zero length, return distance to start point
        if dx == 0 and dy == 0:
            return math.sqrt((px - x1)**2 + (py - y1)**2)
        
        # Calculate parameter t that represents position along the line segment
        # t = 0 means start point, t = 1 means end point
        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
        
        # Clamp t to [0, 1] to stay within the line segment
        t = max(0, min(1, t))
        
        # Find the closest point on the line segment
        closest_x = x1 + t * dx
        closest_y = y1 + t * dy
        
        # Return distance from point to closest point on segment
        return math.sqrt((px - closest_x)**2 + (py - closest_y)**2)
        
    def update(self, dt: float):
        """Update all towers."""
        towers = self.state_manager.entities['towers']
        
        for tower in towers:
            tower.update(dt)
            
    def remove_tower(self, tower):
        """Remove a tower."""
        towers = self.state_manager.entities['towers']
        if tower in towers:
            towers.remove(tower)
            self.occupied_positions.discard((tower.grid_x, tower.grid_y)) 