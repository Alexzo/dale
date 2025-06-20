"""
Ally classes for elvish warriors and ally management.
"""

import pygame
import math
import random
from typing import List, Optional

from ..game.settings import *

class ElfWarrior:
    """Elvish warrior ally that fights enemies automatically."""
    
    def __init__(self, x: float, y: float, sprite_manager):
        """Initialize elf warrior."""
        self.x = x
        self.y = y
        self.sprite_manager = sprite_manager
        
        # Ally stats
        self.max_health = ALLY_HEALTH
        self.health = self.max_health
        self.speed = ALLY_SPEED
        self.size = ALLY_SIZE
        self.damage = ALLY_DAMAGE
        self.attack_range = ALLY_ATTACK_RANGE
        
        # Combat state
        self.target = None
        self.attack_cooldown = 0.0
        self.attack_rate = 1.5  # attacks per second
        
        # Movement
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        
        # Sprite
        self.sprite = sprite_manager.get_sprite('ally')
        if not self.sprite:
            # Fallback sprite
            self.sprite = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(self.sprite, GREEN, (self.size//2, self.size//2), self.size//2)
            
        # Collision rect
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        
        # AI behavior
        self.idle_timer = 0.0
        self.wander_direction_x = random.uniform(-1, 1)
        self.wander_direction_y = random.uniform(-1, 1)
        
    def find_target(self, enemies: List) -> Optional[object]:
        """Find the closest enemy within attack range."""
        closest_enemy = None
        closest_distance = float('inf')
        
        for enemy in enemies:
            distance = self.get_distance_to(enemy.x, enemy.y)
            if distance <= self.attack_range and distance < closest_distance:
                closest_enemy = enemy
                closest_distance = distance
                
        return closest_enemy
        
    def can_attack(self) -> bool:
        """Check if ally can attack."""
        return self.attack_cooldown <= 0
        
    def attack(self, target) -> bool:
        """Attack a target."""
        if self.can_attack() and target:
            target.take_damage(self.damage)
            self.attack_cooldown = 1.0 / self.attack_rate
            return True
        return False
        
    def update(self, dt: float):
        """Update ally state."""
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            
        # Update idle timer
        self.idle_timer += dt
        
        # Basic AI behavior
        if self.target:
            self._move_towards_target(dt)
        else:
            self._wander(dt)
            
        # Update position
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Keep within screen bounds
        self.x = max(self.size//2, min(SCREEN_WIDTH - self.size//2, self.x))
        self.y = max(self.size//2, min(SCREEN_HEIGHT - HUD_HEIGHT - self.size//2, self.y))
        
        # Update collision rect
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
    def _move_towards_target(self, dt: float):
        """Move towards the current target."""
        if not self.target:
            return
            
        # Calculate direction to target
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > self.attack_range * 0.8:  # Move closer if not in optimal range
            # Normalize direction and apply speed
            if distance > 0:
                self.velocity_x = (dx / distance) * self.speed
                self.velocity_y = (dy / distance) * self.speed
        else:
            # Stop moving when in attack range
            self.velocity_x = 0
            self.velocity_y = 0
            
    def _wander(self, dt: float):
        """Wander around when no target is found."""
        # Change direction every few seconds
        if self.idle_timer >= 3.0:
            self.wander_direction_x = random.uniform(-1, 1)
            self.wander_direction_y = random.uniform(-1, 1)
            self.idle_timer = 0.0
            
        # Move slowly in wander direction
        wander_speed = self.speed * 0.3
        self.velocity_x = self.wander_direction_x * wander_speed
        self.velocity_y = self.wander_direction_y * wander_speed
        
    def get_distance_to(self, x: float, y: float) -> float:
        """Get distance to a point."""
        return math.sqrt((self.x - x)**2 + (self.y - y)**2)
        
    def take_damage(self, damage: int):
        """Take damage."""
        self.health -= damage
        self.health = max(0, self.health)
        
    def is_alive(self) -> bool:
        """Check if ally is alive."""
        return self.health > 0
        
    def render(self, screen: pygame.Surface):
        """Render the ally."""
        # Draw ally sprite
        sprite_rect = self.sprite.get_rect()
        sprite_rect.centerx = int(self.x)
        sprite_rect.centery = int(self.y)
        screen.blit(self.sprite, sprite_rect)
        
        # Draw health bar
        self._draw_health_bar(screen)
        
        # Draw attack range when debugging
        if False:  # Set to True for debugging
            pygame.draw.circle(screen, (0, 255, 0, 50), (int(self.x), int(self.y)), int(self.attack_range), 1)
            
    def _draw_health_bar(self, screen: pygame.Surface):
        """Draw ally health bar."""
        bar_width = 28
        bar_height = 4
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.size//2 - 8
        
        # Background
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        
        # Health
        health_width = int((self.health / self.max_health) * bar_width)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 1)

class AllyManager:
    """Manages ally summoning and behavior."""
    
    def __init__(self, sprite_manager, state_manager):
        """Initialize ally manager."""
        self.sprite_manager = sprite_manager
        self.state_manager = state_manager
        
    def spawn_ally_near_player(self, player_x: float, player_y: float):
        """Spawn an ally near the player."""
        # Find a good spawn position near the player
        spawn_attempts = 10
        for _ in range(spawn_attempts):
            # Random position in a circle around the player
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(40, 80)
            
            spawn_x = player_x + math.cos(angle) * distance
            spawn_y = player_y + math.sin(angle) * distance
            
            # Keep within bounds
            spawn_x = max(ALLY_SIZE//2, min(SCREEN_WIDTH - ALLY_SIZE//2, spawn_x))
            spawn_y = max(ALLY_SIZE//2, min(SCREEN_HEIGHT - HUD_HEIGHT - ALLY_SIZE//2, spawn_y))
            
            # Create ally
            ally = ElfWarrior(spawn_x, spawn_y, self.sprite_manager)
            self.state_manager.entities['allies'].append(ally)
            break
            
    def update(self, dt: float):
        """Update all allies."""
        allies = self.state_manager.entities['allies']
        enemies = self.state_manager.entities['enemies']
        
        for ally in allies[:]:  # Use slice copy for safe iteration
            # Find target
            ally.target = ally.find_target(enemies)
            
            # Update ally
            ally.update(dt)
            
            # Attack target if possible
            if ally.target and ally.can_attack():
                distance_to_target = ally.get_distance_to(ally.target.x, ally.target.y)
                if distance_to_target <= ally.attack_range:
                    ally.attack(ally.target)
                    
            # Remove dead allies
            if not ally.is_alive():
                allies.remove(ally) 