# config.py
import os

# Paths
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS_PATH = os.path.join(PROJECT_ROOT, "assets")

# Window Settings
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 640
FPS = 60
TILE_SIZE = 32
MAP_WIDTH = 30
MAP_HEIGHT = 20

# Colors
BROWN = (139, 69, 19)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GRAY = (50, 50, 50)
DEEP_SKY_BLUE = (0, 191, 255)
GOLD = (255, 215, 0)
ORANGE = (255, 165, 0)

# HUD Settings
HUD_HEIGHT = 80

# Game Settings
PLAYER_SPEED = 3
ENEMY_SPEED = 1
BOSS_SPEED = 0.5
COMPANION_SPEED = 3
PROJECTILE_SPEED = 5
SHOOT_COOLDOWN = 20  # Frames
ATTACK_COOLDOWN = 1  # Seconds