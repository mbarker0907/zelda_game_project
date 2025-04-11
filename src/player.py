import pygame
import os
from fireball import Fireball

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Player:
    # **Initialization**
    # Purpose: Sets up the player with sprites, health, and inventory
    def __init__(self, x, y, world):
        self.world = world
        self.rect = pygame.Rect(x, y, 48, 64)  # Player size
        self.speed = 3
        self.sprite_sheet = pygame.image.load(os.path.join(PROJECT_ROOT, "assets/player/player.png")).convert_alpha()
        if self.sprite_sheet.get_width() != 144 or self.sprite_sheet.get_height() != 256:
            raise ValueError(f"Player sprite sheet dimensions are {self.sprite_sheet.get_width()}x{self.sprite_sheet.get_height()}, expected 144x256")
        
        # Extract animation frames
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
        self.health = 3
        self.max_health = 3
        self.heart_sprite = pygame.image.load(os.path.join(PROJECT_ROOT, "assets/ui/heart.png")).convert_alpha()
        self.fireballs = []
        self.explosions = []
        fireball_sheet = pygame.image.load(os.path.join(PROJECT_ROOT, "assets/projectiles/fireball_splash_sheet_final.png")).convert_alpha()
        self.fireball_sprites = [fireball_sheet.subsurface((i * 32, 0, 32, 32)) for i in range(4)]
        self.explosion_sprites = [fireball_sheet.subsurface((i * 32 + 128, 0, 32, 32)) for i in range(4)]
        self.inventory = []
        self.key_sprite = pygame.image.load(os.path.join(PROJECT_ROOT, "assets/ui/key.png")).convert_alpha()
        self.invincible = False
        self.invincibility_duration = 0.5
        self.invincibility_timer = 0

    # **Move with Keyboard**
    # Purpose: Updates player position based on arrow key input
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
            if tile_type == 2:  # Unlocked door
                current_room = self.world.current_room_index
                if current_room == 0:
                    door_transition = (1, (2 * self.world.tile_size, 7 * self.world.tile_size))
                elif current_room == 1:
                    door_transition = (0, (27 * self.world.tile_size, 9 * self.world.tile_size))
            if door_transition:
                new_room_index, (new_x, new_y) = door_transition
                self.world.switch_room(new_room_index)
                self.rect.x = new_x
                self.rect.y = new_y

    # **Move with Joystick**
    # Purpose: Updates player position based on joystick input
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
                door_transition = (1, (2 * self.world.tile_size, 7 * self.world.tile_size))
            elif current_room == 1:
                door_transition = (0, (27 * self.world.tile_size, 9 * self.world.tile_size))
        if door_transition:
            new_room_index, (new_x, new_y) = door_transition
            self.world.switch_room(new_room_index)
            self.rect.x = new_x
            self.rect.y = new_y

    # **Shoot Fireball**
    # Purpose: Creates a fireball in the direction the player is facing
    def shoot_fireball(self):
        fireball_speed = 5
        if self.current_direction == "left":
            vx, vy = -fireball_speed, 0
        elif self.current_direction == "right":
            vx, vy = fireball_speed, 0
        elif self.current_direction == "up":
            vx, vy = 0, -fireball_speed
        elif self.current_direction == "down":
            vx, vy = 0, fireball_speed
        else:
            vx, vy = 0, 0
        fireball = Fireball(self.rect.centerx, self.rect.centery, vx, vy, self.fireball_sprites, self.explosion_sprites)
        self.fireballs.append(fireball)

    # **Update Player State**
    # Purpose: Manages invincibility and explosion animations
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

    # **Update Fireballs**
    # Purpose: Moves fireballs and triggers explosions when they expire
    def update_fireballs(self, window_width, window_height):
        for fireball in self.fireballs[:]:
            if not fireball.update(window_width, window_height):
                explosion = fireball.explode()
                self.explosions.append(explosion)
                self.fireballs.remove(fireball)

    # **Take Damage**
    # Purpose: Reduces health and triggers invincibility when hit
    def take_damage(self):
        if not self.invincible:
            self.health -= 1
            self.invincible = True
            self.invincibility_timer = self.invincibility_duration

    # **Draw Player and HUD**
    # Purpose: Renders the player, fireballs, explosions, health, and inventory
    def draw(self, screen, window_width):
        screen.blit(self.frames[self.current_direction][self.current_frame], self.rect)
        for fireball in self.fireballs:
            fireball.draw(screen)
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
        # Draw inventory HUD
        inventory_x = window_width - 100
        inventory_y = 10
        for item in self.inventory:
            if item == "key":
                screen.blit(self.key_sprite, (inventory_x, inventory_y))
                inventory_x += 40  # Space out items