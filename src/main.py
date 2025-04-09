import pygame
import sys
import os
from player import Player
from world import World

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Syb's Zelda Game")
clock = pygame.time.Clock()

# Initialize joystick (for gamepad support)
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
for joystick in joysticks:
    joystick.init()
    print(f"Gamepad connected: {joystick.get_name()}")

# Create the world and player
world = World()
player = Player(WINDOW_WIDTH // 2 - 24, WINDOW_HEIGHT // 2 - 24)

# Main game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                player.shoot_fireball()
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:  # Button "A" on Logitech Dual Action
                player.shoot_fireball()

    # Get keyboard and joystick input
    keys = pygame.key.get_pressed()
    # Get gamepad input (left analog stick)
    joystick_vx, joystick_vy = 0, 0
    if joysticks:
        joystick = joysticks[0]
        joystick_vx = joystick.get_axis(0)  # Left/Right (X-axis)
        joystick_vy = joystick.get_axis(1)  # Up/Down (Y-axis)
        # Apply deadzone to avoid drift
        deadzone = 0.2
        if abs(joystick_vx) < deadzone:
            joystick_vx = 0
        if abs(joystick_vy) < deadzone:
            joystick_vy = 0
        # Scale joystick input to match keyboard speed
        joystick_vx *= player.speed
        joystick_vy *= player.speed

    # Combine keyboard and joystick input
    if joystick_vx != 0 or joystick_vy != 0:
        # Use joystick input if present
        player.move_with_velocity(joystick_vx, joystick_vy, WINDOW_WIDTH, WINDOW_HEIGHT)
    else:
        # Otherwise use keyboard input
        player.move(keys, WINDOW_WIDTH, WINDOW_HEIGHT)

    # Update
    player.update_fireballs(WINDOW_WIDTH, WINDOW_HEIGHT)

    # Draw
    screen.fill((255, 255, 255))  # White background
    world.draw(screen)  # Draw the tile map
    player.draw(screen)  # Draw the player on top
    pygame.display.flip()

    # Control frame rate
    clock.tick(FPS)

# Quit Pygame
pygame.quit()
sys.exit()