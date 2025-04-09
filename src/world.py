import pygame
import os

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

class World:
    def __init__(self):
        self.tile_size = 32
        self.map_width = 25  # 800 ÷ 32 = 25 tiles wide
        self.map_height = 19  # 608 ÷ 32 = 19 tiles tall (closest integer to 18.75)
        # Load tiles
        self.tiles = {
            0: pygame.image.load(os.path.join(PROJECT_ROOT, "assets/tiles/grass.png")).convert_alpha(),
            1: pygame.image.load(os.path.join(PROJECT_ROOT, "assets/tiles/wall.png")).convert_alpha()
        }
        # Debug: Print tile dimensions
        for tile_type, tile in self.tiles.items():
            print(f"Tile {tile_type} dimensions: {tile.get_width()}x{tile.get_height()}")
        # Ensure tiles are 32x32 (resize if necessary)
        for tile_type in self.tiles:
            if self.tiles[tile_type].get_width() != self.tile_size or self.tiles[tile_type].get_height() != self.tile_size:
                self.tiles[tile_type] = pygame.transform.scale(self.tiles[tile_type], (self.tile_size, self.tile_size))
        # Define the tile map (25x19)
        self.tile_map = [
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # Row 0
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 1
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 2
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 3
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 4
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 5
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 6
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 7
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 8
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 9
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 10
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 11
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 12
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 13
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 14
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 15
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 16
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],  # Row 17
            [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # Row 18
        ]
        # No offset needed since the map fills the window
        self.offset_x = 0
        self.offset_y = 0
        # Pre-render the map to a surface
        self.map_surface = pygame.Surface((self.map_width * self.tile_size, self.map_height * self.tile_size))
        for row in range(self.map_height):
            for col in range(self.map_width):
                tile_type = self.tile_map[row][col]
                tile = self.tiles[tile_type]
                self.map_surface.blit(tile, (col * self.tile_size, row * self.tile_size))

    def draw(self, screen):
        # Blit the pre-rendered map surface
        screen.blit(self.map_surface, (self.offset_x, self.offset_y))

    def get_tile(self, x, y):
        """Get the tile type at the given pixel coordinates."""
        col = int(x // self.tile_size)
        row = int(y // self.tile_size)
        if 0 <= row < self.map_height and 0 <= col < self.map_width:
            return self.tile_map[row][col]
        return 1  # Treat out-of-bounds as a wall

    def is_wall(self, x, y):
        """Check if the tile at the given pixel coordinates is a wall."""
        tile_type = self.get_tile(x, y)
        return tile_type == 1  # Wall tiles are type 1