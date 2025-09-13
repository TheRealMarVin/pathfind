import heapq
import math

from agents.agent import Agent
from agents.agent_factory import factory


@factory.register_decorator("astar")
class AStarAgent(Agent):
    @property
    def display_name(self):
        return "a star"

    @property
    def type_name(self):
        return "astar"

    def __init__(self, start, goal, lookahead_steps=5):
        super().__init__(start, goal)
        self.planned = False
        self.lookahead_steps = lookahead_steps

    def update(self, game_map):
        if not self.planned or self._should_replan(game_map):
            self.plan_path(game_map)
            self.planned = True

        if self.plan:
            self.position = self.plan.pop(0)
            self.visited.append(self.position)

    def _heuristic(self, a, b):
        # here we use Octile distance because it is closer to our movement scheme.
        dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
        return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)

    def _get_neighbors(self, pos, game_map):
        x, y = pos
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < game_map.grid.shape[1] and 0 <= ny < game_map.grid.shape[0]:
                if game_map.grid[ny, nx] == 0 and not game_map.erosion[ny, nx]:
                    move_cost = math.hypot(dx, dy)
                    yield (nx, ny), move_cost

    def _plan_path(self, game_map):
        start, goal = self.position, self.goal
        nodes_to_explore = [(self._heuristic(start, goal), 0.0, start, [])]
        visited = set()
        self.explored.clear()  # Clear explored set for visualization

        while nodes_to_explore:
            total_cost, path_cost, current, path = heapq.heappop(nodes_to_explore)
            if current in visited:
                continue
            visited.add(current)
            self.explored.add(current)

            if current == goal:
                self.plan = path + [goal]
                return

            for (neighbor, move_cost) in self._get_neighbors(current, game_map):
                if neighbor not in visited:
                    new_path_cost = path_cost + move_cost
                    # (1 + 1e-4) is a small trick to break ties and favor depth over width.
                    # The small epsilon will affect the heuristic a bit more a favor deeper nodes
                    new_total_cost = new_path_cost + ((1 + 1e-4) * self._heuristic(neighbor, goal))
                    heapq.heappush(nodes_to_explore, (new_total_cost, new_path_cost, neighbor, path + [current]))

        self.plan = []

    def _should_replan(self, game_map) -> bool:
        """
        Check if replanning is needed by looking ahead in the current plan.
        
        Returns:
            bool: True if replanning is needed, False otherwise
        """
        if not self.plan:
            return True
            
        grid = game_map.grid
        for pos in self.plan[:self.lookahead_steps]:
            x, y = pos
            if not (0 <= y < grid.shape[0] and 0 <= x < grid.shape[1]):
                return True
            if grid[y, x] != 0 or game_map.erosion[y, x]:
                return True
        return False