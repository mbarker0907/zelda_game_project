import pygame
import os
import random
from chest import Chest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class World:
    # **Initialization**
    def __init__(self, window_width, window_height, screen):
        self.window_width = window_width
        self.window_height = window_height
        self.screen = screen
        self.tile_size = 32
        self.map_width = 30
        self.map_height = 20
        self.tiles = {
            0: pygame.image.load(os.path.join(PROJECT_ROOT, "assets/tiles/grass.png")).convert_alpha(),
            1: pygame.image.load(os.path.join(PROJECT_ROOT, "assets/tiles/wall.png")).convert_alpha(),
            2: pygame.image.load(os.path.join(PROJECT_ROOT, "assets/tiles/door.png")).convert_alpha(),
            3: pygame.image.load(os.path.join(PROJECT_ROOT, "assets/tiles/locked_door.png")).convert_alpha(),
            4: pygame.image.load(os.path.join(PROJECT_ROOT, "assets/tiles/water.png")).convert_alpha(),
            5: pygame.image.load(os.path.join(PROJECT_ROOT, "assets/tiles/tree.png")).convert_alpha(),
            6: pygame.image.load(os.path.join(PROJECT_ROOT, "assets/tiles/bridge.png")).convert_alpha(),
            7: pygame.image.load(os.path.join(PROJECT_ROOT, "assets/tiles/town_path.png")).convert_alpha(),
            8: pygame.image.load(os.path.join(PROJECT_ROOT, "assets/tiles/building.png")).convert_alpha()
        }
        self.player = None
        for tile_type, tile in self.tiles.items():
            if tile.get_width() != self.tile_size or tile.get_height() != self.tile_size:
                self.tiles[tile_type] = pygame.transform.scale(tile, (self.tile_size, self.tile_size))
        self.chests = []
        self.checkpoints = []
        self.gold_drops = []
        self.enemy_projectiles = []  # Added for boss projectiles
        # **ASSET REQUIRED**: Add sprite for gold coin drops
        self.gold_sprite = pygame.image.load(os.path.join(PROJECT_ROOT, "assets/items/gold_coin.png")).convert_alpha()
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
            [1, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 1],
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
        self.offset_y = 0
        self.map_surface = pygame.Surface((self.map_width * self.tile_size, self.map_height * self.tile_size))
        self.minimap = pygame.Surface((self.map_width * 5, self.map_height * 5))
        self.explored = [[False for _ in range(self.map_width)] for _ in range(self.map_height)]
        self.render_room()
        self.render_minimap()

    # **Generate Procedural Room**
    def generate_procedural_room(self):
        room = [[1 for _ in range(self.map_width)] for _ in range(self.map_height)]
        # Fill with grass
        for row in range(1, self.map_height - 1):
            for col in range(1, self.map_width - 1):
                room[row][col] = 0
        # Add random obstacles (trees, water)
        for _ in range(10):
            row = random.randint(1, self.map_height - 2)
            col = random.randint(1, self.map_width - 2)
            room[row][col] = random.choice([4, 5])
        # Add door
        room[7][1] = 2
        return room

    # **Initialize Room Objects**
    def initialize_room_objects(self):
        self.chests = []
        self.checkpoints = []
        if self.current_room_index == 1:
            self.checkpoints.append({"rect": pygame.Rect(5 * self.tile_size, 5 * self.tile_size, 32, 32)})
        elif self.current_room_index == 2:
            chest = Chest(20 * self.tile_size, 10 * self.tile_size)
            self.chests.append(chest)

    # **Render Room**
    def render_room(self):
        for row in range(self.map_height):
            for col in range(self.map_width):
                tile_type = self.tile_map[row][col]
                tile = self.tiles[tile_type]
                self.map_surface.blit(tile, (col * self.tile_size, row * self.tile_size))

    # **Render Minimap**
    def render_minimap(self):
        for row in range(self.map_height):
            for col in range(self.map_width):
                if self.explored[row][col]:
                    tile_type = self.tile_map[row][col]
                    color = (0, 255, 0) if tile_type == 0 else (100, 100, 100) if tile_type == 1 else (255, 0, 0)
                    pygame.draw.rect(self.minimap, color, (col * 5, row * 5, 5, 5))

    # **Draw World**
    def draw(self, screen):
        screen.blit(self.map_surface, (self.offset_x, self.offset_y))
        # Update and draw minimap
        player_row = int(self.player.rect.centery // self.tile_size)
        player_col = int(self.player.rect.centerx // self.tile_size)
        if 0 <= player_row < self.map_height and 0 <= player_col < self.map_width:
            self.explored[player_row][player_col] = True
        self.render_minimap()
        screen.blit(self.minimap, (self.window_width - self.map_width * 5 - 10, 10))

    # **Get Tile Type**
    def get_tile_type(self, x, y):
        col = int(x // self.tile_size)
        row = int(y // self.tile_size)
        if 0 <= row < self.map_height and 0 <= col < self.map_width:
            return self.tile_map[row][col]
        return 1

    # **Check Wall**
    def is_wall(self, x, y):
        tile_type = self.get_tile_type(x, y)
        return tile_type in [1, 3, 4, 5, 8]  # Buildings are also walls

    # **Switch Room**
    def switch_room(self, new_room_index):
        self.current_room_index = new_room_index
        self.tile_map = self.rooms[self.current_room_index]
        self.explored = [[False for _ in range(self.map_width)] for _ in range(self.map_height)]
        self.render_room()
        self.initialize_room_objects()
        # Fade out
        fade_surface = pygame.Surface((self.window_width, self.window_height))
        fade_surface.fill((0, 0, 0))
        for alpha in range(0, 255, 10):
            fade_surface.set_alpha(alpha)
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.wait(10)
        # Fade in
        for alpha in range(255, 0, -10):
            fade_surface.set_alpha(alpha)
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.wait(10)

    # **Set Tile**
    def set_tile(self, row, col, tile_type):
        if 0 <= row < self.map_height and 0 <= col < self.map_width:
            self.tile_map[row][col] = tile_type
            self.render_room()

    # **Drop Gold**
    def drop_gold(self, x, y, amount):
        rect = pygame.Rect(x, y, 16, 16)
        self.gold_drops.append({"rect": rect, "amount": amount, "sprite": self.gold_sprite})