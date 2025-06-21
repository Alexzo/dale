"""
Game settings and constants.
"""

import pygame

# Screen settings
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# Colors (RGB values)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
DARK_GREEN = (0, 100, 0)
GOLD = (255, 215, 0)

# Game constants
TILE_SIZE = 32
GRID_WIDTH = SCREEN_WIDTH // TILE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // TILE_SIZE

# Player settings
PLAYER_SPEED = 200  # pixels per second
PLAYER_SIZE = 32
PLAYER_HEALTH = 100

# Player combat settings
PLAYER_ATTACK_DAMAGE = 35
PLAYER_ATTACK_RANGE = 45  # Melee range in pixels
PLAYER_ATTACK_RATE = 1.5  # Attacks per second
PLAYER_ATTACK_KNOCKBACK = 20  # Knockback distance

# Enemy settings
ENEMY_SPEED = 50
ENEMY_SIZE = 24
ENEMY_HEALTH = 30
ENEMY_DAMAGE = 10

# Tower settings
TOWER_SIZE = 32
ARROW_TOWER_COST = 50
ARROW_TOWER_DAMAGE = 25
ARROW_TOWER_RANGE = 150
ARROW_TOWER_FIRE_RATE = 1.0  # shots per second

# Ally settings
ALLY_SIZE = 28
ALLY_COST = 75
ALLY_HEALTH = 60
ALLY_DAMAGE = 20
ALLY_SPEED = 80
ALLY_ATTACK_RANGE = 100

# Resource settings
ESSENCE_PER_ENEMY = 15
STARTING_ESSENCE = 100

# Castle settings
CASTLE_WIDTH = int(SCREEN_WIDTH * 0.2)  # Castle occupies 20% of screen width (256 pixels)
CASTLE_HEIGHT = SCREEN_HEIGHT - 80  # Castle takes full height minus HUD (640 pixels)
CASTLE_SIZE = CASTLE_WIDTH  # Keep for backward compatibility
CASTLE_HEALTH = 500

# Castle position (right side of map)
CASTLE_X = SCREEN_WIDTH - CASTLE_WIDTH // 2  # Right edge minus half width (1152)
CASTLE_Y = (SCREEN_HEIGHT - 80) // 2  # Center vertically (320)

# Projectile settings
ARROW_SPEED = 300
ARROW_SIZE = 8

# Game balance
WAVE_ENEMY_COUNT_BASE = 5
WAVE_ENEMY_COUNT_MULTIPLIER = 1.2
WAVE_DELAY = 5.0  # seconds between waves (reduced for testing)

# Enemy Path System - Updated to target the new castle position
ENEMY_PATH = [
    (50, 150),       # Start: Left side entrance
    (200, 150),      # Move right (horizontal)
    (200, 80),       # Turn up (vertical) 
    (500, 80),       # Move right along top (horizontal)
    (500, 250),      # Turn down (vertical)
    (800, 250),      # Move right toward castle area (horizontal)
    (800, 400),      # Turn down (vertical)
    (600, 400),      # Move left (horizontal)
    (600, 320),      # Turn up toward castle (vertical)
    (900, 320),      # Move right to castle approach (horizontal)
    (1000, 320),     # Get closer to castle (horizontal)
    (CASTLE_X, CASTLE_Y)  # Final: New castle center position
]

# Path visualization
PATH_COLOR = (255, 255, 0, 128)  # Semi-transparent yellow
PATH_WIDTH = 15
WAYPOINT_RADIUS = 8

# Input settings
KEY_UP = [pygame.K_w, pygame.K_UP]
KEY_DOWN = [pygame.K_s, pygame.K_DOWN]
KEY_LEFT = [pygame.K_a, pygame.K_LEFT]
KEY_RIGHT = [pygame.K_d, pygame.K_RIGHT]
KEY_ATTACK = [pygame.K_LSHIFT, pygame.K_RSHIFT, pygame.K_f]  # Left Shift, Right Shift, or F key
KEY_SUMMON_ALLY = [pygame.K_SPACE]
KEY_BUILD_TOWER = [pygame.K_e]
KEY_TOGGLE_BUILD_ZONES = [pygame.K_b]  # B key to toggle no-build zone visibility

# Asset paths
ASSETS_DIR = "assets"
SPRITES_DIR = f"{ASSETS_DIR}/sprites"
SOUNDS_DIR = f"{ASSETS_DIR}/sounds"
MAPS_DIR = f"{ASSETS_DIR}/maps"

# UI settings
HUD_HEIGHT = 80
BUTTON_WIDTH = 120
BUTTON_HEIGHT = 40
FONT_SIZE_SMALL = 16
FONT_SIZE_MEDIUM = 24
FONT_SIZE_LARGE = 32 