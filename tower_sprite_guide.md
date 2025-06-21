# 🏗️ Tower Level Sprite Guide

## Overview
The tower upgrade system now supports custom sprites for each tower level! You can replace the default color-tinted towers with your own artwork for each level.

## 🎨 Sprite Naming Conventions

The game will look for your tower sprites in this priority order:

### Primary Naming Convention
```
tower_level_1.png  # Level 1 tower
tower_level_2.png  # Level 2 tower  
tower_level_3.png  # Level 3 tower
tower_level_4.png  # Level 4 tower
tower_level_5.png  # Level 5 tower
```

### Alternative Naming Conventions (fallbacks)
If the primary names aren't found, the game will try these alternatives:
```
arrow_tower_level_1.png
arrow_tower_level_2.png
arrow_tower_level_3.png
arrow_tower_level_4.png
arrow_tower_level_5.png
```

```
arrow_tower_lv1.png
arrow_tower_lv2.png
arrow_tower_lv3.png
arrow_tower_lv4.png
arrow_tower_lv5.png
```

```
tower_1.png
tower_2.png
tower_3.png
tower_4.png
tower_5.png
```

```
tower_lvl_1.png
tower_lvl_2.png
tower_lvl_3.png
tower_lvl_4.png
tower_lvl_5.png
```

## 📁 Where to Place Your Sprites

Add your tower sprite files to:
```
dale/assets/sprites/towers/
```

Or alternatively:
```
dale/assets/sprites/
```

## 🎯 Sprite Specifications

### Recommended Dimensions
- **Size**: 64x64 pixels (matches TOWER_SIZE)
- **Format**: PNG with transparency support
- **Style**: Pixel art or detailed artwork

### Visual Progression Ideas
Design your towers to show clear progression:

**Level 1 (Basic)**: 
- Simple wooden tower
- Basic materials
- Brown/natural colors

**Level 2 (Improved)**:
- Stone reinforcements
- Better construction
- Stone gray colors

**Level 3 (Advanced)**:
- Metal reinforcements
- Sharper details
- Steel/silver accents

**Level 4 (Superior)**:
- Ornate decorations
- Magical elements
- Golden accents

**Level 5 (Maximum)**:
- Legendary appearance
- Glowing effects
- Pure gold/mythril materials

## 🔧 Fallback System

The game has a smart fallback system:

1. **Custom Sprites**: Uses your level-specific images if found
2. **Color Tinting**: Falls back to base tower with color overlay
3. **Procedural**: Creates simple colored rectangles with level numbers

## 🎮 Testing Your Sprites

1. Place your sprite files in the assets directory
2. Run the game
3. Build a tower and upgrade it
4. Watch console messages to see which sprites are being loaded:
   ```
   🎨 Using level-specific sprite: tower_level_2
   🎨 Using alternative sprite: arrow_tower_lv3
   🎨 Using tinted base sprite for level 4
   ```

## ✨ Example Asset Structure

```
dale/
├── assets/
│   └── sprites/
│       ├── towers/
│       │   ├── tower_level_1.png
│       │   ├── tower_level_2.png
│       │   ├── tower_level_3.png
│       │   ├── tower_level_4.png
│       │   └── tower_level_5.png
│       └── arrow_tower.png (base sprite)
```

## 🎨 Creating Your Tower Sprites

### Design Tips:
- **Consistent Style**: Keep all levels in the same art style
- **Clear Progression**: Each level should look obviously more powerful
- **Good Contrast**: Make sure the tower stands out on the battlefield
- **Details**: Add unique elements like crystals, runes, or armor plating

### Tools You Can Use:
- **Pixel Art**: Aseprite, Piskel, Photoshop
- **Digital Art**: GIMP, Krita, Photoshop
- **AI Generated**: Midjourney, DALL-E (with editing)

## 🚀 Pro Tips

1. **Batch Creation**: Create all 5 levels at once for consistency
2. **Animation Ready**: Design with future animation in mind
3. **Modular Design**: Consider separate elements (base, turret, decorations)
4. **Color Coding**: Use the existing color scheme as inspiration:
   - Level 1: Brown (#8B4513)
   - Level 2: Saddle Brown (#A0522D) 
   - Level 3: Peru (#CD853F)
   - Level 4: Goldenrod (#DAA520)
   - Level 5: Gold (#FFD700)

Start with simple recolors and gradually add more unique elements for each level! 