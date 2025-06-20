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
    
    def __init__(self, x: float, y: float, sprite_manager):
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
        """Set the target position (usually the castle)."""
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
        """Move towards the target position."""
        # Calculate direction to target
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
        
        # Spawn points (edges of the screen)
        self.spawn_points = [
            (0, SCREEN_HEIGHT // 2),  # Left edge
            (SCREEN_WIDTH, SCREEN_HEIGHT // 2),  # Right edge
            (SCREEN_WIDTH // 2, 0),  # Top edge
            (SCREEN_WIDTH // 2, SCREEN_HEIGHT - HUD_HEIGHT)  # Bottom edge
        ]
        
    def spawn_wave(self, enemy_count: int):
        """Spawn a wave of enemies."""
        enemies = self.state_manager.entities['enemies']
        
        for i in range(enemy_count):
            # Choose random spawn point
            spawn_x, spawn_y = random.choice(self.spawn_points)
            
            # Add some random offset
            spawn_x += random.randint(-50, 50)
            spawn_y += random.randint(-50, 50)
            
            # Keep within bounds
            spawn_x = max(0, min(SCREEN_WIDTH, spawn_x))
            spawn_y = max(0, min(SCREEN_HEIGHT - HUD_HEIGHT, spawn_y))
            
            # Create enemy
            enemy = Enemy(spawn_x, spawn_y, self.sprite_manager)
            
            # Set target to castle
            castle_data = self.state_manager.castle_data
            enemy.set_target(castle_data['x'], castle_data['y'])
            
            enemies.append(enemy)
            
    def update(self, dt: float, castle_data: Dict[str, Any]):
        """Update all enemies."""
        enemies = self.state_manager.entities['enemies']
        
        for enemy in enemies[:]:  # Use slice copy for safe iteration
            enemy.update(dt)
            
            # Check if enemy reached the castle
            if enemy.is_at_target():
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