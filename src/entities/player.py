"""
Player character class.
"""

import pygame
import math

from ..game.settings import *

class Player:
    """Player character that can move around the battlefield."""
    
    def __init__(self, x: float, y: float, sprite_manager):
        """Initialize the player."""
        self.x = x
        self.y = y
        self.sprite_manager = sprite_manager
        
        # Player stats
        self.max_health = PLAYER_HEALTH
        self.health = self.max_health
        self.speed = PLAYER_SPEED
        self.size = PLAYER_SIZE
        
        # Movement
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        
        # Sprite
        self.sprite = sprite_manager.get_sprite('player')
        if not self.sprite:
            # Fallback sprite
            self.sprite = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(self.sprite, BLUE, (self.size//2, self.size//2), self.size//2)
            
        # Collision rect
        self.rect = pygame.Rect(x - self.size//2, y - self.size//2, self.size, self.size)
        
    def handle_input(self, keys, dt: float):
        """Handle player input for movement."""
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        
        # Check movement keys
        if any(keys[key] for key in KEY_UP):
            self.velocity_y = -self.speed
        if any(keys[key] for key in KEY_DOWN):
            self.velocity_y = self.speed
        if any(keys[key] for key in KEY_LEFT):
            self.velocity_x = -self.speed
        if any(keys[key] for key in KEY_RIGHT):
            self.velocity_x = self.speed
            
        # Normalize diagonal movement
        if self.velocity_x != 0 and self.velocity_y != 0:
            length = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
            self.velocity_x = (self.velocity_x / length) * self.speed
            self.velocity_y = (self.velocity_y / length) * self.speed
            
    def update(self, dt: float):
        """Update player position and state."""
        # Update position
        self.x += self.velocity_x * dt
        self.y += self.velocity_y * dt
        
        # Keep player within screen bounds
        self.x = max(self.size//2, min(SCREEN_WIDTH - self.size//2, self.x))
        self.y = max(self.size//2, min(SCREEN_HEIGHT - HUD_HEIGHT - self.size//2, self.y))
        
        # Update collision rect
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)
        
    def render(self, screen: pygame.Surface):
        """Render the player."""
        # Draw player sprite
        sprite_rect = self.sprite.get_rect()
        sprite_rect.centerx = int(self.x)
        sprite_rect.centery = int(self.y)
        screen.blit(self.sprite, sprite_rect)
        
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