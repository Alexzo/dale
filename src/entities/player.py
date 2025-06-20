"""
Player character class with animation and melee combat support.
"""

import pygame
import math
import time
from typing import Optional

from ..game.settings import *

class Player:
    """Player character that can move around the battlefield and attack enemies."""
    
    def __init__(self, x: float, y: float, sprite_manager, health: Optional[int] = None, attack_damage: Optional[int] = None):
        """Initialize the player."""
        self.x = x
        self.y = y
        self.sprite_manager = sprite_manager
        
        # Player stats (use provided values or defaults)
        self.max_health = health if health is not None else PLAYER_HEALTH
        self.health = self.max_health
        self.speed = PLAYER_SPEED
        self.size = PLAYER_SIZE
        
        # Combat stats (use provided values or defaults)
        self.attack_damage = attack_damage if attack_damage is not None else PLAYER_ATTACK_DAMAGE
        self.attack_range = PLAYER_ATTACK_RANGE
        self.attack_rate = PLAYER_ATTACK_RATE
        self.knockback_force = PLAYER_ATTACK_KNOCKBACK
        
        # Movement
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.is_moving = False
        self.facing_direction = "down"  # Track which direction player is facing
        
        # Combat state
        self.is_attacking = False
        self.attack_cooldown = 0.0
        self.last_attack_time = 0.0
        self.attack_duration = 0.3  # Duration of attack animation in seconds
        self.attack_timer = 0.0
        
        # Animation
        self.animation_manager = sprite_manager.get_animation('player')
        
        # Sprite (fallback if no animation)
        self.sprite = sprite_manager.get_sprite('player')
        if not self.sprite:
            # Fallback sprite
            self.sprite = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(self.sprite, BLUE, (self.size//2, self.size//2), self.size//2)
            
        # Collision rect
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        
    def handle_input(self, keys, dt: float):
        """Handle player input for movement and combat."""
        # Handle movement input
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        
        # Store previous direction to detect changes
        prev_direction = self.facing_direction
        
        # Check movement keys (can't move while attacking)
        if not self.is_attacking:
            if any(keys[key] for key in KEY_UP):
                self.velocity_y = -self.speed
                self.facing_direction = "up"
            elif any(keys[key] for key in KEY_DOWN):
                self.velocity_y = self.speed
                self.facing_direction = "down"
            
            if any(keys[key] for key in KEY_LEFT):
                self.velocity_x = -self.speed
                self.facing_direction = "left"
            elif any(keys[key] for key in KEY_RIGHT):
                self.velocity_x = self.speed
                self.facing_direction = "right"
                
            # Handle diagonal movement - prioritize most recent input
            if self.velocity_x != 0 and self.velocity_y != 0:
                # Normalize diagonal movement
                length = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
                self.velocity_x = (self.velocity_x / length) * self.speed
                self.velocity_y = (self.velocity_y / length) * self.speed
                
                # For diagonal movement, choose primary direction based on stronger input
                if abs(self.velocity_x) > abs(self.velocity_y):
                    self.facing_direction = "right" if self.velocity_x > 0 else "left"
                else:
                    self.facing_direction = "up" if self.velocity_y < 0 else "down"
        
        # Update movement state for animation
        self.is_moving = (self.velocity_x != 0 or self.velocity_y != 0)
        
        # Handle attack input
        if any(keys[key] for key in KEY_ATTACK) and self.can_attack():
            self.start_attack()
            
    def update(self, dt: float):
        """Update player position and state."""
        # Update attack state
        self._update_attack(dt)
        
        # Update position (only if not attacking)
        if not self.is_attacking:
            self.x += self.velocity_x * dt
            self.y += self.velocity_y * dt
        
        # Keep player within screen bounds
        self.x = max(self.size//2, min(SCREEN_WIDTH - self.size//2, self.x))
        self.y = max(self.size//2, min(SCREEN_HEIGHT - HUD_HEIGHT - self.size//2, self.y))
        
        # Update collision rect
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
        # Update animation
        self._update_animation(dt)
        
    def _update_attack(self, dt: float):
        """Update attack state and timing."""
        # Update attack cooldown
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
            
        # Update attack duration
        if self.is_attacking:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.is_attacking = False
                
    def can_attack(self) -> bool:
        """Check if player can attack."""
        return self.attack_cooldown <= 0 and not self.is_attacking
        
    def start_attack(self):
        """Start an attack."""
        if self.can_attack():
            self.is_attacking = True
            self.attack_timer = self.attack_duration
            self.attack_cooldown = 1.0 / self.attack_rate
            self.last_attack_time = time.time()
            
            # Reset attack animation to start from beginning
            if self.animation_manager and hasattr(self.animation_manager, 'set_direction'):
                # Reset the attack animation for the current direction
                attack_anim = self.animation_manager.get_animation('attack', self.facing_direction)
                if attack_anim:
                    attack_anim.reset()  # Reset to first frame
            
    def get_attack_area(self) -> pygame.Rect:
        """Get the area where the attack can hit enemies."""
        # Create attack area in front of player
        attack_rect = pygame.Rect(
            self.x - self.attack_range,
            self.y - self.attack_range,
            self.attack_range * 2,
            self.attack_range * 2
        )
        return attack_rect
        
    def attack_enemies(self, enemies: list) -> list:
        """Attack enemies in range and return list of hit enemies."""
        if not self.is_attacking:
            return []
            
        hit_enemies = []
        attack_area = self.get_attack_area()
        
        for enemy in enemies:
            # Check if enemy is in attack range
            distance = self.get_distance_to(enemy.x, enemy.y)
            if distance <= self.attack_range:
                # Deal damage
                enemy.take_damage(self.attack_damage)
                hit_enemies.append(enemy)
                
                # Apply knockback
                if distance > 0:
                    knockback_x = (enemy.x - self.x) / distance * self.knockback_force
                    knockback_y = (enemy.y - self.y) / distance * self.knockback_force
                    enemy.x += knockback_x
                    enemy.y += knockback_y
                    
        return hit_enemies
        
    def _update_animation(self, dt: float):
        """Update character animation based on movement and combat state."""
        if self.animation_manager:
            # Check if we have a directional animation manager
            if hasattr(self.animation_manager, 'set_direction'):
                # Directional animation manager
                if self.is_attacking:
                    self.animation_manager.set_animation('attack', self.facing_direction)
                elif self.is_moving:
                    self.animation_manager.set_animation('walk', self.facing_direction)
                else:
                    self.animation_manager.set_animation('idle', self.facing_direction)
            else:
                # Regular animation manager (fallback)
                if self.is_attacking:
                    if hasattr(self.animation_manager, 'set_animation'):
                        self.animation_manager.set_animation('attack')
                    else:
                        self.animation_manager.set_animation('idle')
                elif self.is_moving:
                    self.animation_manager.set_animation('walk')
                else:
                    self.animation_manager.set_animation('idle')
                    
            # Update animation timing
            self.animation_manager.update(dt)
        
    def render(self, screen: pygame.Surface):
        """Render the player."""
        # Get current sprite (animated or static)
        current_sprite = self.sprite
        
        if self.animation_manager:
            animated_frame = self.animation_manager.get_current_frame()
            if animated_frame:
                current_sprite = animated_frame
        
        # Draw player sprite
        sprite_rect = current_sprite.get_rect()
        sprite_rect.centerx = int(self.x)
        sprite_rect.centery = int(self.y)
        screen.blit(current_sprite, sprite_rect)
        
        # Draw health bar
        self._draw_health_bar(screen)
        
    def _draw_health_bar(self, screen: pygame.Surface):
        """Draw player health bar."""
        bar_width = 40
        bar_height = 6
        bar_x = self.x - bar_width // 2
        bar_y = self.y - self.size//2 - 10
        
        # Background
        pygame.draw.rect(screen, RED, (bar_x, bar_y, bar_width, bar_height))
        
        # Health
        health_width = int((self.health / self.max_health) * bar_width)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, health_width, bar_height))
        
        # Border
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 1)
        
    def take_damage(self, damage: int):
        """Take damage."""
        self.health -= damage
        self.health = max(0, self.health)
        
    def heal(self, amount: int):
        """Heal the player."""
        self.health += amount
        self.health = min(self.max_health, self.health)
        
    def is_alive(self) -> bool:
        """Check if player is alive."""
        return self.health > 0
        
    def get_distance_to(self, x: float, y: float) -> float:
        """Get distance to a point."""
        return math.sqrt((self.x - x)**2 + (self.y - y)**2)
        
    def collides_with(self, other_rect: pygame.Rect) -> bool:
        """Check collision with another rect."""
        return self.rect.colliderect(other_rect) 