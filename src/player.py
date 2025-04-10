import pygame
import os
from fireball import Fireball

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Player:
    def __init__(self, x, y, world):
        self.world = world
        self.rect = pygame.Rect(x, y, 48, 64)  # Match new frame size
        self.speed = 3
        
        # Load new sprite sheet
        self.sprite_sheet = pygame.image.load(os.path.join(PROJECT_ROOT, "assets/player/player.png")).convert_alpha()
        if self.sprite_sheet.get_width() != 144 or self.sprite_sheet.get_height() != 256:
            raise ValueError(f"Player sprite sheet dimensions are {self.sprite_sheet.get_width()}x{self.sprite_sheet.get_height()}, expected 144x256")
        
        # Extract frames (48x64)
        self.frames = {
            "down": [], "left": [], "right": [], "up": []
        }
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
        fireball_sheet_path = os.path.join(PROJECT_ROOT, "assets/projectiles/fireball_splash_sheet_final.png")
        print(f"Attempting to load fireball sprite sheet from: {fireball_sheet_path}")
        fireball_sheet = pygame.image.load(fireball_sheet_path).convert_alpha()
        print(f"Fireball sprite sheet loaded, dimensions: {fireball_sheet.get_width()}x{fireball_sheet.get_height()}")
        # Load fireball sprites (first 4 frames)
        self.fireball_sprites = []
        for i in range(4):
            frame = fireball_sheet.subsurface((i * 32, 0, 32, 32))
            self.fireball_sprites.append(frame)
        # Load explosion sprites (last 4 frames)
        self.explosion_sprites = []
        for i in range(4):
            frame = fireball_sheet.subsurface((i * 32 + 128, 0, 32, 32))
            self.explosion_sprites.append(frame)
        
        self.inventory = []
        self.key_sprite = pygame.image.load(os.path.join(PROJECT_ROOT, "assets/ui/key.png")).convert_alpha()

        # Add invincibility timer
        self.invincible = False
        self.invincibility_duration = 0.5  # Seconds
        self.invincibility_timer = 0

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
                    door_transition = (0, (18 * self.world.tile_size, 7 * self.world.tile_size))
            if door_transition:
                new_room_index, (new_x, new_y) = door_transition
                self.world.switch_room(new_room_index)
                self.rect.x = new_x
                self.rect.y = new_y

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
                door_transition = (0, (18 * self.world.tile_size, 7 * self.world.tile_size))
        if door_transition:
            new_room_index, (new_x, new_y) = door_transition
            self.world.switch_room(new_room_index)
            self.rect.x = new_x
            self.rect.y = new_y

    def shoot_fireball(self):
        # Calculate velocity based on direction
        fireball_speed = 5  # Match Fireball's internal speed
        if self.current_direction == "left":
            vx, vy = -fireball_speed, 0
        elif self.current_direction == "right":
            vx, vy = fireball_speed, 0
        elif self.current_direction == "up":
            vx, vy = 0, -fireball_speed
        elif self.current_direction == "down":
            vx, vy = 0, fireball_speed
        else:
            vx, vy = 0, 0  # Default case (shouldn’t happen)
        fireball = Fireball(self.rect.centerx, self.rect.centery, vx, vy, self.fireball_sprites, self.explosion_sprites)
        self.fireballs.append(fireball)

    def update(self):
        if self.explosions:
            for exp in self.explosions[:]:
                exp["frame"] += 0.2
                if exp["frame"] >= len(self.explosion_sprites):
                    self.explosions.remove(exp)
        # Update invincibility timer
        if self.invincible:
            self.invincibility_timer -= 1 / 60  # Assuming 60 FPS
            if self.invincibility_timer <= 0:
                self.invincible = False

    def update_fireballs(self, window_width, window_height):
        for fireball in self.fireballs[:]:
            if not fireball.update(window_width, window_height):  # Update returns False if exploded/off-screen
                explosion = fireball.explode()
                self.explosions.append(explosion)
                self.fireballs.remove(fireball)

    def take_damage(self):
        if not self.invincible:  # Only take damage if not invincible
            self.health -= 1
            self.invincible = True
            self.invincibility_timer = self.invincibility_duration

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
        for i in range(self.max_health):
            heart_x = 10 + i * (self.heart_sprite.get_width() + 10)
            heart_y = 10
            if i < self.health:
                screen.blit(self.heart_sprite, (heart_x, heart_y))
            else:
                empty_heart = self.heart_sprite.copy()
                empty_heart.set_alpha(64)
                screen.blit(empty_heart, (heart_x, heart_y))
        if "key" in self.inventory:
            key_x = window_width - self.key_sprite.get_width() - 10
            key_y = 10
            screen.blit(self.key_sprite, (key_x, key_y))