class ObstacleArea:
    def __init__(self, cells: list[tuple[int, int]], offset: tuple[int, int] = (0, 0), move_pattern: tuple[int, int] = (0, 0)):
        self.cells = cells                                 # Relative cell positions (shape)
        self.initial_offset = offset                       # Initial offset (for reset)
        self.initial_move_pattern = move_pattern           # Initial movement pattern (for reset)
        self.offset = offset                               # Current world offset (x, y)
        self.move_pattern = move_pattern                   # Current movement direction per step

    def get_absolute_positions(self) -> list[tuple[int, int]]:
        ox, oy = self.offset
        return [(x + ox, y + oy) for x, y in self.cells]

    def set_move_pattern(self, dx: int, dy: int):
        self.move_pattern = (dx, dy)

    def plan_move(self) -> tuple[int, int]:
        dx, dy = self.move_pattern
        ox, oy = self.offset
        return ox + dx, oy + dy

    def execute_move(self, x: int, y: int):
        self.offset = (x, y)

    def reset(self):
        self.offset = self.initial_offset
        self.move_pattern = self.initial_move_pattern

    def copy_with_new_offset(self, offset: tuple[int, int]) -> "ObstacleArea":
        return ObstacleArea(self.cells, offset, self.move_pattern)
