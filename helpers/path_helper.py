import math

def compute_path_length(path):
    """
    Compute the total length of a path by summing distances between consecutive positions.

    Args:
        path: A list of (x, y) positions including the start.

    Returns:
        The total path length as a float.
    """
    total = 0.0

    for i in range(1, len(path)):
        dx = path[i][0] - path[i - 1][0]
        dy = path[i][1] - path[i - 1][1]
        total += math.hypot(dx, dy)

    return total

def is_touching(position_1, position_2):
    if type(position_1) is str or type(position_2) is str:
        return False

    dx = abs(position_1[0] - position_2[0])
    dy = abs(position_1[1] - position_2[1])

    return not(dx > 1 or dy > 1)

def count_invalid_moves(path):
    invalid_count = 0
    for i in range(len(path) - 1):
        if not is_touching(path[i], path[i + 1]):
            invalid_count += 1
    return invalid_count