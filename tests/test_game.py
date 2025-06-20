"""
Basic unit tests for the game components.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import from src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.game.game_state import GameStateManager, GameState
from src.game.settings import *
from src.utils.helpers import distance, normalize_vector, clamp

class TestGameState(unittest.TestCase):
    """Test game state management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.state_manager = GameStateManager()
        
    def test_initial_state(self):
        """Test initial game state."""
        self.assertEqual(self.state_manager.get_state(), GameState.MENU)
        self.assertEqual(self.state_manager.player_data['health'], 100)
        self.assertEqual(self.state_manager.player_data['essence'], 100)
        self.assertEqual(self.state_manager.castle_data['health'], 500)
        
    def test_state_changes(self):
        """Test state changes."""
        self.state_manager.change_state(GameState.PLAYING)
        self.assertEqual(self.state_manager.get_state(), GameState.PLAYING)
        self.assertTrue(self.state_manager.is_state(GameState.PLAYING))
        
    def test_essence_management(self):
        """Test essence spending and adding."""
        initial_essence = self.state_manager.player_data['essence']
        
        # Test spending essence
        self.assertTrue(self.state_manager.spend_essence(50))
        self.assertEqual(self.state_manager.player_data['essence'], initial_essence - 50)
        
        # Test spending more than available
        self.assertFalse(self.state_manager.spend_essence(1000))
        
        # Test adding essence
        self.state_manager.add_essence(25)
        self.assertEqual(self.state_manager.player_data['essence'], initial_essence - 50 + 25)
        
    def test_castle_damage(self):
        """Test castle damage."""
        initial_health = self.state_manager.castle_data['health']
        self.state_manager.damage_castle(100)
        self.assertEqual(self.state_manager.castle_data['health'], initial_health - 100)
        
        # Test castle destruction
        self.state_manager.damage_castle(500)  # More than remaining health
        self.assertTrue(self.state_manager.is_castle_destroyed())
        self.assertEqual(self.state_manager.get_state(), GameState.GAME_OVER)

class TestHelpers(unittest.TestCase):
    """Test helper functions."""
    
    def test_distance(self):
        """Test distance calculation."""
        self.assertEqual(distance(0, 0, 3, 4), 5.0)
        self.assertEqual(distance(1, 1, 1, 1), 0.0)
        
    def test_normalize_vector(self):
        """Test vector normalization."""
        x, y = normalize_vector(3, 4)
        self.assertAlmostEqual(x, 0.6)
        self.assertAlmostEqual(y, 0.8)
        
        # Test zero vector
        x, y = normalize_vector(0, 0)
        self.assertEqual(x, 0.0)
        self.assertEqual(y, 0.0)
        
    def test_clamp(self):
        """Test value clamping."""
        self.assertEqual(clamp(5, 0, 10), 5)
        self.assertEqual(clamp(-5, 0, 10), 0)
        self.assertEqual(clamp(15, 0, 10), 10)

class TestGameSettings(unittest.TestCase):
    """Test game settings and constants."""
    
    def test_screen_settings(self):
        """Test screen settings are valid."""
        self.assertGreater(SCREEN_WIDTH, 0)
        self.assertGreater(SCREEN_HEIGHT, 0)
        self.assertGreater(FPS, 0)
        
    def test_game_balance(self):
        """Test game balance values are reasonable."""
        self.assertGreater(PLAYER_HEALTH, 0)
        self.assertGreater(ENEMY_HEALTH, 0)
        self.assertGreater(CASTLE_HEALTH, 0)
        self.assertGreater(ARROW_TOWER_COST, 0)
        self.assertGreater(ALLY_COST, 0)

if __name__ == '__main__':
    unittest.main() 