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
        self.agent_types       = agent_types
        self.maps_to_test      = maps_to_test
        self.spawns_per_map    = spawns_per_map
        self.number_of_iterations = len(agent_types) * maps_to_test * spawns_per_map

        self.cur_agent_idx = 0
        self.cur_map_idx = 0
        self.cur_spawn_idx = 0

        self.map_seed = map_seed or random.randrange(2**32)
        self.map_random_generator = random.Random(self.map_seed)

        self.spawn_data = {}

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
        cfg = config.CONFIG["map"]
        self.width = cfg["grid_width"]
        self.height = cfg["grid_height"]
        self.cell_sz = cfg["cell_size"]

        self.map = Map(self.width, self.height, self.cell_sz)
        self.static_areas, self.dynamic_areas = self._create_areas()

        for area in self.dynamic_areas + self.static_areas:
            area.init_offset = area.offset

        self.spawn_data[(self.cur_map_idx, self.cur_spawn_idx)] = {}

    def _spawn_agent(self):
        key = (self.cur_map_idx, self.cur_spawn_idx)
        if key not in self.spawn_data:
            self.spawn_data[key] = {}

        for area in self.dynamic_areas + self.static_areas:
            area.offset = area.init_offset
            area.move_pattern = area.original_move_pattern

        self.map.update(self.static_areas + self.dynamic_areas)

        key = (self.cur_map_idx, self.cur_spawn_idx)

        if self.cur_agent_idx == 0 or "start" not in self.spawn_data[key]:
            start_pos = self.map.find_free_position(2)
            goal_pos = self.map.find_free_position(2, ignore_positions=[start_pos])
            self.spawn_data[key]["start"] = start_pos
            self.spawn_data[key]["goal"] = goal_pos
        else:
            start_pos = self.spawn_data[key]["start"]
            goal_pos = self.spawn_data[key]["goal"]

        self.start_pos = start_pos
        self.goal_pos = goal_pos
        self.agent_pos = start_pos

        agent_type = self.agent_types[self.cur_agent_idx]
        if agent_type == 'dstar':
            self.agent = DStarLiteAgent(start_pos, goal_pos)
        else:
            self.agent = AStarAgent(start_pos, goal_pos)

        self.last_update = pygame.time.get_ticks()

        print(f"Agent: {agent_type}, Map #{self.cur_map_idx+1}, Spawn #{self.cur_spawn_idx+1}")
        print(f"  Start: {start_pos} -> Goal: {goal_pos}\n")

    def _on_goal_reached(self):
        self.cur_agent_idx += 1

        if self.cur_agent_idx < len(self.agent_types):
            self._spawn_agent()
            return

        self.cur_agent_idx = 0
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
        else:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _create_areas(self):
        static, dynamic = [] , []
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
            shape = random_shape(is_dynamic=True, random_generator=self.map_random_generator)
            off_x = self.map_random_generator.randint(1, width - max(x for x, _ in shape) - 2)
            off_y = self.map_random_generator.randint(1, height - max(y for _, y in shape) - 2)
            move_pattern = self.map_random_generator.choice(move_opts)
            area = ObstacleArea(shape, move_pattern=move_pattern, name=f"Dynamic_{i}")
            area.offset = (off_x, off_y)
            area.original_move_pattern = area.move_pattern
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

        current_positions = set(area.get_absolute_positions())
        if self.agent_pos in proposed_positions and self.agent_pos not in current_positions:
            return True

        return False

    def _collides(self, area, off):
        return self._check_collision(area, off)
