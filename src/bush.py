import pygame
import os

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Bush:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)  # 32x32 collision box matching the sprite
        bush_path = os.path.join(PROJECT_ROOT, "assets/objects/bush.png")
        if not os.path.exists(bush_path):
            raise FileNotFoundError(f"Bush image not found at: {bush_path}")
        self.sprite = pygame.image.load(bush_path).convert_alpha()
        self.destroyed = False  # Flag to indicate if the bush has been hit

    def check_fireball_collision(self, fireballs):
        """Check if a fireball collides with the bush. Return the fireball that hit, if any."""
        if self.destroyed:
            return None
        for fireball in fireballs:
            if not fireball.exploded and self.rect.colliderect(fireball.rect):
                self.destroyed = True
                return fireball  # Return the fireball that caused the collision
        return None

    def draw(self, screen):
        """Draw the bush if it hasn’t been destroyed."""
        if not self.destroyed:
            screen.blit(self.sprite, self.rect)