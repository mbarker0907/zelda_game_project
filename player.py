import pygame

class Player:
    def __init__(self, x, y):
        self.size = 48  # Was 32, now 48—50% bigger
        self.sprites = {
            "back": [pygame.transform.scale(pygame.image.load(f"assets/syb1_bk{i}.png").convert_alpha(), (self.size, self.size)) for i in range(1, 3)],
            "front": [pygame.transform.scale(pygame.image.load(f"assets/syb1_fr{i}.png").convert_alpha(), (self.size, self.size)) for i in range(1, 3)],
            "left": [pygame.transform.scale(pygame.image.load(f"assets/syb1_lf{i}.png").convert_alpha(), (self.size, self.size)) for i in range(1, 3)],
            "right": [pygame.transform.scale(pygame.image.load(f"assets/syb1_rt{i}.png").convert_alpha(), (self.size, self.size)) for i in range(1, 3)]
        }
        self.current_sprite = self.sprites["front"][0]
        self.rect = self.current_sprite.get_rect(topleft=(x, y))
        self.speed = 3  # Was 5, now 3—slower movement
        self.direction = "front"
        self.frame = 0
        self.animation_speed = 0.2

    def move(self, keys, window_width, window_height):
        prev_x, prev_y = self.rect.x, self.rect.y
        moving = False

        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
            self.direction = "left"
            moving = True
        elif keys[pygame.K_RIGHT] and self.rect.right < window_width:
            self.rect.x += self.speed
            self.direction = "right"
            moving = True
        elif keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
            self.direction = "back"
            moving = True
        elif keys[pygame.K_DOWN] and self.rect.bottom < window_height:
            self.rect.y += self.speed
            self.direction = "front"
            moving = True

        if moving:
            self.frame = (self.frame + self.animation_speed) % 2
            self.current_sprite = self.sprites[self.direction][int(self.frame)]
        else:
            self.frame = 0
            self.current_sprite = self.sprites[self.direction][0]

    def draw(self, screen):
        screen.blit(self.current_sprite, self.rect)