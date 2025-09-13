import heapq
import math
from typing import List, Tuple, Dict, Iterable
from collections import defaultdict

import numpy as np

from agents.agent import Agent
from agents.agent_factory import factory


@factory.register_decorator("diverse_dijkstra")
class DiverseDijkstraAgent(Agent):
    @property
    def display_name(self):
        return "Dijkstra (penalized)"

    @property
    def type_name(self):
        return "diverse_dijkstra"

    def __init__(
        self,
        start,
        goal,
        previous_traces=[],
        lambda_overlap=5.0,
        lambda_band=1.0,
        band_radius=2,
        band_falloff="linear",  # "linear" or "inverse"
        tiny_tiebreak=True
    ):
        """
        previous_traces: dict you manage; values are iterables of paths
        lambda_overlap: penalty added to cells exactly on a prior path (per path hit).
        lambda_band: penalty added to cells within 'band_radius' of a prior path (per path).
        band_radius: Manhattan radius around each traced cell to “discourage corridors”.
        band_falloff: "linear" => penalty scales as (1 - d/(band_radius+1));
                      "inverse" => penalty scales as 1/(1+d).
        tiny_tiebreak: if True, add a tiny hashed epsilon to g-cost to break ties deterministically.
        """
        super().__init__(start, goal)
        self.planned = False
        previous_traces or []
        self.lambda_overlap = float(lambda_overlap)
        self.lambda_band = float(lambda_band)
        self.band_radius = int(band_radius)
        self.band_falloff = band_falloff
        self.tiny_tiebreak = tiny_tiebreak

        self._penalty_field = None
        self.previous_traces = []
        for trace in previous_traces:
            if trace["start_pos"] == start and trace["goal_pos"] == goal:
                self.previous_traces.append(trace["agent_visited"])

    def update(self, game_map):
        if not self.planned or not self.plan:
            self.plan_path(game_map)
            self.planned = True

        if self.plan:
            self.position = self.plan.pop(0)
            self.visited.append(self.position)

    def _get_neighbors(self, pos, game_map):
        x, y = pos
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),
                      (-1, -1), (-1, 1), (1, -1), (1, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < game_map.grid.shape[1] and 0 <= ny < game_map.grid.shape[0]:
                if game_map.grid[ny, nx] == 0 and not game_map.erosion[ny, nx]:
                    move_cost = math.hypot(dx, dy)
                    yield (nx, ny), move_cost

    def _reconstruct_path(self, came_from, current):
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def _plan_path(self, game_map):
        start = self.position
        goal = self.goal

        # Build/update penalty field from previous traces
        self._penalty_field = self._build_penalty_field(game_map, start, goal)

        open_set = []
        heapq.heappush(open_set, (0.0, start))
        came_from = {}
        g = {start: 0.0}

        self.explored.clear()

        while open_set:
            current_cost, current = heapq.heappop(open_set)
            self.explored.add(current)

            if current == goal:
                break

            for (nx, ny), move_cost in self._get_neighbors(current, game_map):
                # cost to enter neighbor includes penalty at neighbor cell
                penalty = self._penalty_field[ny, nx]
                step_cost = move_cost + penalty

                new_cost = g[current] + step_cost

                # optional deterministic tiny tiebreaker to diversify equal-cost routes
                if self.tiny_tiebreak:
                    # small hash-based epsilon on the neighbor node
                    # keeps Dijkstra correctness (non-negative, tiny)
                    eps = (hash((nx, ny)) & 0xffff) * 1e-12
                    new_cost += eps

                if (nx, ny) not in g or new_cost < g[(nx, ny)]:
                    g[(nx, ny)] = new_cost
                    heapq.heappush(open_set, (new_cost, (nx, ny)))
                    came_from[(nx, ny)] = current

        if goal in came_from or start == goal:
            self.plan = self._reconstruct_path(came_from, goal)
            if self.plan and self.plan[0] == self.position:
                self.plan = self.plan[1:]
        else:
            self.plan = []

    def _build_penalty_field(self, game_map, start, goal):
        h, w = game_map.grid.shape
        field = np.zeros((h, w), dtype=np.float32)



        # Collect all points from the selected trace sets
        # traced_points = []   # list of (x,y)
        for path in self.previous_traces:
            # overlap penalty for exact path cells
            for (x, y) in path:
                field[y, x] += self.lambda_overlap

                # if 0 <= x < w and 0 <= y < h:
                #     traced_points.append((x, y))

            # optional corridor band penalty
            if self.band_radius > 0 and self.lambda_band > 0:
                for (x, y) in path:
                    x0, y0 = x, y
                    for dy in range(-self.band_radius, self.band_radius + 1):
                        for dx in range(-self.band_radius, self.band_radius + 1):
                            nx, ny = x0 + dx, y0 + dy
                            if 0 <= nx < w and 0 <= ny < h:
                                d = abs(dx) + abs(dy)  # Manhattan band
                                if 0 < d <= self.band_radius:
                                    if self.band_falloff == "linear":
                                        scale = 1.0 - (d / (self.band_radius + 1.0))
                                    else:  # "inverse"
                                        scale = 1.0 / (1.0 + d)
                                    field[ny, nx] += self.lambda_band * scale

        return field
