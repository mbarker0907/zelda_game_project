import pygame
import math

class Player:
    def __init__(self, x, y):
        self.size = 48
        self.sprites = {
            "back": [pygame.transform.scale(pygame.image.load(f"assets/syb1_bk{i}.png").convert_alpha(), (self.size, self.size)) for i in range(1, 3)],
            "front": [pygame.transform.scale(pygame.image.load(f"assets/syb1_fr{i}.png").convert_alpha(), (self.size, self.size)) for i in range(1, 3)],
            "left": [pygame.transform.scale(pygame.image.load(f"assets/syb1_lf{i}.png").convert_alpha(), (self.size, self.size)) for i in range(1, 3)],
            "right": [pygame.transform.scale(pygame.image.load(f"assets/syb1_rt{i}.png").convert_alpha(), (self.size, self.size)) for i in range(1, 3)]
        }
        self.current_sprite = self.sprites["front"][0]
        self.rect = self.current_sprite.get_rect(topleft=(x, y))
        self.speed = 3
        self.direction = "front"
        self.frame = 0
        self.animation_speed = 0.2
        self.fireballs = []  # List to store active fireballs

    def move(self, keys, window_width, window_height):
        vx, vy = 0, 0
        moving = False

        if keys[pygame.K_LEFT]:
            vx -= self.speed
        if keys[pygame.K_RIGHT]:
            vx += self.speed
        if keys[pygame.K_UP]:
            vy -= self.speed
        if keys[pygame.K_DOWN]:
            vy += self.speed

        if vx != 0 and vy != 0:
            length = math.sqrt(vx**2 + vy**2)
            vx = vx * self.speed / length
            vy = vy * self.speed / length

        new_x = self.rect.x + vx
        new_y = self.rect.y + vy
        if 0 <= new_x <= window_width - self.size:
            self.rect.x = new_x
        if 0 <= new_y <= window_height - self.size:
            self.rect.y = new_y

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
        # Create a fireball based on direction
        fireball_size = 16
        fireball_speed = 5
        if self.direction == "front":
            fireball = pygame.Rect(self.rect.centerx - fireball_size // 2, self.rect.bottom, fireball_size, fireball_size)
            velocity = (0, fireball_speed)
        elif self.direction == "back":
            fireball = pygame.Rect(self.rect.centerx - fireball_size // 2, self.rect.top - fireball_size, fireball_size, fireball_size)
            velocity = (0, -fireball_speed)
        elif self.direction == "left":
            fireball = pygame.Rect(self.rect.left - fireball_size, self.rect.centery - fireball_size // 2, fireball_size, fireball_size)
            velocity = (-fireball_speed, 0)
        elif self.direction == "right":
            fireball = pygame.Rect(self.rect.right, self.rect.centery - fireball_size // 2, fireball_size, fireball_size)
            velocity = (fireball_speed, 0)
        self.fireballs.append({"rect": fireball, "velocity": velocity, "distance": 0})

    def update_fireballs(self, window_width, window_height):
        # Update fireball positions and remove if off-screen or too far
        max_distance = 150  # Mid-range limit
        for fb in self.fireballs[:]:  # Copy list to modify during iteration
            fb["rect"].x += fb["velocity"][0]
            fb["rect"].y += fb["velocity"][1]
            fb["distance"] += abs(fb["velocity"][0]) + abs(fb["velocity"][1])
            if (fb["rect"].left > window_width or fb["rect"].right < 0 or
                fb["rect"].top > window_height or fb["rect"].bottom < 0 or
                fb["distance"] > max_distance):
                self.fireballs.remove(fb)

    def draw(self, screen):
        screen.blit(self.current_sprite, self.rect)
        # Draw fireballs as orange circles for now
        for fb in self.fireballs:
            pygame.draw.circle(screen, (255, 100, 0), fb["rect"].center, fb["rect"].width // 2)