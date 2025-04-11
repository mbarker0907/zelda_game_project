import pygame
import sys
import os
import random
from player import Player
from world import World
from enemy import Enemy
from bush import Bush
from companion import Companion
from npc import NPC

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

pygame.init()
pygame.mixer.init()
music_path = os.path.join(PROJECT_ROOT, "assets/audio/background_music.mp3")
pygame.mixer.music.load(music_path)
pygame.mixer.music.play(-1)

hit_sound = pygame.mixer.Sound(os.path.join(PROJECT_ROOT, "assets/audio/hit.wav"))
shoot_sound = pygame.mixer.Sound(os.path.join(PROJECT_ROOT, "assets/audio/shoot.wav"))
gameover_sound = pygame.mixer.Sound(os.path.join(PROJECT_ROOT, "assets/audio/gameover.wav"))

WINDOW_WIDTH = 960
WINDOW_HEIGHT = 640
FPS = 60

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SCALED)
pygame.display.set_caption("Barker's Adventure + Pets!: Nina Barks, Alice Bites")
clock = pygame.time.Clock()

pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
for joystick in joysticks:
    joystick.init()
    print(f"Gamepad connected: {joystick.get_name()}")

title_font = pygame.font.Font(None, 48)
font = pygame.font.Font(None, 36)

def spawn_room_objects(world, enemies, bushes, npcs):
    enemies.clear()
    bushes.clear()
    npcs.clear()
    if world.current_room_index == 0:  # Town
        npcs.append(NPC(15 * world.tile_size, 10 * world.tile_size, "shopkeeper"))
        npcs.append(NPC(18 * world.tile_size, 12 * world.tile_size, "quest_giver"))
    elif world.current_room_index == 1:  # Forest Clearing
        for _ in range(5):
            while True:
                x = random.randint(1, world.map_width - 2) * world.tile_size
                y = random.randint(1, world.map_height - 2) * world.tile_size
                door_x, door_y = 27 * world.tile_size, 9 * world.tile_size
                dist = ((x - door_x) ** 2 + (y - door_y) ** 2) ** 0.5
                if not world.is_wall(x, y) and dist > 100:
                    enemy_type = random.choice(["octorok", "bat", "archer"])
                    enemies.append(Enemy(x, y, enemy_type, world))
                    break
        bushes.extend([
            Bush(8 * world.tile_size, 8 * world.tile_size),
            Bush(10 * world.tile_size, 8 * world.tile_size),
            Bush(12 * world.tile_size, 8 * world.tile_size)
        ])
    elif world.current_room_index == 2:  # Riverside
        for _ in range(3):
            while True:
                x = random.randint(1, world.map_width - 2) * world.tile_size
                y = random.randint(1, world.map_height - 2) * world.tile_size
                if not world.is_wall(x, y):
                    enemy_type = random.choice(["octorok", "bat", "archer"])
                    enemies.append(Enemy(x, y, enemy_type, world))
                    break
    elif world.current_room_index == 3:  # Boss Room
        enemies.append(Enemy(15 * world.tile_size, 10 * world.tile_size, "boss", world))
    world.initialize_room_objects()

