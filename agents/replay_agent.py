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

        self.planned = True
        self.plan = trace["agent_visited"]
        self.explored = set([tuple(pos) for pos in self.plan])
        self.analysis = trace["analysis"]
        self.current_step_analysis = None
        print("XXXXXXXXXXXXXXX")
        for i, step in enumerate(trace["analysis"]):
            print(f"Step: {i}")
            for k,v in step.items():
                print(f"\t{k} : {v}")

    def update(self, game_map):
        if self.plan:
            self.position = self.plan.pop(0)
            if len(self.analysis) > 0:
                self.current_step_analysis = self.analysis.pop(0)
            self.visited.append(self.position)

    def has_reached_goal(self):
        if self.plan:
            return False

        return True

    def update_and_get_state(self):
        super().update_and_get_state()

        if self.current_step_analysis is not None:
            for k, v in self.current_step_analysis.items():
                self.state[k] = v

        return self.state
