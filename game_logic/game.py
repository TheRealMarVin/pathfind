import copy
import config
import pygame

from helpers.path_helper import compute_path_length


class Game:
    def __init__(self, task):
        self.task = task

        self.update_interval = config.CONFIG["game"]["update_interval"]
        self.color_start = config.CONFIG["game"]["color_start"]
        self.color_goal = config.CONFIG["game"]["color_goal"]
        self.color_agent = config.CONFIG["game"]["color_agent"]
        self.cell_size = config.CONFIG["map"]["cell_size"]

        self.gameplay_map = task.gameplay_map
        self.agent = None
        self.last_update = 0

        self.map_trace = self.gameplay_map.get_trace()
        self.map_trace["seed"] = task.seed
        self.map_trace["grid"] = self.gameplay_map.grid.tolist()
        self.map_trace["erosion"] = self.gameplay_map.erosion.tolist()

        self._spawn_agent()

    def _spawn_agent(self):
        self.agent = self.task.agent()

        print(f"Agent: {self.agent.display_name}, Map #{self.task.map_index}, Spawn #{self.task.position_index}\n  Start: {self.agent.start} -> Goal: {self.agent.goal}\n")

    def update(self, now):
        if now - self.last_update >= self.update_interval:
            self.last_update = now
            self.gameplay_map.update(self.agent.position)
            self.agent.update(self.gameplay_map)

    def is_task_completed(self):
        return self.agent.has_reached_goal()

    def get_trace(self):
        agent_trace = {"agent_type": self.agent.type_name, "spawn_index": self.task.position_index,
                       "start_pos": tuple(self.agent.start), "goal_pos": tuple(self.agent.goal),
                       "map_index": self.task.map_index, "agent_visited": copy.deepcopy(self.agent.visited),
                       "agent_explored": copy.deepcopy(list(self.agent.explored)),
                       "planning_time": self.agent.get_planning_time(),
                       "path_length": compute_path_length(self.agent.visited)}
        print("\t\tpath length" ,compute_path_length(self.agent.visited))
        print("\t\tvisited path nodes count", len(self.agent.visited))
        print("\t\texplored path nodes count", len(self.agent.explored))
        return agent_trace, self.map_trace

    def draw(self, surface):
        self.agent.draw(surface)
        self.gameplay_map.draw(surface, self.cell_size)

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

        # Draw start
        gx, gy = self.agent.start
        pygame.draw.rect(
            surface,
            self.color_start,
            pygame.Rect(gx * self.cell_size, gy * self.cell_size, self.cell_size, self.cell_size)
        )
