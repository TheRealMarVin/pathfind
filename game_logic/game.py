import copy
import config
import pygame

from agents.a_star_agent import AStarAgent
from agents.d_star_lite_agent import DStarLiteAgent


class Game:
    def __init__(self, task):
        self.task = task

        self.update_interval = config.CONFIG["game"]["update_interval"]
        self.color_goal = config.CONFIG["game"]["color_goal"]
        self.color_agent = config.CONFIG["game"]["color_agent"]
        self.cell_size = config.CONFIG["map"]["cell_size"]

        self.map = task.map
        self.agent = None
        self.spawn_data = task.position_pairs
        self.last_update = 0

        self.map_trace = {"seed": task.seed, "grid":self.map.grid.tolist(), "erosion":self.map.erosion.tolist(),
                          "agent_type": task.agent_type}

        self._spawn_agent()

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

    def update(self, now):
        if now - self.last_update >= self.update_interval:
            self.last_update = now
            self.map.update(self.agent.position)
            self.agent.update(self.map)

    def is_task_completed(self):
        return self.agent.has_reached_goal()

    def get_trace(self):
        agent_trace = {"agent_type": self.task.agent_type, "spawn_index": self.task.position_index, "map_index": self.task.map_index, "agent_visited": copy.deepcopy(self.agent.visited), "agent_explored": copy.deepcopy(list(self.agent.explored))}
        return agent_trace, self.map_trace

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
