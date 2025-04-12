import pygame
import random
import os
from config import *

class Companion:
    def __init__(self, x, y, companion_type, world):
        self.type = companion_type
        self.world = world  # Store the world reference
        self.speed = COMPANION_SPEED
        self.level = 1
        self.exp = 0
        self.exp_to_next_level = 50
        self.attack_cooldown = 0
        self.attack_flash = 0  # For attack animation
        self.level_up_flash = 0  # For level-up animation

        sprite_configs = {
            "cat": {
                "path": "companions/cat.png",
                "dimensions": (96, 128),
                "frame_size": (32, 32),
                "directions": ["down", "left", "right", "up"],
                "frames_per_direction": 3
            },
            "dog": {
                "path": "companions/dog.png",
                "dimensions": (96, 128),
                "frame_size": (32, 32),
                "directions": ["down", "left", "right", "up"],
                "frames_per_direction": 3
            }
        }

        config = sprite_configs[companion_type]
        sprite_path = config["path"]
        expected_dimensions = config["dimensions"]
        self.frame_size = config["frame_size"]
        self.directions = config["directions"]
        self.frames_per_direction = config["frames_per_direction"]

        self.rect = pygame.Rect(x, y, self.frame_size[0], self.frame_size[1])

        self.sprite_sheet = pygame.image.load(os.path.join(ASSETS_PATH, sprite_path)).convert_alpha()
        actual_dimensions = (self.sprite_sheet.get_width(), self.sprite_sheet.get_height())
        if actual_dimensions != expected_dimensions:
            raise ValueError(f"{self.type} sprite sheet dimensions are {actual_dimensions}, expected {expected_dimensions}")

        self.frames = {direction: [] for direction in self.directions}
        frame_width, frame_height = self.frame_size
        for row, direction in enumerate(self.directions):
            for col in range(self.frames_per_direction):
                frame = self.sprite_sheet.subsurface((col * frame_width, row * frame_height, frame_width, frame_height))
                # Scale the frame to match the rect size (32x32)
                frame = pygame.transform.scale(frame, (self.rect.width, self.rect.height))
                self.frames[direction].append(frame)

        self.current_direction = "down"
        self.current_frame = 0
        self.animation_speed = 0.15
        self.animation_counter = 0
        self.target = None  # Will be set by set_target

    def set_target(self, target):
        self.target = target  # Store the target (e.g., the player)

    def update(self, enemies, player=None):
        if not self.target:
            return

        target_rect = self.target.rect
        dx = target_rect.centerx - self.rect.centerx
        dy = target_rect.centery - self.rect.centery
        dist = (dx ** 2 + dy ** 2) ** 0.5

        if dist > 50:  # Only move if farther than 50 pixels
            if dist != 0:
                dx = dx / dist * self.speed
                dy = dy / dist * self.speed

            # Check for collisions with walls
            new_rect = self.rect.copy()
            new_rect.x += dx
            if not self.world.is_wall(new_rect.centerx, new_rect.centery):
                self.rect.x += dx

            new_rect = self.rect.copy()
            new_rect.y += dy
            if not self.world.is_wall(new_rect.centerx, new_rect.centery):
                self.rect.y += dy

            # Update animation
            self.animation_counter += self.animation_speed
            if self.animation_counter >= 1:
                self.current_frame = (self.current_frame + 1) % self.frames_per_direction
                self.animation_counter = 0

            # Update direction for animation
            if dx > 0:
                self.current_direction = "right"
            elif dx < 0:
                self.current_direction = "left"
            elif dy > 0:
                self.current_direction = "down"
            elif dy < 0:
                self.current_direction = "up"

        # Update attack and level-up effects
        if self.attack_flash > 0:
            self.attack_flash -= 1
        if self.level_up_flash > 0:
            self.level_up_flash -= 1

        # Handle attacking enemies
        self.attack_cooldown -= 1 / 60
        if self.attack_cooldown <= 0:
            for enemy in enemies:
                if not enemy.is_dying and self.rect.colliderect(enemy.rect):
                    enemy.health -= 1
                    self.exp += 10
                    self.attack_flash = 10  # Flash for 10 frames
                    if self.exp >= self.exp_to_next_level:
                        self.level_up()
                    self.attack_cooldown = ATTACK_COOLDOWN
                    break

    def level_up(self):
        self.level += 1
        self.exp -= self.exp_to_next_level
        self.exp_to_next_level *= 1.5
        self.speed += 0.5
        self.level_up_flash = 30  # Flash for 30 frames
        print(f"{self.type} leveled up to level {self.level}!")

    def draw(self, screen):
        frame = self.frames[self.current_direction][self.current_frame].copy()
        if self.attack_flash > 0:
            frame.fill((255, 255, 0, 128), special_flags=pygame.BLEND_RGBA_ADD)
        if self.level_up_flash > 0:
            frame.fill((0, 255, 0, 128), special_flags=pygame.BLEND_RGBA_ADD)
        screen.blit(frame, self.rect)