"""
Sprite loading and management utilities.
"""

import pygame
import os
from typing import Dict, Optional

from ..game.settings import SPRITES_DIR

class SpriteManager:
    """Manages loading and caching of sprites."""
    
    def __init__(self):
        """Initialize the sprite manager."""
        self.sprites: Dict[str, pygame.Surface] = {}
        self.sprite_rects: Dict[str, pygame.Rect] = {}
        
        # Load default sprites (simple colored rectangles for now)
        self._create_default_sprites()
        
    def _create_default_sprites(self):
        """Create default sprites using simple colored rectangles."""
        from ..game.settings import (PLAYER_SIZE, ENEMY_SIZE, TOWER_SIZE, ALLY_SIZE, 
                                    ARROW_SIZE, WHITE, BLACK, BLUE, RED, GREEN, 
                                    BROWN, YELLOW, PURPLE)
        
        # Player sprite (elf warrior)
        player_sprite = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(player_sprite, BLUE, (PLAYER_SIZE//2, PLAYER_SIZE//2), PLAYER_SIZE//2)
        pygame.draw.circle(player_sprite, WHITE, (PLAYER_SIZE//2, PLAYER_SIZE//2), PLAYER_SIZE//2, 2)
        self.sprites['player'] = player_sprite
        
        # Enemy sprite
        enemy_sprite = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(enemy_sprite, RED, (ENEMY_SIZE//2, ENEMY_SIZE//2), ENEMY_SIZE//2)
        pygame.draw.circle(enemy_sprite, BLACK, (ENEMY_SIZE//2, ENEMY_SIZE//2), ENEMY_SIZE//2, 2)
        self.sprites['enemy'] = enemy_sprite
        
        # Tower sprite (arrow tower)
        tower_sprite = pygame.Surface((TOWER_SIZE, TOWER_SIZE), pygame.SRCALPHA)
        pygame.draw.rect(tower_sprite, BROWN, (0, 0, TOWER_SIZE, TOWER_SIZE))
        pygame.draw.rect(tower_sprite, BLACK, (0, 0, TOWER_SIZE, TOWER_SIZE), 2)
        # Add arrow symbol
        pygame.draw.polygon(tower_sprite, YELLOW, [
            (TOWER_SIZE//2, 8),
            (TOWER_SIZE//2 - 4, 16),
            (TOWER_SIZE//2 + 4, 16)
        ])
        self.sprites['arrow_tower'] = tower_sprite
        
        # Ally sprite (elf warrior)
        ally_sprite = pygame.Surface((ALLY_SIZE, ALLY_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(ally_sprite, GREEN, (ALLY_SIZE//2, ALLY_SIZE//2), ALLY_SIZE//2)
        pygame.draw.circle(ally_sprite, BLACK, (ALLY_SIZE//2, ALLY_SIZE//2), ALLY_SIZE//2, 2)
        self.sprites['ally'] = ally_sprite
        
        # Arrow projectile sprite
        arrow_sprite = pygame.Surface((ARROW_SIZE, ARROW_SIZE), pygame.SRCALPHA)
        pygame.draw.circle(arrow_sprite, YELLOW, (ARROW_SIZE//2, ARROW_SIZE//2), ARROW_SIZE//2)
        self.sprites['arrow'] = arrow_sprite
        
        # Essence orb sprite
        essence_sprite = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(essence_sprite, PURPLE, (6, 6), 6)
        pygame.draw.circle(essence_sprite, WHITE, (6, 6), 6, 1)
        self.sprites['essence'] = essence_sprite
        
    def get_sprite(self, name: str) -> Optional[pygame.Surface]:
        """Get a sprite by name."""
        return self.sprites.get(name)
        
    def load_sprite(self, name: str, filepath: str) -> bool:
        """Load a sprite from file."""
        try:
            if os.path.exists(filepath):
                sprite = pygame.image.load(filepath).convert_alpha()
                self.sprites[name] = sprite
                self.sprite_rects[name] = sprite.get_rect()
                return True
        except pygame.error as e:
            print(f"Could not load sprite {name} from {filepath}: {e}")
        return False
        
    def get_sprite_rect(self, name: str) -> Optional[pygame.Rect]:
        """Get the rect for a sprite."""
        return self.sprite_rects.get(name)
        
    def scale_sprite(self, name: str, new_size: tuple) -> bool:
        """Scale a sprite to new size."""
        if name in self.sprites:
            original = self.sprites[name]
            scaled = pygame.transform.scale(original, new_size)
            self.sprites[f"{name}_scaled"] = scaled
            self.sprite_rects[f"{name}_scaled"] = scaled.get_rect()
            return True
        return False 