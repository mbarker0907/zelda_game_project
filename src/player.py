import pygame
import os
import math

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Projectile:
    def __init__(self, x, y, direction, weapon_type):
        self.rect = pygame.Rect(x, y, 8, 8)
        self.direction = direction
        self.speed = 5
        self.weapon_type = weapon_type
        self.explosion_timer = None
        self.explosion_radius = 50 if weapon_type == "bomb" else 0

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
        dx = math.cos(math.radians(self.direction)) * self.speed
        dy = math.sin(math.radians(self.direction)) * self.speed
        self.rect.x += dx
        self.rect.y += dy
        if self.rect.left < 0 or self.rect.right > window_width or self.rect.top < 0 or self.rect.bottom > window_height:
            return False
        return True

    def explode(self):
        if self.weapon_type == "bomb" and self.explosion_timer is not None:
            return {"rect": pygame.Rect(self.rect.centerx - self.explosion_radius, self.rect.centery - self.explosion_radius, self.explosion_radius * 2, self.explosion_radius * 2), "timer": 10}
        return None

    def draw(self, screen):
        if self.explosion_timer is not None:
            pygame.draw.circle(screen, (255, 165, 0), self.rect.center, self.explosion_radius, 2)
        else:
            color = (0, 0, 255) if self.weapon_type == "ice_bolt" else (255, 0, 0) if self.weapon_type == "bomb" else (255, 255, 0)
            pygame.draw.rect(screen, color, self.rect)

