# 🏰 Dale - Enemy Combat System

## New Combat Features

The enemy combat system has been completely redesigned to create a more dynamic and challenging tower defense experience.

### 🏹 Enemy Attack Behavior

#### Tower Attacks
- **Range Detection**: Enemies detect towers within 100 pixels while moving
- **Arrow Attacks**: Enemies shoot red-tinted arrows at towers when in range
- **Damage**: Enemy projectiles deal 5 damage to towers
- **Continuous Fire**: Enemies attack towers at 1.5 attacks per second
- **Movement**: Enemies continue moving while attacking (don't stop for towers)

#### Castle Siege
- **Siege Mode**: When enemies reach within 60 pixels of the castle, they stop and enter siege mode
- **Melee Attacks**: Enemies attack the castle directly with their melee weapons
- **Persistent**: Enemies remain at the castle until killed or the castle is destroyed
- **No Escape**: Enemies no longer disappear after reaching the castle

### 🤖 Enemy AI States

1. **MOVING**: Default state - moving along path, checking for towers to attack
2. **ATTACKING_TOWER**: Shooting arrows at detected towers while continuing movement
3. **ATTACKING_CASTLE**: Stopped at castle, continuously attacking with melee weapons

### ⚔️ Combat Mechanics

#### Enemy Projectiles
- **Visual**: Red-tinted arrows to distinguish from tower arrows
- **Speed**: 200 pixels per second
- **Range**: Limited by projectile lifetime (5 seconds)
- **Collision**: Can damage and destroy towers

#### Tower Vulnerability
- **Health System**: Towers can now be damaged and destroyed by enemy fire
- **Defense**: Higher level towers have more health to withstand attacks
- **Strategic Placement**: Towers need protection from enemy fire

#### Castle Defense
- **No Auto-Kill**: Enemies no longer disappear when reaching the castle
- **Active Defense**: Players must actively kill enemies besieging the castle
- **Pressure**: Constant pressure on castle health from sieging enemies

### 🎮 Gameplay Impact

#### Strategy Changes
- **Tower Placement**: More strategic placement needed to avoid enemy fire
- **Active Defense**: Players must actively engage enemies at the castle
- **Tower Protection**: Upgrading towers becomes more important for survivability
- **Resource Management**: Balance between building towers and maintaining defenses

#### Difficulty Scaling
- **Progressive Threat**: More enemies in later waves means more castle attackers
- **Multi-front Combat**: Players must manage tower attacks and castle defense simultaneously
- **Tactical Decisions**: Choose between advancing to kill enemies or defending key positions

### 🔧 Technical Implementation

#### Constants Added
```python
ENEMY_ATTACK_RANGE = 80          # Range for attacking towers/castle
ENEMY_PROJECTILE_SPEED = 200     # Speed of enemy arrows  
ENEMY_PROJECTILE_DAMAGE = 5      # Damage to towers
ENEMY_TOWER_DETECTION_RANGE = 100 # Range to detect towers while moving
ENEMY_ATTACK_RATE = 1.5          # Attacks per second
ENEMY_CASTLE_SIEGE_DISTANCE = 60  # Distance from castle to start siege
```

#### New Classes
- `EnemyArrow`: Projectile class for enemy attacks on towers
- Enhanced `Enemy` class with AI state management

#### AI State Machine
- State-based enemy behavior with proper transitions
- Separate update methods for each AI state
- Target acquisition and engagement logic

### 🎯 Testing the System

Run the test script to see the new combat system in action:

```bash
python3 test_enemy_combat.py
```

#### What to Observe
1. **Tower Attacks**: Build towers near enemy paths and watch enemies shoot at them
2. **Castle Siege**: Watch enemies stop at the castle and continuously attack
3. **Projectile Effects**: See enemy arrows flying toward towers
4. **Tower Destruction**: Let enemies destroy towers with sustained fire
5. **Persistent Enemies**: Notice enemies don't disappear after reaching castle

### ⚖️ Balance Considerations

#### Enemy Projectile Damage
- **Current**: 5 damage per arrow at 1.5 attacks/second = 7.5 DPS
- **Tower Health**: Level 1 towers have 100 health (13+ seconds to destroy)
- **Upgrade Importance**: Higher level towers survive longer under fire

#### Castle Siege Pressure
- **Multiple Attackers**: Several enemies can siege simultaneously
- **Melee Damage**: Direct application of enemy damage to castle health
- **Time Pressure**: Creates urgency to eliminate threats quickly

This combat system transforms Dale from a passive tower defense into an active combat experience where players must constantly engage threats while managing their defensive infrastructure. 