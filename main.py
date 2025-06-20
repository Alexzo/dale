#!/usr/bin/env python3
"""
Dale
Main entry point for the game.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.game.game_engine import GameEngine

def main():
    """Main function to start the game."""
    try:
        game = GameEngine()
        game.run()
    except KeyboardInterrupt:
        print("\nGame interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 