class Player:
    def __init__(self, x, y, world, font):
        self.world = world
        self.rect = pygame.Rect(x, y, 24, 24)
        self.speed = 3
        self.health = 5
        self.max_health = 5
        self.level = 1
        self.experience = 0  # Using self.experience as originally intended
        self.experience_to_next_level = 10  # Matching name
        self.gold = 0
        self.keys = 0
        self.inventory = []
        self.projectiles = []
        self.explosions = []
        self.direction = 0
        self.current_weapon_index = 0
        self.weapons = ["sword", "bow"]
        self.font = font
        self.shoot_cooldown = 0
        self.shoot_cooldown_max = 20

        # Load and split the sprite sheet (144x256, 4 rows, 3 columns, 48x64 per frame)
        sprite_sheet = pygame.image.load(os.path.join(PROJECT_ROOT, "assets/player/player.png")).convert_alpha()
        self.sprites = {
            "down": [],
            "left": [],
            "right": [],
            "up": []
        }
        frame_width, frame_height = 48, 64
        directions = ["down", "left", "right", "up"]
        for row, direction in enumerate(directions):
            for col in range(3):  # 3 frames per direction
                frame_rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
                frame = sprite_sheet.subsurface(frame_rect)
                frame = pygame.transform.scale(frame, (self.rect.width, self.rect.height))
                self.sprites[direction].append(frame)

        # Animation state
        self.current_direction = "down"
        self.animation_frame = 0
        self.animation_speed = 10  # Update frame every 10 game frames
        self.animation_counter = 0

    @property
    def current_weapon(self):
        return self.weapons[self.current_weapon_index]

    def move(self, keys, window_width, window_height):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
            self.direction = 180
            self.current_direction = "left"
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
            self.direction = 0
            self.current_direction = "right"
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed
            self.direction = 90
            self.current_direction = "up"
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed
            self.direction = 270
            self.current_direction = "down"
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
            if dx > 0 and dy < 0:
                self.direction = 45
                self.current_direction = "right"
            elif dx > 0 and dy > 0:
                self.direction = 315
                self.current_direction = "right"
            elif dx < 0 and dy < 0:
                self.direction = 135
                self.current_direction = "left"
            elif dx < 0 and dy > 0:
                self.direction = 225
                self.current_direction = "left"

        new_rect = self.rect.copy()
        new_rect.x += dx
        if 0 <= new_rect.left and new_rect.right <= window_width and not self.world.is_wall(new_rect.centerx, new_rect.centery):
            self.rect.x += dx

        new_rect = self.rect.copy()
        new_rect.y += dy
        if self.world.hud_height <= new_rect.top and new_rect.bottom <= window_height and not self.world.is_wall(new_rect.centerx, new_rect.centery):
            self.rect.y += dy

        tile_type = self.world.get_tile_type(self.rect.centerx, self.rect.centery)
        if tile_type == 2:  # Door
            if self.world.current_room_index == 0:
                self.world.switch_room(1)
                self.rect.x = 2 * self.world.tile_size
                self.rect.y = 9 * self.world.tile_size + self.world.hud_height
            elif self.world.current_room_index == 1:
                self.world.switch_room(0)
                self.rect.x = 27 * self.world.tile_size
                self.rect.y = 9 * self.world.tile_size + self.world.hud_height
            elif self.world.current_room_index == 2:
                self.world.switch_room(1)
                self.rect.x = 27 * self.world.tile_size
                self.rect.y = 9 * self.world.tile_size + self.world.hud_height
            elif self.world.current_room_index == 3:
                self.world.switch_room(2)
                self.rect.x = 2 * self.world.tile_size
                self.rect.y = 7 * self.world.tile_size + self.world.hud_height

    def move_with_velocity(self, vx, vy, window_width, window_height):
        dx, dy = vx, vy
        if dx != 0 or dy != 0:
            self.direction = math.degrees(math.atan2(dy, dx))
            if self.direction < 0:
                self.direction += 360
            if 45 <= self.direction < 135:
                self.current_direction = "up"
            elif 135 <= self.direction < 225:
                self.current_direction = "left"
            elif 225 <= self.direction < 315:
                self.current_direction = "down"
            else:
                self.current_direction = "right"

        new_rect = self.rect.copy()
        new_rect.x += dx
        if 0 <= new_rect.left and new_rect.right <= window_width and not self.world.is_wall(new_rect.centerx, new_rect.centery):
            self.rect.x += dx

        new_rect = self.rect.copy()
        new_rect.y += dy
        if self.world.hud_height <= new_rect.top and new_rect.bottom <= window_height and not self.world.is_wall(new_rect.centerx, new_rect.centery):
            self.rect.y += dy

        tile_type = self.world.get_tile_type(self.rect.centerx, self.rect.centery)
        if tile_type == 2:
            if self.world.current_room_index == 0:
                self.world.switch_room(1)
                self.rect.x = 2 * self.world.tile_size
                self.rect.y = 9 * self.world.tile_size + self.world.hud_height
            elif self.world.current_room_index == 1:
                self.world.switch_room(0)
                self.rect.x = 27 * self.world.tile_size
                self.rect.y = 9 * self.world.tile_size + self.world.hud_height
            elif self.world.current_room_index == 2:
                self.world.switch_room(1)
                self.rect.x = 27 * self.world.tile_size
                self.rect.y = 9 * self.world.tile_size + self.world.hud_height
            elif self.world.current_room_index == 3:
                self.world.switch_room(2)
                self.rect.x = 2 * self.world.tile_size
                self.rect.y = 7 * self.world.tile_size + self.world.hud_height

    def shoot_projectile(self):
        if self.shoot_cooldown > 0:
            return
        weapon_type = self.current_weapon
        if weapon_type == "bow":
            weapon_type = "ice_bolt" if "ice_bolt" in self.inventory else "arrow"
            projectile = Projectile(self.rect.centerx, self.rect.centery, self.direction, weapon_type)
            self.projectiles.append(projectile)
            self.shoot_cooldown = self.shoot_cooldown_max
        elif weapon_type == "bomb" and "bomb" in self.inventory:
            projectile = Projectile(self.rect.centerx, self.rect.centery, self.direction, "bomb")
            self.projectiles.append(projectile)
            self.inventory.remove("bomb")
            self.shoot_cooldown = self.shoot_cooldown_max

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.experience >= self.experience_to_next_level:
            self.level += 1
            self.experience = 0
            self.experience_to_next_level = int(self.experience_to_next_level * 1.5)
            self.max_health += 1
            self.health = self.max_health

        # Update animation
        self.animation_counter += 1
        if self.animation_counter >= self.animation_speed:
            self.animation_frame = (self.animation_frame + 1) % 3
            self.animation_counter = 0

    def update_projectiles(self, window_width, window_height):
        for projectile in self.projectiles[:]:
            if not projectile.update(window_width, window_height):
                self.projectiles.remove(projectile)
        for explosion in self.explosions[:]:
            explosion["timer"] -= 1
            if explosion["timer"] <= 0:
                self.explosions.remove(explosion)

    def take_damage(self):
        self.health -= 1

    def switch_weapon(self, weapon_index):
        if 0 <= weapon_index < len(self.weapons):
            self.current_weapon_index = weapon_index

    def draw(self, screen, window_width, window_height):
        frame = self.sprites[self.current_direction][self.animation_frame]
        screen.blit(frame, self.rect)
        for projectile in self.projectiles:
            projectile.draw(screen)
        for explosion in self.explosions:
            pygame.draw.circle(screen, (255, 165, 0), explosion["rect"].center, explosion["rect"].width // 2, 2)