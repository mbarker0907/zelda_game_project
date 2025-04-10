import pygame
import os
import random

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class World:
    def __init__(self):
        self.tile_size = 32
        self.map_width = 20
        self.map_height = 15
        # Load tiles
        self.tiles = {
            0: pygame.image.load(os.path.join(PROJECT_ROOT, "assets/tiles/grass.png")).convert_alpha(),  # Grass
            1: pygame.image.load(os.path.join(PROJECT_ROOT, "assets/tiles/wall.png")).convert_alpha(),   # Wall
            2: pygame.image.load(os.path.join(PROJECT_ROOT, "assets/tiles/door.png")).convert_alpha(),   # Door
            3: pygame.image.load(os.path.join(PROJECT_ROOT, "assets/tiles/locked_door.png")).convert_alpha()  # Locked Door
        }
        
        self.player = None
        # Debug: Print tile dimensions
        for tile_type, tile in self.tiles.items():
            print(f"Tile {tile_type} dimensions: {tile.get_width()}x{tile.get_height()}")
        # Ensure tiles are 32x32 (resize if necessary)
        for tile_type in self.tiles:
            if self.tiles[tile_type].get_width() != self.tile_size or self.tiles[tile_type].get_height() != self.tile_size:
                self.tiles[tile_type] = pygame.transform.scale(self.tiles[tile_type], (self.tile_size, self.tile_size))

        self.chests = []
         
        

        # Define room layouts (20x15 tiles each)
        # Room 1: Starting room with a locked door at (18,7)
        self.room1 = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1],  # Locked Door at (18,7)
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]

        # Room 2: Different layout with a door at (1,7)
        self.room2 = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Door at (1,7)
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        ]

        self.rooms = [self.room1, self.room2]
        self.current_room_index = 0
        self.tile_map = self.rooms[self.current_room_index]
        self.chests = []  # Initialize chests list
        self.offset_x = 0
        self.offset_y = 0
        self.map_surface = pygame.Surface((self.map_width * self.tile_size, self.map_height * self.tile_size))
        self.render_room()

    def initialize_room_objects(self):
        if self.current_room_index == 1:  # Room 2
            from chest import Chest  # Import here to avoid circular import
            chest = Chest(10 * self.tile_size, 7 * self.tile_size)
            self.chests.append(chest) 

    def render_room(self):
        for row in range(self.map_height):
            for col in range(self.map_width):
                tile_type = self.tile_map[row][col]
                tile = self.tiles[tile_type]
                self.map_surface.blit(tile, (col * self.tile_size, row * self.tile_size))

    def draw(self, screen):
        screen.blit(self.map_surface, (self.offset_x, self.offset_y))

    def get_tile_type(self, x, y):
        col = int(x // self.tile_size)
        row = int(y // self.tile_size)
        if 0 <= row < self.map_height and 0 <= col < self.map_width:
            return self.tile_map[row][col]
        return 1  # Default to wall if out of bounds

    def is_wall(self, x, y):
        tile_type = self.get_tile_type(x, y)
        return tile_type == 1 or tile_type == 3  # Treat locked doors as walls

    def is_door(self, x, y):
        tile_type = self.get_tile_type(x, y)
        return tile_type == 2

    def switch_room(self, new_room_index):
        self.current_room_index = new_room_index
        self.tile_map = self.rooms[self.current_room_index]
        self.render_room()
        self.initialize_room_objects()  # Call this to spawn chests

    def set_tile(self, row, col, tile_type):
        if 0 <= row < self.map_height and 0 <= col < self.map_width:
            self.tile_map[row][col] = tile_type
            self.render_room()