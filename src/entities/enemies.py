"""
Enemy classes and enemy management.
"""

import pygame
import math
import random
from typing import List, Dict, Any

from ..game.settings import *
from ..game.constants import *
from .projectiles import EnemyArrow

class Enemy:
    """Base enemy class."""
    
    def __init__(self, x: float, y: float, sprite_manager, path_route=None, 
                 health=30, speed=50, size=24, damage=10, enemy_type="enemy"):
        """Initialize enemy."""
        self.x = x
        self.y = y
        self.sprite_manager = sprite_manager
        self.enemy_type = enemy_type
        
        # Enemy stats (now customizable)
        self.max_health = health
        self.health = self.max_health
        self.speed = speed
        self.size = size
        self.damage = damage
        
        # Movement
        self.target_x = 0.0
        self.target_y = 0.0
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        
        # Waypoint system - use assigned route or default to center route
        self.current_waypoint = 0
        if path_route is not None:
            self.path = path_route.copy()
            self.route_index = ENEMY_PATHS.index(path_route) if path_route in ENEMY_PATHS else 0
        else:
            self.path = ENEMY_PATH.copy()  # Default to center route
            self.route_index = 0
        
        # Sprite (try enemy type specific first, then generic)
        self.sprite = sprite_manager.get_sprite(self.enemy_type)
        if not self.sprite:
            self.sprite = sprite_manager.get_sprite('enemy')
        if not self.sprite:
            # Fallback sprite - use default red
            self.sprite = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(self.sprite, RED, (self.size//2, self.size//2), self.size//2)
            
        # Collision rect
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        
        # Combat and AI state
        self.attack_cooldown = 0.0
        self.attack_rate = ENEMY_ATTACK_RATE
        self.attack_range = ENEMY_ATTACK_RANGE
        self.ai_state = ENEMY_STATE_MOVING
        self.current_target = None  # Current tower or castle being attacked
        self.has_reached_castle = False
        
    def set_target(self, target_x: float, target_y: float):
        """Set the target position (first waypoint)."""
        # Start with the first waypoint instead of direct castle targeting
        if self.path and len(self.path) > 0:
            self.target_x = self.path[0][0]
            self.target_y = self.path[0][1]
        else:
            # Fallback to direct targeting if no path
            self.target_x = target_x
            self.target_y = target_y
        
    def update(self, dt: float, towers=None, castle_data=None):
        """Update enemy state with new combat AI."""
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            
        # AI behavior based on current state
        projectile = None
        if self.ai_state == ENEMY_STATE_MOVING:
            self._update_moving_state(dt, towers, castle_data)
        elif self.ai_state == ENEMY_STATE_ATTACKING_TOWER:
            projectile = self._update_attacking_tower_state(dt)
        elif self.ai_state == ENEMY_STATE_ATTACKING_CASTLE:
            self._update_attacking_castle_state(dt, castle_data)
        
        # Update collision rect
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
        return projectile  # Return any projectile created
            
    def _move_towards_target(self, dt: float):
        """Move towards the current waypoint."""
        # Calculate direction to current target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Check if we've reached the current waypoint
        if distance < 20:  # Waypoint reached threshold
            self._advance_to_next_waypoint()
            # Recalculate direction to new target
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Normalize direction and apply speed
            self.velocity_x = (dx / distance) * self.speed
            self.velocity_y = (dy / distance) * self.speed
            
            # Update position
            self.x += self.velocity_x * dt
            self.y += self.velocity_y * dt
            
    def _advance_to_next_waypoint(self):
        """Move to the next waypoint in the path."""
        self.current_waypoint += 1
        if self.current_waypoint < len(self.path):
            # Set next waypoint as target
            self.target_x = self.path[self.current_waypoint][0]
            self.target_y = self.path[self.current_waypoint][1]
        # If we've reached the end of the path, keep the last target (castle)
        
    def _update_moving_state(self, dt: float, towers=None, castle_data=None):
        """Update enemy when in moving state - check for towers to attack and move towards castle."""
        # Check if near castle (reached final destination)
        if castle_data:
            castle_distance = math.sqrt((self.x - castle_data['x'])**2 + (self.y - castle_data['y'])**2)
            if castle_distance <= ENEMY_CASTLE_SIEGE_DISTANCE:
                self.ai_state = ENEMY_STATE_ATTACKING_CASTLE
                self.has_reached_castle = True
                return
        
        # Check for towers in range while moving
        if towers:
            nearest_tower = self._find_nearest_tower_in_range(towers)
            if nearest_tower:
                self.current_target = nearest_tower
                self.ai_state = ENEMY_STATE_ATTACKING_TOWER
                return
        
        # Continue moving towards target
        self._move_towards_target(dt)
        
    def _update_attacking_tower_state(self, dt: float):
        """Update enemy when attacking a tower - continue moving while shooting."""
        if not self.current_target or not self.current_target.is_alive():
            # Tower destroyed or no longer valid, resume moving
            self.ai_state = ENEMY_STATE_MOVING
            self.current_target = None
            return
            
        # Check if tower is still in range (use detection range to avoid rapid state switching)
        tower_distance = math.sqrt((self.x - self.current_target.x)**2 + (self.y - self.current_target.y)**2)
        if tower_distance > ENEMY_TOWER_DETECTION_RANGE:  # Use detection range, not attack range
            # Tower out of range, resume moving
            self.ai_state = ENEMY_STATE_MOVING
            self.current_target = None
            return
            
        # Continue moving towards castle while attacking tower
        # Don't move towards the tower - keep moving towards next waypoint
        self._move_towards_target(dt)
        
        # Attack the tower (return arrow for projectile manager to handle)
        if self.can_attack():
            return self._shoot_at_target(self.current_target)
        return None
            
    def _update_attacking_castle_state(self, dt: float, castle_data=None):
        """Update enemy when attacking the castle."""
        if not castle_data or castle_data['health'] <= 0:
            return
            
        # Stay at castle and keep attacking
        if self.can_attack():
            self._attack_castle_melee(castle_data)
            
    def _find_nearest_tower_in_range(self, towers):
        """Find the nearest tower within detection range."""
        nearest_tower = None
        nearest_distance = float('inf')
        
        for tower in towers:
            if not tower.is_alive():
                continue
                
            distance = math.sqrt((self.x - tower.x)**2 + (self.y - tower.y)**2)
            
            if distance <= ENEMY_TOWER_DETECTION_RANGE and distance < nearest_distance:
                nearest_tower = tower
                nearest_distance = distance
                
        return nearest_tower
        
    def _shoot_at_target(self, target):
        """Shoot an arrow at a target (tower or castle)."""
        if not self.can_attack():
            return None
            
        # Calculate direction to target
        dx = target.x - self.x
        dy = target.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0 and distance <= ENEMY_ATTACK_RANGE:  # Only shoot if within attack range
            dir_x = dx / distance
            dir_y = dy / distance
            
            # Create enemy arrow
            arrow = EnemyArrow(
                self.x, self.y,
                dir_x, dir_y,
                ENEMY_PROJECTILE_DAMAGE,
                self.sprite_manager
            )
            
            self.attack_cooldown = 1.0 / self.attack_rate
            return arrow
            
        return None
        
    def _attack_castle_melee(self, castle_data):
        """Attack castle with melee damage."""
        if self.can_attack():
            # Apply damage directly to castle
            castle_data['health'] -= self.damage
            castle_data['health'] = max(0, castle_data['health'])
            self.attack_cooldown = 1.0 / self.attack_rate
            
    def can_attack(self) -> bool:
        """Check if enemy can attack."""
        return self.attack_cooldown <= 0
        
    def attack(self, target) -> bool:
        """Attack a target."""
        if self.can_attack():
            target.take_damage(self.damage)
            self.attack_cooldown = 1.0 / self.attack_rate
            return True
        return False
        
    def take_damage(self, damage: int):
        """Take damage."""
        self.health -= damage
        self.health = max(0, self.health)
        
    def is_alive(self) -> bool:
        """Check if enemy is alive."""
        return self.health > 0
        
    def get_distance_to_target(self) -> float:
        """Get distance to target."""
        return math.sqrt((self.x - self.target_x)**2 + (self.y - self.target_y)**2)
        
    def is_at_target(self, threshold: float = 32.0) -> bool:
        """Check if enemy has reached the target."""
        return self.get_distance_to_target() <= threshold
        
    def has_reached_castle_position(self) -> bool:
        """Check if enemy has reached the castle and is attacking it."""
        return self.has_reached_castle and self.ai_state == ENEMY_STATE_ATTACKING_CASTLE
        
    def render(self, screen: pygame.Surface):
        """Render the enemy."""
        # Draw enemy sprite
        sprite_rect = self.sprite.get_rect()
        sprite_rect.centerx = int(self.x)
        sprite_rect.centery = int(self.y)
        screen.blit(self.sprite, sprite_rect)
        
        # Draw health bar
        self._draw_health_bar(screen)
        
    def _draw_health_bar(self, screen: pygame.Surface):
        """Draw enemy health bar."""
        bar_width = 24
        bar_height = 4
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.size//2 - 8
        
        # Background
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        
        # Health
        health_width = int((self.health / self.max_health) * bar_width)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))

