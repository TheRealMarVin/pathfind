import config
import pygame



class Agent:
    def __init__(self, start, goal):
        self.cell_size = config.CONFIG["map"]["cell_size"]
        self.start = start
        self.goal = goal
        self.position = start
        self.plan = []  # list of (x, y) steps
        self.explored = set()  # for planning visualization
        self.visited = [start]  # for movement visualization

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
