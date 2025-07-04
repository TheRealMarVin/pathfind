import copy


class TaskSpec:
    def __init__(self, seed, position_index, map_index, game_map, agent):
        self.seed = seed
        self.position_index = position_index
        self.map_index = map_index
        self.map = copy.deepcopy(game_map)
        self.agent = agent