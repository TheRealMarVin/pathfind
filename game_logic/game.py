import copy
import config
import pygame


class Game:
    def __init__(self, task):
        self.task = task

        self.update_interval = config.CONFIG["game"]["update_interval"]
        self.color_goal = config.CONFIG["game"]["color_goal"]
        self.color_agent = config.CONFIG["game"]["color_agent"]
        self.cell_size = config.CONFIG["map"]["cell_size"]

        self.map = task.map
        self.agent = None
        self.last_update = 0

        self.map_trace = {"seed": task.seed, "grid":self.map.grid.tolist(), "erosion":self.map.erosion.tolist(),
                          "agent_type": task.agent}

        self._spawn_agent()

    def _spawn_agent(self):
        self.agent = self.task.agent()

        print(f"Agent: {self.agent.display_name}, Map #{self.task.map_index}, Spawn #{self.task.position_index}\n  Start: {self.agent.start} -> Goal: {self.agent.goal}\n")

    def update(self, now):
        if now - self.last_update >= self.update_interval:
            self.last_update = now
            self.map.update(self.agent.position)
            self.agent.update(self.map)

    def is_task_completed(self):
        return self.agent.has_reached_goal()

    def get_trace(self):
        agent_trace = {"agent_type": self.task.agent, "spawn_index": self.task.position_index, "map_index": self.task.map_index, "agent_visited": copy.deepcopy(self.agent.visited), "agent_explored": copy.deepcopy(list(self.agent.explored))}
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
