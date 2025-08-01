import copy
import config
import pygame


class Game:
    def __init__(self, task):
        self.task = copy.deepcopy(task)

        self.update_interval = config.CONFIG["game"]["update_interval"]
        self.color_start = config.CONFIG["game"]["color_start"]
        self.color_goal = config.CONFIG["game"]["color_goal"]
        self.color_agent = config.CONFIG["game"]["color_agent"]
        self.cell_size = config.CONFIG["map"]["cell_size"]

        self.gameplay_map = task.gameplay_map
        self.agent = None
        self.time_since_last_update = 0

        self.map_trace = self.gameplay_map.get_trace()
        self.map_trace["seed"] = task.seed
        self.map_trace["grid"] = self.gameplay_map.grid.tolist()
        self.map_trace["erosion"] = self.gameplay_map.erosion.tolist()

        self._spawn_agent()

    def _spawn_agent(self):
        self.agent = self.task.agent()

        print(f"Agent: {self.agent.display_name}, Map #{self.task.map_index}, Spawn #{self.task.position_index}\n  Start: {self.agent.start} -> Goal: {self.agent.goal}")

    def update(self, delta_time):
        self.time_since_last_update += delta_time
        if self.time_since_last_update >= self.update_interval:
            self.time_since_last_update = 0
            self.gameplay_map.update(self.agent.position)
            self.agent.update(self.gameplay_map)

    def is_task_completed(self):
        return self.agent.has_reached_goal()

    def get_trace(self):
        agent_trace = {"spawn_index": self.task.position_index,
                       "map_index": self.task.map_index, "agent_visited": copy.deepcopy(self.agent.visited),
                       "agent_explored": copy.deepcopy(list(self.agent.explored))}
        agent_state = self.agent.update_and_get_state()
        agent_trace.update(agent_state)

        print("\t\tpath length" ,agent_state["path_length"])
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
