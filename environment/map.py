import numpy as np
from scipy.ndimage import binary_dilation
import pygame

from environment.obstacle import ObstacleArea
from helpers.map_helpers import random_shape


class Map:
    def __init__(
        self,
        random_generator,
        grid_width=50,
        grid_height=40,
        erosion_size=1,
        num_static_areas=20,
        num_dynamic_areas=5,
        color_obstacle=[0, 0, 0],
        color_grid_line=[200, 200, 200],
        color_erosion=[255, 155, 155],
        **kwargs
    ):
        self.color_erosion = color_erosion
        self.color_obstacle = color_obstacle
        self.color_grid_line = color_grid_line

        self.width = grid_width
        self.height = grid_height
        self.erosion_size = erosion_size
        self.num_static = num_static_areas
        self.num_dynamic = num_dynamic_areas

        self.grid = np.zeros((self.height, self.width), dtype=int)
        self.erosion = np.zeros((self.height, self.width), dtype=bool)

        self.static_areas = []
        self.dynamic_areas = []

        self._generate_obstacles(random_generator, self.num_static, self.num_dynamic)

    def reset(self):
        for area in self.dynamic_areas:
            area.reset()
        self._rebuild_grid()

    def update(self, agent_pos):
        self._update_dynamics(agent_pos)
        self._rebuild_grid()

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

    def get_trace(self):
        map_trace = {
            "grid_width": self.width,
            "grid_height": self.height,
            "erosion_size": self.erosion_size,
            "num_static_areas": self.num_static,
            "num_dynamic_areas": self.num_dynamic,
            "color_obstacle": self.color_obstacle,
            "color_grid_line": self.color_grid_line,
            "color_erosion": self.color_erosion,
        }
        return map_trace

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

    def get_free_positions(self):
        free_positions = []
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if self.grid[y, x] == 0 and not self.erosion[y, x]:
                    free_positions.append((x, y))
        return free_positions
