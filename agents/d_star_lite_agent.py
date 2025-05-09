import heapq
import numpy as np
from agents.agent import Agent


class DStarLiteAgent(Agent):
    def __init__(self, start, goal, lookahead_steps=5):
        super().__init__(start, goal)
        self.lookahead_steps = lookahead_steps

        self.g = {}             # g(s): current known cost to goal
        self.rhs = {}           # rhs(s): one-step lookahead
        self.update_queue = []  # priority queue of states to update
        self.distance_since_last_update = 0        # key modifier for handling dynamic changes
        self.last_position = start
        self.initialized = False

    def update(self, game_map):
        if not self.initialized:
            self._initialize(game_map)
            self._compute_shortest_path(game_map)
            self._extract_path(game_map)
        elif self._should_replan(game_map):
            # simulate change in edge cost due to obstacle
            self.distance_since_last_update += self._heuristic(self.last_position, self.position)
            self.last_position = self.position
            for neighbor_pos in self._get_neighbors(self.position, game_map):
                self._update_vertex(neighbor_pos, game_map)
            self._compute_shortest_path(game_map)
            self._extract_path(game_map)

        if self.plan:
            self.position = self.plan.pop(0)
            self.visited.append(self.position)

    @staticmethod
    def _heuristic(a, b):
        return np.linalg.norm(np.array(a) - np.array(b))

    @staticmethod
    def _get_neighbors(pos, game_map):
        x, y = pos
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < game_map.grid.shape[1] and 0 <= ny < game_map.grid.shape[0]:
                if game_map.grid[ny, nx] == 0 and not game_map.erosion[ny, nx]:
                    yield (nx, ny)

    def _calculate_key(self, state):
        g_rhs = min(self.g.get(state, float('inf')), self.rhs.get(state, float('inf')))
        return (g_rhs + self._heuristic(self.position, state) + self.distance_since_last_update, g_rhs)

    def _initialize(self, game_map):
        self.g.clear()
        self.rhs.clear()
        self.update_queue.clear()
        self.g[self.goal] = float('inf')
        self.rhs[self.goal] = 0
        heapq.heappush(self.update_queue, (self._calculate_key(self.goal), self.goal))
        self.initialized = True

    def _update_vertex(self, node, game_map):
        if node != self.goal:
            self.rhs[node] = min(
                [self.g.get(n, float('inf')) + 1 for n in self._get_neighbors(node, game_map)]
            )

        self.update_queue = [entry for entry in self.update_queue if entry[1] != node]  # remove old entry
        heapq.heapify(self.update_queue)
        if self.g.get(node, float('inf')) != self.rhs.get(node, float('inf')):
            heapq.heappush(self.update_queue, (self._calculate_key(node), node))

    def _compute_shortest_path(self, game_map):
        while self.update_queue:
            k_top, u = self.update_queue[0]
            k_current = self._calculate_key(self.position)

            if k_top >= k_current and self.rhs.get(self.position, float('inf')) == self.g.get(self.position, float('inf')):
                break

            heapq.heappop(self.update_queue)
            self.explored.add(u)  # ← visualize this node as expanded

            if self.g.get(u, float('inf')) > self.rhs.get(u, float('inf')):
                self.g[u] = self.rhs[u]
                for neighbor in self._get_neighbors(u, game_map):
                    self._update_vertex(neighbor, game_map)
            else:
                self.g[u] = float('inf')
                self._update_vertex(u, game_map)
                for neighbor in self._get_neighbors(u, game_map):
                    self._update_vertex(neighbor, game_map)

    def _should_replan(self, game_map):
        for pos in self.plan[:self.lookahead_steps]:
            x, y = pos
            if game_map.grid[y, x] != 0 or game_map.erosion[y, x]:
                return True
        return False

    def _extract_path(self, game_map):
        path = []
        pos = self.position
        while pos != self.goal:
            neighbors = list(self._get_neighbors(pos, game_map))
            if not neighbors:
                break
            pos = min(neighbors, key=lambda n: self.g.get(n, float('inf')))
            path.append(pos)
            if self.g.get(pos, float('inf')) == float('inf'):
                break
        self.plan = path
