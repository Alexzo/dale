# Dale
## Medieval Fantasy Tower Defense

A rich medieval fantasy tower defense game featuring **tower upgrades**, character progression, custom sprite support, and dynamic combat. Play as **Thranduil**, an elvish warrior defending your castle while gaining experience and growing stronger with each battle.

![Game Features](https://img.shields.io/badge/Features-Tower%20Upgrades%20%7C%20Save%20System%20%7C%20Character%20Progression%20%7C%20Custom%20Sprites-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Pygame](https://img.shields.io/badge/Pygame-Graphics-red)

## 🎮 Key Features

### 🏗️ **5-Level Tower Upgrade System**
- **Progressive Upgrades**: Towers can be upgraded from Level 1 to Level 5
- **Stat Scaling**: Each upgrade increases health (+25), damage (+8), and fire rate (every 2 levels)
- **Visual Progression**: Towers change appearance with custom sprites or color progression
- **Strategic Costs**: Upgrade costs: 75, 100, 150, 200 essence for levels 2-5
- **Custom Sprites**: Support for your own tower artwork with automatic detection

### 🏰 **Hybrid Tower Defense Combat**
- **Free Movement**: Move your elvish warrior freely around the battlefield
- **Melee Combat**: Attack enemies directly with your sword using directional animations
- **Strategic Defense**: Build and upgrade arrow towers while personally fighting
- **Interactive Towers**: Click towers to select them and view upgrade options
- **Path-Based Enemies**: Multiple enemy routes targeting different castle sections

### 💾 **Complete Save System** 
- **Continue Games**: Resume exactly where you left off with full game state preservation
- **Tower Persistence**: Tower levels and upgrades are saved across sessions
- **Smart Save Management**: Automatic cleanup and single-save-slot system
- **Session Tracking**: All progress saved including wave, score, essence, and castle health

### ⚔️ **Character Progression System**
- **Leveling Up**: Gain experience from killing enemies, completing waves, and building towers
- **Stat Growth**: +2 Health and +1 Attack per level with full heal on level up
- **Persistent Progress**: Character level and stats carry over between game sessions
- **Customizable Name**: Personalize your character (default: Thranduil)

### 🎨 **Rich Visual System**
- **Custom Tower Sprites**: Use your own artwork for each tower level
- **Directional Animations**: Character faces and animates in 4 directions (up/down/left/right)
- **Attack Animations**: Sword combat with direction-specific attack sequences
- **Enhanced Visuals**: Larger towers (56px) for better visibility and interaction
- **Environment Assets**: Trees, rocks, terrain textures, and path materials

### 🏗️ **Strategic Gameplay**
- **Resource Management**: Collect essence from defeated enemies
- **Tower Strategy**: Build and upgrade towers for maximum effectiveness
- **Smart Building**: Towers cannot be placed on enemy paths (visual no-build zones)
- **Ally System**: Summon elvish warriors that fight automatically
- **Wave Progression**: Increasingly difficult enemy waves with scaling rewards

## 🎯 Gameplay Overview

**Defend Your Castle**: Protect a large, detailed castle on the right side of the battlefield from waves of enemies that follow predetermined paths.

**Character Combat**: Use WASD to move and F/Shift to attack enemies directly with your sword. Each kill grants experience and essence.

**Tower Strategy**: Build arrow towers (50 essence) and upgrade them through 5 levels for increasing power. Click towers to select and view upgrade options.

**Strategic Building**: Spend essence to build arrow towers or summon elvish allies (75 essence). Towers auto-target enemies within range and become more powerful with upgrades.

**Progression System**: Gain experience from combat, level up for permanent stat increases, and carry your character's growth across all game sessions.

## 🎮 Controls

### Movement & Combat
- **WASD** / **Arrow Keys**: Move character in 4 directions
- **F** / **Shift**: Sword attacks with directional animations
- **Mouse Click**: Place towers at cursor location or select existing towers

### Tower Management
- **Click Tower**: Select tower to view stats and upgrade options
- **U**: Upgrade selected tower (if affordable and upgradeable)
- **E**: Build arrow tower near player (50 essence)

### Actions
- **Space**: Summon elvish ally near player (75 essence)
- **B**: Toggle no-build zone visibility
- **ESC**: Open pause menu with save options

### Menus
- **N**: Edit character name (main menu)
- **C**: Continue saved game (main menu)
- **Enter**: Start new game / Resume / Confirm actions

## 🏗️ Tower Upgrade System

### Upgrade Progression
| Level | Cost | Health | Damage | Fire Rate | Visual |
|-------|------|--------|---------|-----------|--------|
| **1** | -    | 100    | 25      | 1.0/sec   | Brown  |
| **2** | 75   | 125    | 33      | 1.2/sec   | Gray   |
| **3** | 100  | 150    | 41      | 1.2/sec   | Silver |
| **4** | 150  | 175    | 49      | 1.4/sec   | Gold   |
| **5** | 200  | 200    | 57      | 1.4/sec   | Bright Gold |

### How to Upgrade
1. **Build a tower** using E key or clicking the Tower button
2. **Click the tower** to select it and view current stats
3. **Press U** or click the "Upgrade" button in the HUD
4. **Watch the tower** change appearance and become more powerful!

### Custom Tower Sprites
Add your own tower artwork! Place files named:
```
assets/sprites/towers/tower_level_1.png
assets/sprites/towers/tower_level_2.png
assets/sprites/towers/tower_level_3.png
assets/sprites/towers/tower_level_4.png
assets/sprites/towers/tower_level_5.png
```

The game automatically detects and uses your custom sprites. See `tower_sprite_guide.md` for detailed instructions.

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
- **Tower levels and upgrades**
- Castle health and time elapsed
- Tower and ally positions/health
- Character progression and level

## 📈 Character Progression

### Experience Sources
- **Enemy Kills**: 25 EXP per enemy defeated
- **Wave Completion**: 50 EXP per wave completed  
- **Tower Building**: 10 EXP per tower constructed
- **Tower Upgrades**: 15 EXP per tower upgraded

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
- **Storage**: 100MB for game files and assets
- **Display**: 1280x720 minimum resolution

## 🗂️ Project Structure

```
dale/
├── main.py                          # Game entry point
├── tower_sprite_guide.md            # Guide for custom tower artwork
├── src/
│   ├── game/
│   │   ├── game_engine.py          # Main game loop and logic
│   │   ├── game_state.py           # State management and save/load
│   │   ├── character_progression.py # Leveling and EXP system
│   │   ├── constants.py            # Game balance and tower upgrade values
│   │   └── settings.py             # Display and control settings
│   ├── entities/
│   │   ├── player.py               # Player character with combat
│   │   ├── enemies.py              # Enemy AI and movement
│   │   ├── towers.py               # Tower system with 5-level upgrades
│   │   ├── allies.py               # Summoned ally AI
│   │   └── projectiles.py          # Arrow projectile physics
│   ├── ui/
│   │   ├── menus.py                # Main menu, pause menu, game over
│   │   ├── hud.py                  # In-game UI with tower upgrade interface
│   │   └── buttons.py              # UI interaction components
│   ├── utils/
│   │   ├── sprites.py              # Sprite loading with custom tower support
│   │   ├── animations.py           # Animation system with directions
│   │   └── sounds.py               # Audio management (placeholder)
│   └── backend/
│       └── database.py             # SQLite save system and progression
├── assets/
│   └── sprites/
│       ├── towers/                 # Custom tower level sprites
│       ├── environment/            # Trees, rocks, terrain textures
│       └── ...                     # Character and entity sprites
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
- **Essence per Enemy**: 15
- **Arrow Tower Cost**: 50 essence
- **Tower Upgrade Costs**: 75, 100, 150, 200 essence
- **Ally Summon Cost**: 75 essence

### Towers & Upgrades
- **Tower Range**: 150 pixels (all levels)
- **Tower Size**: 56x56 pixels for better visibility
- **Base Damage**: 25 (Level 1) → 57 (Level 5)
- **Base Health**: 100 (Level 1) → 200 (Level 5)
- **Fire Rate**: 1.0/sec (Level 1) → 1.4/sec (Level 5)

### Allies & Combat
- **Ally Health**: 100 HP
- **Ally Attack**: 30 damage
- **Castle Health**: 500 HP
- **Enemy Damage to Castle**: 10 HP

### Progression
- **Wave Delay**: 5 seconds between waves
- **Enemy Health**: 30 HP (scales with waves)
- **Enemy Routes**: 3 different paths to castle

## 🚀 Recent Updates

### Version History
- **v2.0** (Latest): 🏗️ **Tower Upgrade System** with 5 levels and custom sprite support
- **v1.3**: Complete save game system with continue functionality
- **v1.2**: Character progression with persistent leveling and EXP
- **v1.1**: Directional animations and attack animation system  
- **v1.0**: Core tower defense with melee combat and strategic building

### Latest Features (v2.0)
- 🏗️ **5-Level Tower Upgrades**: Progressive stat scaling and visual changes
- 🎨 **Custom Sprite Support**: Use your own tower artwork with automatic detection
- 📏 **Enhanced Visuals**: Larger towers (56px) for better visibility
- 🔧 **Bug Fixes**: Fixed essence spending and upgrade coordination
- 📖 **Tower Sprite Guide**: Complete documentation for custom artwork
- 🌲 **Environment Assets**: Trees, rocks, and terrain textures
- 💾 **Enhanced Save System**: Tower levels persist across sessions
- 🎯 **Improved UI**: Tower selection and upgrade interface

### What's New in Tower Upgrades
- **Progressive Power**: Each level significantly increases tower effectiveness
- **Visual Feedback**: Towers change appearance as they upgrade
- **Strategic Depth**: Choose when and which towers to upgrade
- **Resource Management**: Balance between new towers and upgrades
- **Custom Artwork**: Replace default towers with your own sprites

## 🎨 Custom Content

### Tower Sprites
Create your own tower artwork! The game supports:
- **Multiple naming conventions**: `tower_level_X.png`, `arrow_tower_level_X.png`, etc.
- **Automatic scaling**: Your sprites are resized to 56x56 pixels
- **Smart fallbacks**: Game works with or without custom sprites
- **Design freedom**: Any art style from pixel art to detailed illustrations

### Asset Guidelines
- **Format**: PNG with transparency support
- **Recommended Size**: 56x56 pixels (scaled automatically)
- **Style**: Consistent visual progression showing power increase
- **Placement**: `assets/sprites/towers/` directory

See `tower_sprite_guide.md` for complete instructions and design tips!

## 🤝 Contributing

Dale is open source and welcomes contributions! Areas for improvement:
- Additional tower types and upgrade paths
- More enemy varieties and special abilities
- Sound effects and background music
- Additional character classes or customization
- Multiplayer or co-op functionality
- More custom sprite categories

## 📄 License

This project is licensed under the MIT License - see the repository for details.

---

**Ready to build, upgrade, and defend your realm? Download Dale and begin your medieval fantasy tower defense adventure!** 🏰⚔️🔧 