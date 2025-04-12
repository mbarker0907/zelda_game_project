# bush.py
import pygame
import random
from config import *

class Bush:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.sprite = pygame.image.load(os.path.join(ASSETS_PATH, "objects/bush.png")).convert_alpha()
        self.destroyed = False

    def check_projectile_collision(self, projectiles):
        for projectile in projectiles:
            if self.rect.colliderect(projectile.rect) and not self.destroyed:
                self.destroyed = True
                return projectile
        return None

    def drop_item(self, world):
        if random.random() < 0.2:  # 20% chance to drop gold
            world.drop_gold(self.rect.centerx, self.rect.centery, 5)

    def draw(self, screen):
        if not self.destroyed:
            screen.blit(self.sprite, self.rect)