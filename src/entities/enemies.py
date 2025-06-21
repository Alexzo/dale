"""
Enemy classes and enemy management.
"""

import pygame
import math
import random
from typing import List, Dict, Any

from ..game.settings import *

class Enemy:
    """Base enemy class."""
    
    def __init__(self, x: float, y: float, sprite_manager, path_route=None):
        """Initialize enemy."""
        self.x = x
        self.y = y
        self.sprite_manager = sprite_manager
        
        # Enemy stats
        self.max_health = ENEMY_HEALTH
        self.health = self.max_health
        self.speed = ENEMY_SPEED
        self.size = ENEMY_SIZE
        self.damage = ENEMY_DAMAGE
        
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
        
        # Sprite
        self.sprite = sprite_manager.get_sprite('enemy')
        if not self.sprite:
            # Fallback sprite
            self.sprite = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(self.sprite, RED, (self.size//2, self.size//2), self.size//2)
            
        # Collision rect
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        
        # AI state
        self.attack_cooldown = 0.0
        self.attack_rate = 1.0  # attacks per second
        
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
        
    def update(self, dt: float):
        """Update enemy state."""
        # Move towards target
        self._move_towards_target(dt)
        
        # Update collision rect
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            
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
        
    def has_completed_path(self, threshold: float = 32.0) -> bool:
        """Check if enemy has completed the entire path and reached the castle."""
        # Only return True if we've gone through all waypoints and reached the final position
        return (self.current_waypoint >= len(self.path) - 1 and 
                self.get_distance_to_target() <= threshold)
        
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

class EnemyManager:
    """Manages enemy spawning and behavior."""
    
    def __init__(self, sprite_manager, state_manager):
        """Initialize enemy manager."""
        self.sprite_manager = sprite_manager
        self.state_manager = state_manager
        
        # Spawn points for each route (starting point of each path)
        self.spawn_points = [path[0] for path in ENEMY_PATHS] if ENEMY_PATHS else [(50, 100)]
        
    def spawn_wave(self, enemy_count: int):
        """Spawn a wave of enemies using multiple routes."""
        enemies = self.state_manager.entities['enemies']
        
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
            
            # Create enemy with the selected route
            enemy = Enemy(spawn_x, spawn_y, self.sprite_manager, selected_path)
            
            # Initialize waypoint system (enemy will start moving to first waypoint)
            castle_data = self.state_manager.castle_data
            enemy.set_target(castle_data['x'], castle_data['y'])  # This sets up the waypoint system
            
            enemies.append(enemy)
            
        print(f"🏹 Spawned {enemy_count} enemies across {len(ENEMY_PATHS)} different routes!")
        
    def update(self, dt: float, castle_data: Dict[str, Any]):
        """Update all enemies."""
        enemies = self.state_manager.entities['enemies']
        
        for enemy in enemies[:]:  # Use slice copy for safe iteration
            enemy.update(dt)
            
            # Check if enemy has completed the entire path and reached the castle
            if enemy.has_completed_path():
                # Attack castle
                if enemy.can_attack():
                    # Create a simple castle-like object for the attack
                    class CastleTarget:
                        def __init__(self, state_manager):
                            self.state_manager = state_manager
                        def take_damage(self, damage):
                            self.state_manager.damage_castle(damage)
                    
                    castle_target = CastleTarget(self.state_manager)
                    enemy.attack(castle_target)
                    
                # Remove enemy after attacking
                enemies.remove(enemy)
                
            # Remove dead enemies (handled by game engine)
            elif not enemy.is_alive():
                enemies.remove(enemy) 