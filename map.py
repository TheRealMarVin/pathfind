import pygame
import numpy as np
import random
from scipy.ndimage import binary_dilation

from constants import CELL_SIZE, COLOR_OBSTACLE, COLOR_GRID_LINE, COLOR_EROSION


class Map:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=int)

    def update(self, obstacle_areas):
        """
        Clears the grid, adds border walls, then overlays obstacles from each area.
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

    def draw(self, surface):
        """
        Draws the grid with obstacles and an erosion (inflated boundary) overlay.
        """
        # Draw the basic grid and obstacles.
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                if self.grid[y, x] == 1:
                    pygame.draw.rect(surface, COLOR_OBSTACLE, rect)
                pygame.draw.rect(surface, COLOR_GRID_LINE, rect, 1)

        # Compute erosion (inflated boundaries) using morphological dilation.
        obs_bool = (self.grid == 1)
        # Structure for 8-connected dilation.
        structure = np.ones((3, 3), dtype=bool)
        dilated = binary_dilation(obs_bool, structure=structure)
        erosion_boundary = dilated & ~obs_bool

        # Draw the erosion boundaries.
        for y in range(self.height):
            for x in range(self.width):
                if erosion_boundary[y, x]:
                    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(surface, COLOR_EROSION, rect, 1)