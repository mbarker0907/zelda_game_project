import pygame
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Companion:
    def __init__(self, x, y, companion_type="cat"):
        self.companion_type = companion_type
        # Set size based on type
        if companion_type == "cat":
            self.frame_width = 16
            self.frame_height = 16
        else:  # Default to dog size
            self.frame_width = 32
            self.frame_height = 32
        self.rect = pygame.Rect(x, y, self.frame_width, self.frame_height)  # Adjust collision box
        self.speed = 2
        
        # Load sprite sheet
        sprite_sheet_path = os.path.join(PROJECT_ROOT, f"assets/player/{companion_type}.png")
        self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        if self.sprite_sheet.get_width() != 96 or self.sprite_sheet.get_height() != 128:
            raise ValueError(f"{companion_type}.png dimensions are {self.sprite_sheet.get_width()}x{self.sprite_sheet.get_height()}, expected 96x128")
        
        # Extract and scale frames
        original_frame_width = 32
        original_frame_height = 32
        self.frames = {
            "down": [], "left": [], "right": [], "up": []
        }
        directions = ["down", "left", "right", "up"]
        for row, direction in enumerate(directions):
            for col in range(3):
                frame = self.sprite_sheet.subsurface((col * original_frame_width, row * original_frame_height, original_frame_width, original_frame_height))
                # Scale to desired size
                frame = pygame.transform.scale(frame, (self.frame_width, self.frame_height))
                self.frames[direction].append(frame)
        
        self.current_direction = "down"
        self.current_frame = 0
        self.animation_speed = 0.15
        self.animation_counter = 0

    def update(self, target_rect):
        dx = target_rect.centerx - self.rect.centerx
        dy = target_rect.centery - self.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance > 40:
            if distance != 0:
                dx, dy = dx / distance, dy / distance
            self.rect.x += int(dx * self.speed)
            self.rect.y += int(dy * self.speed)
        if abs(dx) > abs(dy):
            self.current_direction = "right" if dx > 0 else "left"
        else:
            self.current_direction = "down" if dy > 0 else "up"
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.current_frame = (self.current_frame + 1) % 3
            self.animation_counter = 0

    def draw(self, screen):
        frame = self.frames[self.current_direction][self.current_frame]
        screen.blit(frame, self.rect)