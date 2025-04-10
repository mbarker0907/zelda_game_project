import pygame
import os

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Fireball:
    def __init__(self, x, y, vx, vy, fireball_sprites, explosion_sprites, fireball_animation_speed=0.3):
        # Center the 32x32 sprite, but keep a smaller hitbox for precision
        self.rect = pygame.Rect(x - 16, y - 16, 32, 32)  # 32x32 sprite, centered
        self.vx = vx
        self.vy = vy
        self.frame = 0
        self.animation_speed = fireball_animation_speed
        # Use the fireball sprites passed from Player
        self.frames = fireball_sprites  # List of 5 fireball frames (32x32)
        self.explosion_sprites = explosion_sprites  # List of 3 explosion frames
        self.sprite = self.frames[0]
        self.exploded = False  # Flag to indicate if the fireball has hit something

    def update(self, window_width, window_height):
        if self.exploded:
            return False  # Remove fireball after explosion
        # Update position
        self.rect.x += self.vx
        self.rect.y += self.vy
        # Update animation
        self.frame += self.animation_speed
        if self.frame >= len(self.frames):
            self.frame = 0
        self.sprite = self.frames[int(self.frame)]
        # Check if off-screen
        return (0 <= self.rect.x <= window_width and
                0 <= self.rect.y <= window_height)

    def explode(self):
        """Mark the fireball as exploded and return explosion data."""
        self.exploded = True
        return {
            "x": self.rect.centerx,
            "y": self.rect.centery,
            "frame": 0  # Start explosion animation at frame 0
        }

    def draw(self, screen):
        if not self.exploded:
            screen.blit(self.sprite, self.rect)