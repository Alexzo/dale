"""
Sprite loading and management utilities.
"""

import pygame
import os
import math
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
        self.create_procedural_textures()  # Create environment textures
        
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
        
        # Environment texture files
        environment_files = {
            'path_stone': 'environment/stone_path.png',
            'path_dirt': 'environment/dirt_road.png', 
            'path_grass': 'environment/grass_trail.png',
            'grass_tile': 'environment/grass.png',
            'stone_tile': 'environment/stone.png',
            'dirt_tile': 'environment/dirt.png',
            'tree_oak': 'environment/oak_tree.png',
            'tree_pine': 'environment/pine_tree.png',
            'tree_birch': 'environment/birch_tree.png',
            'rock_small': 'environment/rock_small.png',
            'rock_medium': 'environment/rock_medium.png',
            'rock_large': 'environment/rock_large.png',
            'boulder': 'environment/boulder.png'
        }
        
        # Load sprites with proper scaling
        for sprite_name, file_path in sprite_files.items():
            full_path = os.path.join(SPRITES_DIR, file_path)
            if self.load_sprite_with_scaling(sprite_name, full_path):
                print(f"✅ Loaded pixel art: {sprite_name}")
            else:
                print(f"⚠️  Could not load {sprite_name}, will use default")
                
        # Load environment textures
        for texture_name, file_path in environment_files.items():
            full_path = os.path.join(SPRITES_DIR, file_path)
            if self.load_environment_texture(texture_name, full_path):
                print(f"✅ Loaded environment texture: {texture_name}")
            else:
                print(f"⚠️  Could not load {texture_name}, will create procedural texture")
                
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
        
        animation_types = ['idle', 'walk', 'attack']
        directions = ['up', 'down', 'left', 'right']
        loaded_any = False
        
        # Track loaded attack frames for potential flipping
        attack_frames_loaded = {}
        
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
                    if anim_type == 'idle':
                        frame_duration = 0.3
                        loop = True
                    elif anim_type == 'walk':
                        frame_duration = 0.15
                        loop = True
                    elif anim_type == 'attack':
                        frame_duration = 0.08
                        loop = False  # Attack animations don't loop
                        attack_frames_loaded[direction] = frames
                    
                    animation = Animation(frames, frame_duration, loop)
                    anim_manager.add_directional_animation(anim_type, direction, animation)
                    loaded_any = True
        
        # Handle missing attack directions by flipping existing ones
        if 'attack' in [anim for anim in animation_types]:
            self._create_missing_attack_directions(anim_manager, attack_frames_loaded)
        
        return loaded_any
        
    def _create_missing_attack_directions(self, anim_manager: DirectionalAnimationManager, attack_frames_loaded: Dict[str, List[pygame.Surface]]):
        """Create missing attack directions by flipping existing ones."""
        # If we have right but not left, create left by flipping right
        if 'right' in attack_frames_loaded and 'left' not in attack_frames_loaded:
            left_frames = [pygame.transform.flip(frame, True, False) for frame in attack_frames_loaded['right']]
            left_animation = Animation(left_frames, 0.08, False)
            anim_manager.add_directional_animation('attack', 'left', left_animation)
            print("✅ Created left attack animation by flipping right frames")
        
        # If we have left but not right, create right by flipping left
        elif 'left' in attack_frames_loaded and 'right' not in attack_frames_loaded:
            right_frames = [pygame.transform.flip(frame, True, False) for frame in attack_frames_loaded['left']]
            right_animation = Animation(right_frames, 0.08, False)
            anim_manager.add_directional_animation('attack', 'right', right_animation)
            print("✅ Created right attack animation by flipping left frames")
        
        # If we have up but not down, create down by flipping up
        if 'up' in attack_frames_loaded and 'down' not in attack_frames_loaded:
            down_frames = [pygame.transform.flip(frame, False, True) for frame in attack_frames_loaded['up']]
            down_animation = Animation(down_frames, 0.08, False)
            anim_manager.add_directional_animation('attack', 'down', down_animation)
            print("✅ Created down attack animation by flipping up frames")
        
        # If we have down but not up, create up by flipping down  
        elif 'down' in attack_frames_loaded and 'up' not in attack_frames_loaded:
            up_frames = [pygame.transform.flip(frame, False, True) for frame in attack_frames_loaded['down']]
            up_animation = Animation(up_frames, 0.08, False)
            anim_manager.add_directional_animation('attack', 'up', up_animation)
            print("✅ Created up attack animation by flipping down frames")
        
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
        
    def load_environment_texture(self, name: str, filepath: str) -> bool:
        """Load an environment texture from file."""
        try:
            if os.path.exists(filepath):
                texture = pygame.image.load(filepath).convert_alpha()
                # Environment textures are kept at original size for tiling
                self.sprites[name] = texture
                self.sprite_rects[name] = texture.get_rect()
                return True
        except pygame.error as e:
            print(f"Could not load environment texture {name} from {filepath}: {e}")
        return False
        
    def create_procedural_textures(self):
        """Create procedural environment textures as fallbacks."""
        # Create stone path texture
        if 'path_stone' not in self.sprites:
            stone_texture = self._create_stone_texture(32, 32)
            self.sprites['path_stone'] = stone_texture
            
        # Create dirt road texture  
        if 'path_dirt' not in self.sprites:
            dirt_texture = self._create_dirt_texture(32, 32)
            self.sprites['path_dirt'] = dirt_texture
            
        # Create grass trail texture
        if 'path_grass' not in self.sprites:
            grass_texture = self._create_grass_texture(32, 32)
            self.sprites['path_grass'] = grass_texture
            
        # Create tree sprites
        if 'tree_oak' not in self.sprites:
            oak_tree = self._create_oak_tree(48, 64)
            self.sprites['tree_oak'] = oak_tree
            
        if 'tree_pine' not in self.sprites:
            pine_tree = self._create_pine_tree(40, 72)
            self.sprites['tree_pine'] = pine_tree
            
        if 'tree_birch' not in self.sprites:
            birch_tree = self._create_birch_tree(44, 68)
            self.sprites['tree_birch'] = birch_tree
            
        # Create rock sprites
        if 'rock_small' not in self.sprites:
            small_rock = self._create_rock(24, 20, (100, 100, 110))
            self.sprites['rock_small'] = small_rock
            
        if 'rock_medium' not in self.sprites:
            medium_rock = self._create_rock(36, 30, (90, 90, 100))
            self.sprites['rock_medium'] = medium_rock
            
        if 'rock_large' not in self.sprites:
            large_rock = self._create_rock(48, 40, (80, 80, 90))
            self.sprites['rock_large'] = large_rock
            
        if 'boulder' not in self.sprites:
            boulder = self._create_rock(60, 50, (70, 70, 80))
            self.sprites['boulder'] = boulder
            
        print("🎨 Created procedural environment textures, trees, and rocks")
        
    def _create_stone_texture(self, width: int, height: int) -> pygame.Surface:
        """Create a procedural stone texture."""
        import random
        texture = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Base stone color
        base_color = (120, 120, 130)
        texture.fill(base_color)
        
        # Add stone pattern
        for _ in range(width * height // 8):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            # Darker spots
            color_offset = random.randint(-30, -10)
            dark_color = tuple(max(0, c + color_offset) for c in base_color)
            pygame.draw.circle(texture, dark_color, (x, y), 1)
            
        # Add lighter highlights
        for _ in range(width * height // 12):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            color_offset = random.randint(10, 25)
            light_color = tuple(min(255, c + color_offset) for c in base_color)
            pygame.draw.circle(texture, light_color, (x, y), 1)
            
        return texture
        
    def _create_dirt_texture(self, width: int, height: int) -> pygame.Surface:
        """Create a procedural dirt texture."""
        import random
        texture = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Base dirt color
        base_color = (101, 67, 33)
        texture.fill(base_color)
        
        # Add dirt variation
        for _ in range(width * height // 6):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            color_offset = random.randint(-20, 20)
            varied_color = tuple(max(0, min(255, c + color_offset)) for c in base_color)
            pygame.draw.circle(texture, varied_color, (x, y), 1)
            
        return texture
        
    def _create_grass_texture(self, width: int, height: int) -> pygame.Surface:
        """Create a procedural grass texture."""
        import random
        texture = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Base grass color
        base_color = (34, 139, 34)
        texture.fill(base_color)
        
        # Add grass blades (small lines)
        for _ in range(width * height // 4):
            x = random.randint(0, width - 2)
            y = random.randint(0, height - 3)
            # Different shades of green
            green_offset = random.randint(-20, 30)
            grass_color = (max(0, min(255, 34 + green_offset)), 
                          max(0, min(255, 139 + green_offset // 2)), 
                          max(0, min(255, 34 + green_offset // 3)))
            pygame.draw.line(texture, grass_color, (x, y), (x, y + 2), 1)
            
        return texture
        
    def _create_oak_tree(self, width: int, height: int) -> pygame.Surface:
        """Create a procedural oak tree sprite."""
        import random
        tree = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Tree trunk
        trunk_width = width // 6
        trunk_height = height // 2
        trunk_x = width // 2 - trunk_width // 2
        trunk_y = height - trunk_height
        trunk_color = (101, 67, 33)  # Brown
        pygame.draw.rect(tree, trunk_color, (trunk_x, trunk_y, trunk_width, trunk_height))
        
        # Tree crown (multiple overlapping circles for oak shape)
        crown_color = (34, 139, 34)  # Forest green
        crown_dark = (25, 100, 25)   # Darker green for depth
        
        # Main crown circles
        crown_radius = width // 3
        crown_y = height // 3
        
        # Multiple overlapping circles for full oak crown
        crown_positions = [
            (width // 2, crown_y),                    # Center
            (width // 2 - crown_radius // 2, crown_y + 5),  # Left
            (width // 2 + crown_radius // 2, crown_y + 5),  # Right
            (width // 2, crown_y - crown_radius // 3),       # Top
        ]
        
        for pos in crown_positions:
            pygame.draw.circle(tree, crown_color, pos, crown_radius)
            # Add darker edge for depth
            pygame.draw.circle(tree, crown_dark, pos, crown_radius, 2)
        
        return tree
        
    def _create_pine_tree(self, width: int, height: int) -> pygame.Surface:
        """Create a procedural pine tree sprite."""
        tree = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Tree trunk
        trunk_width = width // 8
        trunk_height = height // 4
        trunk_x = width // 2 - trunk_width // 2
        trunk_y = height - trunk_height
        trunk_color = (92, 51, 23)  # Dark brown
        pygame.draw.rect(tree, trunk_color, (trunk_x, trunk_y, trunk_width, trunk_height))
        
        # Pine tree triangular shape (3 overlapping triangles)
        crown_color = (0, 100, 0)    # Dark green
        crown_light = (0, 130, 0)    # Lighter green
        
        # Three triangular sections getting smaller towards top
        triangle_heights = [height // 3, height // 3, height // 4]
        triangle_y_positions = [height - trunk_height - 5, height // 2, height // 4]
        
        for i, (tri_height, tri_y) in enumerate(zip(triangle_heights, triangle_y_positions)):
            tri_width = width - i * (width // 6)  # Get narrower towards top
            
            # Triangle points
            points = [
                (width // 2, tri_y - tri_height),           # Top point
                (width // 2 - tri_width // 2, tri_y),       # Bottom left
                (width // 2 + tri_width // 2, tri_y)        # Bottom right
            ]
            
            pygame.draw.polygon(tree, crown_color, points)
            # Add lighter edge
            pygame.draw.polygon(tree, crown_light, points, 2)
        
        return tree
        
    def _create_birch_tree(self, width: int, height: int) -> pygame.Surface:
        """Create a procedural birch tree sprite."""
        import random
        tree = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Birch trunk (white with black marks)
        trunk_width = width // 7
        trunk_height = height * 2 // 3
        trunk_x = width // 2 - trunk_width // 2
        trunk_y = height - trunk_height
        trunk_color = (245, 245, 220)  # Off-white
        pygame.draw.rect(tree, trunk_color, (trunk_x, trunk_y, trunk_width, trunk_height))
        
        # Add characteristic birch bark marks
        mark_color = (50, 50, 50)  # Dark gray
        for i in range(4):
            mark_y = trunk_y + i * (trunk_height // 4) + random.randint(-5, 5)
            pygame.draw.line(tree, mark_color, 
                           (trunk_x, mark_y), (trunk_x + trunk_width, mark_y), 2)
        
        # Birch crown (light, airy appearance)
        crown_color = (144, 238, 144)  # Light green
        crown_dark = (105, 200, 105)   # Medium green
        
        # Smaller, more delicate crown than oak
        crown_radius = width // 4
        crown_y = height // 4
        
        # Light, scattered crown
        crown_positions = [
            (width // 2, crown_y),
            (width // 2 - crown_radius // 2, crown_y + 8),
            (width // 2 + crown_radius // 2, crown_y + 8),
        ]
        
        for pos in crown_positions:
            pygame.draw.circle(tree, crown_color, pos, crown_radius)
            pygame.draw.circle(tree, crown_dark, pos, crown_radius, 1)
        
        return tree
        
    def _create_rock(self, width: int, height: int, base_color: tuple) -> pygame.Surface:
        """Create a procedural rock sprite."""
        import random
        rock = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Create irregular rock shape using polygon
        center_x = width // 2
        center_y = height // 2
        
        # Generate irregular rock outline
        num_points = 8
        points = []
        for i in range(num_points):
            angle = (i / num_points) * 2 * 3.14159
            # Add randomness to radius for irregular shape
            radius_variance = random.uniform(0.7, 1.0)
            base_radius_x = (width // 2 - 2) * radius_variance
            base_radius_y = (height // 2 - 2) * radius_variance
            
            x = center_x + int(base_radius_x * math.cos(angle))
            y = center_y + int(base_radius_y * math.sin(angle))
            points.append((x, y))
        
        # Fill the rock shape
        pygame.draw.polygon(rock, base_color, points)
        
        # Add shading and highlights
        darker_color = tuple(max(0, c - 30) for c in base_color)
        lighter_color = tuple(min(255, c + 40) for c in base_color)
        
        # Dark outline
        pygame.draw.polygon(rock, darker_color, points, 2)
        
        # Add some texture spots
        for _ in range(width * height // 100):
            spot_x = random.randint(2, width - 3)
            spot_y = random.randint(2, height - 3)
            
            # Check if spot is inside the rock (simple bounds check)
            if (center_x - width//3 < spot_x < center_x + width//3 and 
                center_y - height//3 < spot_y < center_y + height//3):
                
                spot_color = random.choice([darker_color, lighter_color])
                pygame.draw.circle(rock, spot_color, (spot_x, spot_y), 1)
        
        return rock 