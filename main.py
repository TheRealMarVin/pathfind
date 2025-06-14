import argparse
import pygame

from config import load_config
from game import Game


def main(config):
    pygame.init()
    screen = pygame.display.set_mode((config["map"]["grid_width"] * config["map"]["cell_size"], config["map"]["grid_height"] * config["map"]["cell_size"]))
    pygame.display.set_caption("Map Generator & Path Planning Experiment")
    clock = pygame.time.Clock()

    game = Game()

    running = True
    background_color = config["color_background"]
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
        screen.fill(background_color)
        game.draw(screen)
        pygame.display.flip()
        clock.tick(config["fps"])

    pygame.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configuration to launch the small game and configure the bot.")
    parser.add_argument("--config", type=str, default="configs/simple_config.yaml", help="Config file to determine the experimentation to run")
    parser.add_argument("--schema", type=str, default="configs/schemas/project_schema.yaml", help="Schema file to validate the config")
    args = parser.parse_args()

    config = load_config(args.config, args.schema)

    main(config)
