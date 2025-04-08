import pygame

# Initialize Pygame
pygame.init()

# Set up the game window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Zelda Game Project")

# Player properties
player_size = 40
player_x = WINDOW_WIDTH // 2 - player_size // 2  # Center horizontally
player_y = WINDOW_HEIGHT // 2 - player_size // 2  # Center vertically
player_speed = 5

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_x > 0:
        player_x -= player_speed
    if keys[pygame.K_RIGHT] and player_x < WINDOW_WIDTH - player_size:
        player_x += player_speed
    if keys[pygame.K_UP] and player_y > 0:
        player_y -= player_speed
    if keys[pygame.K_DOWN] and player_y < WINDOW_HEIGHT - player_size:
        player_y += player_speed

    # Draw everything
    screen.fill(WHITE)  # Background
    pygame.draw.rect(screen, GREEN, (player_x, player_y, player_size, player_size))  # Player

    # Update display
    pygame.display.flip()
    clock.tick(60)  # 60 FPS

# Quit Pygame
pygame.quit()