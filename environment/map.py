import numpy as np
from scipy.ndimage import binary_dilation
import pygame

import config
from environment.obstacle import ObstacleArea
from helpers.helpers import random_shape


class Map:
    def __init__(self, width, height, random_generator, num_static=0, num_dynamic=0):
        self.color_erosion = config.CONFIG['map']['color_erosion']
        self.color_obstacle = config.CONFIG['map']['color_obstacle']
        self.color_grid_line = config.CONFIG['map']['color_grid_line']
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width), dtype=int)
        self.erosion = np.zeros((height, width), dtype=bool)

        self.static_areas = []
        self.dynamic_areas = []

        self._generate_obstacles(random_generator, num_static, num_dynamic)

    def _generate_obstacles(self, random_generator, num_static, num_dynamic):
        self.static_areas.clear()
        self.dynamic_areas.clear()

        for _ in range(num_static):
            shape = random_shape(random_generator)
            offset = random_generator.randint(1, self.width - 2), random_generator.randint(1, self.height - 2)
            self.static_areas.append(ObstacleArea(shape, offset))

        for _ in range(num_dynamic):
            shape = random_shape(random_generator)
            offset = random_generator.randint(1, self.width - 2), random_generator.randint(1, self.height - 2)
            dx, dy = random_generator.choice([-1, 1]), random_generator.choice([-1, 1])
            self.dynamic_areas.append(ObstacleArea(shape, offset, move_pattern=(dx, dy)))

        self._rebuild_grid()

    def reset(self):
        for area in self.dynamic_areas:
            area.reset()
        self._rebuild_grid()

    def update(self, agent_pos):
        self._update_dynamics(agent_pos)
        self._rebuild_grid()

    def _update_dynamics(self, agent_pos):
        for area in self.dynamic_areas:
            dx, dy = area.move_pattern
            ox, oy = area.offset
            old_positions = set(area.get_absolute_positions())

            block_x = block_y = False

            for cx, cy in area.cells:
                abs_x, abs_y = cx + ox, cy + oy

                # Check proposed positions
                new_x = abs_x + dx
                new_y = abs_y + dy

                # --- Check X direction ---
                if (new_x < 0 or new_x >= self.width or
                        abs_y < 0 or abs_y >= self.height or
                        (self.grid[abs_y, new_x] == 1 and (new_x, abs_y) not in old_positions) or
                        (new_x, abs_y) == agent_pos):
                    block_x = True
                elif (new_x, abs_y) == agent_pos:
                    block_x = True

                # --- Check Y direction ---
                if (new_y < 0 or new_y >= self.height or
                        abs_x < 0 or abs_x >= self.width or
                        (self.grid[new_y, abs_x] == 1 and (abs_x, new_y) not in old_positions) or
                        (abs_x, new_y) == agent_pos):
                    block_y = True
                elif (abs_x, new_y) == agent_pos:
                    block_y = True

            # Update direction if blocked
            new_dx = -dx if block_x else dx
            new_dy = -dy if block_y else dy

            # Final move
            area.set_move_pattern(new_dx, new_dy)
            area.execute_move(ox + new_dx, oy + new_dy)

    def _rebuild_grid(self):
        self.grid[:, :] = 0
        self.grid[0, :] = 1
        self.grid[-1, :] = 1
        self.grid[:, 0] = 1
        self.grid[:, -1] = 1

        for area in self.static_areas + self.dynamic_areas:
            for x, y in area.get_absolute_positions():
                if 0 <= x < self.width and 0 <= y < self.height:
                    self.grid[y, x] = 1

        self.erosion = binary_dilation(self.grid, iterations=1)

    def find_free_position(self, min_dist=2, ignore=[]):
        attempts = 0
        max_attempts = 1000
        while attempts < max_attempts:
            x = np.random.randint(1, self.width - 1)
            y = np.random.randint(1, self.height - 1)

            if self.grid[y, x] == 0 and not self.erosion[y, x]:
                too_close = False
                for ox, oy in ignore:
                    if abs(x - ox) + abs(y - oy) < min_dist:
                        too_close = True
                        break
                if not too_close:
                    return x, y
            attempts += 1
        raise RuntimeError("Failed to find free position after many attempts")

    def draw(self, surface, cell_size):
        for y in range(self.height):
            for x in range(self.width):
                rect = pygame.Rect(x * cell_size, y * cell_size, cell_size, cell_size)
                if self.grid[y, x] == 1:
                    pygame.draw.rect(surface, self.color_obstacle, rect)
                elif self.erosion[y, x]:
                    pygame.draw.rect(surface, self.color_erosion, rect)

        for x in range(self.width):
            pygame.draw.line(surface, self.color_grid_line, (x * cell_size, 0), (x * cell_size, self.height * cell_size))
        for y in range(self.height):
            pygame.draw.line(surface, self.color_grid_line, (0, y * cell_size), (self.width * cell_size, y * cell_size))
