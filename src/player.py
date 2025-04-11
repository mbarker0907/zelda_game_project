import pygame
import os
from projectile import Projectile  # Renamed from Fireball for generality

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Player:
    # **Initialization**
    def __init__(self, x, y, world, font):
        self.world = world
        self.rect = pygame.Rect(x, y, 48, 64)
        self.speed = 3
        self.health = 100
        self.max_health = 100
        self.level = 1
        self.exp = 0
        self.exp_to_next_level = 100
        self.gold = 0
        self.inventory = ["fireball"]
        self.current_weapon = "fireball"
        self.shoot_cooldown = 0
        self.font = font  # Store the font for rendering text
       
        # **ASSET REQUIRED**: Add player sprite sheet
        self.sprite_sheet = pygame.image.load(os.path.join(PROJECT_ROOT, "assets/player/player.png")).convert_alpha()
        if self.sprite_sheet.get_width() != 144 or self.sprite_sheet.get_height() != 256:
            raise ValueError(f"Player sprite sheet dimensions are {self.sprite_sheet.get_width()}x{self.sprite_sheet.get_height()}, expected 144x256")
        self.frames = {"down": [], "left": [], "right": [], "up": []}
        directions = ["down", "left", "right", "up"]
        for row, direction in enumerate(directions):
            for col in range(3):
                frame = self.sprite_sheet.subsurface((col * 48, row * 64, 48, 64))
                self.frames[direction].append(frame)
        self.current_direction = "down"
        self.current_frame = 0
        self.animation_speed = 0.15
        self.animation_counter = 0
        # Stats and leveling
        self.level = 1
        self.experience = 0
        self.exp_to_next_level = 100
        self.health = 3
        self.max_health = 3
        self.attack = 1
        self.heart_sprite = pygame.image.load(os.path.join(PROJECT_ROOT, "assets/ui/heart.png")).convert_alpha()
        self.projectiles = []
        self.explosions = []
        # **ASSET REQUIRED**: Add sprites for different projectiles (fireball, ice bolt)
        projectile_sheet = pygame.image.load(os.path.join(PROJECT_ROOT, "assets/projectiles/fireball_splash_sheet_final.png")).convert_alpha()
        self.projectile_sprites = {
            "fireball": [projectile_sheet.subsurface((i * 32, 0, 32, 32)) for i in range(4)],           
            "ice_bolt": [pygame.image.load(os.path.join(PROJECT_ROOT, "assets/projectiles/ice_bolt.png")).convert_alpha()]
            }
        self.explosion_sprites = [projectile_sheet.subsurface((i * 32 + 128, 0, 32, 32)) for i in range(4)]
        # Inventory and weapons
        self.inventory = ["fireball", "ice_bolt"]  # Starting weapons
        self.current_weapon = "fireball"
        self.projectile_power = 1  # Upgraded by powerups
        self.gold = 0
        self.invincible = False
        self.invincibility_duration = 0.5
        self.invincibility_timer = 0
        # HUD elements
        self.key_sprite = pygame.image.load(os.path.join(PROJECT_ROOT, "assets/ui/key.png")).convert_alpha()
        # **ASSET REQUIRED**: Add sprite for gold coin in HUD
        self.gold_sprite = pygame.image.load(os.path.join(PROJECT_ROOT, "assets/ui/gold.png")).convert_alpha()
        # **ASSET REQUIRED**: Add sprites for each weapon in HUD
        self.weapon_sprites = {
            "fireball": pygame.image.load(os.path.join(PROJECT_ROOT, "assets/ui/fireball_icon.png")).convert_alpha(),
            "ice_bolt": pygame.image.load(os.path.join(PROJECT_ROOT, "assets/ui/ice_bolt_icon.png")).convert_alpha()
        }

    # **Move with Keyboard**
    def move(self, keys, window_width, window_height):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx = -self.speed
            self.current_direction = "left"
        elif keys[pygame.K_RIGHT]:
            dx = self.speed
            self.current_direction = "right"
        elif keys[pygame.K_UP]:
            dy = -self.speed
            self.current_direction = "up"
        elif keys[pygame.K_DOWN]:
            dy = self.speed
            self.current_direction = "down"
        if dx != 0 or dy != 0:
            new_x = self.rect.x + dx
            new_y = self.rect.y + dy
            new_rect = pygame.Rect(new_x, new_y, self.rect.width, self.rect.height)
            if 0 <= new_x <= window_width - self.rect.width and 0 <= new_y <= window_height - self.rect.height:
                if not self.world.is_wall(new_rect.centerx, new_rect.centery):
                    self.rect.x = new_x
                    self.rect.y = new_y
                    self.animation_counter += self.animation_speed
                    if self.animation_counter >= 1:
                        self.current_frame = (self.current_frame + 1) % 3
                        self.animation_counter = 0
            tile_type = self.world.get_tile_type(new_rect.centerx, new_rect.centery)
            door_transition = None
            if tile_type == 2:
                current_room = self.world.current_room_index
                if current_room == 0:
                    door_transition = (1, (27 * self.world.tile_size, 9 * self.world.tile_size))
                elif current_room == 1:
                    door_transition = (2, (2 * self.world.tile_size, 7 * self.world.tile_size))
                elif current_room == 2:
                    door_transition = (3, (2 * self.world.tile_size, 7 * self.world.tile_size))
                elif current_room == 3:
                    door_transition = (0, (15 * self.world.tile_size, 10 * self.world.tile_size))
            if door_transition:
                new_room_index, (new_x, new_y) = door_transition
                self.world.switch_room(new_room_index)
                self.rect.x = new_x
                self.rect.y = new_y

    # **Move with Joystick**
    def move_with_velocity(self, vx, vy, window_width, window_height):
        new_x = self.rect.x + int(vx)
        new_y = self.rect.y + int(vy)
        new_rect = pygame.Rect(new_x, new_y, self.rect.width, self.rect.height)
        if 0 <= new_x <= window_width - self.rect.width and 0 <= new_y <= window_height - self.rect.height:
            if not self.world.is_wall(new_rect.centerx, new_rect.centery):
                self.rect.x = new_x
                self.rect.y = new_y
                self.animation_counter += self.animation_speed
                if self.animation_counter >= 1:
                    self.current_frame = (self.current_frame + 1) % 3
                    self.animation_counter = 0
        if vx > 0:
            self.current_direction = "right"
        elif vx < 0:
            self.current_direction = "left"
        elif vy > 0:
            self.current_direction = "down"
        elif vy < 0:
            self.current_direction = "up"
        tile_type = self.world.get_tile_type(new_rect.centerx, new_rect.centery)
        door_transition = None
        if tile_type == 2:
            current_room = self.world.current_room_index
            if current_room == 0:
                door_transition = (1, (27 * self.world.tile_size, 9 * self.world.tile_size))
            elif current_room == 1:
                door_transition = (2, (2 * self.world.tile_size, 7 * self.world.tile_size))
            elif current_room == 2:
                door_transition = (3, (2 * self.world.tile_size, 7 * self.world.tile_size))
            elif current_room == 3:
                door_transition = (0, (15 * self.world.tile_size, 10 * self.world.tile_size))
            if door_transition:
                new_room_index, (new_x, new_y) = door_transition
                self.world.switch_room(new_room_index)
                self.rect.x = new_x
                self.rect.y = new_y

    # **Shoot Projectile**
    def shoot_projectile(self):
        projectile_speed = 5
        if self.current_direction == "left":
            vx, vy = -projectile_speed, 0
        elif self.current_direction == "right":
            vx, vy = projectile_speed, 0
        elif self.current_direction == "up":
            vx, vy = 0, -projectile_speed
        elif self.current_direction == "down":
            vx, vy = 0, projectile_speed
        else:
            vx, vy = 0, 0
        projectile = Projectile(self.rect.centerx, self.rect.centery, vx, vy, self.projectile_sprites[self.current_weapon], self.explosion_sprites, self.current_weapon, self.projectile_power)
        self.projectiles.append(projectile)

    # **Switch Weapon**
    def switch_weapon(self, index):
        if index < len(self.inventory):
            self.current_weapon = self.inventory[index]
            print(f"Switched to {self.current_weapon}")

    # **Update Player State**
    def update(self):
        if self.explosions:
            for exp in self.explosions[:]:
                exp["frame"] += 0.2
                if exp["frame"] >= len(self.explosion_sprites):
                    self.explosions.remove(exp)
        if self.invincible:
            self.invincibility_timer -= 1 / 60
            if self.invincibility_timer <= 0:
                self.invincible = False
        # Level up if enough experience
        if self.experience >= self.exp_to_next_level:
            self.level_up()

    # **Level Up**
    def level_up(self):
        self.level += 1
        self.experience -= self.exp_to_next_level
        self.exp_to_next_level *= 1.5
        self.max_health += 1
        self.health = self.max_health
        self.attack += 1
        print(f"Player leveled up to level {self.level}!")

    # **Update Projectiles**
    def update_projectiles(self, window_width, window_height):
        for projectile in self.projectiles[:]:
            if not projectile.update(window_width, window_height):
                explosion = projectile.explode()
                self.explosions.append(explosion)
                self.projectiles.remove(projectile)

    # **Take Damage**
    def take_damage(self):
        if not self.invincible:
            self.health -= 1
            self.invincible = True
            self.invincibility_timer = self.invincibility_duration

   
        # **Draw Player and HUD**
    def draw(self, screen, window_width):
        screen.blit(self.frames[self.current_direction][self.current_frame], self.rect)
        for projectile in self.projectiles:
            projectile.draw(screen)
        for exp in self.explosions:
            frame = int(exp["frame"])
            if frame < len(self.explosion_sprites):
                sprite = self.explosion_sprites[frame]
                sprite_rect = sprite.get_rect(center=(exp["x"], exp["y"]))
                screen.blit(sprite, sprite_rect)
        # Draw health
        for i in range(self.max_health):
            heart_x = 10 + i * (self.heart_sprite.get_width() + 10)
            heart_y = 10
            if i < self.health:
                screen.blit(self.heart_sprite, (heart_x, heart_y))
            else:
                empty_heart = self.heart_sprite.copy()
                empty_heart.set_alpha(64)
                screen.blit(empty_heart, (heart_x, heart_y))
        # Draw current weapon
        screen.blit(self.weapon_sprites[self.current_weapon], (window_width // 2 - 16, 10))
        # Draw level and experience
        level_text = self.font.render(f"Level: {self.level}", True, (255, 255, 255))
        exp_text = self.font.render(f"EXP: {self.experience}/{self.exp_to_next_level}", True, (255, 255, 255))
        screen.blit(level_text, (10, 50))
        screen.blit(exp_text, (10, 80))
        # Draw EXP bar
        exp_bar_width = 100
        exp_ratio = self.experience / self.exp_to_next_level
        pygame.draw.rect(screen, (50, 50, 50), (10, 110, exp_bar_width, 10))
        pygame.draw.rect(screen, (0, 191, 255), (10, 110, exp_bar_width * exp_ratio, 10))
        # Draw inventory keys
        key_count = self.inventory.count("key")
        if key_count > 0:
            screen.blit(self.key_sprite, (10, 140))
            key_text = self.font.render(f"x{key_count}", True, (255, 255, 255))
            screen.blit(key_text, (40, 140))
        # Draw gold with icon
        gold_text = self.font.render(f"Gold: {self.gold}", True, (255, 215, 0))
        screen.blit(self.gold_sprite, (window_width - 120, 10))  # Adjusted position to top-right
        screen.blit(gold_text, (window_width - 90, 10))