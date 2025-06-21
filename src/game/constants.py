"""
Game constants and numerical values for Dale.
Centralized location for all game balance parameters.
"""

# =============================================================================
# CHARACTER PROGRESSION
# =============================================================================
CHARACTER_BASE_HEALTH = 100
CHARACTER_HEALTH_PER_LEVEL = 2
CHARACTER_BASE_ATTACK = 35
CHARACTER_ATTACK_PER_LEVEL = 1
CHARACTER_BASE_SPEED = 150
CHARACTER_ATTACK_RANGE = 45
CHARACTER_ATTACK_RATE = 1.5  # Attacks per second
CHARACTER_KNOCKBACK = 20

# Experience system
EXP_BASE_REQUIREMENT = 100  # EXP needed for level 2
EXP_GROWTH_RATE = 1.5  # Multiplier for each level
EXP_PER_ENEMY_KILL = 25
EXP_PER_WAVE_COMPLETE = 50
EXP_PER_TOWER_BUILT = 10

# =============================================================================
# ENEMIES
# =============================================================================
ENEMY_BASE_HEALTH = 30
ENEMY_BASE_DAMAGE = 10
ENEMY_BASE_SPEED = 80
ENEMY_HEALTH_GROWTH_PER_WAVE = 5
ENEMY_DAMAGE_GROWTH_PER_WAVE = 2

# Enemy types
ORC_HEALTH_MULTIPLIER = 1.0
ORC_DAMAGE_MULTIPLIER = 1.0
ORC_SPEED_MULTIPLIER = 1.0

GOBLIN_HEALTH_MULTIPLIER = 0.7
GOBLIN_DAMAGE_MULTIPLIER = 0.8
GOBLIN_SPEED_MULTIPLIER = 1.3

# =============================================================================
# TOWERS
# =============================================================================
ARROW_TOWER_DAMAGE = 25
ARROW_TOWER_RANGE = 150
ARROW_TOWER_FIRE_RATE = 1.0  # Shots per second
ARROW_TOWER_COST = 50

# =============================================================================
# ALLIES
# =============================================================================
ALLY_HEALTH = 80
ALLY_DAMAGE = 20
ALLY_ATTACK_RATE = 0.8
ALLY_SPEED = 120
ALLY_COST = 75

# =============================================================================
# CASTLE
# =============================================================================
CASTLE_BASE_HEALTH = 500
CASTLE_WIDTH_PERCENT = 0.2  # 20% of screen width
CASTLE_HEIGHT_PERCENT = 0.8  # 80% of screen height

# =============================================================================
# WAVES AND SPAWNING
# =============================================================================
WAVE_ENEMY_COUNT_BASE = 5
WAVE_ENEMY_COUNT_MULTIPLIER = 1.3
WAVE_DELAY = 5.0  # Seconds between waves
ENEMY_SPAWN_INTERVAL = 1.0  # Seconds between individual enemy spawns

# =============================================================================
# RESOURCES
# =============================================================================
STARTING_ESSENCE = 100
ESSENCE_PER_ENEMY = 15
ESSENCE_PER_WAVE = 25

# =============================================================================
# PROJECTILES
# =============================================================================
ARROW_SPEED = 300
ARROW_DAMAGE = 25
PROJECTILE_LIFETIME = 3.0  # Seconds before auto-cleanup

# =============================================================================
# GAME MECHANICS
# =============================================================================
PATH_WIDTH = 40
WAYPOINT_RADIUS = 8
TOWER_SIZE = 32
PLAYER_SIZE = 48
# ENEMY_SIZE removed - now using specific sizes per enemy type (ORC_SIZE, URUK_HAI_SIZE)
ALLY_SIZE = 40
ARROW_SIZE = 8

# =============================================================================
# SCORING
# =============================================================================
POINTS_PER_ENEMY_KILL = 10
POINTS_PER_WAVE_COMPLETE = 100
POINTS_PER_TOWER_BUILT = 20
POINTS_PER_ALLY_SUMMONED = 30

# =============================================================================
# LEVEL REQUIREMENTS CALCULATION
# =============================================================================
def get_exp_requirement_for_level(level: int) -> int:
    """Calculate EXP required to reach a specific level."""
    if level <= 1:
        return 0
    return int(EXP_BASE_REQUIREMENT * (EXP_GROWTH_RATE ** (level - 2)))

