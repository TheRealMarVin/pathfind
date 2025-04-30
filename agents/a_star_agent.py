import heapq

from agents.agent import Agent


class AStarAgent(Agent):
    def __init__(self, start, goal, lookahead_steps=5):
        super().__init__(start, goal)
        self.planned = False
        self.lookahead_steps = lookahead_steps

    def heuristic(self, a, b):
        dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
        return max(dx, dy)  # Chebyshev distance for 8 directions

    def get_neighbors(self, pos, grid):
        x, y = pos
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid.shape[1] and 0 <= ny < grid.shape[0]:
                if grid[ny, nx] == 0:
                    yield (nx, ny)

    def _plan_path(self, game_map):
        start, goal = self.start, self.goal
        grid = game_map.grid
        heap = [(0 + self.heuristic(start, goal), 0, start, [])]
        visited = set()

        while heap:
            f, g, current, path = heapq.heappop(heap)
            if current in visited:
                continue
            visited.add(current)
            self.explored.add(current)

            if current == goal:
                self.plan = path + [goal]
                return

            for neighbor in self.get_neighbors(current, grid):
                if neighbor not in visited:
                    heapq.heappush(heap, (
                        g + 1 + self.heuristic(neighbor, goal),
                        g + 1,
                        neighbor,
                        path + [current]
                    ))

        self.plan = []

    def _should_replan(self, game_map):
        """Check next few steps for new obstacles."""
        grid = game_map.grid
        for pos in self.plan[:self.lookahead_steps]:
            x, y = pos
            if grid[y, x] != 0:
                return True
        return False

    def update(self, game_map):
        if not self.planned or self._should_replan(game_map):
            self._plan_path(game_map)
            self.planned = True

        if self.plan:
            self.position = self.plan.pop(0)
            self.visited.append(self.position)
