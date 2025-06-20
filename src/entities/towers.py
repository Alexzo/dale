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
            
        # Check if too close to castle
        castle_data = self.state_manager.castle_data
        castle_grid_x = int(castle_data['x'] // TILE_SIZE)
        castle_grid_y = int(castle_data['y'] // TILE_SIZE)
        
        castle_size_tiles = 2  # Castle takes 2x2 tiles
        if (abs(grid_x - castle_grid_x) <= castle_size_tiles and 
            abs(grid_y - castle_grid_y) <= castle_size_tiles):
            return False
            
        return True
        
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