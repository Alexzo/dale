"""
Sound management system for the game.
"""

import pygame
import os
from typing import Dict, Optional

from ..game.settings import SOUNDS_DIR

class SoundManager:
    """Manages loading and playing of sounds and music."""
    
    def __init__(self):
        """Initialize the sound manager."""
        pygame.mixer.init()
        
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.music_volume = 0.7
        self.sound_volume = 0.8
        self.sound_enabled = True
        self.music_enabled = True
        
        # Load default sounds (if available)
        self._load_default_sounds()
        
    def _load_default_sounds(self):
        """Load default sound effects."""
        # For now, we'll create placeholder sounds or load them if files exist
        sound_files = {
            'arrow_fire': 'arrow_fire.wav',
            'enemy_hit': 'enemy_hit.wav',
            'enemy_death': 'enemy_death.wav',
            'tower_build': 'tower_build.wav',
            'ally_summon': 'ally_summon.wav',
            'castle_damage': 'castle_damage.wav',
            'essence_collect': 'essence_collect.wav',
            'wave_start': 'wave_start.wav'
        }
        
        for sound_name, filename in sound_files.items():
            filepath = os.path.join(SOUNDS_DIR, filename)
            if os.path.exists(filepath):
                try:
                    sound = pygame.mixer.Sound(filepath)
                    self.sounds[sound_name] = sound
                except pygame.error as e:
                    print(f"Could not load sound {sound_name}: {e}")
                    
    def load_sound(self, name: str, filepath: str) -> bool:
        """Load a sound from file."""
        try:
            if os.path.exists(filepath):
                sound = pygame.mixer.Sound(filepath)
                self.sounds[name] = sound
                return True
        except pygame.error as e:
            print(f"Could not load sound {name} from {filepath}: {e}")
        return False
        
    def play_sound(self, name: str, volume: Optional[float] = None) -> bool:
        """Play a sound effect."""
        if not self.sound_enabled:
            return False
            
        if name in self.sounds:
            sound = self.sounds[name]
            if volume is not None:
                sound.set_volume(volume)
            else:
                sound.set_volume(self.sound_volume)
            sound.play()
            return True
        return False
        
    def play_music(self, filepath: str, loops: int = -1) -> bool:
        """Play background music."""
        if not self.music_enabled:
            return False
            
        try:
            if os.path.exists(filepath):
                pygame.mixer.music.load(filepath)
                pygame.mixer.music.set_volume(self.music_volume)
                pygame.mixer.music.play(loops)
                return True
        except pygame.error as e:
            print(f"Could not play music {filepath}: {e}")
        return False
        
    def stop_music(self):
        """Stop background music."""
        pygame.mixer.music.stop()
        
    def pause_music(self):
        """Pause background music."""
        pygame.mixer.music.pause()
        
    def unpause_music(self):
        """Unpause background music."""
        pygame.mixer.music.unpause()
        
    def set_sound_volume(self, volume: float):
        """Set sound effects volume (0.0 to 1.0)."""
        self.sound_volume = max(0.0, min(1.0, volume))
        
    def set_music_volume(self, volume: float):
        """Set music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume)
        
    def toggle_sound(self):
        """Toggle sound effects on/off."""
        self.sound_enabled = not self.sound_enabled
        
    def toggle_music(self):
        """Toggle music on/off."""
        self.music_enabled = not self.music_enabled
        if not self.music_enabled:
            self.stop_music()
            
    def cleanup(self):
        """Clean up sound resources."""
        pygame.mixer.quit() 