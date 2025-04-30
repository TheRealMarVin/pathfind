from agents.agent import Agent


class DStarLiteAgent(Agent):
    def __init__(self, start, goal):
        super().__init__(start, goal)
        # Initialize D* Lite structures (RHS, G, open list, etc.)
        self.initialized = False

    def update(self, game_map):
        if not self.initialized:
            # TODO: implement D* Lite init and plan
            self.initialized = True
            self.plan = [self.start, self.goal]  # stub fallback
        if self.plan:
            self.position = self.plan.pop(0)
            self.visited.append(self.position)
