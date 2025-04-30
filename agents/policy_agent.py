from agents.agent import Agent


class PolicyAgent(Agent):
    def update(self, game_map):
        # For now: move randomly toward goal
        x, y = self.position
        gx, gy = self.goal
        dx = np.sign(gx - x)
        dy = np.sign(gy - y)
        new_pos = (x + dx, y + dy)
        if game_map.grid[new_pos[1], new_pos[0]] == 0:
            self.position = new_pos
            self.visited.append(self.position)
