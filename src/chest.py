# chest.py
import pygame
import random
from config import *

class Chest:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.is_open = False
        self.item = random.choice(["key", "bomb", "health_potion", "ice_bolt"])
        self.sprite = pygame.image.load(os.path.join(ASSETS_PATH, "objects/chest.png")).convert_alpha()
        self.open_sprite = pygame.image.load(os.path.join(ASSETS_PATH, "objects/chest_open.png")).convert_alpha()

    def check_collision(self, player_rect):
        if not self.is_open and self.rect.colliderect(player_rect):
            self.is_open = True
            return self.item
        return None

    def draw(self, screen):
        sprite = self.open_sprite if self.is_open else self.sprite
        screen.blit(sprite, self.rect)