import heapq
import math
from typing import List, Tuple, Dict

from agents.agent import Agent
from agents.agent_factory import factory


@factory.register_decorator("dijkstra")
class DijkstraAgent(Agent):
    @property
    def display_name(self):
        return "Dijkstra"

    @property
    def type_name(self):
        return "dijkstra"

    def __init__(self, start, goal, lookahead_steps=None):
        super().__init__(start, goal)
        self.planned = False
        self.lookahead_steps = lookahead_steps  # Not used, kept for API compatibility

    def update(self, game_map):
        """
        Moves one step on the planned path. Replans if no plan exists.
        """
        if not self.planned or not self.plan:
            self.plan_path(game_map)
            self.planned = True

        if self.plan:
            self.position = self.plan.pop(0)
            self.visited.append(self.position)

    def _get_neighbors(self, pos, game_map):
        """
        Get all traversable neighbors of a position.
        Returns list of tuples: (neighbor_position, move_cost)
        """
        x, y = pos
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1),  # 4-directional
                     (-1, -1), (-1, 1), (1, -1), (1, 1)]  # 8-directional
        
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < game_map.grid.shape[1] and 0 <= ny < game_map.grid.shape[0]:
                if game_map.grid[ny, nx] == 0 and not game_map.erosion[ny, nx]:
                    # Calculate movement cost (1 for cardinal, sqrt(2) for diagonal)
                    move_cost = math.hypot(dx, dy)
                    yield (nx, ny), move_cost

    def _reconstruct_path(self, came_from: Dict[Tuple[int, int], Tuple[int, int]], 
                         current: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        Reconstruct the path from start to goal using the came_from dictionary.
        """
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path

    def _plan_path(self, game_map):
        """
        Plan a path from current position to goal using Dijkstra's algorithm.
        """
        start = self.position
        goal = self.goal
        
        # Initialize data structures
        open_set = []  # Priority queue
        heapq.heappush(open_set, (0, start))  # (distance, position)
        
        came_from = {}  # For path reconstruction
        cost_so_far = {start: 0}  # g-score
        
        # For visualization
        self.explored.clear()
        
        while open_set:
            current_cost, current = heapq.heappop(open_set)
            
            # Add to explored set for visualization
            self.explored.add(current)
            
            if current == goal:
                break
                
            for neighbor, move_cost in self._get_neighbors(current, game_map):
                new_cost = cost_so_far[current] + move_cost
                
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost  # Dijkstra's uses g(n) only
                    heapq.heappush(open_set, (priority, neighbor))
                    came_from[neighbor] = current
        
        # Reconstruct path if goal was reached
        if goal in came_from or start == goal:
            self.plan = self._reconstruct_path(came_from, goal)
            # Remove the first element (current position) if it exists
            if self.plan and self.plan[0] == self.position:
                self.plan = self.plan[1:]
        else:
            self.plan = []  # No path found
