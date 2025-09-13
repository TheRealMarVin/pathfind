import copy

import config
import numpy as np
import pygame
import time

from helpers.path_helper import compute_path_length


class Agent:
    def __init__(self, start, goal):
        self.cell_size = config.CONFIG["map"]["cell_size"]
        # TODO These should be in the state
        self.start = start
        self.goal = goal
        self.position = start
        self.plan = []  # list of (x, y) steps
        self.explored = set()  # for planning visualization
        self.visited = []  # for movement visualization
        self._planning_times = []

        self.state = {"agent_type": self.type_name, "start_pos": tuple(start), "goal_pos": tuple(goal)}

    def update(self, game_map):
        """
        Moves one step on the planned path or calls policy if no planning used.
        Should be overridden by subclasses.
        """
        raise NotImplementedError()


    def has_reached_goal(self):
        if self.position == self.goal:
            return True

        return False

    def draw(self, surface):
        """Visualize explored and visited positions."""
        for (x, y) in self.explored:
            rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
            pygame.draw.rect(surface, (173, 216, 230), rect)  # light blue = explored

        for (x, y) in self.visited:
            rect = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
            pygame.draw.rect(surface, (144, 238, 144), rect)  # light green = visited

    def plan_path(self, game_map):
        start_time = time.perf_counter()
        self._plan_path(game_map)
        planning_time = time.perf_counter() - start_time
        self._planning_times.append(planning_time)

    def _plan_path(self, game_map):
        raise NotImplementedError()

    def update_and_get_state(self):
        #TODO should just be a getter
        self.state["planning_time"] = np.array(self._planning_times).sum()
        self.state["path_length"] = compute_path_length(self.visited)

        self.state["agent_visited"] = copy.deepcopy(self.agent.visited)
        self.state["agent_explored"] = copy.deepcopy(list(self.agent.explored))

        return self.state
