"""
Character progression system for Dale.
Handles experience points, leveling up, and stat calculations.
"""

from typing import Dict, Any, List, Optional
from .constants import (
    EXP_PER_ENEMY_KILL, EXP_PER_WAVE_COMPLETE, EXP_PER_TOWER_BUILT,
    get_exp_requirement_for_level, get_character_health_at_level, 
    get_character_attack_at_level
)

class CharacterProgression:
    """Manages character progression, EXP, and leveling."""
    
    def __init__(self, database):
        """Initialize character progression system."""
        self.database = database
        self.session_exp_gained = 0
        self.session_level_ups = []
        self.character_data = self.database.get_character_data()
        
    def get_current_level(self) -> int:
        """Get current character level."""
        return self.character_data['level']
        
    def get_current_exp(self) -> int:
        """Get current EXP in current level."""
        return self.character_data['current_exp']
        
    def get_total_exp(self) -> int:
        """Get total EXP earned."""
        return self.character_data['total_exp']
        
    def get_exp_for_next_level(self) -> int:
        """Get EXP required for next level."""
        return get_exp_requirement_for_level(self.character_data['level'] + 1)
        
    def get_exp_progress_percent(self) -> float:
        """Get progress to next level as percentage."""
        exp_needed = self.get_exp_for_next_level()
        if exp_needed <= 0:
            return 100.0
        return min(100.0, (self.character_data['current_exp'] / exp_needed) * 100.0)
        
    def get_character_health(self) -> int:
        """Get character health based on current level."""
        return get_character_health_at_level(self.character_data['level'])
        
    def get_character_attack(self) -> int:
        """Get character attack power based on current level."""
        return get_character_attack_at_level(self.character_data['level'])
        
    def add_exp(self, source: str, amount: Optional[int] = None) -> Dict[str, Any]:
        """Add EXP from various sources."""
        if amount is None:
            # Use default amounts based on source
            exp_amounts = {
                'enemy_kill': EXP_PER_ENEMY_KILL,
                'wave_complete': EXP_PER_WAVE_COMPLETE,
                'tower_built': EXP_PER_TOWER_BUILT
            }
            amount = exp_amounts.get(source, 0)
        
        if amount <= 0:
            return {'level_up': False, 'exp_gained': 0}
            
        # Track session EXP
        self.session_exp_gained += amount
        
        # Add EXP and check for level ups
        level_up_info = self.database.add_character_exp(amount)
        
        # Update local character data
        self.character_data = self.database.get_character_data()
        
        # Track level ups in this session
        if level_up_info['level_up']:
            levels_gained = level_up_info['levels_gained']
            for i in range(levels_gained):
                new_level = level_up_info['old_level'] + i + 1
                self.session_level_ups.append({
                    'level': new_level,
                    'health_gained': 2,  # From constants.CHARACTER_HEALTH_PER_LEVEL
                    'attack_gained': 1   # From constants.CHARACTER_ATTACK_PER_LEVEL
                })
        
        return level_up_info
        
    def add_enemy_kill_exp(self) -> Dict[str, Any]:
        """Add EXP for killing an enemy."""
        return self.add_exp('enemy_kill')
        
    def add_wave_complete_exp(self) -> Dict[str, Any]:
        """Add EXP for completing a wave."""
        return self.add_exp('wave_complete')
        
    def add_tower_built_exp(self) -> Dict[str, Any]:
        """Add EXP for building a tower."""
        return self.add_exp('tower_built')
        
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of EXP and level ups for this session."""
        return {
            'exp_gained': self.session_exp_gained,
            'level_ups': self.session_level_ups,
            'levels_gained': len(self.session_level_ups),
            'starting_level': self.character_data['level'] - len(self.session_level_ups),
            'ending_level': self.character_data['level']
        }
        
    def reset_session(self):
        """Reset session tracking (call at start of new game)."""
        self.session_exp_gained = 0
        self.session_level_ups = []
        self.character_data = self.database.get_character_data()
        
    def get_character_display_info(self) -> Dict[str, Any]:
        """Get character info for display in menus."""
        return {
            'name': self.character_data['name'],
            'level': self.character_data['level'],
            'current_exp': self.character_data['current_exp'],
            'exp_for_next_level': self.get_exp_for_next_level(),
            'exp_progress_percent': self.get_exp_progress_percent(),
            'health': self.get_character_health(),
            'attack': self.get_character_attack(),
            'total_exp': self.character_data['total_exp'],
            'games_played': self.character_data['games_played'],
            'total_enemies_killed': self.character_data['total_enemies_killed'],
            'total_waves_completed': self.character_data['total_waves_completed'],
            'total_towers_built': self.character_data['total_towers_built']
        }
        
    def get_character_name(self) -> str:
        """Get current character name."""
        return self.character_data['name']
        
    def set_character_name(self, name: str):
        """Set character name."""
        if name.strip():  # Only update if name is not empty
            self.database.update_character_name(name.strip())
            self.character_data = self.database.get_character_data()  # Refresh data
        
    def get_level_up_message(self, level: int) -> str:
        """Get a congratulatory message for leveling up."""
        name = self.character_data['name']
        messages = [
            f"🎉 {name} reached Level {level}! Your training pays off!",
            f"⚔️ {name} achieved Level {level}! You grow stronger!",
            f"🌟 Level {level}, {name}! Power courses through you!",
            f"🔥 {name} attained Level {level}! Your skills improve!",
            f"💪 Level {level}, {name}! You feel more capable!",
            f"✨ {name} reached Level {level}! Your experience shows!",
            f"🏆 Level {level}, {name}! Excellence achieved!",
            f"⭐ {name} achieved Level {level}! Your legend grows!",
        ]
        
        # Use level to pick a consistent message
        return messages[(level - 1) % len(messages)] 