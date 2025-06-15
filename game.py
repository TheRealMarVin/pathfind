import copy
import json
import os

import yaml

import config
import numpy as np
import pygame

from datetime import datetime
from agents.a_star_agent import AStarAgent
from agents.d_star_lite_agent import DStarLiteAgent
from environment.map import Map


class Game:
    def __init__(self, task):
        self.task = task

        self.update_interval = config.CONFIG["game"]["update_interval"]
        self.color_goal = config.CONFIG["game"]["color_goal"]
        self.color_agent = config.CONFIG["game"]["color_agent"]
        self.cell_size = config.CONFIG["map"]["cell_size"]

        # self.current_map_index = 0
        # self.current_spawn_index = 0
        # self.current_agent_index = 0

        self.map = task.map
        self.agent = None
        self.spawn_data = task.position_pairs
        self.last_update = 0

        # self.agent_traces = []
        # self.map_traces={}
        self.map_trace = {"seed": task.seed, "grid":self.map.grid.tolist(), "erosion":self.map.erosion.tolist(),
                          "agent_type": task.agent_type}

        # self._init_map()
        self._spawn_agent()

    # def _init_map(self):
    #     seed = self.map_seed + self.current_map_index
    #
    #     self.random_generator = random.Random(seed)
    #     np.random.seed(seed)
    #
    #     self.map = Map(
    #         config.CONFIG["map"]["grid_width"],
    #         config.CONFIG["map"]["grid_height"],
    #         self.random_generator,
    #         config.CONFIG["map"]["num_static_areas"],
    #         config.CONFIG["map"]["num_dynamic_areas"]
    #     )
    #
    #     free_positions = self.map.get_free_positions()
    #     max_possible_pairs = len(free_positions) * (len(free_positions) - 1)  # n * (n-1) since order matters
    #     spawns_per_map = min(self.spawns_per_map, max_possible_pairs)
    #
    #     if spawns_per_map < self.spawns_per_map:
    #         print(
    #             f"Warning: Reduced spawns_per_map from {self.spawns_per_map} to {spawns_per_map} to respect map size constraints")
    #
    #     max_attempts = 250
    #     self.spawn_data.clear()
    #     used_pairs = set()
    #
    #     for i in range(spawns_per_map):
    #         attempts = 0
    #         while attempts < max_attempts:
    #             # Randomly select start and goal from free positions
    #             start_idx, goal_idx = np.random.choice(len(free_positions), 2, replace=False)
    #             start = free_positions[start_idx]
    #             goal = free_positions[goal_idx]
    #
    #             # Create a unique key for this pair (order matters)
    #             pair_key = (start, goal)
    #
    #             if pair_key not in used_pairs:
    #                 used_pairs.add(pair_key)
    #                 self.spawn_data[i] = {"start": start, "goal": goal}
    #                 break
    #
    #             attempts += 1
    #         else:
    #             print(f"Warning: Could not find unique start-goal pair after {max_attempts} attempts")
    #             break
    #
    #     self.map_traces[self.current_map_index] = {"index":self.current_map_index, "seed":seed,
    #                                                "grid":self.map.grid.tolist(), "erosion":self.map.erosion.tolist()}

    def _spawn_agent(self):
        start_pos = self.spawn_data["start"]
        goal_pos = self.spawn_data["goal"]

        # TODO make a factory
        agent_type = self.task.agent_type

        if agent_type == "astar":
            self.agent = AStarAgent(start_pos, goal_pos)
        elif agent_type == "dstar":
            self.agent = DStarLiteAgent(start_pos, goal_pos)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

        print(f"Agent: {agent_type}, Map #{self.task.map_index}, Spawn #{self.task.position_index}\n  Start: {start_pos} -> Goal: {goal_pos}\n")

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update >= self.update_interval:
            self.last_update = now
            self.map.update(self.agent.position)
            self.agent.update(self.map)

        # if self.agent.has_reached_goal():
        #     self._on_goal_reached()

    def is_task_completed(self):
        return self.agent.has_reached_goal()

    def get_trace(self):
        agent_trace = {"agent_type": self.task.agent_type, "spawn_index": self.task.position_index, "map_index": self.task.map_index, "agent_visited": copy.deepcopy(self.agent.visited), "agent_explored": copy.deepcopy(list(self.agent.explored))}
        return agent_trace, self.map_trace

    # def _on_goal_reached(self):
    #     self.agent_traces.append({"agent_index": self.current_agent_index, "spawn_index": self.current_spawn_index, "map_index": self.current_map_index, "agent_visited": copy.deepcopy(self.agent.visited), "agent_explored": copy.deepcopy(list(self.agent.explored))})
    #     self.current_agent_index += 1
    #
    #     if self.current_agent_index >= len(self.agent_types):
    #         self.current_agent_index = 0
    #         self.current_spawn_index += 1
    #
    #         if self.current_spawn_index >= self.spawns_per_map:
    #             self.current_spawn_index = 0
    #             self.current_map_index += 1
    #
    #             if self.current_map_index >= self.maps_to_test:
    #                 self.export_runtime_data()
    #
    #                 pygame.quit()
    #                 raise SystemExit("And... it's done!")
    #
    #             self._init_map()
    #         else:
    #             self.map.reset()
    #
    #     else:
    #         self.map.reset()
    #
    #     self._spawn_agent()

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

    # def export_runtime_data(self):
    #     name = config.CONFIG['experiment_name']
    #
    #     timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    #     output_dir = os.path.join("outputs", name + "-" + timestamp)
    #     os.makedirs(output_dir, exist_ok=True)
    #
    #     with open(os.path.join(output_dir, "agent_output.json"), "w") as f:
    #         json.dump(self.agent_traces, f, indent=4)
    #
    #     with open(os.path.join(output_dir, "map_output.json"), "w") as f:
    #         json.dump(self.map_traces, f, indent=4)
    #
    #     with open(os.path.join(output_dir, "used_config.yaml"), "w") as f:
    #         yaml.dump(config.CONFIG, f, default_flow_style=False, sort_keys=False)
