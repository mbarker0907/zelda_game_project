import pygame
from player import Player

# Initialize Pygame and joystick
pygame.init()
pygame.joystick.init()

# Set up the game window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Zelda Game Project")

# Initialize gamepad (if connected)
if pygame.joystick.get_count() > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Gamepad connected: {joystick.get_name()}")
else:
    print("No gamepad detected—using keyboard only.")

# Create player
player = Player(WINDOW_WIDTH // 2 - 24, WINDOW_HEIGHT // 2 - 24)
WHITE = (255, 255, 255)

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Default keyboard input
    keys = pygame.key.get_pressed()

    # Override with gamepad input if available
    if pygame.joystick.get_count() > 0:
        joy_x = joystick.get_axis(0)  # -1 (left) to 1 (right)
        joy_y = joystick.get_axis(1)  # -1 (up) to 1 (down)
        # Custom keys dict based on joystick input
        keys = {
            pygame.K_LEFT: joy_x < -0.1 or keys[pygame.K_LEFT],
            pygame.K_RIGHT: joy_x > 0.1 or keys[pygame.K_RIGHT],
            pygame.K_UP: joy_y < -0.1 or keys[pygame.K_UP],
            pygame.K_DOWN: joy_y > 0.1 or keys[pygame.K_DOWN]
        }

    player.move(keys, WINDOW_WIDTH, WINDOW_HEIGHT)

    # Draw
    screen.fill(WHITE)
    player.draw(screen)

    pygame.display.flip()
    clock.tick(60)

# Cleanup
pygame.joystick.quit()
pygame.quit()