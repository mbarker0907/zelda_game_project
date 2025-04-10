import pygame
import math
import os
from fireball import Fireball

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class Player:
    def __init__(self, x, y, world):
        self.world = world  # Store the world object for collision and door checks
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
        # Load final fireball sprite sheet with error handling
        fireball_path = os.path.join(PROJECT_ROOT, "assets/projectiles/fireball_splash_sheet_final.png")
        print(f"Attempting to load fireball sprite sheet from: {fireball_path}")
        if not os.path.exists(fireball_path):
            raise FileNotFoundError(f"Fireball sprite sheet not found at: {fireball_path}")
        self.fireball_sheet = pygame.image.load(fireball_path).convert_alpha()
        # Verify dimensions
        expected_width = 256  # 8 frames * 32 pixels
        expected_height = 32
        actual_width, actual_height = self.fireball_sheet.get_width(), self.fireball_sheet.get_height()
        if (actual_width, actual_height) != (expected_width, expected_height):
            raise ValueError(f"Fireball sprite sheet dimensions are {actual_width}x{actual_height}, expected {expected_width}x{expected_height}")
        print(f"Fireball sprite sheet loaded, dimensions: {actual_width}x{actual_height}")
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

        # Health and invincibility
        self.max_health = 3  # 3 hearts
        self.health = self.max_health
        self.invincible = False
        self.invincibility_timer = 0
        self.invincibility_duration = 60  # 1 second at 60 FPS

        # Load heart sprite for health display (24x24 for larger hearts)
        heart_path = os.path.join(PROJECT_ROOT, "assets/ui/heart.png")
        if not os.path.exists(heart_path):
            self.heart_sprite = pygame.Surface((24, 24))
            self.heart_sprite.fill((255, 0, 0))  # Red square as placeholder
        else:
            self.heart_sprite = pygame.transform.scale(pygame.image.load(heart_path).convert_alpha(), (24, 24))

    def take_damage(self):
        """Reduce health by 1 and make the player invincible for 1 second."""
        if not self.invincible:
            self.health = max(0, self.health - 1)
            self.invincible = True
            self.invincibility_timer = 0
            print(f"Player took damage! Health: {self.health}")
            if self.health <= 0:
                print("Game Over! Player has died.")

    def update(self):
        """Update invincibility timer and state."""
        if self.invincible:
            self.invincibility_timer += 1
            if self.invincibility_timer >= self.invincibility_duration:
                self.invincible = False
                self.invincibility_timer = 0
                self.current_sprite.set_alpha(255)  # Reset alpha
            # Add a blinking effect during invincibility
            if (self.invincibility_timer // 5) % 2 == 0:
                self.current_sprite.set_alpha(255)
            else:
                self.current_sprite.set_alpha(128)  # Semi-transparent for blinking effect
        else:
            self.current_sprite.set_alpha(255)  # Ensure full opacity when not invincible

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

        # Calculate new position
        new_x = self.rect.x + vx
        new_y = self.rect.y + vy

        # Check for collisions with walls
        can_move = True
        # Test the four corners of the player's rect after movement
        if self.world.is_wall(new_x, new_y):
            can_move = False
        if self.world.is_wall(new_x + self.size - 1, new_y):
            can_move = False
        if self.world.is_wall(new_x, new_y + self.size - 1):
            can_move = False
        if self.world.is_wall(new_x + self.size - 1, new_y + self.size - 1):
            can_move = False

        # Check for door interaction (center of player)
        door_transition = None
        tile_type = self.world.get_tile_type(new_x + self.size // 2, new_y + self.size // 2)
        if tile_type == 2:  # Unlocked door
            current_room = self.world.current_room_index
            if current_room == 0:  # Room 1 to Room 2
                door_transition = (1, (2 * self.world.tile_size, 7 * self.world.tile_size))
            elif current_room == 1:  # Room 2 to Room 1
                door_transition = (0, (2 * self.world.tile_size, 7 * self.world.tile_size))
        elif tile_type == 3:  # Locked door (optional feedback)
            print("The door is locked.")

        # Update position if no collision
        if can_move and 0 <= new_x <= window_width - self.size and 0 <= new_y <= window_height - self.size:
            self.rect.x = new_x
            self.rect.y = new_y

        # Handle door transition
        if door_transition:
            new_room_index, (new_x, new_y) = door_transition
            self.world.switch_room(new_room_index)
            self.rect.x = new_x
            self.rect.y = new_y
            print(f"Transitioned to room {new_room_index + 1}, player position: ({self.rect.x}, {self.rect.y})")

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

        # Calculate new position
        new_x = self.rect.x + vx
        new_y = self.rect.y + vy

        # Check for collisions with walls
        can_move = True
        if self.world.is_wall(new_x, new_y):
            can_move = False
        if self.world.is_wall(new_x + self.size - 1, new_y):
            can_move = False
        if self.world.is_wall(new_x, new_y + self.size - 1):
            can_move = False
        if self.world.is_wall(new_x + self.size - 1, new_y + self.size - 1):
            can_move = False

        # Check for door interaction (trigger when near the door)
        door_transition = None
        player_center_x = new_x + self.size // 2
        player_center_y = new_y + self.size // 2
        # Convert player center to tile coordinates
        col = int(player_center_x // self.world.tile_size)
        row = int(player_center_y // self.world.tile_size)
        # Check if the tile at (col, row) is a door
        if 0 <= row < self.world.map_height and 0 <= col < self.world.map_width:
            tile_type = self.world.tile_map[row][col]
            if tile_type == 2:  # Unlocked door
                current_room = self.world.current_room_index
                if current_room == 0:  # Room 1
                    # Transition to room 2, position Syb in front of the door at (1,7)
                    door_x = 1 * self.world.tile_size
                    door_y = 7 * self.world.tile_size
                    # Position Syb to the right of the door (since door is on left wall of room 2)
                    new_player_x = door_x + self.world.tile_size  # One tile to the right
                    new_player_y = door_y + (self.world.tile_size - self.size) // 2  # Center vertically
                    door_transition = (1, (new_player_x, new_player_y))
                elif current_room == 1:  # Room 2
                    # Transition to room 1, position Syb in front of the door at (18,7)
                    door_x = 18 * self.world.tile_size
                    door_y = 7 * self.world.tile_size
                    # Position Syb to the left of the door (since door is on right wall of room 1)
                    new_player_x = door_x - self.size  # One tile to the left
                    new_player_y = door_y + (self.world.tile_size - self.size) // 2  # Center vertically
                    door_transition = (0, (new_player_x, new_player_y))
            elif tile_type == 3:  # Locked door (optional feedback)
                print("The door is locked.")

        if can_move and 0 <= new_x <= window_width - self.size and 0 <= new_y <= window_height - self.size:
            self.rect.x = new_x
            self.rect.y = new_y

        if door_transition:
            new_room_index, (new_x, new_y) = door_transition
            self.world.switch_room(new_room_index)
            self.rect.x = new_x
            self.rect.y = new_y
            print(f"Transitioned to room {new_room_index + 1}, player position: ({self.rect.x}, {self.rect.y})")

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
        # Determine fireball direction based on the player's current direction
        vx, vy = 0, 0
        fireball_speed = 5
        if self.direction == "left":
            vx = -fireball_speed
        elif self.direction == "right":
            vx = fireball_speed
        elif self.direction == "back":  # Up
            vy = -fireball_speed
        elif self.direction == "front":  # Down
            vy = fireball_speed

        # Override direction if a key is currently pressed
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            vx, vy = -fireball_speed, 0
            self.direction = "left"
        elif keys[pygame.K_RIGHT]:
            vx, vy = fireball_speed, 0
            self.direction = "right"
        elif keys[pygame.K_UP]:
            vx, vy = 0, -fireball_speed
            self.direction = "back"
        elif keys[pygame.K_DOWN]:
            vx, vy = 0, fireball_speed
            self.direction = "front"

        # Create a new Fireball object with the player's fireball sprites
        fireball = Fireball(
            self.rect.centerx, self.rect.centery, vx, vy,
            self.fireball_sprites, self.explosion_sprites,
            self.fireball_animation_speed
        )
        self.fireballs.append(fireball)

    def update_fireballs(self, window_width, window_height):
        # Update fireballs and remove those that are off-screen or exploded
        for fireball in self.fireballs[:]:
            if fireball.update(window_width, window_height):
                # Check for collisions with walls
                if (self.world.is_wall(fireball.rect.x, fireball.rect.y) or
                    self.world.is_wall(fireball.rect.x + fireball.rect.width - 1, fireball.rect.y) or
                    self.world.is_wall(fireball.rect.x, fireball.rect.y + fireball.rect.height - 1) or
                    self.world.is_wall(fireball.rect.x + fireball.rect.width - 1, fireball.rect.y + fireball.rect.height - 1)):
                    # Fireball hit a wall, trigger explosion
                    explosion = fireball.explode()
                    self.explosions.append(explosion)
                    self.fireballs.remove(fireball)
            else:
                # Fireball went off-screen, remove it without explosion
                self.fireballs.remove(fireball)

        # Update explosions
        for exp in self.explosions[:]:
            exp["frame"] += self.explosion_animation_speed
            if exp["frame"] >= 3:  # Stop after the last explosion frame (0, 1, 2)
                self.explosions.remove(exp)

    def draw(self, screen):
        screen.blit(self.current_sprite, self.rect)
        # Draw fireballs
        for fireball in self.fireballs:
            fireball.draw(screen)
        # Draw explosions
        for exp in self.explosions:
            frame = int(exp["frame"])
            if frame < len(self.explosion_sprites):
                sprite = self.explosion_sprites[frame]
                sprite_rect = sprite.get_rect(center=(exp["x"], exp["y"]))
                screen.blit(sprite, sprite_rect)
        # Draw health (hearts) in the top-left corner
        for i in range(self.max_health):
            heart_x = 10 + i * (self.heart_sprite.get_width() + 10)  # 10px padding, 10px between hearts
            heart_y = 10  # 10px from the top
            if i < self.health:
                screen.blit(self.heart_sprite, (heart_x, heart_y))
            else:
                # Draw an empty heart (semi-transparent)
                empty_heart = self.heart_sprite.copy()
                empty_heart.set_alpha(64)  # 25% opacity for empty hearts
                screen.blit(empty_heart, (heart_x, heart_y))