def get_total_exp_for_level(level: int) -> int:
    """Calculate total EXP needed to reach a specific level from level 1."""
    total = 0
    for lvl in range(2, level + 1):
        total += get_exp_requirement_for_level(lvl)
    return total

def get_character_health_at_level(level: int) -> int:
    """Calculate character health at a specific level."""
    return CHARACTER_BASE_HEALTH + (level - 1) * CHARACTER_HEALTH_PER_LEVEL

def get_character_attack_at_level(level: int) -> int:
    """Calculate character attack power at a specific level."""
    return CHARACTER_BASE_ATTACK + (level - 1) * CHARACTER_ATTACK_PER_LEVEL 

# Tower upgrade system constants
TOWER_MAX_LEVEL = 5
TOWER_STARTING_LEVEL = 1

# Tower upgrade costs (essence cost for each level)
TOWER_UPGRADE_COSTS = {
    2: 75,   # Level 1 -> 2: 75 essence
    3: 100,  # Level 2 -> 3: 100 essence  
    4: 150,  # Level 3 -> 4: 150 essence
    5: 200   # Level 4 -> 5: 200 essence
}

# Tower repair costs (essence cost based on tower level)
TOWER_REPAIR_BASE_COST = 25      # Base repair cost
TOWER_REPAIR_COST_PER_LEVEL = 10 # Additional cost per tower level
TOWER_REPAIR_HEALTH_PERCENT = 0.5 # Repair restores 50% of max health

# Tower stat bonuses per level
TOWER_HEALTH_PER_LEVEL = 25        # +25 health per level
TOWER_DAMAGE_BONUS_PER_LEVEL = 8   # +8 damage per level
TOWER_ATTACK_SPEED_BONUS_EVERY_2_LEVELS = 0.2  # +0.2 attacks/sec every 2 levels

# Base tower stats (level 1)
TOWER_BASE_HEALTH = 100
TOWER_BASE_DAMAGE = 25      # From settings.py ARROW_TOWER_DAMAGE
TOWER_BASE_ATTACK_SPEED = 1.0  # From settings.py ARROW_TOWER_FIRE_RATE
TOWER_BASE_RANGE = 150      # From settings.py ARROW_TOWER_RANGE

# Visual indicators for tower levels
TOWER_LEVEL_COLORS = {
    1: (139, 69, 19),    # Brown (basic)
    2: (160, 82, 45),    # Saddle brown  
    3: (205, 133, 63),   # Peru
    4: (218, 165, 32),   # Goldenrod
    5: (255, 215, 0)     # Gold (max level)
}

# Enemy type constants - Orcs (basic) and Uruk Hai (advanced)
# Orc stats (basic enemy type)
ORC_HEALTH = 30
ORC_SPEED = 50
ORC_DAMAGE = 10
ORC_SIZE = 24
ORC_COLOR = (0, 100, 0)  # Dark green

# Uruk Hai stats (advanced enemy type - stronger than Orcs)
URUK_HAI_HEALTH = 50      # +20 health over Orcs
URUK_HAI_SPEED = 60       # +10 speed over Orcs  
URUK_HAI_DAMAGE = 15      # +5 damage over Orcs
URUK_HAI_SIZE = 28        # Slightly larger than Orcs
URUK_HAI_COLOR = (40, 40, 40)  # Dark gray/black

# Enemy spawning ratios (per wave)
ORC_SPAWN_RATIO = 0.7     # 70% of enemies are Orcs
URUK_HAI_SPAWN_RATIO = 0.3  # 30% of enemies are Uruk Hai

# Enemy wave progression
URUK_HAI_START_WAVE = 3   # Uruk Hai start appearing from wave 3

# Enemy combat behavior constants
ENEMY_ATTACK_RANGE = 200         # Range at which enemies can attack towers/castle (much increased)
ENEMY_PROJECTILE_SPEED = 250     # Speed of enemy arrows (increased)
ENEMY_PROJECTILE_DAMAGE = 1      # Damage dealt by enemy projectiles to towers
ENEMY_TOWER_DETECTION_RANGE = 220  # Range to detect towers while moving (much increased)
ENEMY_ATTACK_RATE = 2.5          # Attacks per second (increased again)
ENEMY_CASTLE_SIEGE_DISTANCE = 250  # Distance from castle where enemies stop to attack (increased for multiple routes)

# Enemy AI states
ENEMY_STATE_MOVING = "moving"
ENEMY_STATE_ATTACKING_TOWER = "attacking_tower"  
ENEMY_STATE_ATTACKING_CASTLE = "attacking_castle" 