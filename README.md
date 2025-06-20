# Dale

A medieval fantasy-themed tower defense game with pixel art graphics where you defend magical castles while freely moving around the battlefield.

## Features

- **Hybrid Tower Defense**: Move freely while defending your castle
- **Resource Management**: Collect essence from defeated enemies
- **Summoning System**: Summon elvish warrior allies to fight automatically
- **Tower Building**: Build arrow towers to defend strategic positions
- **Medieval Fantasy Theme**: Pixel art style with magical elements

## Gameplay

- Defend your magical castle from waves of enemies
- Move your character freely around the battlefield
- Collect essence dropped by defeated enemies
- Use essence to either:
  - Summon elvish warrior allies
  - Build defensive arrow towers
- Allies will automatically attack nearby enemies
- Survive increasingly difficult waves

## Controls

- **WASD** / **Arrow Keys**: Move character
- **Mouse**: Interact with UI, place towers
- **Space**: Summon ally (if enough essence)
- **E**: Build tower (if enough essence)

## Installation

1. Install Python 3.8 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python main.py
   ```

## Project Structure

```
tower_defense_game/
├── main.py              # Game entry point
├── src/                 # Source code
│   ├── game/           # Core game logic
│   ├── entities/       # Game entities (player, enemies, towers, allies)
│   ├── ui/             # User interface components
│   ├── utils/          # Utility functions
│   └── backend/        # Simple data storage
├── assets/             # Game assets
│   ├── sprites/        # Pixel art sprites
│   ├── sounds/         # Audio files
│   └── maps/           # Level data
└── tests/              # Unit tests
```

## Development

This game is built using:
- **Python 3.8+**
- **Pygame** for graphics and input handling
- **SQLite** for simple data storage
- **Pixel Art** graphics style 