#!/usr/bin/env python3
"""
Test script for the new enemy combat system in Dale.
Demonstrates enemies attacking towers and sieging the castle.
"""

import pygame
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.game.game_engine import GameEngine

def main():
    """Run the combat test."""
    print("🏰 Dale - Enemy Combat System Test")
    print("=" * 50)
    print()
    print("New Enemy Combat Features:")
    print("• Enemies attack towers while passing by (shooting arrows)")
    print("• Enemies siege the castle when they reach it")
    print("• Enemies continue attacking until killed or castle falls")
    print("• Enemy projectiles can damage and destroy towers")
    print()
    print("Test Instructions:")
    print("• Build towers near enemy paths to see them get attacked")
    print("• Watch enemies stop at the castle and attack it continuously")
    print("• Notice how enemies don't disappear after reaching castle")
    print("• Try to kill sieging enemies before they destroy the castle")
    print()
    print("Controls:")
    print("• WASD/Arrow Keys: Move character")
    print("• F/Shift: Attack enemies")
    print("• Left Click: Build tower (50 essence)")
    print("• Click tower then U: Upgrade tower")
    print("• Q: Summon ally (75 essence)")
    print("• ESC: Pause game")
    print()
    
    try:
        # Create and run the game engine
        game = GameEngine()
        game.run()
        
    except KeyboardInterrupt:
        print("\n🛑 Game interrupted by user")
    except Exception as e:
        print(f"❌ Error running combat test: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        print("👋 Combat test complete!")

if __name__ == "__main__":
    main() 