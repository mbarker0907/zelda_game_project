import pygame
import os
import random
from config import *

class Chest:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
        self.is_open = False
        self.sprite = pygame.image.load(os.path.join(ASSETS_PATH, "objects/chest_closed.png")).convert_alpha()
        self.sprite_open = pygame.image.load(os.path.join(ASSETS_PATH, "objects/chest_open.png")).convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (TILE_SIZE, TILE_SIZE))
        self.sprite_open = pygame.transform.scale(self.sprite_open, (TILE_SIZE, TILE_SIZE))

    def open(self):
        self.is_open = True

    def draw(self, screen):
        sprite = self.sprite_open if self.is_open else self.sprite
        screen.blit(sprite, self.rect)

class World:
    def __init__(self, screen):
        self.screen = screen
        self.hud_height = 0
        self.tile_size = TILE_SIZE
        self.map_width = MAP_WIDTH
        self.map_height = MAP_HEIGHT
        self.tiles = {
            0: pygame.image.load(os.path.join(ASSETS_PATH, "tiles/grass.png")).convert_alpha(),
            1: pygame.image.load(os.path.join(ASSETS_PATH, "tiles/wall.png")).convert_alpha(),
            2: pygame.image.load(os.path.join(ASSETS_PATH, "tiles/door.png")).convert_alpha(),
            3: pygame.image.load(os.path.join(ASSETS_PATH, "tiles/locked_door.png")).convert_alpha(),
            4: pygame.image.load(os.path.join(ASSETS_PATH, "tiles/water.png")).convert_alpha(),
            5: pygame.image.load(os.path.join(ASSETS_PATH, "tiles/tree.png")).convert_alpha(),
            6: pygame.image.load(os.path.join(ASSETS_PATH, "tiles/bridge.png")).convert_alpha(),
            7: pygame.image.load(os.path.join(ASSETS_PATH, "tiles/town_path.png")).convert_alpha(),
            8: pygame.image.load(os.path.join(ASSETS_PATH, "tiles/building.png")).convert_alpha()
        }
        self.player = None
        for tile_type, tile in self.tiles.items():
            if tile.get_width() != self.tile_size or tile.get_height() != self.tile_size:
                self.tiles[tile_type] = pygame.transform.scale(tile, (self.tile_size, self.tile_size))
        self.chests = []
        self.checkpoints = []
        self.gold_drops = []
        self.item_drops = []
        self.enemy_projectiles = []
        self.gold_sprite = pygame.image.load(os.path.join(ASSETS_PATH, "items/gold_coin.png")).convert_alpha()
        self.item_sprites = {
            "bomb": pygame.image.load(os.path.join(ASSETS_PATH, "items/bomb.png")).convert_alpha(),
            "ice_bolt": pygame.image.load(os.path.join(ASSETS_PATH, "items/ice_bolt.png")).convert_alpha()
        }
        # Room 0: Town
        self.room0 = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1],
            [1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1],
            [1, 7, 7, 8, 8, 7, 7, 8, 8, 7, 7, 8, 8, 7, 7, 8, 8, 7, 7, 8, 8, 7, 7, 8, 8, 7, 7, 7, 7, 1],
            [1, 7, 7, 8, 8, 7, 7, 8, 8, 7, 7, 8, 8, 7, 7, 8, 8, 7, 7, 8, 8, 7, 7, 8, 8, 7, 7, 7, 7, 1],
            [1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1],
            [1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1],
            [1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1],
            [1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1],
            [1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 2, 1],
            [1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1],
            [1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1],
            [1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1],
            [1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1],
            [1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1],
            [1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1],
            [1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1],
            [1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1],
            [1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
        # Room 1: Forest Clearing
        self.room1 = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 5, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 5, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 5, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 5, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
        # Room 2: Riverside (Procedurally Generated)
        self.room2 = self.generate_procedural_room()
        # Room 3: Boss Room
        self.room3 = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        ]
        self.rooms = [self.room0, self.room1, self.room2, self.room3]
        self.current_room_index = 0
        self.tile_map = self.rooms[self.current_room_index]
        self.chests = []
        self.offset_x = 0
        self.offset_y = self.hud_height
        self.map_surface = pygame.Surface((self.map_width * self.tile_size, self.map_height * self.tile_size))
        self.minimap = pygame.Surface((self.map_width * 5, self.map_height * 5))
        self.explored = [[False for _ in range(self.map_width)] for _ in range(self.map_height)]
        self.day_night_cycle = 0
        self.day_night_speed = 0.001
        self.is_night = False
        self.render_room()

    def generate_procedural_room(self):
        room = [[1 for _ in range(self.map_width)] for _ in range(self.map_height)]
        for y in range(1, self.map_height - 1):
            for x in range(1, self.map_width - 1):
                room[y][x] = 0
        river_start_y = random.randint(5, self.map_height - 6)
        for x in range(self.map_width):
            for y in range(river_start_y, river_start_y + 3):
                room[y][x] = 4  # Water
        bridge_x = random.randint(5, self.map_width - 6)
        for y in range(river_start_y, river_start_y + 3):
            room[y][bridge_x] = 6  # Bridge
        for _ in range(10):
            tree_x = random.randint(1, self.map_width - 2)
            tree_y = random.randint(1, self.map_height - 2)
            if room[tree_y][tree_x] == 0:
                room[tree_y][tree_x] = 5  # Tree
        room[7][1] = 2  # Door to previous room
        return room

    def render_room(self):
        self.map_surface.fill((0, 0, 0))
        for y in range(self.map_height):
            for x in range(self.map_width):
                tile_type = self.tile_map[y][x]
                self.map_surface.blit(self.tiles[tile_type], (x * self.tile_size, y * self.tile_size))

    def render_minimap(self, enemies, npcs):
        self.minimap.fill((0, 0, 0))
        for y in range(self.map_height):
            for x in range(self.map_width):
                if self.explored[y][x]:
                    tile_type = self.tile_map[y][x]
                    color = (0, 255, 0) if tile_type == 0 else (128, 128, 128) if tile_type == 1 else (255, 255, 0) if tile_type in [2, 3] else (0, 0, 255) if tile_type == 4 else (0, 128, 0)
                    pygame.draw.rect(self.minimap, color, (x * 5, y * 5, 5, 5))
        if self.player:
            player_x = int(self.player.rect.centerx // self.tile_size)
            player_y = int((self.player.rect.centery - self.hud_height) // self.tile_size)
            pygame.draw.rect(self.minimap, (255, 0, 0), (player_x * 5, player_y * 5, 5, 5))
            self.explored[player_y][player_x] = True
        for enemy in enemies:
            enemy_x = int(enemy.rect.centerx // self.tile_size)
            enemy_y = int((enemy.rect.centery - self.hud_height) // self.tile_size)
            pygame.draw.rect(self.minimap, (255, 0, 255), (enemy_x * 5, enemy_y * 5, 5, 5))
        for npc in npcs:
            npc_x = int(npc.rect.centerx // self.tile_size)
            npc_y = int((npc.rect.centery - self.hud_height) // self.tile_size)
            pygame.draw.rect(self.minimap, (0, 255, 255), (npc_x * 5, npc_y * 5, 5, 5))

    def draw(self, screen, enemies, npcs):
        screen.blit(self.map_surface, (self.offset_x, self.offset_y))
        for chest in self.chests:
            chest.draw(screen)
        self.render_minimap(enemies, npcs)
        screen.blit(pygame.transform.scale(self.minimap, (self.map_width * 5, self.map_height * 5)), (WINDOW_WIDTH - self.map_width * 5 - 10, self.hud_height + 10))
        if self.is_night:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT - self.hud_height))
            overlay.fill((0, 0, 50))
            overlay.set_alpha(100)
            screen.blit(overlay, (0, self.hud_height))
        else:
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT - self.hud_height))
            overlay.fill((255, 255, 200))
            overlay.set_alpha(50)
            screen.blit(overlay, (0, self.hud_height))

    def update(self):
        self.day_night_cycle += self.day_night_speed
        if self.day_night_cycle >= 1:
            self.day_night_cycle = 0
        self.is_night = self.day_night_cycle > 0.5

    def is_wall(self, x, y):
        tile_x = int(x // self.tile_size)
        tile_y = int((y - self.hud_height) // self.tile_size)
        if 0 <= tile_x < self.map_width and 0 <= tile_y < self.map_height:
            return self.tile_map[tile_y][tile_x] in [1, 4, 5, 8]
        return True

    def get_tile_type(self, x, y):
        tile_x = int(x // self.tile_size)
        tile_y = int((y - self.hud_height) // self.tile_size)
        if 0 <= tile_x < self.map_width and 0 <= tile_y < self.map_height:
            return self.tile_map[tile_y][tile_x]
        return 1

    def switch_room(self, room_index):
        self.current_room_index = room_index
        self.tile_map = self.rooms[self.current_room_index]
        self.explored = [[False for _ in range(self.map_width)] for _ in range(self.map_height)]
        self.render_room()

    def drop_gold(self, x, y, amount):
        self.gold_drops.append({"rect": pygame.Rect(x - 8, y - 8, 16, 16), "amount": amount})

    def drop_item(self, x, y, item_type):
        self.item_drops.append({"rect": pygame.Rect(x - 8, y - 8, 16, 16), "type": item_type})