from agents.agent import Agent


class ReplayAgent(Agent):
    @property
    def display_name(self):
        return "replay"

    def __init__(self, start, goal, plan):
        super().__init__(start, goal)
        self.planned = True
        self.plan = plan
        self.explored = set([tuple(pos) for pos in plan])

    def update(self, game_map):
        if self.plan:
            self.position = self.plan.pop(0)
            self.visited.append(self.position)
