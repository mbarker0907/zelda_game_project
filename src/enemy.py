# enemy.py
import pygame
import os
import random
from config import *
from projectile import Projectile

class Enemy:
    def __init__(self, x, y, enemy_type, world):
        self.world = world
        self.type = enemy_type
        self.speed = ENEMY_SPEED if enemy_type != "boss" else BOSS_SPEED
        self.health = 2 if enemy_type != "boss" else 10
        self.attack = 1
        self.direction = random.choice(["left", "right", "up", "down"])
        self.animation_counter = 0
        self.animation_speed = 0.1
        self.current_frame = 0
        self.is_dying = False
        self.death_timer = 0
        self.frozen = False
        self.freeze_timer = 0
        self.damage_flash = 0  # For visual feedback

        sprite_configs = {
            "archer": {
                "path": "enemies/archer.png",
                "dimensions": (144, 192),
                "frame_size": (48, 48),
                "directions": ["down", "left", "right", "up"],
                "frames_per_direction": 3
            },
            "octorok": {
                "path": "enemies/octorok.png",
                "dimensions": (144, 192),
                "frame_size": (48, 48),
                "directions": ["down", "left", "right", "up"],
                "frames_per_direction": 3
            },
            "bat": {
                "path": "enemies/bat.png",
                "dimensions": (128, 96),
                "frame_size": (32, 32),
                "directions": ["down"],
                "frames_per_direction": 4
            },
            "boss": {
                "path": "enemies/boss.png",
                "dimensions": (216, 384),
                "frame_size": (72, 96),
                "directions": ["down", "left", "right", "up"],
                "frames_per_direction": 3
            }
        }

        config = sprite_configs[enemy_type]
        sprite_path = config["path"]
        expected_dimensions = config["dimensions"]
        self.frame_size = config["frame_size"]
        self.directions = config["directions"]
        self.frames_per_direction = config["frames_per_direction"]

        self.rect = pygame.Rect(x, y + self.world.hud_height, self.frame_size[0], self.frame_size[1])

        self.sprite_sheet = pygame.image.load(os.path.join(ASSETS_PATH, sprite_path)).convert_alpha()
        actual_dimensions = (self.sprite_sheet.get_width(), self.sprite_sheet.get_height())
        if actual_dimensions != expected_dimensions:
            raise ValueError(f"{self.type} sprite sheet dimensions are {actual_dimensions}, expected {expected_dimensions}")

        self.frames = {direction: [] for direction in self.directions}
        frame_width, frame_height = self.frame_size
        for row, direction in enumerate(self.directions):
            for col in range(self.frames_per_direction):
                frame = self.sprite_sheet.subsurface((col * frame_width, row * frame_height, frame_width, frame_height))
                self.frames[direction].append(frame)

        if self.type == "boss":
            boss_projectile_sheet = pygame.image.load(os.path.join(ASSETS_PATH, "projectiles/fireball_splash_sheet_final.png")).convert_alpha()
            self.boss_projectile_sprites = [boss_projectile_sheet.subsurface((i * 32, 0, 32, 32)) for i in range(4)]
            self.boss_explosion_sprites = [boss_projectile_sheet.subsurface((i * 32 + 128, 0, 32, 32)) for i in range(4)]
        self.shoot_cooldown = 0

    def update(self, window_width, window_height, player_projectiles):
        if self.is_dying:
            self.death_timer -= 1 / 60
            if self.death_timer <= 0:
                self.health = 0
            return

        if self.frozen:
            self.freeze_timer -= 1 / 60
            if self.freeze_timer <= 0:
                self.frozen = False
            return

        if self.damage_flash > 0:
            self.damage_flash -= 1

        if self.type == "boss":
            self.shoot_cooldown -= 1 / 60
            if self.shoot_cooldown <= 0:
                for direction in ["left", "right", "up", "down"]:
                    if direction == "left":
                        vx, vy = -5, 0
                    elif direction == "right":
                        vx, vy = 5, 0
                    elif direction == "up":
                        vx, vy = 0, -5
                    elif direction == "down":
                        vx, vy = 0, 5
                    projectile = Projectile(self.rect.centerx, self.rect.centery, (vx, vy), "fireball",
                                           self.boss_projectile_sprites, self.boss_explosion_sprites, power=1)
                    self.world.enemy_projectiles.append(projectile)
                self.shoot_cooldown = 2

        for projectile in player_projectiles:
            if self.rect.colliderect(projectile.rect) and not self.is_dying:
                self.health -= projectile.power
                self.damage_flash = 10  # Flash for 10 frames
                if projectile.weapon_type == "ice_bolt":
                    self.frozen = True
                    self.freeze_timer = 2  # Freeze for 2 seconds
                player_projectiles.remove(projectile)
                if self.health <= 0:
                    self.is_dying = True
                    self.death_timer = 0.5
                    self.world.drop_gold(self.rect.centerx, self.rect.centery - self.world.hud_height, random.randint(5, 10))
                    if random.random() < 0.1:  # 10% chance to drop an item
                        self.world.drop_item(self.rect.centerx, self.rect.centery - self.world.hud_height, "bomb")
                    break

        if random.random() < 0.02:
            self.direction = random.choice(self.directions)

        dx, dy = 0, 0
        if self.direction == "left":
            dx = -self.speed
        elif self.direction == "right":
            dx = self.speed
        elif self.direction == "up":
            dy = -self.speed
        elif self.direction == "down":
            dy = self.speed

        new_x = self.rect.x + dx
        new_y = self.rect.y + dy
        new_rect = pygame.Rect(new_x, new_y, self.rect.width, self.rect.height)

        adjusted_window_height = window_height - self.world.hud_height
        if (0 <= new_x <= window_width - self.rect.width and
            self.world.hud_height <= new_y <= window_height - self.rect.height and
            not self.world.is_wall(new_rect.centerx, new_rect.centery)):
            self.rect.x = new_x
            self.rect.y = new_y
            self.animation_counter += self.animation_speed
            if self.animation_counter >= 1:
                self.current_frame = (self.current_frame + 1) % self.frames_per_direction
                self.animation_counter = 0

    def is_dead(self):
        return self.health <= 0 and not self.is_dying

    def draw(self, screen):
        direction = self.direction if self.direction in self.frames else self.directions[0]
        frame = self.frames[direction][self.current_frame].copy()
        if self.damage_flash > 0:
            frame.fill((255, 0, 0, 128), special_flags=pygame.BLEND_RGBA_ADD)
        if self.frozen:
            frame.fill((0, 0, 255, 64), special_flags=pygame.BLEND_RGBA_ADD)
        screen.blit(frame, self.rect)