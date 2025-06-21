"""
Game state management system.
"""

from enum import Enum
from typing import Dict, Any
from . import settings

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
            'x': getattr(settings, 'CASTLE_X', 1152),  # Use new castle position
            'y': getattr(settings, 'CASTLE_Y', 320)
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
            'x': settings.CASTLE_X,
            'y': settings.CASTLE_Y
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
        
    def get_saveable_game_state(self) -> Dict[str, Any]:
        """Get complete game state that can be saved and resumed."""
        # Save basic state data
        state_data = {
            'player_data': self.player_data.copy(),
            'castle_data': self.castle_data.copy(),
            'game_data': self.game_data.copy(),
        }
        
        # Save entity positions and states (simplified for JSON storage)
        state_data['entities'] = {
            'towers': [
                {
                    'grid_x': tower.grid_x,
                    'grid_y': tower.grid_y,
                    'level': getattr(tower, 'level', 1),
                    'health': getattr(tower, 'health', 100)
                } for tower in self.entities['towers']
            ],
            'allies': [
                {
                    'x': ally.x,
                    'y': ally.y,
                    'health': getattr(ally, 'health', 100)
                } for ally in self.entities['allies']
            ]
            # Note: We don't save enemies/projectiles as they're temporary
        }
        
        return state_data
        
    def load_game_state(self, saved_data: Dict[str, Any]):
        """Load game state from saved data."""
        try:
            # Load basic game state
            self.player_data = saved_data['game_state']['player_data'].copy()
            self.castle_data = saved_data['game_state']['castle_data'].copy()
            self.game_data = saved_data['game_state']['game_data'].copy()
            
            # Override specific values from the saved game record
            self.game_data['current_wave'] = saved_data['wave_number']
            self.game_data['score'] = saved_data['score']
            self.player_data['essence'] = saved_data['essence']
            self.castle_data['health'] = saved_data['castle_health']
            self.game_data['time_elapsed'] = saved_data['time_elapsed']
            
            # Clear current entities (they'll be recreated by managers)
            for entity_list in self.entities.values():
                entity_list.clear()
                
            # Store entity data for managers to recreate
            self.saved_entity_data = saved_data['game_state'].get('entities', {})
            
            print(f"✅ Loaded game state: Wave {self.game_data['current_wave']}, Score {self.game_data['score']}")
            
        except Exception as e:
            print(f"❌ Failed to load game state: {e}")
            # Fall back to reset game if loading fails
            self.reset_game()
            
    def get_saved_entity_data(self) -> Dict[str, Any]:
        """Get saved entity data for managers to recreate entities."""
        return getattr(self, 'saved_entity_data', {}) 