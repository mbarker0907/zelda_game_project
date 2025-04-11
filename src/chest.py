import pygame
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Chest:
    # **Initialization**
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.is_open = False
        self.item = "key"
        self.sprite = pygame.image.load(os.path.join(PROJECT_ROOT, "assets/objects/chest.png")).convert_alpha()
        self.open_sprite = pygame.image.load(os.path.join(PROJECT_ROOT, "assets/objects/chest_open.png")).convert_alpha()

    # **Check Collision**
    def check_collision(self, player_rect):
        if not self.is_open and self.rect.colliderect(player_rect):
            self.is_open = True
            return self.item
        return None

    # **Draw Chest**
    def draw(self, screen):
        sprite = self.open_sprite if self.is_open else self.sprite
        screen.blit(sprite, self.rect)