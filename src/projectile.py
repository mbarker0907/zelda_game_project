import pygame

class Projectile:
    # **Initialization**
    def __init__(self, x, y, vx, vy, sprites, explosion_sprites, projectile_type, power):
        self.rect = pygame.Rect(x, y, 16, 16)
        self.vx = vx
        self.vy = vy
        self.sprites = sprites
        self.explosion_sprites = explosion_sprites
        self.current_frame = 0
        self.animation_speed = 0.2
        self.animation_counter = 0
        self.lifetime = 120
        self.type = projectile_type
        self.power = power

    # **Update Projectile**
    def update(self, window_width, window_height):
        self.rect.x += self.vx
        self.rect.y += self.vy
        self.lifetime -= 1
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.current_frame = (self.current_frame + 1) % len(self.sprites)
            self.animation_counter = 0
        return 0 <= self.rect.x <= window_width and 0 <= self.rect.y <= window_height and self.lifetime > 0

    # **Explode**
    def explode(self):
        return {"x": self.rect.centerx, "y": self.rect.centery, "frame": 0}

    # **Draw Projectile**
    def draw(self, screen):
        screen.blit(self.sprites[self.current_frame], self.rect)