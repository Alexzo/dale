# Development Guide - Dale

This document provides guidance for developing and extending the Dale game.

## Project Structure

```
tower_defense_game/
├── main.py                 # Game entry point
├── requirements.txt        # Python dependencies
├── README.md              # Project documentation
├── DEVELOPMENT.md         # This file
├── src/                   # Source code
│   ├── game/             # Core game logic
│   │   ├── game_engine.py    # Main game loop and engine
│   │   ├── game_state.py     # Game state management
│   │   └── settings.py       # Game constants and configuration
│   ├── entities/         # Game entities
│   │   ├── player.py         # Player character (elf warrior)
│   │   ├── enemies.py        # Enemy types and AI
│   │   ├── towers.py         # Defensive towers
│   │   ├── allies.py         # Summoned allies (elf warriors)
│   │   └── projectiles.py    # Arrows and other projectiles
│   ├── ui/               # User interface
│   │   ├── hud.py           # Heads-up display
│   │   ├── menus.py         # Game menus
│   │   └── buttons.py       # UI buttons
│   ├── utils/            # Utility modules
│   │   ├── sprites.py       # Sprite management
│   │   ├── sounds.py        # Sound management
│   │   └── helpers.py       # Helper functions
│   └── backend/          # Data storage
│       └── database.py      # SQLite database for scores
├── assets/               # Game assets
│   ├── sprites/         # Pixel art sprites
│   │   └── player/         # Player character sprites
│   ├── sounds/          # Sound effects and music
│   └── maps/            # Level data
└── tests/               # Unit tests
    └── test_game.py        # Basic game tests
```

## Core Game Mechanics

### 1. Player Movement
- WASD/Arrow keys for free movement around the battlefield
- Player can move anywhere except through solid objects

### 2. Resource Management
- **Essence**: Primary resource collected from defeated enemies
- Used for summoning allies and building towers
- Starting amount: 100 essence

### 3. Defensive Mechanics
- **Arrow Towers**: Automatically target and shoot enemies within range
- **Elf Warrior Allies**: Summoned units that attack enemies automatically
- Both require essence to create

### 4. Enemy Waves
- Enemies spawn from screen edges and move toward the castle
- Wave difficulty increases over time
- Enemies drop essence when defeated

### 5. Win/Lose Conditions
- **Lose**: Castle health reaches 0
- **Victory**: Survive increasing waves (endless gameplay)

## Key Classes Overview

### GameEngine (src/game/game_engine.py)
- Main game loop and event handling
- Coordinates all game systems
- Manages rendering and updates

### GameStateManager (src/game/game_state.py)
- Tracks game state (menu, playing, game over)
- Manages player/castle health and resources
- Handles game progression

### Entity Classes
- **Player**: Moveable character controlled by user
- **Enemy**: AI-controlled units that attack the castle
- **ArrowTower**: Defensive structure that shoots arrows
- **ElfWarrior**: Allied unit that fights enemies
- **Arrow**: Projectile fired by towers

## Adding New Features

### Adding New Enemy Types
1. Create new enemy class inheriting from `Enemy` in `entities/enemies.py`
2. Add sprite creation in `utils/sprites.py`
3. Update `EnemyManager.spawn_wave()` to include new enemy type

### Adding New Tower Types
1. Create new tower class in `entities/towers.py`
2. Add tower building logic in `TowerManager`
3. Update UI in `ui/hud.py` for new tower buttons

### Adding Sound Effects
1. Place sound files in `assets/sounds/`
2. Load sounds in `utils/sounds.py`
3. Play sounds in appropriate game events

### Adding New Levels/Maps
1. Create map data files in `assets/maps/`
2. Implement map loading system
3. Update spawn points and castle positions

## Game Balance Configuration

Key balance values in `src/game/settings.py`:

```python
# Player
PLAYER_HEALTH = 100
PLAYER_SPEED = 200

# Enemies
ENEMY_HEALTH = 30
ENEMY_SPEED = 50
ENEMY_DAMAGE = 10

# Towers
ARROW_TOWER_COST = 50
ARROW_TOWER_DAMAGE = 25
ARROW_TOWER_RANGE = 150

# Allies
ALLY_COST = 75
ALLY_HEALTH = 60
ALLY_DAMAGE = 20

# Resources
ESSENCE_PER_ENEMY = 15
STARTING_ESSENCE = 100
```

## Testing

Run unit tests:
```bash
cd tests
python3 -m unittest test_game.py
```

## Performance Considerations

- Game runs at 60 FPS (configurable in settings)
- Entity updates use delta time for smooth movement
- Sprites are cached in SpriteManager
- Database operations are lightweight SQLite

## Future Enhancement Ideas

1. **Multiple Enemy Types**: Fast enemies, armored enemies, flying enemies
2. **Tower Upgrades**: Upgrade existing towers for better performance
3. **Special Abilities**: Player spells or abilities with cooldowns
4. **Multiplayer**: Cooperative defense mode
5. **Campaign Mode**: Progressive levels with story
6. **Boss Enemies**: Large enemies with special mechanics
7. **Power-ups**: Temporary buffs for player or defenses
8. **Pixel Art Sprites**: Replace placeholder graphics with proper pixel art

## Asset Guidelines

### Sprite Requirements
- 32x32 pixels for most entities
- PNG format with transparency
- Pixel art style for medieval fantasy theme

### Sound Requirements
- WAV or OGG format
- Keep file sizes reasonable (<1MB per sound)
- Medieval/fantasy themed audio

## Contributing

When contributing to the codebase:

1. Follow Python PEP 8 style guidelines
2. Add docstrings to all classes and methods
3. Write unit tests for new features
4. Update this documentation for significant changes
5. Test thoroughly before submitting changes

## Debug Features

Set debug flags in game files for development:
- Tower range visualization: Set debug flag in `towers.py`
- Ally attack range: Set debug flag in `allies.py`
- FPS display: Add to HUD rendering
- Collision boxes: Add rectangle rendering in entity render methods 