class Orc(Enemy):
    """Orc enemy - basic enemy type."""
    
    def __init__(self, x: float, y: float, sprite_manager, path_route=None):
        """Initialize Orc with Orc-specific stats."""
        super().__init__(
            x, y, sprite_manager, path_route,
            health=ORC_HEALTH,
            speed=ORC_SPEED,
            size=ORC_SIZE,
            damage=ORC_DAMAGE,
            enemy_type="orc"
        )
        
        # Create Orc-specific fallback sprite if none found
        if not self.sprite or self.sprite == sprite_manager.get_sprite('enemy'):
            self.sprite = self._create_orc_sprite()
            
    def _create_orc_sprite(self) -> pygame.Surface:
        """Create Orc-specific sprite."""
        sprite = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        # Draw Orc as dark green circle with simple features
        pygame.draw.circle(sprite, ORC_COLOR, (self.size//2, self.size//2), self.size//2)
        pygame.draw.circle(sprite, BLACK, (self.size//2, self.size//2), self.size//2, 2)
        
        # Add simple orc features (tusks)
        tusk_size = self.size // 8
        pygame.draw.rect(sprite, WHITE, (self.size//2 - 4, self.size//2 + 2, 2, tusk_size))
        pygame.draw.rect(sprite, WHITE, (self.size//2 + 2, self.size//2 + 2, 2, tusk_size))
        
        return sprite

class UrukHai(Enemy):
    """Uruk Hai enemy - advanced enemy type with superior stats."""
    
    def __init__(self, x: float, y: float, sprite_manager, path_route=None):
        """Initialize Uruk Hai with enhanced stats."""
        super().__init__(
            x, y, sprite_manager, path_route,
            health=URUK_HAI_HEALTH,
            speed=URUK_HAI_SPEED,
            size=URUK_HAI_SIZE,
            damage=URUK_HAI_DAMAGE,
            enemy_type="uruk_hai"
        )
        
        # Create Uruk Hai-specific fallback sprite if none found
        if not self.sprite or self.sprite == sprite_manager.get_sprite('enemy'):
            self.sprite = self._create_uruk_hai_sprite()
            
    def _create_uruk_hai_sprite(self) -> pygame.Surface:
        """Create Uruk Hai-specific sprite."""
        sprite = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        # Draw Uruk Hai as dark gray/black circle with armor details
        pygame.draw.circle(sprite, URUK_HAI_COLOR, (self.size//2, self.size//2), self.size//2)
        pygame.draw.circle(sprite, BLACK, (self.size//2, self.size//2), self.size//2, 2)
        
        # Add armor plating (metallic look)
        armor_color = (80, 80, 80)
        pygame.draw.arc(sprite, armor_color, 
                       (self.size//4, self.size//4, self.size//2, self.size//2), 
                       0, 3.14, 3)
        
        # Add larger tusks/fangs
        tusk_size = self.size // 6
        pygame.draw.rect(sprite, WHITE, (self.size//2 - 5, self.size//2 + 1, 3, tusk_size))
        pygame.draw.rect(sprite, WHITE, (self.size//2 + 2, self.size//2 + 1, 3, tusk_size))
        
        # Red eyes for intimidation
        pygame.draw.circle(sprite, RED, (self.size//2 - 3, self.size//2 - 4), 2)
        pygame.draw.circle(sprite, RED, (self.size//2 + 3, self.size//2 - 4), 2)
        
        return sprite

class EnemyManager:
    """Manages enemy spawning and behavior."""
    
    def __init__(self, sprite_manager, state_manager):
        """Initialize enemy manager."""
        self.sprite_manager = sprite_manager
        self.state_manager = state_manager
        
        # Spawn points for each route (starting point of each path)
        self.spawn_points = [path[0] for path in ENEMY_PATHS] if ENEMY_PATHS else [(50, 100)]
        
    def spawn_wave(self, enemy_count: int):
        """Spawn a wave of enemies using multiple routes and enemy types."""
        enemies = self.state_manager.entities['enemies']
        current_wave = self.state_manager.game_data['current_wave']
        
        orc_count = 0
        uruk_hai_count = 0
        
        for i in range(enemy_count):
            # Randomly select a route for this enemy
            route_index = random.randint(0, len(ENEMY_PATHS) - 1)
            selected_path = ENEMY_PATHS[route_index]
            spawn_point = self.spawn_points[route_index]
            
            # Use the selected path's starting point
            spawn_x, spawn_y = spawn_point
            
            # Add small random offset to prevent enemies from overlapping
            spawn_x += random.randint(-30, 30)
            spawn_y += random.randint(-30, 30)
            
            # Keep within bounds
            spawn_x = max(0, min(SCREEN_WIDTH, spawn_x))
            spawn_y = max(0, min(SCREEN_HEIGHT - HUD_HEIGHT, spawn_y))
            
            # Determine enemy type based on wave and ratios
            enemy = self._create_enemy_by_type(spawn_x, spawn_y, selected_path, current_wave)
            
            if isinstance(enemy, Orc):
                orc_count += 1
            elif isinstance(enemy, UrukHai):
                uruk_hai_count += 1
            
            # Initialize waypoint system (enemy will start moving to first waypoint)
            castle_data = self.state_manager.castle_data
            enemy.set_target(castle_data['x'], castle_data['y'])  # This sets up the waypoint system
            
            enemies.append(enemy)
            
        # Print spawn summary
        enemy_types = []
        if orc_count > 0:
            enemy_types.append(f"{orc_count} Orcs")
        if uruk_hai_count > 0:
            enemy_types.append(f"{uruk_hai_count} Uruk Hai")
            
        enemy_summary = " and ".join(enemy_types)
        print(f"🏹 Wave {current_wave}: Spawned {enemy_summary} across {len(ENEMY_PATHS)} routes!")
        
    def _create_enemy_by_type(self, spawn_x: float, spawn_y: float, selected_path, current_wave: int):
        """Create an enemy of the appropriate type based on wave progression."""
        # Before wave 3, only spawn Orcs
        if current_wave < URUK_HAI_START_WAVE:
            return Orc(spawn_x, spawn_y, self.sprite_manager, selected_path)
        
        # From wave 3 onwards, use spawn ratios
        if random.random() < ORC_SPAWN_RATIO:
            return Orc(spawn_x, spawn_y, self.sprite_manager, selected_path)
        else:
            return UrukHai(spawn_x, spawn_y, self.sprite_manager, selected_path)
        
    def update(self, dt: float, castle_data: Dict[str, Any]):
        """Update all enemies with new combat system."""
        enemies = self.state_manager.entities['enemies']
        towers = self.state_manager.entities['towers']
        projectiles = self.state_manager.entities['projectiles']
        
        for enemy in enemies[:]:  # Use slice copy for safe iteration
            # Update enemy with towers and castle data for combat AI
            projectile = enemy.update(dt, towers, castle_data)
            
            # Add any projectile created by the enemy
            if projectile:
                projectiles.append(projectile)
            
            # Remove dead enemies (handled by game engine)
            if not enemy.is_alive():
                enemies.remove(enemy)
                
        # Handle enemy projectile collisions with towers
        self._handle_enemy_projectile_collisions(projectiles, towers)
        
    def _handle_enemy_projectile_collisions(self, projectiles, towers):
        """Handle collisions between enemy projectiles and towers."""
        for projectile in projectiles[:]:  # Use slice copy for safe iteration
            # Only handle enemy arrows
            if not isinstance(projectile, EnemyArrow):
                continue
                
            # Check collision with towers
            hit_tower = projectile.check_collision(towers)
            if (hit_tower and 
                hasattr(hit_tower, 'is_alive') and hasattr(hit_tower, 'take_damage') and 
                hasattr(hit_tower, 'health') and getattr(hit_tower, 'is_alive')()):
                # Damage the tower
                getattr(hit_tower, 'take_damage')(projectile.damage)
                projectiles.remove(projectile)
                
                # Show tower was hit
                remaining_health = getattr(hit_tower, 'health')
                if remaining_health <= 0:
                    print(f"💥 Tower destroyed by enemy fire!")
                else:
                    print(f"🎯 Tower hit! Health: {remaining_health}/{getattr(hit_tower, 'max_health', 100)}") 