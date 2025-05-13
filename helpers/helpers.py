import random


def make_horizontal_line(length):
    """Return a list of (x, y) positions for a horizontal line starting at (0,0)."""
    return [(i, 0) for i in range(length)]

def make_vertical_line(length):
    """Return a list of (x, y) positions for a vertical line starting at (0,0)."""
    return [(0, i) for i in range(length)]

def make_block(width, height):
    """Return a list of (x, y) positions for a block (rectangle) starting at (0,0)."""
    return [(x, y) for y in range(height) for x in range(width)]

def random_shape(random_generator):
    """
    Randomly select a shape template.
    For dynamic obstacles, you might allow slightly different options.
    """
    shape_type = random_generator.choice(["block", "horizontal", "vertical", "L"])
    if shape_type == "block":
        w = random_generator.randint(2, 5)
        h = random_generator.randint(2, 5)
        return make_block(w, h)
    elif shape_type == "horizontal":
        length = random_generator.randint(3, 7)
        return make_horizontal_line(length)
    elif shape_type == "vertical":
        length = random_generator.randint(3, 7)
        return make_vertical_line(length)
    elif shape_type == "L":
        # A simple L-shape: three cells
        return [(0, 0), (1, 0), (0, 1)]