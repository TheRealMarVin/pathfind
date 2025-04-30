import pygame
import numpy as np
import random

from agents.a_star_agent import AStarAgent
from agents.agent import Agent
from constants import GRID_WIDTH, GRID_HEIGHT, NUM_STATIC_AREAS, NUM_DYNAMIC_AREAS, UPDATE_INTERVAL, CELL_SIZE, \
    COLOR_ROBOT, COLOR_GOAL, COLOR_BG, FPS
from game import Game
from map import Map
from obstacle import ObstacleArea


# ================= Main Function =================
def main():
    pygame.init()
    screen = pygame.display.set_mode((GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE))
    pygame.display.set_caption("Map Generator & Path Planning Experiment")
    clock = pygame.time.Clock()

    # Create an Experiment instance (base does nothing) and a Game instance.
    game = Game()

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
