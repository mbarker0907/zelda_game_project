import pygame
import os

pygame.init()

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Construct the path to the fireball sprite sheet
fireball_path = os.path.join(PROJECT_ROOT, "assets/projectiles/fireball_sheet.png")
print(f"Attempting to load fireball sprite sheet from: {fireball_path}")

# Try to load the image
try:
    fireball_sheet = pygame.image.load(fireball_path).convert_alpha()
    print("Successfully loaded fireball sprite sheet!")
except Exception as e:
    print(f"Failed to load fireball sprite sheet: {e}")

pygame.quit()