import pygame
from player import Player

pygame.init()
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Zelda Game Project")

player = Player(WINDOW_WIDTH // 2 - 24, WINDOW_HEIGHT // 2 - 24)  # 48/2 = 24
WHITE = (255, 255, 255)

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.move(keys, WINDOW_WIDTH, WINDOW_HEIGHT)

    screen.fill(WHITE)
    player.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()