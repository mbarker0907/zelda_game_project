# projectile.py
import pygame
import math
from config import *

class Projectile:
    def __init__(self, x, y, direction_or_velocity, weapon_type, sprites=None, explosion_sprites=None, power=1):
        self.rect = pygame.Rect(x, y, 8, 8) if weapon_type in ["arrow", "ice_bolt", "bomb"] else pygame.Rect(x, y, 32, 32)
        self.weapon_type = weapon_type
        self.power = power
        self.explosion_timer = None
        self.explosion_radius = 50 if weapon_type == "bomb" else 0
        self.explosion_sprites = explosion_sprites
        self.current_frame = 0
        self.animation_speed = 0.2
        self.animation_counter = 0

        if isinstance(direction_or_velocity, tuple):  # Enemy projectile (vx, vy)
            self.vx, self.vy = direction_or_velocity
            self.speed = ((self.vx ** 2 + self.vy ** 2) ** 0.5)
            self.direction = math.degrees(math.atan2(self.vy, self.vx))
        else:  # Player projectile (direction in degrees)
            self.direction = direction_or_velocity
            self.speed = PROJECTILE_SPEED
            self.vx = math.cos(math.radians(self.direction)) * self.speed
            self.vy = math.sin(math.radians(self.direction)) * self.speed

        self.sprites = sprites  # For enemy projectiles (e.g., fireball)

    def update(self, window_width, window_height):
        if self.explosion_timer is not None:
            self.explosion_timer -= 1
            if self.explosion_timer <= 0:
                return False
            return True

        if self.weapon_type == "bomb":
            self.speed -= 0.1
            if self.speed <= 0:
                self.explosion_timer = 10
                return True

        self.rect.x += self.vx
        self.rect.y += self.vy

        if (self.rect.left < 0 or self.rect.right > window_width or
            self.rect.top < 0 or self.rect.bottom > window_height):
            return False

        if self.sprites:
            self.animation_counter += self.animation_speed
            if self.animation_counter >= 1:
                self.current_frame = (self.current_frame + 1) % len(self.sprites)
                self.animation_counter = 0
        return True

    def explode(self):
        if self.weapon_type == "bomb" and self.explosion_timer is not None:
            return {
                "rect": pygame.Rect(self.rect.centerx - self.explosion_radius,
                                   self.rect.centery - self.explosion_radius,
                                   self.explosion_radius * 2, self.explosion_radius * 2),
                "timer": 10
            }
        elif self.weapon_type == "fireball" and self.explosion_sprites:
            return {
                "x": self.rect.centerx,
                "y": self.rect.centery,
                "frame": 0,
                "sprites": self.explosion_sprites
            }
        return None

    def draw(self, screen):
        if self.explosion_timer is not None and self.weapon_type == "bomb":
            pygame.draw.circle(screen, ORANGE, self.rect.center, self.explosion_radius, 2)
        elif self.sprites:  # Enemy projectiles
            sprite = self.sprites[self.current_frame]
            sprite_rect = sprite.get_rect(center=self.rect.center)
            screen.blit(sprite, sprite_rect)
        else:  # Player projectiles
            color = (0, 0, 255) if self.weapon_type == "ice_bolt" else (255, 0, 0) if self.weapon_type == "bomb" else (255, 255, 0)
            pygame.draw.rect(screen, color, self.rect)