import pygame
import os
import random
from projectile import Projectile

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Enemy:
    def __init__(self, x, y, enemy_type, world):
        self.world = world
        self.type = enemy_type
        self.speed = 1.0 if enemy_type != "boss" else 0.5  # Adjusted speed
        self.health = 2 if enemy_type != "boss" else 10
        self.attack = 1
        self.direction = random.choice(["left", "right", "up", "down"])
        self.animation_counter = 0
        self.animation_speed = 0.1
        self.current_frame = 0
        self.is_dying = False
        self.death_timer = 0

        # Define sprite sheet properties for each enemy type
        sprite_configs = {
            "archer": {
                "path": "assets/enemies/archer.png",
                "dimensions": (144, 192),
                "frame_size": (48, 48),
                "directions": ["down", "left", "right", "up"],
                "frames_per_direction": 3
            },
            "octorok": {
                "path": "assets/enemies/octorok.png",
                "dimensions": (144, 192),
                "frame_size": (48, 48),
                "directions": ["down", "left", "right", "up"],
                "frames_per_direction": 3
            },
            "bat": {
                "path": "assets/enemies/bat.png",
                "dimensions": (128, 96),
                "frame_size": (32, 32),
                "directions": ["down"],
                "frames_per_direction": 4
            },
            "boss": {
                "path": "assets/enemies/boss.png",
                "dimensions": (216, 384),
                "frame_size": (72, 96),
                "directions": ["down", "left", "right", "up"],
                "frames_per_direction": 3
            }
        }

        # Load sprite sheet based on enemy type
        config = sprite_configs[enemy_type]
        sprite_path = config["path"]
        expected_dimensions = config["dimensions"]
        self.frame_size = config["frame_size"]
        self.directions = config["directions"]
        self.frames_per_direction = config["frames_per_direction"]

        # Set rect size based on frame size
        self.rect = pygame.Rect(x, y, self.frame_size[0], self.frame_size[1])

        # Load and validate sprite sheet
        self.sprite_sheet = pygame.image.load(os.path.join(PROJECT_ROOT, sprite_path)).convert_alpha()
        actual_dimensions = (self.sprite_sheet.get_width(), self.sprite_sheet.get_height())
        if actual_dimensions != expected_dimensions:
            raise ValueError(f"{self.type} sprite sheet dimensions are {actual_dimensions}, expected {expected_dimensions}")

        # Split into frames
        self.frames = {direction: [] for direction in self.directions}
        frame_width, frame_height = self.frame_size
        for row, direction in enumerate(self.directions):
            for col in range(self.frames_per_direction):
                frame = self.sprite_sheet.subsurface((col * frame_width, row * frame_height, frame_width, frame_height))
                self.frames[direction].append(frame)

    def update(self, window_width, window_height, projectiles):
        if self.is_dying:
            self.death_timer += 1
            if self.death_timer > 30:
                self.world.drop_gold(self.rect.x, self.rect.y, random.randint(1, 5))
                return
        for projectile in projectiles:
            if self.rect.colliderect(projectile.rect):
                damage = projectile.power
                self.health -= damage
                self.world.player.experience += 10
                projectiles.remove(projectile)
                if self.health <= 0:
                    self.is_dying = True
        if not self.is_dying:
            dx = self.world.player.rect.centerx - self.rect.centerx
            dy = self.world.player.rect.centery - self.rect.centery
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist > 0:
                dx, dy = dx / dist, dy / dist
                new_x = self.rect.x + dx * self.speed
                new_y = self.rect.y + dy * self.speed
                new_rect = pygame.Rect(new_x, new_y, self.rect.width, self.rect.height)
                if 0 <= new_x <= window_width - self.rect.width and 0 <= new_y <= window_height - self.rect.height:
                    if not self.world.is_wall(new_rect.centerx, new_rect.centery):
                        self.rect.x = new_x
                        self.rect.y = new_y
            if self.type != "bat":
                if abs(dx) > abs(dy):
                    self.direction = "right" if dx > 0 else "left"
                else:
                    self.direction = "down" if dy > 0 else "up"
                if self.direction not in self.directions:
                    self.direction = "down"
            self.animation_counter += self.animation_speed
            if self.animation_counter >= 1:
                self.current_frame = (self.current_frame + 1) % self.frames_per_direction
                self.animation_counter = 0
            if self.type == "boss" and random.random() < 0.05:
                self.shoot_projectile()

    def shoot_projectile(self):
        projectile_sprites = [pygame.image.load(os.path.join(PROJECT_ROOT, "assets/projectiles/boss_projectile.png")).convert_alpha()]
        dx = self.world.player.rect.centerx - self.rect.centerx
        dy = self.world.player.rect.centery - self.rect.centery
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist > 0:
            dx, dy = dx / dist, dy / dist
            projectile = Projectile(self.rect.centerx, self.rect.centery, dx * 5, dy * 5, projectile_sprites, [], "boss_projectile", 2)
            # Append to world.enemy_projectiles
            if hasattr(self.world, 'enemy_projectiles'):
                self.world.enemy_projectiles.append(projectile)
            else:
                print("Warning: self.world.enemy_projectiles not found. Boss projectile not added.")

    def draw(self, screen):
        if not self.is_dying:
            direction = "down" if self.type == "bat" else self.direction
            screen.blit(self.frames[direction][self.current_frame], self.rect)

    def is_dead(self):
        return self.is_dying and self.death_timer > 30