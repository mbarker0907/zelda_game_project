import pygame
import os

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Chest:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)  # 32x32 collision box matching the sprite
        self.closed_sprite = pygame.image.load(os.path.join(PROJECT_ROOT, "assets/objects/chest_closed.png")).convert_alpha()
        self.open_sprite = pygame.image.load(os.path.join(PROJECT_ROOT, "assets/objects/chest_open.png")).convert_alpha()
        self.is_open = False  # Start closed
        self.item = "key"  # Item given when opened

    def check_collision(self, player_rect):
        """Check if the player collides with the chest. Open it and return the item if not already open."""
        if not self.is_open and self.rect.colliderect(player_rect):
            self.is_open = True
            return self.item
        return None

    def draw(self, screen):
        """Draw the chest based on its state."""
        if self.is_open:
            screen.blit(self.open_sprite, self.rect)
        else:
            screen.blit(self.closed_sprite, self.rect)