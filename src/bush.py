import pygame
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Bush:
    # **Initialization**
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.destroyed = False
        self.sprite = pygame.image.load(os.path.join(PROJECT_ROOT, "assets/objects/bush.png")).convert_alpha()

    # **Check Projectile Collision**
    def check_projectile_collision(self, projectiles):
        if self.destroyed:
            return None
        for projectile in projectiles:
            if self.rect.colliderect(projectile.rect):
                self.destroyed = True
                return projectile
        return None

    # **Draw Bush**
    def draw(self, screen):
        if not self.destroyed:
            screen.blit(self.sprite, self.rect)