def init_game():
    world = World(WINDOW_WIDTH, WINDOW_HEIGHT, screen)
    player = Player(WINDOW_WIDTH // 2 - 24, WINDOW_HEIGHT // 2 - 24, world, font)
    world.player = player
    enemies = []
    bushes = []
    npcs = []
    cat = Companion(player.rect.x + 40, player.rect.y, "cat")
    dog = Companion(cat.rect.x + 40, cat.rect.y, "dog")
    spawn_room_objects(world, enemies, bushes, npcs)
    return world, player, enemies, bushes, cat, dog, npcs

world, player, enemies, bushes, cat, dog, npcs = init_game()
game_state = "title"
door_unlocked = False
weather_alpha = 0
previous_room_index = world.current_room_index
current_shopkeeper = None

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif game_state == "title" and event.key == pygame.K_SPACE:
                game_state = "playing"
            elif game_state == "playing" and event.key == pygame.K_SPACE:
                player.shoot_projectile()
                shoot_sound.play()
            elif game_state == "playing" and event.key == pygame.K_e:
                for npc in npcs:
                    if player.rect.colliderect(npc.rect):
                        if npc.type == "shopkeeper":
                            current_shopkeeper = npc
                            game_state = "shopping"
                        else:
                            npc.interact(player)
            elif game_state == "playing" and event.key == pygame.K_1:
                player.switch_weapon(0)
            elif game_state == "playing" and event.key == pygame.K_2:
                player.switch_weapon(1)
            elif game_state == "game_over" and event.key == pygame.K_r:
                world, player, enemies, bushes, cat, dog, npcs = init_game()
                game_state = "playing"
                door_unlocked = False
                previous_room_index = world.current_room_index
            elif game_state == "shopping" and event.key == pygame.K_e:
                game_state = "playing"
                current_shopkeeper = None
            elif game_state == "shopping":
                keys = pygame.key.get_pressed()
                if current_shopkeeper:
                    items_to_remove = []  # Track items to remove after iteration
                    for idx, (item, price) in enumerate(current_shopkeeper.shop_items.items()):
                        if keys[pygame.K_1 + idx] and player.gold >= price:
                            if item == "ice_bolt" and "ice_bolt" in player.inventory:
                                continue
                            player.gold -= price
                            if item == "health_potion":
                                player.health = player.max_health
                            else:
                                player.inventory.append(item)
                            print(f"Bought {item}!")
                            items_to_remove.append(item)  # Mark item for removal
                    # Remove items after iteration
                    for item in items_to_remove:
                        current_shopkeeper.mark_item_sold(item)
        elif event.type == pygame.JOYBUTTONDOWN and game_state == "playing":
            if event.button == 0:
                player.shoot_projectile()
                shoot_sound.play()

    if game_state == "title":
        screen.fill((0, 0, 0))
        title_text = title_font.render("Barker's Adventure + Pets!:", True, (255, 255, 255))
        subtitle_text = title_font.render("Nina Bites, Alice Meows", True, (255, 255, 255))
        start_text = font.render("Press SPACE to Start", True, (255, 255, 0))
        screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, WINDOW_HEIGHT // 2 - 60))
        screen.blit(subtitle_text, (WINDOW_WIDTH // 2 - subtitle_text.get_width() // 2, WINDOW_HEIGHT // 2 - 20))
        screen.blit(start_text, (WINDOW_WIDTH // 2 - start_text.get_width() // 2, WINDOW_HEIGHT // 2 + 40))
        player.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)

    elif game_state == "playing":
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

        if world.current_room_index != previous_room_index:
            spawn_room_objects(world, enemies, bushes, npcs)
            previous_room_index = world.current_room_index
            door_unlocked = False
            print(f"Entered Room {world.current_room_index}")

        player.update()
        player.update_projectiles(WINDOW_WIDTH, WINDOW_HEIGHT)
        cat.update(player.rect, enemies)
        dog.update(cat.rect, enemies)
        if world.current_room_index != 0:
            for enemy in enemies:
                enemy.update(WINDOW_WIDTH, WINDOW_HEIGHT, player.projectiles)
                if not enemy.is_dying and player.rect.colliderect(enemy.rect):
                    player.take_damage()
                    hit_sound.play()
            enemies = [enemy for enemy in enemies if not enemy.is_dead()]
            for projectile in world.enemy_projectiles[:]:
                if not projectile.update(WINDOW_WIDTH, WINDOW_HEIGHT):
                    world.enemy_projectiles.remove(projectile)
                elif player.rect.colliderect(projectile.rect):
                    player.take_damage()
                    hit_sound.play()
                    world.enemy_projectiles.remove(projectile)
            for bush in bushes[:]:
                hit_projectile = bush.check_projectile_collision(player.projectiles)
                if hit_projectile:
                    explosion = hit_projectile.explode()
                    player.explosions.append(explosion)
                    player.projectiles.remove(hit_projectile)
            bushes = [bush for bush in bushes if not bush.destroyed]
            if len(enemies) == 0 and not door_unlocked and world.current_room_index == 1:
                if world.tile_map[9][28] == 3:
                    world.set_tile(9, 28, 2)
                    door_unlocked = True
                    print("Door unlocked!")
            for gold in world.gold_drops[:]:
                if player.rect.colliderect(gold["rect"]):
                    player.gold += gold["amount"]
                    world.gold_drops.remove(gold)
        for checkpoint in world.checkpoints:
            if player.rect.colliderect(checkpoint["rect"]):
                player.health = player.max_health
                print("Checkpoint activated!")

        if player.health <= 0:
            game_state = "game_over"
            gameover_sound.play()

        screen.fill((200, 200, 200))
        world.draw(screen)
        if world.current_room_index != 0:
            for bush in bushes:
                bush.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
            for projectile in world.enemy_projectiles:
                projectile.draw(screen)
        else:
            for npc in npcs:
                npc.draw(screen)
        for checkpoint in world.checkpoints:
            pygame.draw.rect(screen, (255, 215, 0), checkpoint["rect"])
        for gold in world.gold_drops:
            screen.blit(gold["sprite"], gold["rect"])
        cat.draw(screen)
        dog.draw(screen)
        player.draw(screen, WINDOW_WIDTH, WINDOW_HEIGHT)
        if world.current_room_index != 0:
            weather_alpha = (weather_alpha + 1) % 255
            rain_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            rain_surface.fill((0, 0, 255))
            rain_surface.set_alpha(weather_alpha // 4)
            screen.blit(rain_surface, (0, 0))

    elif game_state == "shopping":
        screen.fill((0, 0, 0))
        shop_text = font.render("Shopkeeper: Welcome! Buy something? (Press E to exit)", True, (255, 255, 255))
        screen.blit(shop_text, (WINDOW_WIDTH // 2 - shop_text.get_width() // 2, 100))
        for idx, (item, price) in enumerate(current_shopkeeper.shop_items.items()):
            item_text = font.render(f"{idx + 1}. {item}: {price} gold (You have {player.gold} gold)", True, (255, 255, 0) if player.gold >= price else (255, 0, 0))
            screen.blit(item_text, (WINDOW_WIDTH // 2 - item_text.get_width() // 2, 150 + idx * 40))

    elif game_state == "game_over":
        screenA = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        screenA.fill((0, 0, 0))
        screen.blit(screenA, (0, 0))
        game_over_text = font.render("Game Over", True, (255, 0, 0))
        restart_text = font.render("Press R to Restart", True, (255, 255, 255))
        screen.blit(game_over_text, (WINDOW_WIDTH // 2 - 50, WINDOW_HEIGHT // 2 - 20))
        screen.blit(restart_text, (WINDOW_WIDTH // 2 - 70, WINDOW_HEIGHT // 2 + 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()