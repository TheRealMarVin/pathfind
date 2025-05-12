class ObstacleArea:
    def __init__(self, cells, move_pattern=(0, 0), name=None):
        """
        cells: list of (x, y) positions defining the shape (relative to a local origin).
        move_pattern: (dx, dy) movement to apply each update.
        name: optional identifier.
        """
        self.cells = cells
        self.move_pattern = move_pattern
        self.original_move_pattern = move_pattern
        self.name = name or f"Area_{id(self)}"
        self.offset = (0, 0)  # current position offset on the grid

    def get_absolute_positions(self, offset=None):
        """Return the positions of the shape cells on the grid based on offset.
           If offset is None, use the current offset.
        """
        if offset is None:
            offset = self.offset
        ox, oy = offset
        return [(x + ox, y + oy) for (x, y) in self.cells]
