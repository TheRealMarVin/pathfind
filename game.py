import copy
import datetime
import json
import os

import config
import numpy as np
import pygame
import random

from agents.a_star_agent import AStarAgent
from agents.d_star_lite_agent import DStarLiteAgent
from environment.map import Map


class Game:
    def __init__(self, map_seed: int | None = None):
        if config.CONFIG['game']['seed'] is not None:
            map_seed = config.CONFIG['game']['seed']
        else:
            self.map_seed = random.randint(0, 99999)

        self.map_seed = map_seed

        self.agent_types = config.CONFIG['game']['agent_types']
        self.maps_to_test = config.CONFIG['game']['maps_to_test']
        self.spawns_per_map = config.CONFIG['game']['spawns_per_map']
        self.update_interval = config.CONFIG['game']['update_interval']
        self.color_goal = config.CONFIG['game']['color_goal']
        self.color_agent = config.CONFIG['game']['color_agent']

        self.current_map_index = 0
        self.current_spawn_index = 0
        self.current_agent_index = 0

        self.map = None
        self.agent = None
        self.spawn_data = {}
        self.last_update = 0
        self.cell_size = config.CONFIG['map']['cell_size']

        self.agent_traces = []
        self.map_traces={}

        self._init_map()
        self._spawn_agent()

    def _init_map(self):
        seed = self.map_seed + self.current_map_index

        self.random_generator = random.Random(seed)
        np.random.seed(seed)

        self.map = Map(
            config.CONFIG['map']['grid_width'],
            config.CONFIG['map']['grid_height'],
            self.random_generator,
            config.CONFIG['map']['num_static_areas'],
            config.CONFIG['map']['num_dynamic_areas']
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
        self.agent_traces.append({"agent_index": self.current_agent_index, "spawn_index": self.current_spawn_index, "map_index": self.current_map_index, "agent_visited": copy.deepcopy(self.agent.visited), "agent_explored": copy.deepcopy(list(self.agent.explored))})
        self.current_agent_index += 1

        if self.current_agent_index >= len(self.agent_types):
            self.current_agent_index = 0
            self.current_spawn_index += 1

            if self.current_spawn_index >= self.spawns_per_map:
                self.current_spawn_index = 0
                self.current_map_index += 1

                if self.current_map_index >= self.maps_to_test:
                    self.export_runtime_data()

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
            self.color_goal,
            pygame.Rect(gx * self.cell_size, gy * self.cell_size, self.cell_size, self.cell_size)
        )

        # Draw agent
        ax, ay = self.agent.position
        pygame.draw.rect(
            surface,
            self.color_agent,
            pygame.Rect(ax * self.cell_size, ay * self.cell_size, self.cell_size, self.cell_size)
        )

    def export_runtime_data(self):
        # Create unique output folder
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_dir = os.path.join("outputs", timestamp)
        os.makedirs(output_dir, exist_ok=True)

        # Write agent traces
        with open(os.path.join(output_dir, "agent_output.json"), "w") as f:
            json.dump(self.agent_traces, f, indent=4)

        # Write map traces
        with open(os.path.join(output_dir, "map_output.json"), "w") as f:
            json.dump(self.map_traces, f, indent=4)
