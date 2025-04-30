import pygame
import numpy as np
import random

from constants import GRID_WIDTH, GRID_HEIGHT, NUM_STATIC_AREAS, NUM_DYNAMIC_AREAS, UPDATE_INTERVAL, CELL_SIZE, \
    COLOR_ROBOT, COLOR_GOAL, COLOR_BG, FPS
from game import Game
from map import Map
from obstacle import ObstacleArea



# ================= Experiment Base Class =================
class Experiment:
    def __init__(self, game_map):
        """
        Holds a reference to the Map for later use in path planning (A*, D*, etc.).
        """
        self.game_map = game_map

    def update(self):
        """
        Intended to be overridden to implement path planning.
        The base implementation does nothing.
        """
        pass


# ================= Main Function =================
def main():
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    pygame.display.set_caption("Map Generator & Path Planning Experiment")
    clock = pygame.time.Clock()

    # Create an Experiment instance (base does nothing) and a Game instance.
    experiment = Experiment(None)
    game = Game(experiment)
    experiment.game_map = game.map  # give experiment a reference to the map

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        game.update()
        screen.fill(COLOR_BG)
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    main()
