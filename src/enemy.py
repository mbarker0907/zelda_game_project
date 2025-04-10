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

        # Health and death state
        self.health = 3  # Enemies take 3 hits to defeat
        self.is_dying = False  # Flag to indicate if the enemy is in its death animation
        self.death_timer = 0  # Timer for the death animation
        self.death_duration = 60  # 1 second at 60 FPS
        self.alpha = 255  # Alpha value for fading out during death

        # Load the enemy sprite sheet based on type
        if enemy_type == "skeleton":
            sprite_sheet_path = os.path.join(PROJECT_ROOT, "assets/enemies/skeleton_sheet.png")
        elif enemy_type == "octorok":
            sprite_sheet_path = os.path.join(PROJECT_ROOT, "assets/enemies/octorok_sheet.png")
        else:
            raise ValueError(f"Unsupported enemy type: {enemy_type}")

        if not os.path.exists(sprite_sheet_path):
            raise FileNotFoundError(f"Enemy sprite sheet not found at: {sprite_sheet_path}")
        self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        # Verify dimensions (assuming 144x192 for 3x4 frames)
        expected_width = 144  # 3 frames wide (48x3)
        expected_height = 192  # 4 frames tall (48x4)
        actual_width, actual_height = self.sprite_sheet.get_width(), self.sprite_sheet.get_height()
        if actual_width < expected_width or actual_height < expected_height:
            raise ValueError(f"Enemy sprite sheet dimensions {actual_width}x{actual_height} are smaller than required {expected_width}x{expected_height}")
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

    def check_fireball_collision(self, fireballs):
        """Check for collisions with fireballs and reduce health if hit."""
        if self.is_dying:
            return  # Skip collision checks if already dying

        for fireball in fireballs[:]:  # Copy the list to allow modification
            if not fireball.exploded and self.rect.colliderect(fireball.rect):
                self.health -= 1
                # Trigger explosion and add it to the player's explosions list
                explosion = fireball.explode()
                self.world.player.explosions.append(explosion)  # Access player via world
                fireballs.remove(fireball)  # Remove the fireball on hit
                print(f"{self.enemy_type} hit! Health: {self.health}")
                if self.health <= 0:
                    self.is_dying = True
                break  # Exit the loop after a hit to avoid multiple hits in one frame

    def update(self, window_width, window_height, fireballs):
        # Check for fireball collisions
        self.check_fireball_collision(fireballs)

        # If dying, play the death animation
        if self.is_dying:
            self.death_timer += 1
            # Fade out by reducing alpha
            self.alpha = max(0, 255 - (255 * self.death_timer // self.death_duration))
            # Add a blinking effect: toggle visibility every 5 frames
            if (self.death_timer // 5) % 2 == 0:
                self.current_sprite.set_alpha(self.alpha)
            else:
                self.current_sprite.set_alpha(0)  # Invisible for a brief moment
            return  # Skip movement and animation updates while dying

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

    def is_dead(self):
        """Return True if the enemy has finished its death animation."""
        return self.is_dying and self.death_timer >= self.death_duration