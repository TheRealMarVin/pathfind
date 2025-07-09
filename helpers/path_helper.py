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
