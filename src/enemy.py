import pygame
import os
import random

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Enemy:
    def __init__(self, x, y, enemy_type, world):
        self.world = world
        self.size = 48  # Using 48x48 frames from the resized sprite sheet
        self.enemy_type = enemy_type
        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.speed = 2
        self.direction = "right"  # Start moving right
        self.frame = 0  # Frame index (0 to 2)
        self.frame_timer = 0  # Timer to control animation speed
        self.animation_speed = 0.2  # Frames per update
        self.direction_timer = 0
        self.direction_interval = 120  # 2 seconds at 60 FPS

        # Load the skeleton sprite sheet
        if enemy_type == "skeleton":
            sprite_sheet_path = os.path.join(PROJECT_ROOT, "assets/enemies/skeleton_sheet.png")
            if not os.path.exists(sprite_sheet_path):
                raise FileNotFoundError(f"Skeleton sprite sheet not found at: {sprite_sheet_path}")
            self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
            # Verify dimensions
            expected_width = 144  # 3 frames wide (48x3)
            expected_height = 192  # 4 frames tall (48x4)
            actual_width, actual_height = self.sprite_sheet.get_width(), self.sprite_sheet.get_height()
            if (actual_width, actual_height) != (expected_width, expected_height):
                raise ValueError(f"Skeleton sprite sheet dimensions are {actual_width}x{actual_height}, expected {expected_width}x{expected_height}")

            # Extract walking frames for each direction
            self.walking_frames = {
                "up": [],
                "right": [],
                "down": [],
                "left": []
            }
            frame_width = 48
            frame_height = 48
            try:
                # Row 1: Walking up (y=0)
                for i in range(3):
                    frame = self.sprite_sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
                    self.walking_frames["up"].append(frame)

                # Row 2: Walking right (y=48)
                for i in range(3):
                    frame = self.sprite_sheet.subsurface((i * frame_width, 48, frame_width, frame_height))
                    self.walking_frames["right"].append(frame)

                # Row 3: Walking down (y=96)
                for i in range(3):
                    frame = self.sprite_sheet.subsurface((i * frame_width, 96, frame_width, frame_height))
                    self.walking_frames["down"].append(frame)

                # Row 4: Walking left (y=144)
                for i in range(3):
                    frame = self.sprite_sheet.subsurface((i * frame_width, 144, frame_width, frame_height))
                    self.walking_frames["left"].append(frame)

                self.current_sprite = self.walking_frames["right"][0]
            except pygame.error as e:
                raise pygame.error(f"Failed to extract frames from sprite sheet: {e}")
        else:
            raise ValueError(f"Unsupported enemy type: {enemy_type}")

    def update(self, window_width, window_height):
        # Update direction timer
        self.direction_timer += 1
        if self.direction_timer >= self.direction_interval:
            # Randomly choose a new direction
            self.direction = random.choice(["up", "down", "left", "right"])
            self.direction_timer = 0

        # Calculate velocity based on direction
        vx, vy = 0, 0
        if self.direction == "up":
            vy = -self.speed
        elif self.direction == "down":
            vy = self.speed
        elif self.direction == "left":
            vx = -self.speed
        elif self.direction == "right":
            vx = self.speed

        # Check for collisions
        new_x = self.rect.x + vx
        new_y = self.rect.y + vy

        can_move = True
        if self.world.is_wall(new_x, new_y):
            can_move = False
        if self.world.is_wall(new_x + self.size - 1, new_y):
            can_move = False
        if self.world.is_wall(new_x, new_y + self.size - 1):
            can_move = False
        if self.world.is_wall(new_x + self.size - 1, new_y + self.size - 1):
            can_move = False

        # If the enemy hits a wall, choose a new direction immediately
        if not can_move:
            self.direction = random.choice(["up", "down", "left", "right"])
            self.direction_timer = 0
            # Recalculate velocity with the new direction
            vx, vy = 0, 0
            if self.direction == "up":
                vy = -self.speed
            elif self.direction == "down":
                vy = self.speed
            elif self.direction == "left":
                vx = -self.speed
            elif self.direction == "right":
                vx = self.speed
            new_x = self.rect.x + vx
            new_y = self.rect.y + vy

        # Update position if within bounds
        if 0 <= new_x <= window_width - self.size:
            self.rect.x = new_x
        if 0 <= new_y <= window_height - self.size:
            self.rect.y = new_y

        # Update animation frame
        frames_for_direction = self.walking_frames.get(self.direction, [])
        if not frames_for_direction:
            raise ValueError(f"No frames found for direction: {self.direction}")

        # Use a timer to control frame changes
        self.frame_timer += self.animation_speed
        if self.frame_timer >= 1:
            self.frame_timer -= 1
            self.frame = (self.frame + 1) % len(frames_for_direction)  # Cycle through frames (0, 1, 2)
        self.current_sprite = frames_for_direction[self.frame]

    def draw(self, screen):
        screen.blit(self.current_sprite, self.rect)