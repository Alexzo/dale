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
ENEMY_SIZE = 32
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