import pygame
import os

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Companion:
    def __init__(self, x, y, companion_type="cat"):
        self.rect = pygame.Rect(x, y, 32, 32)  # 32x32 collision box
        self.speed = 2  # Slower than player (assumes player speed is 3-5)
        self.companion_type = companion_type
        
        # Load sprite sheet
        sprite_sheet_path = os.path.join(PROJECT_ROOT, f"assets/player/{companion_type}.png")
        self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        
        # Verify dimensions
        if self.sprite_sheet.get_width() != 96 or self.sprite_sheet.get_height() != 128:
            raise ValueError(f"{companion_type}.png dimensions are {self.sprite_sheet.get_width()}x{self.sprite_sheet.get_height()}, expected 96x128")
        
        # Extract frames (3 columns x 4 rows)
        self.frame_width = 32
        self.frame_height = 32
        self.frames = {
            "down": [],
            "left": [],
            "right": [],
            "up": []
        }
        directions = ["down", "left", "right", "up"]
        for row, direction in enumerate(directions):
            for col in range(3):
                frame = self.sprite_sheet.subsurface((col * self.frame_width, row * self.frame_height, self.frame_width, self.frame_height))
                self.frames[direction].append(frame)
        
        # Animation state
        self.current_direction = "down"
        self.current_frame = 0
        self.animation_speed = 0.15  # Frames per update
        self.animation_counter = 0

    def update(self, player_rect):
        """Follow the player and update animation."""
        # Calculate direction to player
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        # Move toward player if too far
        if distance > 40:  # Keep a small gap
            if distance != 0:
                dx, dy = dx / distance, dy / distance
            self.rect.x += int(dx * self.speed)
            self.rect.y += int(dy * self.speed)
        
        # Match player's direction based on movement
        if abs(dx) > abs(dy):
            self.current_direction = "right" if dx > 0 else "left"
        else:
            self.current_direction = "down" if dy > 0 else "up"
        
        # Update animation
        self.animation_counter += self.animation_speed
        if self.animation_counter >= 1:
            self.current_frame = (self.current_frame + 1) % 3  # Cycle through 3 frames
            self.animation_counter = 0

    def draw(self, screen):
        """Draw the current frame."""
        frame = self.frames[self.current_direction][self.current_frame]
        screen.blit(frame, self.rect)