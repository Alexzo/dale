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
CASTLE_SIZE = 64
CASTLE_HEALTH = 500

# Projectile settings
ARROW_SPEED = 300
ARROW_SIZE = 8

# Game balance
WAVE_ENEMY_COUNT_BASE = 5
WAVE_ENEMY_COUNT_MULTIPLIER = 1.2
WAVE_DELAY = 5.0  # seconds between waves (reduced for testing)

# Input settings
KEY_UP = [pygame.K_w, pygame.K_UP]
KEY_DOWN = [pygame.K_s, pygame.K_DOWN]
KEY_LEFT = [pygame.K_a, pygame.K_LEFT]
KEY_RIGHT = [pygame.K_d, pygame.K_RIGHT]
KEY_SUMMON_ALLY = [pygame.K_SPACE]
KEY_BUILD_TOWER = [pygame.K_e]

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