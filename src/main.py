import pygame
import random
import math
import os
from config import *
from player import Player
from world import World
from enemy import Enemy
from npc import NPC
from hud import HUD
from bush import Bush
from companion import Companion

pygame.init()
pygame.mixer.init()
pygame.joystick.init()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Barker's Adventure + Pets!: Nina Bites, Alice Meows")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.state = "title"
        self.hud = None  # Initialize as None; will be set in init_game
        self.world = None
        self.player = None
        self.enemies = []
        self.npcs = []
        self.bushes = []
        self.companions = []
        self.joystick = None
        self.joystick_deadzone = 0.2
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            print(f"Gamepad connected: {self.joystick.get_name()}")
        self.title_music = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "music/title_music.mp3"))
        self.game_music = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "music/game_music.mp3"))
        self.shoot_sound = pygame.mixer.Sound(os.path.join(ASSETS_PATH, "sfx/shoot.wav"))
        self.title_music.set_volume(0.5)
        self.game_music.set_volume(0.5)
        self.music_playing = None
        self.weather = "clear"
        self.weather_timer = 0
        self.weather_duration = 3000
        self.debug_mode = False

    def init_game(self):
        self.world = World(self.screen)
        self.player = Player(WINDOW_WIDTH // 2 - 24, WINDOW_HEIGHT // 2 - 24, self.world, self.font)
        self.world.player = self.player
        self.hud = HUD(self.player, self.font)  # Create HUD after player is initialized
        self.enemies = []
        self.npcs = []
        self.bushes = []
        self.companions = []
        self.spawn_room_objects()
        self.companions.append(Companion(WINDOW_WIDTH // 2 - 48, WINDOW_HEIGHT // 2 - 24, "dog", self.world))
        self.companions.append(Companion(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 24, "cat", self.world))
        for companion in self.companions:
            companion.set_target(self.player)

    def spawn_room_objects(self):
        self.enemies.clear()
        self.npcs.clear()
        self.bushes.clear()
        self.world.chests.clear()
        self.world.checkpoints.clear()
        self.world.gold_drops.clear()
        self.world.item_drops.clear()

        if self.world.current_room_index == 0:  # Town
            self.npcs.append(NPC(15 * self.world.tile_size, 10 * self.world.tile_size + self.world.hud_height, "shopkeeper", self.player))
            self.npcs.append(NPC(18 * self.world.tile_size, 12 * self.world.tile_size + self.world.hud_height, "quest_giver", self.player))
        elif self.world.current_room_index == 1:  # Forest Clearing
            for _ in range(5):
                enemy_type = random.choice(["octorok", "bat", "archer"])
                while True:
                    x = random.randint(2, self.world.map_width - 3) * self.world.tile_size
                    y = random.randint(2, self.world.map_height - 3) * self.world.tile_size + self.world.hud_height
                    if not self.world.is_wall(x, y):
                        self.enemies.append(Enemy(x, y, enemy_type, self.world))
                        break
            for x in [8, 10, 12]:
                self.bushes.append(Bush(x * self.world.tile_size, 8 * self.world.tile_size + self.world.hud_height))
        elif self.world.current_room_index == 2:  # Riverside
            for _ in range(3):
                enemy_type = random.choice(["octorok", "bat", "archer"])
                while True:
                    x = random.randint(2, self.world.map_width - 3) * self.world.tile_size
                    y = random.randint(2, self.world.map_height - 3) * self.world.tile_size + self.world.hud_height
                    if not self.world.is_wall(x, y):
                        self.enemies.append(Enemy(x, y, enemy_type, self.world))
                        break
            self.world.chests.append(Chest(20 * self.world.tile_size, 10 * self.world.tile_size + self.world.hud_height))
        elif self.world.current_room_index == 3:  # Boss Room
            self.enemies.append(Enemy(15 * self.world.tile_size, 5 * self.world.tile_size + self.world.hud_height, "boss", self.world))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.state == "title" and event.key == pygame.K_SPACE:
                    self.state = "playing"
                    self.init_game()
                    self.title_music.stop()
                    self.game_music.play(-1)
                elif self.state == "playing":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "paused"
                    elif event.key == pygame.K_F1:
                        self.debug_mode = not self.debug_mode
                    elif event.key == pygame.K_1:
                        self.player.switch_weapon(0)  # Sword
                    elif event.key == pygame.K_2:
                        self.player.switch_weapon(1)  # Bow
                elif self.state == "paused":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "playing"
                    elif event.key == pygame.K_UP:
                        current_volume = self.game_music.get_volume()
                        self.game_music.set_volume(min(1.0, current_volume + 0.1))
                    elif event.key == pygame.K_DOWN:
                        current_volume = self.game_music.get_volume()
                        self.game_music.set_volume(max(0.0, current_volume - 0.1))
                elif self.state == "game_over" and event.key == pygame.K_r:
                    self.state = "title"
                    self.game_music.stop()
                    self.title_music.play(-1)

        if self.state == "playing":
            keys = pygame.key.get_pressed()
            self.player.move(keys, WINDOW_WIDTH, WINDOW_HEIGHT)
            if keys[pygame.K_SPACE]:
                self.player.shoot_projectile()
                self.shoot_sound.play()
            if keys[pygame.K_e]:
                for npc in self.npcs:
                    if npc.rect.colliderect(self.player.rect):
                        npc.interact()
                        self.state = "shopping" if npc.type == "shopkeeper" else "playing"
            for chest in self.world.chests:
                if chest.rect.colliderect(self.player.rect) and not chest.is_open:
                    chest.open()
                    item = random.choice(["key", "bomb", "health_potion", "ice_bolt"])
                    if item == "health_potion":
                        self.player.health = min(self.player.health + 2, self.player.max_health)
                    elif item == "key":
                        self.player.keys += 1
                    else:
                        self.player.inventory.append(item)

        elif self.state == "shopping":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_e]:
                self.state = "playing"
            for npc in self.npcs:
                if npc.type == "shopkeeper" and npc.rect.colliderect(self.player.rect):
                    items = npc.shop_items
                    if keys[pygame.K_1] and self.player.gold >= items["ice_bolt"] and "ice_bolt" in items:
                        self.player.inventory.append("ice_bolt")
                        self.player.gold -= items["ice_bolt"]
                    elif keys[pygame.K_2] and self.player.gold >= items["health_potion"] and "health_potion" in items:
                        self.player.health = min(self.player.health + 2, self.player.max_health)
                        self.player.gold -= items["health_potion"]

        if self.joystick:
            axis_x = self.joystick.get_axis(0)
            axis_y = self.joystick.get_axis(1)
            if abs(axis_x) < self.joystick_deadzone:
                axis_x = 0
            if abs(axis_y) < self.joystick_deadzone:
                axis_y = 0
            if self.state == "playing":
                self.player.move_with_velocity(axis_x * self.player.speed, axis_y * self.player.speed, WINDOW_WIDTH, WINDOW_HEIGHT)

        return True

    def update(self):
        if self.state != "playing":
            return

        self.player.update()
        self.player.update_projectiles(WINDOW_WIDTH, WINDOW_HEIGHT - self.hud.get_height())
        self.world.update()

        for enemy in self.enemies[:]:
            enemy.update(self.player)
            if enemy.is_dead():
                self.player.experience += 1
                self.world.drop_gold(enemy.rect.centerx, enemy.rect.centery, 10)
                if random.random() < 0.1:
                    self.world.drop_item(enemy.rect.centerx, enemy.rect.centery, "bomb")
                self.enemies.remove(enemy)
                for npc in self.npcs:
                    if npc.type == "quest_giver":
                        npc.kills += 1

        for npc in self.npcs:
            npc.update()

        for bush in self.bushes[:]:
            for projectile in self.player.projectiles:
                if bush.rect.colliderect(projectile.rect):
                    self.world.drop_gold(bush.rect.centerx, bush.rect.centery, 5)
                    self.bushes.remove(bush)
                    break

        for companion in self.companions:
            companion.update(self.enemies, self.player)

        for gold in self.world.gold_drops[:]:
            if self.player.rect.colliderect(gold["rect"]):
                self.player.gold += gold["amount"]
                self.world.gold_drops.remove(gold)

        for item in self.world.item_drops[:]:
            if self.player.rect.colliderect(item["rect"]):
                if item["type"] == "bomb":
                    self.player.inventory.append("bomb")
                self.world.item_drops.remove(item)

        if self.world.current_room_index == 1 and not self.enemies:
            for y in range(self.world.map_height):
                for x in range(self.world.map_width):
                    if self.world.tile_map[y][x] == 3:  # Locked door
                        self.world.tile_map[y][x] = 2  # Unlock door
                        self.world.render_room()

        self.weather_timer += 1
        if self.weather_timer >= self.weather_duration:
            self.weather = random.choice(["clear", "rain", "fog"])
            self.weather_timer = 0

        if self.player.health <= 0:
            self.state = "game_over"
            self.game_music.stop()
            self.title_music.play(-1)

    def draw(self):
        self.screen.fill((200, 200, 200))
        if self.state == "title":
            title_text = self.font.render("Barker's Adventure + Pets!: Nina Bites, Alice Meows", True, (255, 255, 255))
            start_text = self.font.render("Press SPACE to Start", True, (255, 255, 255))
            self.screen.blit(title_text, (WINDOW_WIDTH // 2 - title_text.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
            self.screen.blit(start_text, (WINDOW_WIDTH // 2 - start_text.get_width() // 2, WINDOW_HEIGHT // 2 + 50))
            if self.music_playing != "title":
                self.title_music.play(-1)
                self.music_playing = "title"
        elif self.state in ["playing", "shopping", "paused"]:
            self.world.draw(self.screen, self.enemies, self.npcs)
            for bush in self.bushes:
                bush.draw(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen)
            for npc in self.npcs:
                npc.draw(self.screen)
            for companion in self.companions:
                companion.draw(self.screen)
            self.player.draw(self.screen, WINDOW_WIDTH, WINDOW_HEIGHT - self.hud.get_height())
            for gold in self.world.gold_drops:
                self.screen.blit(self.world.gold_sprite, gold["rect"])
            for item in self.world.item_drops:
                self.screen.blit(self.world.item_sprites[item["type"]], item["rect"])
            if self.weather == "rain":
                for _ in range(50):
                    x = random.randint(0, WINDOW_WIDTH)
                    y = random.randint(self.hud.get_height(), WINDOW_HEIGHT)
                    pygame.draw.line(self.screen, (0, 0, 255), (x, y), (x, y + 5), 2)
            elif self.weather == "fog":
                overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT - self.hud.get_height()))
                overlay.fill((200, 200, 200))
                overlay.set_alpha(50)
                self.screen.blit(overlay, (0, self.hud.get_height()))
            self.hud.draw(self.screen, self.world)
            if self.state == "paused":
                pause_text = self.font.render("Paused - ESC to Resume", True, (255, 255, 255))
                volume_text = self.font.render(f"Volume: {int(self.game_music.get_volume() * 100)}%", True, (255, 255, 255))
                self.screen.blit(pause_text, (WINDOW_WIDTH // 2 - pause_text.get_width() // 2, WINDOW_HEIGHT // 2 - 50))
                self.screen.blit(volume_text, (WINDOW_WIDTH // 2 - volume_text.get_width() // 2, WINDOW_HEIGHT // 2 + 50))
            if self.debug_mode:
                for enemy in self.enemies:
                    pygame.draw.rect(self.screen, (255, 0, 0), enemy.rect, 2)
                for npc in self.npcs:
                    pygame.draw.rect(self.screen, (0, 255, 0), npc.rect, 2)
                for companion in self.companions:
                    pygame.draw.rect(self.screen, (0, 0, 255), companion.rect, 2)
        elif self.state == "game_over":
            game_over_text = self.font.render("Game Over - Press R to Restart", True, (255, 255, 255))
            self.screen.blit(game_over_text, (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, WINDOW_HEIGHT // 2))
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()