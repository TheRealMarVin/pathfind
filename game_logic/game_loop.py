import pygame
import time

from concurrent.futures import ThreadPoolExecutor, as_completed
from debug.debug_window import debug_queue, toggle_debug_window
from game_logic.game import Game
from helpers.log_helpers import export_runtime_data
from helpers.task_helpers import create_tasks
from tqdm import tqdm


def interactive_main_loop(config):
    agent_traces = []
    map_traces = {}

    index = 0
    tasks = create_tasks(agent_traces)
    if len(tasks) == 0:
        return

    pygame.init()
    screen = pygame.display.set_mode((config["map"]["grid_width"] * config["map"]["cell_size"],
                                      config["map"]["grid_height"] * config["map"]["cell_size"]))
    pygame.display.set_caption("Map Generator & Path Planning Experiment")
    clock = pygame.time.Clock()

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

        if game.is_task_completed():
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


def run_task(task, fps):
    game = Game(task)
    interval = 1.0 / fps

    while not game.is_task_completed():
        game.update(time.time() * 1000)
        time.sleep(interval)

    agent_trace, map_trace = game.get_trace()
    return {
        "map_index": task.map_index,
        "agent_trace": agent_trace,
        "map_trace": map_trace,
    }

def run_experiments_parallel(config, max_workers=4):
    tasks = create_tasks()
    if not tasks:
        print("No tasks to run.")
        return

    fps = config["fps"]
    results = []
    print(f"Running {len(tasks)} tasks using {max_workers} workers...")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(run_task, task, fps) for task in tasks]

        for future in tqdm(as_completed(futures), total=len(futures)):
            try:
                results.append(future.result())
            except Exception as e:
                print(f"Task failed with exception: {e}")

    # Group traces
    map_traces = {}
    agent_traces = []

    for result in results:
        map_traces[result["map_index"]] = result["map_trace"]
        agent_traces.append(result["agent_trace"])

    name = config["experiment_name"]
    output_folder = config["output_folder"]
    export_runtime_data(name, output_folder, agent_traces, map_traces)