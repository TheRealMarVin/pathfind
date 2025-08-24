import heapq
import numpy as np
from agents.agent import Agent
from agents.agent_factory import factory


@factory.register_decorator("dstar")
class DStarLiteAgent(Agent):
    @property
    def display_name(self):
        return "d star"

    @property
    def type_name(self):
        return "dstar"

    def __init__(self, start, goal, lookahead_steps=5, verbose=False, epsilon: float = 1e-4):
        super().__init__(start, goal)
        self.lookahead_steps = lookahead_steps
        self.verbose = verbose
        self.epsilon = epsilon

        self.g = {}
        self.rhs = {}
        self.update_queue = []
        self.distance_since_last_update = 0
        self.last_position = start
        self.initialized = False

    def update(self, game_map):
        self._debug_state("Update Start")

        if not self.initialized:
            self._initialize(game_map)
            self.plan_path(game_map)
            self._extract_path(game_map)

        elif self._should_replan(game_map):
            self.distance_since_last_update += self._heuristic(self.last_position, self.position)
            self.last_position = self.position

            affected = [self.position] + list(self._get_neighbors(self.position, game_map))
            affected += [p for p in self.plan[:self.lookahead_steps]
                         if game_map.grid[p[1], p[0]] != 0 or game_map.erosion[p[1], p[0]]]

            for pos in set(affected):
                self._update_vertex(pos, game_map)

            self.plan_path(game_map)
            self._extract_path(game_map)

        if not self.plan:
            self.rhs[self.position] = float("inf")
            self._update_vertex(self.position, game_map)
            self._compute_shortest_path(game_map)
            self._extract_path(game_map)

        if self.plan:
            self.position = self.plan.pop(0)
            self.visited.append(self.position)

        self._debug_state("Update End")

    def apply_dynamic_changes(self, blocked_positions, game_map):
        for pos in blocked_positions:
            x, y = pos
            game_map.grid[y, x] = 1
            self._update_vertex(pos, game_map)
            for neighbor in self._get_neighbors(pos, game_map):
                self._update_vertex(neighbor, game_map)

        self._compute_shortest_path(game_map)
        self._extract_path(game_map)

    def _initialize(self, game_map):
        self.g.clear()
        self.rhs.clear()
        self.update_queue.clear()
        self.g[self.goal] = float("inf")
        self.rhs[self.goal] = 0
        heapq.heappush(self.update_queue, (self._calculate_key(self.goal), self.goal))
        self.initialized = True

    def _calculate_key(self, state):
        g_rhs = min(self.g.get(state, float("inf")), self.rhs.get(state, float("inf")))
        return (g_rhs + self._heuristic(self.position, state) + self.distance_since_last_update, g_rhs)

    def _calculate_key(self, state):
        g_rhs = min(self.g.get(state, float("inf")), self.rhs.get(state, float("inf")))

        h = (1.0 + self.epsilon) * self._heuristic(self.position, state)
        return (g_rhs + h + self.distance_since_last_update, g_rhs)

    @staticmethod
    def _heuristic(a, b):
        return np.linalg.norm(np.array(a) - np.array(b))

    @staticmethod
    def _get_neighbors(pos, game_map):
        x, y = pos
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < game_map.grid.shape[1] and 0 <= ny < game_map.grid.shape[0]:
                if game_map.grid[ny, nx] == 0 and not game_map.erosion[ny, nx]:
                    yield (nx, ny)

    def _update_vertex(self, node, game_map):
        if node != self.goal:
            neighbors = list(self._get_neighbors(node, game_map))
            if neighbors:
                self.rhs[node] = min(self.g.get(n, float("inf")) + 1 for n in neighbors)
            else:
                self.rhs[node] = float("inf")

        self.update_queue = [e for e in self.update_queue if e[1] != node]
        heapq.heapify(self.update_queue)

        if self.g.get(node, float("inf")) != self.rhs.get(node, float("inf")):
            heapq.heappush(self.update_queue, (self._calculate_key(node), node))

    def _plan_path(self, game_map, max_expansions=50000):
        expanded = 0
        while self.update_queue:
            k_start = self._calculate_key(self.position)
            k_old, u = heapq.heappop(self.update_queue)
            k_new = self._calculate_key(u)

            if k_old < k_new:
                heapq.heappush(self.update_queue, (k_new, u))
                continue

            if not (k_old < k_start or
                    self.rhs.get(self.position, float("inf")) != self.g.get(self.position, float("inf"))):
                return

            self.explored.add(u)

            if self.g.get(u, float("inf")) > self.rhs.get(u, float("inf")):
                self.g[u] = self.rhs[u]
                for n in self._get_neighbors(u, game_map):
                    self._update_vertex(n, game_map)
            else:
                self.g[u] = float("inf")
                self._update_vertex(u, game_map)
                for n in self._get_neighbors(u, game_map):
                    self._update_vertex(n, game_map)

            expanded += 1
            if expanded >= max_expansions:
                return

    def _should_replan(self, game_map):
        for pos in self.plan[:self.lookahead_steps]:
            x, y = pos
            if game_map.grid[y, x] != 0 or game_map.erosion[y, x]:
                return True
        return False

    def _extract_path(self, game_map):
        self.plan = []

        if self.g.get(self.position, float("inf")) == float("inf"):
            return

        visited = set()
        pos = self.position
        steps = 0
        max_steps = game_map.grid.size

        while pos != self.goal and steps < max_steps:
            visited.add(pos)

            best_next = None
            best_val = float("inf")
            for n in self._get_neighbors(pos, game_map):
                val = 1 + self.g.get(n, float("inf"))
                if val < best_val:
                    best_val, best_next = val, n

            if best_next is None or best_val == float("inf") or best_next in visited:
                break

            self.plan.append(best_next)
            pos = best_next
            steps += 1

        if pos != self.goal:
            self.plan.clear()

    def _debug_state(self, label, extra=""):
        if not self.verbose:
            return
        g_val = self.g.get(self.position, float('inf'))
        rhs_val = self.rhs.get(self.position, float('inf'))
        print(f"[{label}] pos={self.position} g={g_val:.2f} rhs={rhs_val:.2f} queue={len(self.update_queue)} {extra}")
