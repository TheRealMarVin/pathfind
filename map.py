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
                    pygame.draw.rect(surface, COLOR_EROSION, rect)

                pygame.draw.rect(surface, COLOR_GRID_LINE, rect, 1)

    def find_free_position(self, min_distance=1, max_attempts=1000, ignore_positions=None):
        """
        Finds a position at least `min_distance` away from any obstacle or ignored position.
        Uses Chebyshev distance (diagonal = straight).
        Raises RuntimeError if no valid position can be found.
        """
        ignore_positions = ignore_positions or []

        # Base obstacle mask from the map
        obs_mask = (self.grid == 1).copy()

        # Temporarily mark ignored positions as obstacles
        for x, y in ignore_positions:
            if 0 <= x < self.width and 0 <= y < self.height:
                obs_mask[y, x] = 1

        # Inflate by distance
        structure = np.ones((2 * min_distance + 1, 2 * min_distance + 1), dtype=bool)
        inflated = binary_dilation(obs_mask, structure=structure)

        # Safe = outside of inflated zones and not actual obstacle or erosion
        safe_mask = ~inflated

        candidates = np.argwhere(safe_mask)
        if candidates.size == 0:
            raise RuntimeError("Map is too dense: no safe position available at that distance.")

        # Try random candidates first
        for _ in range(max_attempts):
            y, x = candidates[np.random.randint(len(candidates))]
            if not self.grid[y, x] and not self.erosion[y, x] and (x, y) not in ignore_positions:
                return (x, y)

        # Brute-force fallback
        for y in range(self.height):
            for x in range(self.width):
                if safe_mask[y, x] and not self.grid[y, x] and not self.erosion[y, x] and (
                x, y) not in ignore_positions:
                    return (x, y)

        raise RuntimeError("Failed to find a valid position: map may be too dense.")

