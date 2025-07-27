from agents.agent import Agent


class ReplayAgent(Agent):
    @property
    def display_name(self):
        return "replay"

    @property
    def type_name(self):
        return "replay"

    def __init__(self, trace):
        super().__init__(trace["start_pos"], trace["goal_pos"])

        self.trace = trace
        self.planned = True
        self.plan = trace["agent_visited"]
        self.explored = set([tuple(pos) for pos in self.plan])

    def update(self, game_map):
        if self.plan:
            self.position = self.plan.pop(0)
            self.visited.append(self.position)

    def has_reached_goal(self):
        if self.plan:
            return False

        return True
