import config
import numpy as np
import pygame
import random

from agents.a_star_agent import AStarAgent
from agents.d_star_lite_agent import DStarLiteAgent
from constants import COLOR_GOAL, NUM_STATIC_AREAS, NUM_DYNAMIC_AREAS, COLOR_AGENT
from environment.map import Map


class Game:
    def __init__(self, map_seed: int | None = None):
        if config.CONFIG['game']['seed'] is not None:
            map_seed = config.CONFIG['game']['seed']
        self.map_seed = map_seed

        self.agent_types = config.CONFIG['game']['agent_types']
        self.maps_to_test = config.CONFIG['game']['maps_to_test']
        self.spawns_per_map = config.CONFIG['game']['spawns_per_map']
        self.update_interval = config.CONFIG['game']['update_interval']

        self.current_map_index = 0
        self.current_spawn_index = 0
        self.current_agent_index = 0

        self.map = None
        self.agent = None
        self.spawn_data = {}
        self.last_update = 0
        self.cell_size = config.CONFIG['map']['cell_size']

        self._init_map()
        self._spawn_agent()

    def _init_map(self):
        seed = self.map_seed or random.randint(0, 99999)
        self.random_generator = random.Random(seed)
        np.random.seed(seed)

        self.map = Map(
            config.CONFIG['map']['grid_width'],
            config.CONFIG['map']['grid_height'],
            self.random_generator,
            NUM_STATIC_AREAS,
            NUM_DYNAMIC_AREAS
        )

        self.spawn_data.clear()
        for i in range(self.spawns_per_map):
            start = self.map.find_free_position()
            goal = self.map.find_free_position(ignore=[start])
            self.spawn_data[i] = {"start": start, "goal": goal}

    def _spawn_agent(self):
        key = self.current_spawn_index
        start_pos = self.spawn_data[key]["start"]
        goal_pos = self.spawn_data[key]["goal"]

        agent_type = self.agent_types[self.current_agent_index % len(self.agent_types)]

        if agent_type == "astar":
            self.agent = AStarAgent(start_pos, goal_pos)
        elif agent_type == "dstar":
            self.agent = DStarLiteAgent(start_pos, goal_pos)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

        print(f"Agent: {agent_type}, Map #{self.current_map_index + 1}, Spawn #{self.current_spawn_index + 1}\n  Start: {start_pos} -> Goal: {goal_pos}\n")

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >= self.update_interval:
            self.last_update = now
            self.map.update(self.agent.position)
            self.agent.update(self.map)

        if self.agent.has_reached_goal():
            self._on_goal_reached()

    def _on_goal_reached(self):
        self.current_agent_index += 1
        if self.current_agent_index >= len(self.agent_types):
            self.current_agent_index = 0
            self.current_spawn_index += 1

            if self.current_spawn_index >= self.spawns_per_map:
                self.current_spawn_index = 0
                self.current_map_index += 1

                if self.current_map_index >= self.maps_to_test:
                    pygame.quit()
                    raise SystemExit("And... it's done!")

                self._init_map()
            else:
                self.map.reset()

        else:
            self.map.reset()

        self._spawn_agent()

    def draw(self, surface):
        self.agent.draw(surface)
        self.map.draw(surface, self.cell_size)

        # Draw goal
        gx, gy = self.agent.goal
        pygame.draw.rect(
            surface,
            COLOR_GOAL,
            pygame.Rect(gx * self.cell_size, gy * self.cell_size, self.cell_size, self.cell_size)
        )

        # Draw agent
        ax, ay = self.agent.position
        pygame.draw.rect(
            surface,
            COLOR_AGENT,
            pygame.Rect(ax * self.cell_size, ay * self.cell_size, self.cell_size, self.cell_size)
        )
