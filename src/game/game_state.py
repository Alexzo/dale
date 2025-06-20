"""
Game state management system.
"""

from enum import Enum
from typing import Dict, Any

class GameState(Enum):
    """Game state enumeration."""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    VICTORY = "victory"

class GameStateManager:
    """Manages the current game state and game data."""
    
    def __init__(self):
        self.current_state = GameState.MENU
        self.previous_state = GameState.MENU
        
        # Game data
        self.player_data = {
            'health': 100,
            'x': 400,
            'y': 300,
            'essence': 100
        }
        
        self.castle_data = {
            'health': 500,
            'max_health': 500,
            'x': 640,  # Center of screen
            'y': 360
        }
        
        self.game_data = {
            'current_wave': 1,
            'score': 0,
            'enemies_killed': 0,
            'towers_built': 0,
            'allies_summoned': 0,
            'time_elapsed': 0.0
        }
        
        self.entities = {
            'enemies': [],
            'towers': [],
            'allies': [],
            'projectiles': [],
            'essences': []  # Collectible essence orbs
        }
        
    def change_state(self, new_state: GameState):
        """Change the current game state."""
        self.previous_state = self.current_state
        self.current_state = new_state
        
    def get_state(self) -> GameState:
        """Get the current game state."""
        return self.current_state
        
    def is_state(self, state: GameState) -> bool:
        """Check if current state matches given state."""
        return self.current_state == state
        
    def reset_game(self):
        """Reset game data for a new game."""
        self.player_data = {
            'health': 100,
            'x': 400,
            'y': 300,
            'essence': 100
        }
        
        self.castle_data = {
            'health': 500,
            'max_health': 500,
            'x': 640,
            'y': 360
        }
        
        self.game_data = {
            'current_wave': 1,
            'score': 0,
            'enemies_killed': 0,
            'towers_built': 0,
            'allies_summoned': 0,
            'time_elapsed': 0.0
        }
        
        # Clear all entities
        for entity_list in self.entities.values():
            entity_list.clear()
            
    def add_score(self, points: int):
        """Add points to the score."""
        self.game_data['score'] += points
        
    def spend_essence(self, amount: int) -> bool:
        """Spend essence if player has enough."""
        if self.player_data['essence'] >= amount:
            self.player_data['essence'] -= amount
            return True
        return False
        
    def add_essence(self, amount: int):
        """Add essence to player's resources."""
        self.player_data['essence'] += amount
        
    def damage_castle(self, damage: int):
        """Apply damage to the castle."""
        self.castle_data['health'] -= damage
        if self.castle_data['health'] <= 0:
            self.castle_data['health'] = 0
            self.change_state(GameState.GAME_OVER)
            
    def is_castle_destroyed(self) -> bool:
        """Check if castle is destroyed."""
        return self.castle_data['health'] <= 0
        
    def next_wave(self):
        """Advance to the next wave."""
        self.game_data['current_wave'] += 1
        
    def get_save_data(self) -> Dict[str, Any]:
        """Get data for saving to backend."""
        return {
            'score': self.game_data['score'],
            'wave_reached': self.game_data['current_wave'],
            'enemies_killed': self.game_data['enemies_killed'],
            'towers_built': self.game_data['towers_built'],
            'allies_summoned': self.game_data['allies_summoned'],
            'time_elapsed': self.game_data['time_elapsed']
        } 