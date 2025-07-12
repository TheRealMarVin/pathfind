import random
import numpy as np
from agents.agent import Agent
from dataclasses import dataclass

@dataclass
class Direction:
    dx: int
    dy: int
    
    def __hash__(self):
        return hash((self.dx, self.dy))

class MonteCarloAgent(Agent):
    @property
    def display_name(self):
        return "monte carlo"

    @property
    def type_name(self):
        return "monte_carlo"

    def __init__(self, start, goal, path_length=100, direction_bias=0.8):
        super().__init__(start, goal)
        self.max_steps = path_length
        self.direction_bias = direction_bias  # Probability to continue in same direction
        self.planned = False

    def update(self, game_map):
        if not self.planned:
            self.plan_path(game_map)
            self.planned = True

        if self.plan:
            self.position = self.plan.pop(0)
            self.visited.append(self.position)

    def has_reached_goal(self):
        return not self.plan

    def _is_valid_move(self, x, y, game_map, visited):
        # Check if position is within bounds
        if not (0 <= x < game_map.grid.shape[1] and 0 <= y < game_map.grid.shape[0]):
            return False
            
        # Check if position is not a wall and not eroded
        if game_map.grid[y, x] != 0 or game_map.erosion[y, x]:
            return False
            
        # Check if position hasn't been visited
        return (x, y) not in visited

    def _get_possible_moves(self, x, y, game_map, visited):
        moves = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue  # Skip current position
                    
                new_x, new_y = x + dx, y + dy
                if self._is_valid_move(new_x, new_y, game_map, visited):
                    moves.append((new_x, new_y, Direction(dx, dy)))
        return moves

    def _plan_path(self, game_map):
        self.plan = []
        current = self.start
        visited = set([current])
        last_direction = None
        
        for _ in range(self.max_steps):
            x, y = current
            moves = self._get_possible_moves(x, y, game_map, visited)
            
            if not moves:
                break  # No valid moves available
            
            # If we have a last direction and random check passes, try to continue in that direction
            if last_direction and random.random() < self.direction_bias:
                # Find moves in the same direction
                same_dir_moves = [m for m in moves if m[2] == last_direction]
                if same_dir_moves:
                    chosen = random.choice(same_dir_moves)
                    current = (chosen[0], chosen[1])
                    self.plan.append(current)
                    visited.add(current)
                    self.explored.add(current)
                    continue
            
            # Either no direction bias or couldn't continue in same direction
            chosen = random.choice(moves)
            current = (chosen[0], chosen[1])
            last_direction = chosen[2]
            self.plan.append(current)
            visited.add(current)
            self.explored.add(current)
