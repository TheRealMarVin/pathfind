import argparse
import pygame

from config import load_config
from debug.debug_window import debug_queue, toggle_debug_window
from game_logic.game import Game
from helpers.log_helpers import export_runtime_data
from helpers.task_helpers import create_tasks


def main(config):
    index = 0
    tasks = create_tasks()
    if len(tasks) == 0:
        return

    pygame.init()
    screen = pygame.display.set_mode((config["map"]["grid_width"] * config["map"]["cell_size"], config["map"]["grid_height"] * config["map"]["cell_size"]))
    pygame.display.set_caption("Map Generator & Path Planning Experiment")
    clock = pygame.time.Clock()

    map_traces = {}
    agent_traces = []

    task = tasks[index]
    game = Game(task)

    fps = config["fps"]
    background_color = config["color_background"]
    record_trace = config["record_trace"]

    debug_enabled = False
    running = True
    paused = False
    previous_time = pygame.time.get_ticks()
    while running:
        delta_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_x:
                    game = Game(game.task)
                elif event.key == pygame.K_d:
                    toggle_debug_window()
                    debug_enabled = not debug_enabled
                elif event.key == pygame.K_p:
                    if paused:
                        paused = False
                        previous_time = pygame.time.get_ticks()
                    else:
                        paused = True
                elif event.key == pygame.K_s:
                    if paused:
                        delta_time = game.update_interval
        if debug_enabled:
            debug_queue.put(game.agent.update_and_get_state())
        if not paused:
            now = pygame.time.get_ticks()
            delta_time = now - previous_time
            previous_time = now

        game.update(delta_time)
        screen.fill(background_color)
        game.draw(screen)
        pygame.display.flip()
        clock.tick(fps)

        if  game.is_task_completed():
            if record_trace:
                agent_trace, map_trace = game.get_trace()
                map_traces[tasks[index].map_index] = map_trace
                agent_traces.append(agent_trace)

            index += 1
            if index < len(tasks):
                task = tasks[index]

                game = Game(task)
            else:
                running = False

    if record_trace:
        name = config["experiment_name"]
        output_folder = config["output_folder"]
        export_runtime_data(name, output_folder, agent_traces, map_traces)

    pygame.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configuration to launch the small game and configure the bot.")
    parser.add_argument("--config", type=str, default="configs/simple_generate_config.yaml", help="Config file to determine the experimentation to run")
    parser.add_argument("--schema", type=str, default="configs/schemas/project_schema.yaml", help="Schema file to validate the config")
    args = parser.parse_args()

    project_config = load_config(args.config, args.schema)

    main(project_config)
