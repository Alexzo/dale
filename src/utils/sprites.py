"""
Sprite loading and management utilities.
"""

import pygame
import os
from typing import Dict, Optional, List, Union

from ..game.settings import SPRITES_DIR
from .animations import Animation, AnimationManager, DirectionalAnimationManager, SpriteSheetLoader

class SpriteManager:
    """Manages loading and caching of sprites and animations."""
    
    def __init__(self):
        """Initialize the sprite manager."""
        self.sprites: Dict[str, pygame.Surface] = {}
        self.sprite_rects: Dict[str, pygame.Rect] = {}
        self.animations: Dict[str, Union[AnimationManager, DirectionalAnimationManager]] = {}
        
        # Load pixel art sprites and animations
        self._load_pixel_art_sprites()
        self._load_animations()
        self._create_default_sprites()
        
    def _load_pixel_art_sprites(self):
        """Load pixel art sprites from files."""
        from ..game.settings import (PLAYER_SIZE, ENEMY_SIZE, TOWER_SIZE, ALLY_SIZE, ARROW_SIZE)
        
        # Define sprite file mapping
        sprite_files = {
            'player': 'player/elf_warrior.png',
            'ally': 'allies/elf_warrior.png',
            'enemy_orc': 'enemies/orc.png',
            'enemy_goblin': 'enemies/goblin.png',
            'arrow_tower': 'towers/arrow_tower.png',
            'castle': 'ui/castle.png',
            'arrow': 'projectiles/arrow.png',
            'essence': 'ui/essence_orb.png'
        }
        
        # Load sprites with proper scaling
        for sprite_name, file_path in sprite_files.items():
            full_path = os.path.join(SPRITES_DIR, file_path)
            if self.load_sprite_with_scaling(sprite_name, full_path):
                print(f"✅ Loaded pixel art: {sprite_name}")
            else:
                print(f"⚠️  Could not load {sprite_name}, will use default")
                
    def _load_animations(self):
        """Load character animations."""
        player_animations = self._create_player_animations()
        if player_animations:
            self.animations['player'] = player_animations
            print("✅ Loaded player animations")
        else:
            print("⚠️  Could not load player animations, will use static sprite")
            
    def _create_player_animations(self) -> Optional[DirectionalAnimationManager]:
        """Create directional animations for the player character."""
        from ..game.settings import PLAYER_SIZE
        
        anim_manager = DirectionalAnimationManager()
        player_sprite_path = os.path.join(SPRITES_DIR, 'player')
        
        # Try to load from spritesheet first
        spritesheet_path = os.path.join(player_sprite_path, 'elf_warrior_spritesheet.png')
        if os.path.exists(spritesheet_path):
            # Load from spritesheet (assuming 4 frames of idle, 4 frames of walk)
            all_frames = SpriteSheetLoader.load_spritesheet(spritesheet_path, 64, 64, 8)
            if len(all_frames) >= 8:
                # Scale frames to game size
                scaled_frames = [pygame.transform.scale(frame, (PLAYER_SIZE, PLAYER_SIZE)) for frame in all_frames]
                
                # Create directional animations from base frames
                idle_frames = scaled_frames[0:4]  # First 4 frames for idle
                walk_frames = scaled_frames[4:8]  # Next 4 frames for walking
                
                self._create_directional_animations(anim_manager, idle_frames, walk_frames)
                return anim_manager
        
        # Try to load individual frame files
        idle_frames = self._load_animation_frames(player_sprite_path, 'idle', PLAYER_SIZE)
        walk_frames = self._load_animation_frames(player_sprite_path, 'walk', PLAYER_SIZE)
        
        if idle_frames or walk_frames:
            # Use loaded frames or fallback to single frame
            if not idle_frames and walk_frames:
                idle_frames = [walk_frames[0]]  # Use first walk frame for idle
            elif not walk_frames and idle_frames:
                walk_frames = idle_frames  # Use idle frames for walking
            
            self._create_directional_animations(anim_manager, idle_frames, walk_frames)
            return anim_manager
            
        # Fallback: create simple animation from single sprite
        single_sprite_path = os.path.join(player_sprite_path, 'elf_warrior.png')
        if os.path.exists(single_sprite_path):
            try:
                sprite = pygame.image.load(single_sprite_path).convert_alpha()
                scaled_sprite = pygame.transform.scale(sprite, (PLAYER_SIZE, PLAYER_SIZE))
                
                # Create directional animations from single frame
                self._create_directional_animations(anim_manager, [scaled_sprite], [scaled_sprite])
                return anim_manager
            except pygame.error as e:
                print(f"Error loading single sprite: {e}")
                
        return None
        
    def _create_directional_animations(self, anim_manager: DirectionalAnimationManager, 
                                     idle_frames: List[pygame.Surface], 
                                     walk_frames: List[pygame.Surface]):
        """Create directional animations from base frames or load directional frames."""
        if not idle_frames or not walk_frames:
            return
            
        player_sprite_path = os.path.join(SPRITES_DIR, 'player')
        
        # Try to load directional frames first
        directional_frames_loaded = self._load_directional_frames(anim_manager, player_sprite_path)
        
        if directional_frames_loaded:
            print("✅ Loaded directional animation frames from files")
            return
            
        # Fallback: create directional variations from base frames
        print("🔄 Creating directional animations from base frames")
        
        # Base frames (facing down/forward)
        idle_down = Animation(idle_frames, 0.3, True)
        walk_down = Animation(walk_frames, 0.15, True)
        
        # Create directional variations
        # Down (original)
        anim_manager.add_directional_animation('idle', 'down', idle_down)
        anim_manager.add_directional_animation('walk', 'down', walk_down)
        
        # Up (flip vertically)
        idle_up_frames = [pygame.transform.flip(frame, False, True) for frame in idle_frames]
        walk_up_frames = [pygame.transform.flip(frame, False, True) for frame in walk_frames]
        anim_manager.add_directional_animation('idle', 'up', Animation(idle_up_frames, 0.3, True))
        anim_manager.add_directional_animation('walk', 'up', Animation(walk_up_frames, 0.15, True))
        
        # Left (flip horizontally)
        idle_left_frames = [pygame.transform.flip(frame, True, False) for frame in idle_frames]
        walk_left_frames = [pygame.transform.flip(frame, True, False) for frame in walk_frames]
        anim_manager.add_directional_animation('idle', 'left', Animation(idle_left_frames, 0.3, True))
        anim_manager.add_directional_animation('walk', 'left', Animation(walk_left_frames, 0.15, True))
        
        # Right (original - assuming sprite naturally faces right, or flip if needed)
        anim_manager.add_directional_animation('idle', 'right', idle_down)  # Use down as right
        anim_manager.add_directional_animation('walk', 'right', walk_down)  # Use down as right
        
    def _load_directional_frames(self, anim_manager: DirectionalAnimationManager, sprite_path: str) -> bool:
        """Load directional animation frames from files if they exist."""
        from ..game.settings import PLAYER_SIZE
        
        animation_types = ['idle', 'walk']
        directions = ['up', 'down', 'left', 'right']
        loaded_any = False
        
        for anim_type in animation_types:
            for direction in directions:
                # Try to load frames for this animation and direction
                frames = []
                for i in range(1, 5):  # Try to load 4 frames
                    frame_path = os.path.join(sprite_path, f"{anim_type}_{direction}_{i}.png")
                    if os.path.exists(frame_path):
                        try:
                            frame = pygame.image.load(frame_path).convert_alpha()
                            scaled_frame = pygame.transform.scale(frame, (PLAYER_SIZE, PLAYER_SIZE))
                            frames.append(scaled_frame)
                        except pygame.error as e:
                            print(f"Error loading {frame_path}: {e}")
                            break
                    else:
                        break  # If one frame is missing, don't use this direction
                
                # If we loaded all 4 frames for this direction, add the animation
                if len(frames) == 4:
                    frame_duration = 0.3 if anim_type == 'idle' else 0.15
                    animation = Animation(frames, frame_duration, True)
                    anim_manager.add_directional_animation(anim_type, direction, animation)
                    loaded_any = True
        
        return loaded_any
        
    def _load_animation_frames(self, folder_path: str, animation_name: str, target_size: int) -> List[pygame.Surface]:
        """Load animation frames from individual files."""
        frames = SpriteSheetLoader.load_frame_sequence(folder_path, animation_name)
        if frames:
            # Scale frames to target size
            return [pygame.transform.scale(frame, (target_size, target_size)) for frame in frames]
        return []
        
    def load_sprite_with_scaling(self, name: str, filepath: str) -> bool:
        """Load a sprite from file and scale it appropriately."""
        try:
            if os.path.exists(filepath):
                original_sprite = pygame.image.load(filepath).convert_alpha()
                target_size = self._get_target_size_for_sprite(name)
                scaled_sprite = pygame.transform.scale(original_sprite, target_size)
                
                self.sprites[f"{name}_original"] = original_sprite
                self.sprites[name] = scaled_sprite
                self.sprite_rects[name] = scaled_sprite.get_rect()
                return True
        except pygame.error as e:
            print(f"Could not load sprite {name} from {filepath}: {e}")
        return False
    
    def _get_target_size_for_sprite(self, sprite_name: str) -> tuple:
        """Get the appropriate size for different sprite types."""
        from ..game.settings import (PLAYER_SIZE, ENEMY_SIZE, TOWER_SIZE, ALLY_SIZE, ARROW_SIZE)
        
        size_mapping = {
            'player': (PLAYER_SIZE, PLAYER_SIZE),
            'ally': (ALLY_SIZE, ALLY_SIZE),
            'enemy_orc': (ENEMY_SIZE, ENEMY_SIZE),
            'enemy_goblin': (ENEMY_SIZE, ENEMY_SIZE),
            'enemy': (ENEMY_SIZE, ENEMY_SIZE),
            'arrow_tower': (TOWER_SIZE, TOWER_SIZE),
            'castle': (64, 64),
            'arrow': (ARROW_SIZE, ARROW_SIZE),
            'essence': (12, 12)
        }
        
        return size_mapping.get(sprite_name, (32, 32))
        
    def _create_default_sprites(self):
        """Create default sprites using simple colored rectangles (fallbacks)."""
        from ..game.settings import (PLAYER_SIZE, ENEMY_SIZE, TOWER_SIZE, ALLY_SIZE, 
                                    ARROW_SIZE, WHITE, BLACK, BLUE, RED, GREEN, 
                                    BROWN, YELLOW, PURPLE)
        
        # Only create defaults for sprites that weren't loaded from files
        if 'player' not in self.sprites:
            player_sprite = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(player_sprite, BLUE, (PLAYER_SIZE//2, PLAYER_SIZE//2), PLAYER_SIZE//2)
            pygame.draw.circle(player_sprite, WHITE, (PLAYER_SIZE//2, PLAYER_SIZE//2), PLAYER_SIZE//2, 2)
            self.sprites['player'] = player_sprite
            print("🔄 Using default player sprite")
        
        if 'enemy' not in self.sprites:
            enemy_sprite = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(enemy_sprite, RED, (ENEMY_SIZE//2, ENEMY_SIZE//2), ENEMY_SIZE//2)
            pygame.draw.circle(enemy_sprite, BLACK, (ENEMY_SIZE//2, ENEMY_SIZE//2), ENEMY_SIZE//2, 2)
            self.sprites['enemy'] = enemy_sprite
            print("🔄 Using default enemy sprite")
        
        if 'arrow_tower' not in self.sprites:
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
            print("🔄 Using default tower sprite")
        
        if 'ally' not in self.sprites:
            ally_sprite = pygame.Surface((ALLY_SIZE, ALLY_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(ally_sprite, GREEN, (ALLY_SIZE//2, ALLY_SIZE//2), ALLY_SIZE//2)
            pygame.draw.circle(ally_sprite, BLACK, (ALLY_SIZE//2, ALLY_SIZE//2), ALLY_SIZE//2, 2)
            self.sprites['ally'] = ally_sprite
            print("🔄 Using default ally sprite")
        
        if 'arrow' not in self.sprites:
            arrow_sprite = pygame.Surface((ARROW_SIZE, ARROW_SIZE), pygame.SRCALPHA)
            pygame.draw.circle(arrow_sprite, YELLOW, (ARROW_SIZE//2, ARROW_SIZE//2), ARROW_SIZE//2)
            self.sprites['arrow'] = arrow_sprite
            print("🔄 Using default arrow sprite")
        
        if 'essence' not in self.sprites:
            essence_sprite = pygame.Surface((12, 12), pygame.SRCALPHA)
            pygame.draw.circle(essence_sprite, PURPLE, (6, 6), 6)
            pygame.draw.circle(essence_sprite, WHITE, (6, 6), 6, 1)
            self.sprites['essence'] = essence_sprite
            print("🔄 Using default essence sprite")
            
    def get_sprite(self, name: str) -> Optional[pygame.Surface]:
        """Get a sprite by name."""
        return self.sprites.get(name)
        
    def get_animation(self, name: str) -> Optional[Union[AnimationManager, DirectionalAnimationManager]]:
        """Get an animation manager by name."""
        return self.animations.get(name)
        
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