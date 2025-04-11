import pygame
import sys
import os
import random
from player import Player
from world import World
from enemy import Enemy
from bush import Bush
from companion import Companion

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Initialize Pygame
pygame.init()

# Initialize Pygame mixer for audio
pygame.mixer.init()
music_path = os.path.join(PROJECT_ROOT, "assets/audio/background_music.mp3")
pygame.mixer.music.load(music_path)
pygame.mixer.music.play(-1)  # Loop indefinitely

# Load sound effects
hit_sound = pygame.mixer.Sound(os.path.join(PROJECT_ROOT, "assets/audio/hit.wav"))
shoot_sound = pygame.mixer.Sound(os.path.join(PROJECT_ROOT, "assets/audio/shoot.wav"))
gameover_sound = pygame.mixer.Sound(os.path.join(PROJECT_ROOT, "assets/audio/gameover.wav"))

# Constants
WINDOW_WIDTH = 960
WINDOW_HEIGHT = 640
FPS = 60

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED)
pygame.display.set_caption("Barker's Adventure + Pets!: Nina Barks, Alice Bites")
clock = pygame.time.Clock()

# Initialize joystick
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
for joystick in joysticks:
    joystick.init()
    print(f"Gamepad connected: {joystick.get_name()}")

# Fonts for title screen and game over
title_font = pygame.font.Font(None, 48)  # Bigger font for title
font = pygame.font.Font(None, 36)        # Regular font for instructions

# **Game Initialization Function**
# Purpose: Sets up the game world, player, enemies, bushes, and companions when starting or restarting
def init_game():
    # Pass WINDOW_WIDTH, WINDOW_HEIGHT, and screen to World
    world = World(WINDOW_WIDTH, WINDOW_HEIGHT, screen)
    player = Player(WINDOW_WIDTH // 2 - 24, WINDOW_HEIGHT // 2 - 24, world)
    world.player = player
    enemies = []
    if world.current_room_index == 0:
        for _ in range(3):
            while True:
                x = random.randint(1, world.map_width - 2) * world.tile_size
                y = random.randint(1, world.map_height - 2) * world.tile_size
                if not world.is_wall(x, y):
                    enemies.append(Enemy(x, y, "octorok", world))
                    break
    bushes = [
        Bush(8 * world.tile_size, 8 * world.tile_size),
        Bush(10 * world.tile_size, 8 * world.tile_size),
        Bush(12 * world.tile_size, 8 * world.tile_size)
    ]
    cat = Companion(player.rect.x + 40, player.rect.y, "cat")
    dog = Companion(cat.rect.x + 40, cat.rect.y, "dog")
    world.initialize_room_objects()
    return world, player, enemies, bushes, cat, dog

# Initial game setup
world, player, enemies, bushes, cat, dog = init_game()
game_state = "title"
door_unlocked = False  # Flag to track door state

# **Main Game Loop**
# Purpose: Runs continuously, handling events, updating game state, and rendering
running = True
while running:
    # **Event Handling**
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif game_state == "title" and event.key == pygame.K_SPACE:
                game_state = "playing"
            elif game_state == "playing" and event.key == pygame.K_SPACE:
                player.shoot_fireball()
                shoot_sound.play()
            elif game_state == "game_over" and event.key == pygame.K_r:
                world, player, enemies, bushes, cat, dog = init_game()
                game_state = "playing"
                door_unlocked = False  # Reset door state on restart
        elif event.type == pygame.JOYBUTTONDOWN and game_state == "playing":
            if event.button == 0:
                player.shoot_fireball()
                shoot_sound.play()

    # **Title Screen State**
    if game_state == "title":
        screen.fill((0, 0, 0))
        title_text = title_font.render("Barker's Adventure + Pets!:", True, (255, 255, 255))
        subtitle_text = title_font.render("Nina Bites, Alice Meows", True, (255, 255, 255))
        start_text = font.render("Press SPACE to Start", True, (255, 255, 0))
        screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, WINDOW_HEIGHT // 2 - 60))
        screen.blit(subtitle_text, (WINDOW_WIDTH // 2 - subtitle_text.get_width() // 2, WINDOW_HEIGHT // 2 - 20))
        screen.blit(start_text, (WINDOW_WIDTH // 2 - start_text.get_width() // 2, WINDOW_HEIGHT // 2 + 40))

    # **Playing State**
    elif game_state == "playing":
        # **Handle Input**
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

        # **Update Game State**
        player.update()
        player.update_fireballs(WINDOW_WIDTH, WINDOW_HEIGHT)
        cat.update(player.rect)
        dog.update(cat.rect)
        if world.current_room_index == 0:
            for enemy in enemies:
                enemy.update(WINDOW_WIDTH, WINDOW_HEIGHT, player.fireballs)
                if not enemy.is_dying and player.rect.colliderect(enemy.rect):
                    player.take_damage()
                    hit_sound.play()
            enemies = [enemy for enemy in enemies if not enemy.is_dead()]
            print(f"Enemies remaining: {len(enemies)}")
            print(f"Tile at (9, 28): {world.tile_map[9][28]}")
            for bush in bushes[:]:
                hit_fireball = bush.check_fireball_collision(player.fireballs)
                if hit_fireball:
                    explosion = hit_fireball.explode()
                    player.explosions.append(explosion)
                    player.fireballs.remove(hit_fireball)
            bushes = [bush for bush in bushes if not bush.destroyed]
            # Check if door should be unlocked
            if len(enemies) == 0 and not door_unlocked:
                if world.tile_map[9][28] == 3:
                    world.set_tile(9, 28, 2)
                    door_unlocked = True
                    print("Door unlocked!")
                else:
                    print("All enemies defeated, but door tile is not a locked door (type 3).")
            elif len(enemies) > 0:
                print("Enemies remain - door not unlocked yet.")
            elif door_unlocked:
                print("Door already unlocked.")
        elif world.current_room_index == 1:
            for chest in world.chests:
                item = chest.check_collision(player.rect)
                if item and item not in player.inventory:
                    player.inventory.append(item)
                    print(f"Collected {item}!")

        if player.health <= 0:
            game_state = "game_over"
            gameover_sound.play()

        # **Draw Everything**
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
        cat.draw(screen)
        dog.draw(screen)
        player.draw(screen, WINDOW_WIDTH)

    # **Game Over State**
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