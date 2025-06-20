"""
Projectile classes for arrows and other projectiles.
"""

import pygame
import math
from typing import List, Optional

from ..game.settings import *

class Projectile:
    """Base projectile class."""
    
    def __init__(self, x: float, y: float, dir_x: float, dir_y: float, damage: int, speed: float, sprite_manager):
        """Initialize projectile."""
        self.x = x
        self.y = y
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.damage = damage
        self.speed = speed
        self.sprite_manager = sprite_manager
        
        # Projectile properties
        self.size = 8
        self.lifetime = 5.0  # seconds (increased for better range)
        self.age = 0.0
        
        # Collision rect
        self.rect = pygame.Rect(int(x) - self.size//2, int(y) - self.size//2, self.size, self.size)
        
    def update(self, dt: float):
        """Update projectile position."""
        # Move projectile
        self.x += self.dir_x * self.speed * dt
        self.y += self.dir_y * self.speed * dt
        
        # Update age
        self.age += dt
        
        # Update collision rect
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
    def is_expired(self) -> bool:
        """Check if projectile should be removed."""
        return (self.age >= self.lifetime or 
                self.x < 0 or self.x > SCREEN_WIDTH or
                self.y < 0 or self.y > SCREEN_HEIGHT)
        
    def check_collision(self, targets: List) -> Optional[object]:
        """Check collision with a list of targets."""
        for target in targets:
            if hasattr(target, 'rect') and self.rect.colliderect(target.rect):
                return target
        return None
        
    def render(self, screen: pygame.Surface):
        """Render the projectile."""
        # Default rendering - should be overridden by subclasses
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.size//2)

class Arrow(Projectile):
    """Arrow projectile fired by arrow towers."""
    
    def __init__(self, x: float, y: float, dir_x: float, dir_y: float, damage: int, sprite_manager):
        """Initialize arrow."""
        super().__init__(x, y, dir_x, dir_y, damage, ARROW_SPEED, sprite_manager)
        
        self.size = ARROW_SIZE
        
        # Get arrow sprite
        self.sprite = sprite_manager.get_sprite('arrow')
        if not self.sprite:
            # Fallback sprite
            self.sprite = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(self.sprite, YELLOW, (self.size//2, self.size//2), self.size//2)
            
        # Calculate rotation angle for arrow direction
        self.angle = math.degrees(math.atan2(dir_y, dir_x))
        
    def render(self, screen: pygame.Surface):
        """Render the arrow with proper rotation."""
        # Rotate sprite based on direction
        rotated_sprite = pygame.transform.rotate(self.sprite, -self.angle)
        sprite_rect = rotated_sprite.get_rect()
        sprite_rect.centerx = int(self.x)
        sprite_rect.centery = int(self.y)
        screen.blit(rotated_sprite, sprite_rect)

class ProjectileManager:
    """Manages all projectiles in the game."""
    
    def __init__(self, sprite_manager):
        """Initialize projectile manager."""
        self.sprite_manager = sprite_manager
        
    def update(self, dt: float, projectiles: list):
        """Update all projectiles."""
        for projectile in projectiles[:]:  # Use slice copy for safe iteration
            projectile.update(dt)
            
            # Remove expired projectiles
            if projectile.is_expired():
                projectiles.remove(projectile)
        
    def create_arrow(self, x: float, y: float, target_x: float, target_y: float, damage: int) -> Arrow:
        """Create an arrow projectile aimed at a target."""
        # Calculate direction
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            dir_x = dx / distance
            dir_y = dy / distance
        else:
            dir_x = 1.0
            dir_y = 0.0
            
        return Arrow(x, y, dir_x, dir_y, damage, self.sprite_manager) 