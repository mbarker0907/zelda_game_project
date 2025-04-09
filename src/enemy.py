import pygame
import os

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Enemy:
    def __init__(self, x, y, enemy_type, world):
        self.world = world
        self.size = 32  # Skeleton frames are 32x32
        self.enemy_type = enemy_type
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.speed = 2
        self.direction = "right"
        self.frame = 0
        self.animation_speed = 0.2
        self.direction_timer = 0
        self.direction_interval = 120  # 2 seconds at 60 FPS

        # Load the skeleton sprite sheet
        if enemy_type == "skeleton":
            sprite_sheet_path = os.path.join(PROJECT_ROOT, "assets/enemies/skeleton_sheet.png")
            if not os.path.exists(sprite_sheet_path):
                raise FileNotFoundError(f"Skeleton sprite sheet not found at: {sprite_sheet_path}")
            self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
            # Verify dimensions
            expected_width = 96  # 3 frames wide
            expected_height = 128  # 4 frames tall
            actual_width, actual_height = self.sprite_sheet.get_width(), self.sprite_sheet.get_height()
            if (actual_width, actual_height) != (expected_width, expected_height):
                raise ValueError(f"Skeleton sprite sheet dimensions are {actual_width}x{actual_height}, expected {expected_width}x{expected_height}")
            # Extract walking frames (first 2 frames in the first row)
            self.walking_frames = []
            frame_width = 32
            frame_height = 32
            for i in range(2):  # First 2 frames
                frame = self.sprite_sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
                self.walking_frames.append(frame)
            self.current_sprite = self.walking_frames[0]
        else:
            raise ValueError(f"Unsupported enemy type: {enemy_type}")

    def update(self, window_width, window_height):
        self.direction_timer += 1
        if self.direction_timer >= self.direction_interval:
            self.direction = "left" if self.direction == "right" else "right"
            self.direction_timer = 0

        vx = self.speed if self.direction == "right" else -self.speed
        new_x = self.rect.x + vx
        new_y = self.rect.y

        can_move = True
        if self.world.is_wall(new_x, new_y):
            can_move = False
        if self.world.is_wall(new_x + self.size - 1, new_y):
            can_move = False
        if self.world.is_wall(new_x, new_y + self.size - 1):
            can_move = False
        if self.world.is_wall(new_x + self.size - 1, new_y + self.size - 1):
            can_move = False

        if not can_move:
            self.direction = "left" if self.direction == "right" else "right"
            self.direction_timer = 0
            vx = self.speed if self.direction == "right" else -self.speed
            new_x = self.rect.x + vx

        if 0 <= new_x <= window_width - self.size:
            self.rect.x = new_x

        self.frame = (self.frame + self.animation_speed) % 2
        self.current_sprite = self.walking_frames[int(self.frame)]

    def draw(self, screen):
        screen.blit(self.current_sprite, self.rect)