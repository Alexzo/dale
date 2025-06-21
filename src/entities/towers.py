"""
Tower classes and tower management.
"""

import pygame
import math
from typing import List, Optional

from ..game.settings import *
from ..game.constants import *
from .projectiles import Arrow

class ArrowTower:
    """Arrow tower that shoots arrows at enemies."""
    
    def __init__(self, grid_x: int, grid_y: int, sprite_manager, level: int = TOWER_STARTING_LEVEL):
        """Initialize arrow tower."""
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.x = grid_x * TILE_SIZE + TILE_SIZE // 2
        self.y = grid_y * TILE_SIZE + TILE_SIZE // 2
        self.sprite_manager = sprite_manager
        
        # Tower level and upgrade system
        self.level = level
        self.max_health = self._calculate_health()
        self.health = self.max_health
        
        # Tower stats (calculated based on level)
        self.damage = self._calculate_damage()
        self.range = TOWER_BASE_RANGE  # Range doesn't change with level
        self.fire_rate = self._calculate_fire_rate()
        self.size = TOWER_SIZE
        
        # Firing state
        self.last_fire_time = 0.0
        self.target = None
        
        # Sprite (color changes with level)
        self.sprite = self._create_level_sprite()
            
        # Collision rect
        self.rect = pygame.Rect(self.x - self.size//2, self.y - self.size//2, self.size, self.size)
        
    def _calculate_health(self) -> int:
        """Calculate tower health based on level."""
        return TOWER_BASE_HEALTH + (self.level - 1) * TOWER_HEALTH_PER_LEVEL
        
    def _calculate_damage(self) -> int:
        """Calculate tower damage based on level."""
        return TOWER_BASE_DAMAGE + (self.level - 1) * TOWER_DAMAGE_BONUS_PER_LEVEL
        
    def _calculate_fire_rate(self) -> float:
        """Calculate tower fire rate based on level."""
        # Fire rate increases every 2 levels
        speed_bonus_levels = (self.level - 1) // 2
        return TOWER_BASE_ATTACK_SPEED + speed_bonus_levels * TOWER_ATTACK_SPEED_BONUS_EVERY_2_LEVELS
        
    def _create_level_sprite(self) -> pygame.Surface:
        """Create tower sprite with level-appropriate color."""
        # Try to get base sprite first
        base_sprite = self.sprite_manager.get_sprite('arrow_tower')
        
        if base_sprite:
            # Tint the sprite based on level
            level_color = TOWER_LEVEL_COLORS.get(self.level, TOWER_LEVEL_COLORS[1])
            sprite = base_sprite.copy()
            
            # Create a colored overlay
            color_overlay = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
            color_overlay.fill((*level_color, 100))  # Semi-transparent color
            sprite.blit(color_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
            
            return sprite
        else:
            # Fallback sprite with level color
            sprite = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            level_color = TOWER_LEVEL_COLORS.get(self.level, TOWER_LEVEL_COLORS[1])
            
            pygame.draw.rect(sprite, level_color, (0, 0, self.size, self.size))
            pygame.draw.rect(sprite, BLACK, (0, 0, self.size, self.size), 2)
            
            # Add level indicator and arrow symbol
            pygame.draw.polygon(sprite, YELLOW, [
                (self.size//2, 8),
                (self.size//2 - 4, 16),
                (self.size//2 + 4, 16)
            ])
            
            return sprite
            
    def can_upgrade(self) -> bool:
        """Check if tower can be upgraded."""
        return self.level < TOWER_MAX_LEVEL
        
    def get_upgrade_cost(self) -> int:
        """Get the essence cost to upgrade to next level."""
        if not self.can_upgrade():
            return 0
        return TOWER_UPGRADE_COSTS.get(self.level + 1, 0)
        
    def upgrade(self) -> bool:
        """Upgrade the tower to the next level."""
        if not self.can_upgrade():
            return False
            
        self.level += 1
        
        # Update stats
        old_max_health = self.max_health
        self.max_health = self._calculate_health()
        self.health += (self.max_health - old_max_health)  # Heal by health increase amount
        self.damage = self._calculate_damage()
        self.fire_rate = self._calculate_fire_rate()
        
        # Update sprite appearance
        self.sprite = self._create_level_sprite()
        
        print(f"🔧 Tower upgraded to level {self.level}! Damage: {self.damage}, Health: {self.health}, Fire Rate: {self.fire_rate:.1f}")
        return True
        
    def take_damage(self, damage: int):
        """Tower takes damage (for future enemy mechanics)."""
        self.health -= damage
        self.health = max(0, self.health)
        
    def is_alive(self) -> bool:
        """Check if tower is still functional."""
        return self.health > 0
        
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
        
        # Track tower built for stats
        self.state_manager.game_data['towers_built'] += 1
        self.state_manager.add_score(10)  # Bonus points for building
        
        return True
        
    def try_upgrade_tower(self, tower: ArrowTower) -> bool:
        """Try to upgrade a tower."""
        if not tower.can_upgrade():
            return False
            
        upgrade_cost = tower.get_upgrade_cost()
        if not self.state_manager.spend_essence(upgrade_cost):
            return False
            
        # Upgrade the tower
        success = tower.upgrade()
        if success:
            self.state_manager.add_score(15)  # Bonus points for upgrading
            
        return success
        
    def get_tower_at_position(self, grid_x: int, grid_y: int) -> Optional[ArrowTower]:
        """Get the tower at a specific grid position."""
        for tower in self.state_manager.entities['towers']:
            if tower.grid_x == grid_x and tower.grid_y == grid_y:
                return tower
        return None
        
    def get_tower_near_position(self, x: float, y: float, max_distance: float = 32) -> Optional[ArrowTower]:
        """Get the tower near a world position."""
        for tower in self.state_manager.entities['towers']:
            distance = math.sqrt((tower.x - x)**2 + (tower.y - y)**2)
            if distance <= max_distance:
                return tower
        return None
        
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
        """Check if tower position is too close to any enemy path."""
        # Define minimum distance from path (path width + tower size + buffer)
        min_distance = PATH_WIDTH // 2 + TOWER_SIZE // 2 + 10  # 10 pixel buffer
        
        # Check distance to each path segment for all enemy paths
        for enemy_path in ENEMY_PATHS:
            for i in range(len(enemy_path) - 1):
                start_point = enemy_path[i]
                end_point = enemy_path[i + 1]
                
                # Calculate distance from tower position to this path segment
                distance = self._point_to_line_segment_distance(
                    tower_x, tower_y,
                    start_point[0], start_point[1],
                    end_point[0], end_point[1]
                )
                
                if distance < min_distance:
                    return True  # Too close to any path
                    
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