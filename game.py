import config
import pygame
import random

from agents.a_star_agent import AStarAgent
from agents.d_star_lite_agent import DStarLiteAgent
from constants import COLOR_GOAL, NUM_STATIC_AREAS, NUM_DYNAMIC_AREAS, UPDATE_INTERVAL, COLOR_AGENT
from environment.map import Map
from environment.obstacle import ObstacleArea
from helpers.helpers import random_shape


class Game:
    def __init__(self,
                 agent_types: list[str] = ["dstar", "astar"],
                 maps_to_test: int = 3,
                 spawns_per_map: int = 2,
                 map_seed: int | None = None):
        # experiment configuration
        self.agent_types       = agent_types
        self.maps_to_test      = maps_to_test
        self.spawns_per_map    = spawns_per_map
        self.number_of_iterations = len(agent_types) * maps_to_test * spawns_per_map

        # indices
        self.cur_agent_idx = 0
        self.cur_map_idx = 0
        self.cur_spawn_idx = 0

        # map generation
        self.map_seed = map_seed or random.randrange(2**32)
        self.map_random_generator = random.Random(self.map_seed)

        self._generate_new_map()
        self._spawn_agent()

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >= UPDATE_INTERVAL:
            self.last_update = now
            self.agent.update(self.map)

        self._update_objects()
        self.map.update(self.static_areas + self.dynamic_areas)

        if self.agent.has_reached_goal():
            self._on_goal_reached()

    def draw(self, surface):
        self.agent.draw(surface)
        self.map.draw(surface)

        if self.agent_pos is not None:
            rx, ry = self.agent_pos
            rect = pygame.Rect(rx * self.cell_sz, ry * self.cell_sz, self.cell_sz, self.cell_sz)
            pygame.draw.rect(surface, COLOR_AGENT, rect)

        if self.goal_pos is not None:
            gx, gy = self.goal_pos
            rect = pygame.Rect(gx * self.cell_sz, gy * self.cell_sz, self.cell_sz, self.cell_sz)
            pygame.draw.rect(surface, COLOR_GOAL, rect)

    def _generate_new_map(self):
        cfg          = config.CONFIG["map"]
        self.width   = cfg["grid_width"]
        self.height  = cfg["grid_height"]
        self.cell_sz = cfg["cell_size"]

        self.map = Map(self.width, self.height, self.cell_sz)
        self.static_areas, self.dynamic_areas = self._create_areas()

        for area in self.dynamic_areas + self.static_areas:
            area.init_offset = area.offset

        self.cur_spawn_idx = 0

    def _spawn_agent(self):
        for area in self.dynamic_areas + self.static_areas:
            area.offset = area.init_offset

        self.map.update(self.static_areas + self.dynamic_areas)

        self.start_pos = self.map.find_free_position(2)
        self.goal_pos  = self.map.find_free_position(2, ignore_positions=[self.start_pos])
        self.agent_pos = self.start_pos

        agent_type = self.agent_types[self.cur_agent_idx]
        if agent_type == 'dstar':
            self.agent = DStarLiteAgent(self.start_pos, self.goal_pos)
        else:
            self.agent = AStarAgent(self.start_pos, self.goal_pos)

        self.last_update = pygame.time.get_ticks()

    def _on_goal_reached(self):
        self.cur_spawn_idx += 1
        if self.cur_spawn_idx < self.spawns_per_map:
            self._spawn_agent()
            return

        self.cur_spawn_idx = 0
        self.cur_map_idx += 1

        if self.cur_map_idx < self.maps_to_test:
            self.map_seed = random.randrange(2**32)
            self.map_random_generator = random.Random(self.map_seed)
            self._generate_new_map()
            self._spawn_agent()
            return

        self.cur_map_idx = 0
        self.cur_agent_idx += 1

        if self.cur_agent_idx < len(self.agent_types):
            self.map_seed = random.randrange(2**32)
            self.map_random_generator = random.Random(self.map_seed)
            self._generate_new_map()
            self._spawn_agent()
        else:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _create_areas(self):
        static, dynamic = [], []
        width = self.width
        height = self.height

        for i in range(NUM_STATIC_AREAS):
            shape = random_shape(is_dynamic=False, random_generator=self.map_random_generator)
            off_x = self.map_random_generator.randint(1, width - max(x for x, _ in shape) - 2)
            off_y = self.map_random_generator.randint(1, height - max(y for _, y in shape) - 2)
            area = ObstacleArea(shape, move_pattern=(0, 0), name=f"Static_{i}")
            area.offset = (off_x, off_y)
            static.append(area)

        move_opts = [(-1, 0), (1, 0), (0, -1), (0, 1),
                     (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for i in range(NUM_DYNAMIC_AREAS):
            shape = random_shape(is_dynamic=True, rng=self.map_random_generator)
            off_x = self.map_random_generator.randint(1, width - max(x for x, _ in shape) - 2)
            off_y = self.map_random_generator.randint(1, height - max(y for _, y in shape) - 2)
            move_pattern = self.map_random_generator.choice(move_opts)
            area = ObstacleArea(shape, move_pattern=move_pattern, name=f"Dynamic_{i}")
            area.offset = (off_x, off_y)
            dynamic.append(area)

        return static, dynamic

    def _update_objects(self):
        for area in self.dynamic_areas:
            ox, oy = area.offset
            dx0, dy0 = area.move_pattern
            target = (ox + dx0, oy + dy0)

            if not self._collides(area, target):
                area.offset = target
                continue

            collide_x = self._collides(area, (ox + dx0, oy))
            collide_y = self._collides(area, (ox, oy + dy0))

            if not collide_x and not collide_y:
                new_off = (ox + dx0, oy)
                if self._collides(area, new_off):
                    new_off = (ox, oy + dy0)
                area.offset = new_off
            else:
                dx = -dx0 if collide_x else dx0
                dy = -dy0 if collide_y else dy0
                area.move_pattern = (dx, dy)
                reflected = (ox + dx, oy + dy)
                if not self._collides(area, reflected):
                    area.offset = reflected

    def _check_collision(self, area, proposed_offset):
        proposed_positions = area.get_absolute_positions(offset=proposed_offset)
        for (x, y) in proposed_positions:
            if x < 1 or x >= self.width - 1 or y < 1 or y >= self.height - 1:
                return True

        static_positions = set()
        for sta in self.static_areas:
            static_positions.update(sta.get_absolute_positions())
        for pos in proposed_positions:
            if pos in static_positions:
                return True

        for dyn_area in self.dynamic_areas:
            if dyn_area is area:
                continue
            other_positions = set(dyn_area.get_absolute_positions())
            for pos in proposed_positions:
                if pos in other_positions:
                    return True
        return False

    def _collides(self, area, off):
        return self._check_collision(area, off)
