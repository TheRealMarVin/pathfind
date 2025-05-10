import config
import pygame
import numpy as np
import random

from agents.a_star_agent import AStarAgent
from agents.d_star_lite_agent import DStarLiteAgent
from constants import COLOR_START, COLOR_GOAL, NUM_STATIC_AREAS, NUM_DYNAMIC_AREAS, \
    UPDATE_INTERVAL, COLOR_ROBOT
from helpers import random_shape
from map import Map
from obstacle import ObstacleArea


class Game:
    def __init__(self, seed=None, agent_type='dstar'):
        self.agent_type = agent_type  # 'astar' or 'dstar'
        self.seed = seed or random.randint(0, 2 ** 32 - 1)
        random.seed(self.seed)
        np.random.seed(self.seed)
        self._initialize_game()

    def _initialize_game(self):
        self.width = config.CONFIG["map"]["grid_width"]
        self.height = config.CONFIG["map"]["grid_height"]
        self.cell_size = config.CONFIG["map"]["cell_size"]
        self.map = Map(self.width, self.height, self.cell_size)
        self.static_areas = []
        self.dynamic_areas = []
        self._create_areas()

        self.map.update(self.static_areas + self.dynamic_areas)

        self.start_pos = self.map.find_free_position(2)
        self.agent_pos = self.start_pos
        self.goal_pos = self.map.find_free_position(2, ignore_positions=[self.start_pos])

        if self.agent_type == 'dstar':
            self.agent = DStarLiteAgent(self.start_pos, self.goal_pos)
        else:
            self.agent = AStarAgent(self.start_pos, self.goal_pos)

        self.last_update = pygame.time.get_ticks()

    def reset_same_map(self):
        # Re-initialize using the same seed
        random.seed(self.seed)
        np.random.seed(self.seed)
        self._initialize_game()

    def reset_new_map(self):
        # Re-initialize with a new seed
        self.seed = random.randint(0, 999999)
        random.seed(self.seed)
        np.random.seed(self.seed)
        self._initialize_game()

    def _create_areas(self):
        """
        Create the specified number of static and dynamic obstacle areas with random shapes.
        """
        # Create static areas.
        for i in range(NUM_STATIC_AREAS):
            shape = random_shape(is_dynamic=False)
            max_x = max(x for (x, _) in shape)
            max_y = max(y for (_, y) in shape)
            offset_x = random.randint(1, self.width - max_x - 2)
            offset_y = random.randint(1, self.height - max_y - 2)
            area = ObstacleArea(shape, move_pattern=(0, 0), name=f"Static_{i}")
            area.offset = (offset_x, offset_y)
            self.static_areas.append(area)

        # Create dynamic areas.
        move_options = [(-1, 0), (1, 0), (0, -1), (0, 1),
                        (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for i in range(NUM_DYNAMIC_AREAS):
            shape = random_shape(is_dynamic=True)
            max_x = max(x for (x, _) in shape)
            max_y = max(y for (_, y) in shape)
            offset_x = random.randint(1, self.width - max_x - 2)
            offset_y = random.randint(1, self.height - max_y - 2)
            move_pattern = random.choice(move_options)
            area = ObstacleArea(shape, move_pattern=move_pattern, name=f"Dynamic_{i}")
            area.offset = (offset_x, offset_y)
            self.dynamic_areas.append(area)

    def _check_collision(self, area, proposed_offset):
        """
        Check if area, when placed at proposed_offset, collides with:
          - Border walls.
          - Any static area.
          - Any other dynamic area.
        """
        proposed_positions = area.get_absolute_positions(offset=proposed_offset)
        # Check borders.
        for (x, y) in proposed_positions:
            if x < 1 or x >= self.width - 1 or y < 1 or y >= self.height - 1:
                return True
        # Check static areas.
        static_positions = set()
        for sta in self.static_areas:
            static_positions.update(sta.get_absolute_positions())
        for pos in proposed_positions:
            if pos in static_positions:
                return True
        # Check other dynamic areas.
        for dyn_area in self.dynamic_areas:
            if dyn_area is area:
                continue
            other_positions = set(dyn_area.get_absolute_positions())
            for pos in proposed_positions:
                if pos in other_positions:
                    return True
        return False

    def _collides(self, area, off):
        """True if `area` would collide when placed at offset `off`."""
        return self._check_collision(area, off)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >= UPDATE_INTERVAL:

            for area in self.dynamic_areas:
                ox, oy = area.offset
                dx0, dy0 = area.move_pattern
                target = (ox + dx0, oy + dy0)

                # ---------- 1. try full diagonal step ----------
                if not self._collides(area, target):
                    area.offset = target
                    continue

                # ---------- 2. probe each axis separately ----------
                collide_x = self._collides(area, (ox + dx0, oy))
                collide_y = self._collides(area, (ox,       oy + dy0))

                # ---------- 3. decide what to do ----------
                if not collide_x and not collide_y:
                    new_off = (ox + dx0, oy)
                    if self._collides(area, new_off):
                        new_off = (ox, oy + dy0)
                    area.offset = new_off
                    # keep the same velocity (still diagonal)
                else:
                    # at least one axis blocked ► bounce
                    dx = -dx0 if collide_x else dx0
                    dy = -dy0 if collide_y else dy0
                    area.move_pattern = (dx, dy)

                    reflected = (ox + dx, oy + dy)
                    if not self._collides(area, reflected):
                        area.offset = reflected

            self.last_update = now
            self.agent.update(self.map)

        self.map.update(self.static_areas + self.dynamic_areas)

    def draw(self, surface):
        """
        Draw the map, robot, and goal.
        """
        self.agent.draw(surface)
        self.map.draw(surface)
        # Draw robot.
        if self.agent_pos is not None:
            rx, ry = self.agent_pos
            rect = pygame.Rect(rx * self.cell_size, ry * self.cell_size, self.cell_size, self.cell_size)
            pygame.draw.rect(surface, COLOR_ROBOT, rect)

        # Draw goal.
        if self.goal_pos is not None:
            gx, gy = self.goal_pos
            rect = pygame.Rect(gx * self.cell_size, gy * self.cell_size, self.cell_size, self.cell_size)
            pygame.draw.rect(surface, COLOR_GOAL, rect)
