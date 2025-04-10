import pygame
import sys
import os
from player import Player
from world import World
from enemy import Enemy
from bush import Bush

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

# Font for FPS and game over display
font = pygame.font.Font(None, 36)

# Game initialization function
def init_game():
    world = World()
    player = Player(WINDOW_WIDTH // 2 - 24, WINDOW_HEIGHT // 2 - 24, world)
    world.player = player
    enemies = []
    if world.current_room_index == 0:
        octorok1 = Enemy(300, 300, "octorok", world)
        octorok2 = Enemy(350, 300, "octorok", world)
        octorok3 = Enemy(400, 300, "octorok", world)
        enemies = [octorok1, octorok2, octorok3]
    bushes = [
        Bush(5 * world.tile_size, 5 * world.tile_size),
        Bush(6 * world.tile_size, 5 * world.tile_size),
        Bush(7 * world.tile_size, 5 * world.tile_size)
    ]
    world.initialize_room_objects()  # Spawn chests initially
    return world, player, enemies, bushes

# Initial game setup
world, player, enemies, bushes = init_game()
game_state = "playing"  # Start in playing state

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif game_state == "playing" and event.key == pygame.K_SPACE:
                player.shoot_fireball()
            elif game_state == "game_over" and event.key == pygame.K_r:
                world, player, enemies, bushes = init_game()
                game_state = "playing"
        elif event.type == pygame.JOYBUTTONDOWN and game_state == "playing":
            if event.button == 0:
                player.shoot_fireball()

    if game_state == "playing":
        # Handle input
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

        # Move player
        if joystick_vx != 0 or joystick_vy != 0:
            player.move_with_velocity(joystick_vx, joystick_vy, WINDOW_WIDTH, WINDOW_HEIGHT)
        else:
            player.move(keys, WINDOW_WIDTH, WINDOW_HEIGHT)

        # Update game state
        player.update()
        player.update_fireballs(WINDOW_WIDTH, WINDOW_HEIGHT)
        if world.current_room_index == 0:
            for enemy in enemies:
                enemy.update(WINDOW_WIDTH, WINDOW_HEIGHT, player.fireballs)
                player_collision_rect = player.rect.inflate(4, 4)
                enemy_collision_rect = enemy.rect.inflate(4, 4)
                if not enemy.is_dying and player_collision_rect.colliderect(enemy_collision_rect):
                    player.take_damage()
            enemies = [enemy for enemy in enemies if not enemy.is_dead()]

            # Update bushes
            for bush in bushes[:]:
                hit_fireball = bush.check_fireball_collision(player.fireballs)
                if hit_fireball:
                    explosion = hit_fireball.explode()
                    player.explosions.append(explosion)
                    player.fireballs.remove(hit_fireball)
            bushes = [bush for bush in bushes if not bush.destroyed]

            # Unlock door in room 1
            if len(enemies) == 0 and world.tile_map[7][18] == 3:
                world.set_tile(7, 18, 2)
                print("Door unlocked!")
        elif world.current_room_index == 1:
            # Update chests in room 2
            for chest in world.chests:
                item = chest.check_collision(player.rect)
                if item and item not in player.inventory:
                    player.inventory.append(item)
                    print(f"Collected {item}!")

        # Check for game over
        if player.health <= 0:
            game_state = "game_over"

        # Draw everything
        screen.fill((200, 200, 200))
        world.draw(screen)
        if world.current_room_index == 0:
            for bush in bushes:
                bush.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
        elif world.current_room_index == 1:
            for chest in world.chests:
                chest.draw(screen)
        player.draw(screen, WINDOW_WIDTH)

        
    elif game_state == "game_over":
        screen.fill((0, 0, 0))
        game_over_text = font.render("Game Over", True, (255, 0, 0))
        restart_text = font.render("Press R to Restart", True, (255, 255, 255))
        screen.blit(game_over_text, (WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 20))
        screen.blit(restart_text, (WINDOW_WIDTH // 2 - 70, WINDOW_HEIGHT // 2 + 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()