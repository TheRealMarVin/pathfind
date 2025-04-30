GRID_WIDTH = 50             # number of cells horizontally
GRID_HEIGHT = 40            # number of cells vertically
CELL_SIZE = 5              # pixel size of each cell
FPS = 30                    # frames per second for the game loop

NUM_STATIC_AREAS = 3        # number of static (non-moving) obstacle groups
NUM_DYNAMIC_AREAS = 4       # number of moving obstacle groups
UPDATE_INTERVAL = 500       # ms between dynamic obstacle moves

# Colors (RGB)
COLOR_BG = (255, 255, 255)       # white background
COLOR_OBSTACLE = (0, 0, 0)       # black obstacles
COLOR_GRID_LINE = (200, 200, 200)
COLOR_ROBOT = (0, 255, 0)        # green for robot
COLOR_GOAL = (255, 0, 0)         # red for goal
COLOR_EROSION = (255, 165, 0)    # orange for erosion boundary