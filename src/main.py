import pygame
import sys
import os
from player import Player
from world import World
from enemy import Enemy

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
FPS = 60

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED)
pygame.display.set_caption("Syb's Zelda Game")
clock = pygame.time.Clock()

# Initialize joystick
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
for joystick in joysticks:
    joystick.init()
    print(f"Gamepad connected: {joystick.get_name()}")

# Create the world and player
world = World()
player = Player(WINDOW_WIDTH // 2 - 24, WINDOW_HEIGHT // 2 - 24, world)

# Spawn the skeleton in room 1
enemies = []
if world.current_room_index == 0:
    skeleton = Enemy(200, 200, "skeleton", world)
    enemies.append(skeleton)

# Font for FPS display
font = pygame.font.Font(None, 36)

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                player.shoot_fireball()
        elif event.type == pygame.JOYBUTTONDOWN:
            if event.button == 0:
                player.shoot_fireball()

    keys = pygame.key.get_pressed()
    joystick_vx, joystick_vy = 0, 0
    if joysticks:
        joystick = joysticks[0]
        joystick_vx = joystick.get_axis(0)
        joystick_vy = joystick.get_axis(1)
        deadzone = 0.2
        if abs(joystick_vx) < deadzone:
            joystick_vx = 0
        if abs(joystick_vy) < deadzone:
            joystick_vy = 0
        joystick_vx *= player.speed
        joystick_vy *= player.speed

    if joystick_vx != 0 or joystick_vy != 0:
        player.move_with_velocity(joystick_vx, joystick_vy, WINDOW_WIDTH, WINDOW_HEIGHT)
    else:
        player.move(keys, WINDOW_WIDTH, WINDOW_HEIGHT)

    # Update
    player.update_fireballs(WINDOW_WIDTH, WINDOW_HEIGHT)
    if world.current_room_index == 0:
        for enemy in enemies:
            enemy.update(WINDOW_WIDTH, WINDOW_HEIGHT)

    # Draw
    screen.fill((255, 255, 255))
    world.draw(screen)
    if world.current_room_index == 0:
        for enemy in enemies:
            enemy.draw(screen)
    player.draw(screen)
    fps = str(int(clock.get_fps()))
    fps_text = font.render(fps, True, (255, 255, 255))
    fps_rect = fps_text.get_rect(topright=(WINDOW_WIDTH - 10, 10))
    screen.blit(fps_text, fps_rect)
    pygame.display.flip()

    clock.tick(FPS)

pygame.quit()
sys.exit()