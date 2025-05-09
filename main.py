import argparse
import pygame
import random

from constants import GRID_WIDTH, GRID_HEIGHT, CELL_SIZE, COLOR_BG, FPS
from game import Game


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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    game.reset_same_map()
                elif event.key == pygame.K_n:
                    game.reset_new_map()

        game.update()
        screen.fill(COLOR_BG)
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configuration to launch the small game and configure the bot.")
    parser.add_argument("--seed", type=int, help="Seed for the random number generator")
    parser.add_argument("--config", type=str, default=None, help="Config file to determine the experimentation to run")

    args = parser.parse_args()

    if args.seed is not None:
        seed_value = args.seed
    else:
        seed_value = random.randint(0, 2 ** 32 - 1)

    random.seed(seed_value)
    print("seed_value", seed_value)

    main()
