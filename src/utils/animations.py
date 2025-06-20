"""
Animation system for sprite-based animations.
"""

import pygame
from typing import List, Dict, Optional
import os

class Animation:
    """Handles a single animation sequence."""
    
    def __init__(self, frames: List[pygame.Surface], frame_duration: float = 0.1, loop: bool = True):
        """
        Initialize animation.
        
        Args:
            frames: List of pygame surfaces representing animation frames
            frame_duration: Duration each frame is displayed (in seconds)
            loop: Whether the animation should loop
        """
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop
        self.current_frame = 0
        self.time_since_last_frame = 0.0
        self.finished = False
        
    def update(self, dt: float):
        """Update animation timing."""
        if self.finished and not self.loop:
            return
            
        self.time_since_last_frame += dt
        
        if self.time_since_last_frame >= self.frame_duration:
            self.time_since_last_frame = 0.0
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True
                    
    def get_current_frame(self) -> pygame.Surface:
        """Get the current frame surface."""
        if not self.frames:
            return pygame.Surface((32, 32), pygame.SRCALPHA)
        return self.frames[self.current_frame]
        
    def reset(self):
        """Reset animation to beginning."""
        self.current_frame = 0
        self.time_since_last_frame = 0.0
        self.finished = False
        
    def is_finished(self) -> bool:
        """Check if non-looping animation is finished."""
        return self.finished

class AnimationManager:
    """Manages multiple animations for a single entity."""
    
    def __init__(self):
        """Initialize animation manager."""
        self.animations: Dict[str, Animation] = {}
        self.current_animation = ""
        self.current_anim_obj: Optional[Animation] = None
        
    def add_animation(self, name: str, animation: Animation):
        """Add an animation."""
        self.animations[name] = animation
        
        # If this is the first animation, make it current
        if not self.current_animation:
            self.set_animation(name)
            
    def set_animation(self, name: str, force_restart: bool = False):
        """Set the current animation."""
        if name not in self.animations:
            return False
            
        # Don't restart if it's the same animation unless forced
        if name == self.current_animation and not force_restart:
            return True
            
        self.current_animation = name
        self.current_anim_obj = self.animations[name]
        
        # Reset animation if switching or forced
        if force_restart or name != self.current_animation:
            self.current_anim_obj.reset()
            
        return True
        
    def update(self, dt: float):
        """Update current animation."""
        if self.current_anim_obj:
            self.current_anim_obj.update(dt)
            
    def get_current_frame(self) -> Optional[pygame.Surface]:
        """Get current animation frame."""
        if self.current_anim_obj:
            return self.current_anim_obj.get_current_frame()
        return None
        
    def get_current_animation_name(self) -> str:
        """Get current animation name."""
        return self.current_animation

class SpriteSheetLoader:
    """Utility class for loading sprites from spritesheets."""
    
    @staticmethod
    def load_spritesheet(filepath: str, frame_width: int, frame_height: int, 
                        frame_count: Optional[int] = None) -> List[pygame.Surface]:
        """
        Load frames from a spritesheet.
        
        Args:
            filepath: Path to spritesheet image
            frame_width: Width of each frame
            frame_height: Height of each frame  
            frame_count: Number of frames to load (None = all possible)
            
        Returns:
            List of pygame surfaces representing frames
        """
        frames = []
        
        try:
            if not os.path.exists(filepath):
                return frames
                
            spritesheet = pygame.image.load(filepath).convert_alpha()
            sheet_width = spritesheet.get_width()
            sheet_height = spritesheet.get_height()
            
            # Calculate how many frames fit
            frames_per_row = sheet_width // frame_width
            rows = sheet_height // frame_height
            total_possible_frames = frames_per_row * rows
            
            actual_frame_count = frame_count if frame_count is not None else total_possible_frames
            actual_frame_count = min(actual_frame_count, total_possible_frames)
                
            for i in range(actual_frame_count):
                row = i // frames_per_row
                col = i % frames_per_row
                
                x = col * frame_width
                y = row * frame_height
                
                frame_rect = pygame.Rect(x, y, frame_width, frame_height)
                frame = spritesheet.subsurface(frame_rect).copy()
                frames.append(frame)
                
        except pygame.error as e:
            print(f"Error loading spritesheet {filepath}: {e}")
            
        return frames
    
    @staticmethod
    def load_frame_sequence(folder_path: str, base_name: str, extension: str = ".png") -> List[pygame.Surface]:
        """
        Load numbered frame sequence from folder.
        
        Args:
            folder_path: Path to folder containing frames
            base_name: Base name of frame files (e.g., "walk")
            extension: File extension
            
        Returns:
            List of pygame surfaces representing frames
        """
        frames = []
        
        if not os.path.exists(folder_path):
            return frames
            
        # Look for numbered files: walk_1.png, walk_2.png, etc.
        frame_num = 1
        while True:
            filename = f"{base_name}_{frame_num}{extension}"
            filepath = os.path.join(folder_path, filename)
            
            if not os.path.exists(filepath):
                break
                
            try:
                frame = pygame.image.load(filepath).convert_alpha()
                frames.append(frame)
                frame_num += 1
            except pygame.error as e:
                print(f"Error loading frame {filepath}: {e}")
                break
                
        return frames 