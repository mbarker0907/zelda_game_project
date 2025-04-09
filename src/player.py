import pygame
import math
import os

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Player:
    def __init__(self, x, y):
        self.size = 48
        # Load Syb's sprites
        self.sprites = {
            "back": [pygame.transform.scale(pygame.image.load(os.path.join(PROJECT_ROOT, f"assets/player/syb1_bk{i}.png")).convert_alpha(), (self.size, self.size)) for i in range(1, 3)],
            "front": [pygame.transform.scale(pygame.image.load(os.path.join(PROJECT_ROOT, f"assets/player/syb1_fr{i}.png")).convert_alpha(), (self.size, self.size)) for i in range(1, 3)],
            "left": [pygame.transform.scale(pygame.image.load(os.path.join(PROJECT_ROOT, f"assets/player/syb1_lf{i}.png")).convert_alpha(), (self.size, self.size)) for i in range(1, 3)],
            "right": [pygame.transform.scale(pygame.image.load(os.path.join(PROJECT_ROOT, f"assets/player/syb1_rt{i}.png")).convert_alpha(), (self.size, self.size)) for i in range(1, 3)]
        }
        self.current_sprite = self.sprites["front"][0]
        self.rect = self.current_sprite.get_rect(topleft=(x, y))
        self.speed = 3
        self.direction = "front"
        self.frame = 0
        self.animation_speed = 0.2
        self.fireballs = []
        # Load new fireball sprite sheet
        fireball_path = os.path.join(PROJECT_ROOT, "assets/projectiles/fireball_splash_sheet_final.png")
        self.fireball_sheet = pygame.image.load(fireball_path).convert_alpha()
        self.fireball_frame_width = 32
        self.fireball_frame_height = 32
        self.fireball_sprites = []
        self.explosion_sprites = []
        # Extract frames (5 fireball frames + 3 explosion frames)
        for i in range(8):
            frame = self.fireball_sheet.subsurface((i * self.fireball_frame_width, 0, self.fireball_frame_width, self.fireball_frame_height))
            if i < 5:  # Fireball frames (0-4)
                self.fireball_sprites.append(frame)  # Keep at 32x32
            else:  # Explosion frames (5-7)
                # Center smaller explosion frames
                if i == 6:  # Medium explosion (24x24)
                    frame = pygame.transform.scale(frame, (24, 24))
                elif i == 7:  # Small explosion (16x16)
                    frame = pygame.transform.scale(frame, (16, 16))
                self.explosion_sprites.append(frame)
        self.fireball_size = 32
        self.explosion_size = 32  # Base size, adjusted for smaller explosions
        self.fireball_animation_speed = 0.3  # Faster animation for fireball
        self.explosion_animation_speed = 0.2  # Slightly slower for explosion
        self.explosions = []
        # Debug: Print loaded frames
        print(f"Loaded {len(self.fireball_sprites)} fireball frames")
        print(f"Loaded {len(self.explosion_sprites)} explosion frames")

    def move(self, keys, window_width, window_height):
        vx, vy = 0, 0
        moving = False

        if keys[pygame.K_LEFT]:
            print("Left key pressed")
            vx -= self.speed
        if keys[pygame.K_RIGHT]:
            print("Right key pressed")
            vx += self.speed
        if keys[pygame.K_UP]:
            print("Up key pressed")
            vy -= self.speed
        if keys[pygame.K_DOWN]:
            print("Down key pressed")
            vy += self.speed

        if vx != 0 and vy != 0:
            length = math.sqrt(vx**2 + vy**2)
            vx = vx * self.speed / length
            vy = vy * self.speed / length

        new_x = self.rect.x + vx
        new_y = self.rect.y + vy
        print(f"Attempting to move to: ({new_x}, {new_y})")
        if 0 <= new_x <= window_width - self.size:
            self.rect.x = new_x
        if 0 <= new_y <= window_height - self.size:
            self.rect.y = new_y
        print(f"Player position: ({self.rect.x}, {self.rect.y})")

        if vx < 0:
            self.direction = "left"
            moving = True
        elif vx > 0:
            self.direction = "right"
            moving = True
        elif vy < 0:
            self.direction = "back"
            moving = True
        elif vy > 0:
            self.direction = "front"
            moving = True

        if moving:
            self.frame = (self.frame + self.animation_speed) % 2
            self.current_sprite = self.sprites[self.direction][int(self.frame)]
        else:
            self.frame = 0
            self.current_sprite = self.sprites[self.direction][0]

    def move_with_velocity(self, vx, vy, window_width, window_height):
        moving = False

        new_x = self.rect.x + vx
        new_y = self.rect.y + vy
        print(f"Attempting to move to (gamepad): ({new_x}, {new_y})")
        if 0 <= new_x <= window_width - self.size:
            self.rect.x = new_x
        if 0 <= new_y <= window_height - self.size:
            self.rect.y = new_y
        print(f"Player position (gamepad): ({self.rect.x}, {self.rect.y})")

        if vx < 0:
            self.direction = "left"
            moving = True
        elif vx > 0:
            self.direction = "right"
            moving = True
        elif vy < 0:
            self.direction = "back"
            moving = True
        elif vy > 0:
            self.direction = "front"
            moving = True

        if moving:
            self.frame = (self.frame + self.animation_speed) % 2
            self.current_sprite = self.sprites[self.direction][int(self.frame)]
        else:
            self.frame = 0
            self.current_sprite = self.sprites[self.direction][0]

    def shoot_fireball(self):
        fireball_speed = 5
        if self.direction == "front":
            fireball = pygame.Rect(self.rect.centerx - self.fireball_size // 2, self.rect.bottom, self.fireball_size, self.fireball_size)
            velocity = (0, fireball_speed)
        elif self.direction == "back":
            fireball = pygame.Rect(self.rect.centerx - self.fireball_size // 2, self.rect.top - self.fireball_size, self.fireball_size, self.fireball_size)
            velocity = (0, -fireball_speed)
        elif self.direction == "left":
            fireball = pygame.Rect(self.rect.left - self.fireball_size, self.rect.centery - self.fireball_size // 2, self.fireball_size, self.fireball_size)
            velocity = (-fireball_speed, 0)
        elif self.direction == "right":
            fireball = pygame.Rect(self.rect.right, self.rect.centery - self.fireball_size // 2, self.fireball_size, self.fireball_size)
            velocity = (fireball_speed, 0)
        self.fireballs.append({"rect": fireball, "velocity": velocity, "distance": 0, "frame": 0})

    def update_fireballs(self, window_width, window_height):
        max_distance = 150
        for fb in self.fireballs[:]:
            fb["rect"].x += fb["velocity"][0]
            fb["rect"].y += fb["velocity"][1]
            fb["distance"] += abs(fb["velocity"][0]) + abs(fb["velocity"][1])
            fb["frame"] = (fb["frame"] + self.fireball_animation_speed) % 5  # Cycle through 5 fireball frames
            if (fb["rect"].left > window_width or fb["rect"].right < 0 or
                fb["rect"].top > window_height or fb["rect"].bottom < 0 or
                fb["distance"] > max_distance):
                explosion_rect = pygame.Rect(
                    fb["rect"].centerx - self.explosion_size // 2,
                    fb["rect"].centery - self.explosion_size // 2,
                    self.explosion_size, self.explosion_size
                )
                self.explosions.append({"rect": explosion_rect, "frame": 0})
                self.fireballs.remove(fb)

        for exp in self.explosions[:]:
            exp["frame"] += self.explosion_animation_speed
            if exp["frame"] >= 3:  # Stop after the last explosion frame (0, 1, 2)
                self.explosions.remove(exp)

    def draw(self, screen):
        screen.blit(self.current_sprite, self.rect)
        for fb in self.fireballs:
            sprite = self.fireball_sprites[int(fb["frame"])]
            screen.blit(sprite, fb["rect"])
        for exp in self.explosions:
            frame_index = int(exp["frame"])
            sprite = self.explosion_sprites[frame_index]
            # Adjust position for smaller explosion frames
            if frame_index == 1:  # Medium explosion (24x24)
                offset = (self.explosion_size - 24) // 2
                screen.blit(sprite, (exp["rect"].x + offset, exp["rect"].y + offset))
            elif frame_index == 2:  # Small explosion (16x16)
                offset = (self.explosion_size - 16) // 2
                screen.blit(sprite, (exp["rect"].x + offset, exp["rect"].y + offset))
            else:  # Large explosion (32x32)
                screen.blit(sprite, exp["rect"])