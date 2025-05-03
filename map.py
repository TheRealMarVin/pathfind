import pygame
import numpy as np
from scipy.ndimage import binary_dilation

from constants import CELL_SIZE, COLOR_OBSTACLE, COLOR_GRID_LINE, COLOR_EROSION


class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=int)
        self.erosion = np.zeros((height, width), dtype=bool)

    def update(self, obstacle_areas):
        """
        Clears the grid, adds border walls, then overlays obstacles from each area,
        and computes erosion for static obstacles.
        """
        self.grid[:, :] = 0
        # Add border walls.
        self.grid[0, :] = 1
        self.grid[-1, :] = 1
        self.grid[:, 0] = 1
        self.grid[:, -1] = 1

        for area in obstacle_areas:
            for x, y in area.get_absolute_positions():
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.grid[y, x] = 1

        # Precompute erosion for static objects
        self.erosion = self.compute_erosion(self.grid)

    def compute_erosion(self, grid):
        """
        Computes erosion (inflated boundary) for the given grid.
        Returns a boolean array where erosion is True.
        """
        obs_bool = (grid == 1)
        structure = np.ones((3, 3), dtype=bool)
        dilated = binary_dilation(obs_bool, structure=structure)
        erosion_boundary = dilated & ~obs_bool
        return erosion_boundary

    def is_blocked(self, x, y):
        """
        Returns True if (x, y) is in obstacle or erosion.
        """
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.grid[y, x] == 1 or self.erosion[y, x]
        return True  # Treat out-of-bounds as blocked

    def draw(self, surface):
        """
        Draws the grid with obstacles and precomputed erosion overlay.
        """
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)

                if self.grid[y, x] == 1:
                    pygame.draw.rect(surface, COLOR_OBSTACLE, rect)
                elif self.erosion[y, x]:
                    pygame.draw.rect(surface, COLOR_EROSION, rect, 1)

                pygame.draw.rect(surface, COLOR_GRID_LINE, rect, 1)
