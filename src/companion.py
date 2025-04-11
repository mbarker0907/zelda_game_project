import pygame
import os
import random

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Companion:
    def __init__(self, x, y, companion_type):
        self.type = companion_type
        self.rect = pygame.Rect(x, y, 32, 32)  # Match the frame size (32x32)
        self.speed = 2
        # Load sprite sheet
        sprite_path = "assets/companions/cat.png" if companion_type == "cat" else "assets/companions/dog.png"
        self.sprite_sheet = pygame.image.load(os.path.join(PROJECT_ROOT, sprite_path)).convert_alpha()
        # Validate sprite sheet dimensions
        if self.sprite_sheet.get_width() != 96 or self.sprite_sheet.get_height() != 128:
            raise ValueError(f"{self.type} sprite sheet dimensions are {self.sprite_sheet.get_width()}x{self.sprite_sheet.get_height()}, expected 96x128")
        # Split into frames
        self.frames = {"down": [], "left": [], "right": [], "up": []}
        directions = ["down", "left", "right", "up"]
        for row, direction in enumerate(directions):
            for col in range(3):
                frame = self.sprite_sheet.subsurface((col * 32, row * 32, 32, 32))
                self.frames[direction].append(frame)
        self.current_direction = "down"
        self.current_frame = 0
        self.animation_speed = 0.15
        self.animation_counter = 0
        # Companion stats
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 50
        self.attack = 1

    def update(self, target_rect, enemies, other_companion=None):
        # Follow the target (player or other companion)
        dx = target_rect.centerx - self.rect.centerx
        dy = target_rect.centery - self.rect.centery
        dist = (dx ** 2 + dy ** 2) ** 0.5
        target_dist = 60 if self.type == "cat" else 80
        if dist > target_dist:
            dx, dy = dx / dist, dy / dist
            self.rect.x += dx * self.speed
            self.rect.y += dy * self.speed
            # Update direction based on movement
            if abs(dx) > abs(dy):
                self.current_direction = "right" if dx > 0 else "left"
            else:
                self.current_direction = "down" if dy > 0 else "up"
            # Update animation
            self.animation_counter += self.animation_speed
            if self.animation_counter >= 1:
                self.current_frame = (self.current_frame + 1) % 3
                self.animation_counter = 0
        # Avoid overlapping with the other companion
        if other_companion:
            dx = other_companion.rect.centerx - self.rect.centerx
            dy = other_companion.rect.centery - self.rect.centery
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist < 32 and dist > 0:
                dx, dy = dx / dist, dy / dist
                self.rect.x -= dx * self.speed
                self.rect.y -= dy * self.speed
        # Attack enemies
        for enemy in enemies:
            if self.rect.colliderect(enemy.rect):
                enemy.health -= self.attack
                self.experience += 5
                if self.experience >= self.exp_to_next_level:
                    self.level += 1
                    self.experience -= self.exp_to_next_level
                    self.exp_to_next_level *= 1.5
                    self.attack += 1
                    print(f"{self.type} leveled up to level {self.level}!")

    def draw(self, screen):
        screen.blit(self.frames[self.current_direction][self.current_frame], self.rect)