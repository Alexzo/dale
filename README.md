# Dale
## Medieval Fantasy Tower Defense

A rich medieval fantasy tower defense game featuring character progression, save systems, and dynamic combat. Play as **Thranduil**, an elvish warrior defending your castle while gaining experience and growing stronger with each battle.

![Game Features](https://img.shields.io/badge/Features-Save%20System%20%7C%20Character%20Progression%20%7C%20Combat-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Pygame](https://img.shields.io/badge/Pygame-Graphics-red)

## 🎮 Key Features

### 🏰 **Hybrid Tower Defense Combat**
- **Free Movement**: Move your elvish warrior freely around the battlefield
- **Melee Combat**: Attack enemies directly with your sword using directional animations
- **Strategic Defense**: Build arrow towers and summon allies while personally fighting
- **Path-Based Enemies**: Enemies follow specific routes to your castle

### 💾 **Complete Save System** 
- **Continue Games**: Resume exactly where you left off with full game state preservation
- **Smart Save Management**: Automatic cleanup and single-save-slot system
- **Session Tracking**: All progress saved including wave, score, essence, and castle health

### ⚔️ **Character Progression System**
- **Leveling Up**: Gain experience from killing enemies, completing waves, and building towers
- **Stat Growth**: +2 Health and +1 Attack per level with full heal on level up
- **Persistent Progress**: Character level and stats carry over between game sessions
- **Customizable Name**: Personalize your character (default: Thranduil)

### 🎨 **Rich Visual System**
- **Directional Animations**: Character faces and animates in 4 directions (up/down/left/right)
- **Attack Animations**: Sword combat with direction-specific attack sequences
- **Pixel Art Style**: Detailed sprites with smooth animation systems
- **Visual Feedback**: Path visualization, no-build zones, and UI indicators

### 🏗️ **Strategic Gameplay**
- **Resource Management**: Collect essence from defeated enemies
- **Smart Building**: Towers cannot be placed on enemy paths (visual no-build zones)
- **Ally System**: Summon elvish warriors that fight automatically
- **Wave Progression**: Increasingly difficult enemy waves with scaling rewards

## 🎯 Gameplay Overview

**Defend Your Castle**: Protect a large, detailed castle on the right side of the battlefield from waves of enemies that follow predetermined paths.

**Character Combat**: Use WASD to move and F/Shift to attack enemies directly with your sword. Each kill grants experience and essence.

**Strategic Building**: Spend essence to build arrow towers (50 essence) or summon elvish allies (75 essence). Towers auto-target enemies within range.

**Progression System**: Gain experience from combat, level up for permanent stat increases, and carry your character's growth across all game sessions.

## 🎮 Controls

### Movement & Combat
- **WASD** / **Arrow Keys**: Move character in 4 directions
- **F** / **Shift**: Sword attacks with directional animations
- **Mouse Click**: Place towers at cursor location

### Actions
- **Space**: Summon elvish ally near player (75 essence)
- **E**: Build arrow tower near player (50 essence)
- **B**: Toggle no-build zone visibility
- **ESC**: Open pause menu with save options

### Menus
- **N**: Edit character name (main menu)
- **C**: Continue saved game (main menu)
- **Enter**: Start new game / Resume / Confirm actions

## 💾 Save System

### How It Works
1. **During Game**: Press ESC → "Save & Quit to Menu" preserves complete game state
2. **Main Menu**: Shows saved game info if available:
   ```
   Continue Game Available:
   • Wave 5 - Score: 2500
   • 150 Essence - Castle: 450 HP
   • Time: 245.3s
   
   Press C to Continue Game
   Press ENTER for New Game
   ```
3. **Smart Management**: New games delete old saves, game over clears saves

### What's Saved
- Player position, health, and essence
- Current wave number and score
- Castle health and time elapsed
- Tower and ally positions/health
- Character progression and level

## 📈 Character Progression

### Experience Sources
- **Enemy Kills**: 25 EXP per enemy defeated
- **Wave Completion**: 50 EXP per wave completed  
- **Tower Building**: 10 EXP per tower constructed

### Level Benefits
- **Health**: +2 HP per level (starts at 50 HP)
- **Attack**: +1 Attack per level (starts at 35 damage)
- **Full Heal**: Complete health restoration on level up
- **EXP Requirements**: Level 2 needs 100 EXP, scaling by 1.5x per level

### Persistence
- Character level and stats carry over between all game sessions
- Character name customization with 20 character limit
- Career statistics tracking (games played, enemies killed, etc.)

## 🛠️ Installation & Setup

### Prerequisites
- **Python 3.8+** required
- **Pygame** for graphics and input
- **SQLite** for save data (included with Python)

### Quick Start
```bash
# Clone the repository
git clone https://github.com/Alexzo/dale.git
cd dale

# Install dependencies
pip install pygame

# Run the game
python main.py
```

### System Requirements
- **OS**: Windows, macOS, or Linux
- **RAM**: 512MB minimum
- **Storage**: 50MB for game files
- **Display**: 1200x800 minimum resolution

## 🗂️ Project Structure

```
dale/
├── main.py                          # Game entry point
├── src/
│   ├── game/
│   │   ├── game_engine.py          # Main game loop and logic
│   │   ├── game_state.py           # State management and save/load
│   │   ├── character_progression.py # Leveling and EXP system
│   │   ├── constants.py            # Game balance values
│   │   └── settings.py             # Display and control settings
│   ├── entities/
│   │   ├── player.py               # Player character with combat
│   │   ├── enemies.py              # Enemy AI and movement
│   │   ├── towers.py               # Arrow tower system
│   │   ├── allies.py               # Summoned ally AI
│   │   └── projectiles.py          # Arrow projectile physics
│   ├── ui/
│   │   ├── menus.py                # Main menu, pause menu, game over
│   │   ├── hud.py                  # In-game UI and stats display
│   │   └── buttons.py              # UI interaction components
│   ├── utils/
│   │   ├── sprites.py              # Sprite loading and management
│   │   ├── animations.py           # Animation system with directions
│   │   └── sounds.py               # Audio management (placeholder)
│   └── backend/
│       └── database.py             # SQLite save system and progression
├── assets/
│   └── sprites/                    # Character and entity sprites
└── README.md                       # This file
```

## 🎯 Game Balance

### Character Stats
- **Starting Health**: 50 HP (+2 per level)
- **Starting Attack**: 35 damage (+1 per level)
- **Attack Range**: 45 pixels
- **Attack Speed**: 1.5 attacks per second
- **Movement Speed**: 200 pixels per second

### Economy
- **Starting Essence**: 100
- **Essence per Enemy**: 10
- **Arrow Tower Cost**: 50 essence
- **Ally Summon Cost**: 75 essence

### Towers & Allies
- **Tower Range**: 150 pixels
- **Tower Damage**: 25 per shot
- **Tower Fire Rate**: 1 shot per second
- **Ally Health**: 100 HP
- **Ally Attack**: 30 damage

### Progression
- **Wave Delay**: 5 seconds between waves
- **Enemy Health**: 30 HP (scales with waves)
- **Castle Health**: 500 HP
- **Enemy Damage to Castle**: 10 HP

## 🚀 Recent Updates

### Version History
- **v1.3** (Latest): Complete save game system with continue functionality
- **v1.2**: Character progression with persistent leveling and EXP
- **v1.1**: Directional animations and attack animation system  
- **v1.0**: Core tower defense with melee combat and strategic building

### Latest Features
- 💾 **Save & Continue System**: Full game state persistence
- 📊 **Character Progression**: Persistent leveling across sessions
- 🎭 **Name Customization**: Personalize your character
- ⏸️ **Pause Menu**: Save/quit options during gameplay
- 🗺️ **Path Visualization**: Enemy routes with no-build zones
- 🏰 **Enhanced Castle**: Larger, more detailed castle design

## 🤝 Contributing

Dale is open source and welcomes contributions! Areas for improvement:
- Additional enemy types and behaviors
- More tower varieties and upgrade systems
- Sound effects and background music
- Additional character classes or customization
- Multiplayer or co-op functionality

## 📄 License

This project is licensed under the MIT License - see the repository for details.

---

**Ready to defend your realm? Download Dale and begin your medieval fantasy adventure!** 🏰⚔️ 