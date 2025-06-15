import argparse
import copy
import json
import numpy as np
import os
import pygame
import random
import yaml

from datetime import datetime
from tqdm import tqdm

import config
from config import load_config
from environment.map import Map
from game import Game

# TODO should not be here!!!
def find_start_and_goal_positions(spawns_per_map, free_positions):
    max_attempts = 250
    spawn_data = {}
    used_pairs = set()

    for i in range(spawns_per_map):
        attempts = 0
        while attempts < max_attempts:
            # Randomly select start and goal from free positions
            start_idx, goal_idx = np.random.choice(len(free_positions), 2, replace=False)
            start = free_positions[start_idx]
            goal = free_positions[goal_idx]

            # Create a unique key for this pair (order matters)
            pair_key = (start, goal)

            if pair_key not in used_pairs:
                used_pairs.add(pair_key)
                spawn_data[i] = {"start": start, "goal": goal}
                break

            attempts += 1
        else:
            print(f"Warning: Could not find unique start-goal pair after {max_attempts} attempts")
            break

    return spawn_data

def create_map(seed):
    # TODO needed before
    #seed = self.map_seed + self.current_map_index

    random_generator = random.Random(seed)
    np.random.seed(seed)

    map = Map(
        config.CONFIG["map"]["grid_width"],
        config.CONFIG["map"]["grid_height"],
        random_generator,
        config.CONFIG["map"]["num_static_areas"],
        config.CONFIG["map"]["num_dynamic_areas"]
    )

    return map

def create_positions(map, spawns_per_map):
    free_positions = map.get_free_positions()
    max_possible_pairs = len(free_positions) * (len(free_positions) - 1)  # n * (n-1) since order matters
    spawns_per_map = min(spawns_per_map, max_possible_pairs)

    if spawns_per_map < spawns_per_map:
        print(
            f"Warning: Reduced spawns_per_map from {spawns_per_map} to {spawns_per_map} to respect map size constraints")

    start_goal_pairs = find_start_and_goal_positions(spawns_per_map, free_positions)
    return start_goal_pairs

class TaskSpec:
    def __init__(self, seed, position_index, map_index, game_map, position_pairs, agent_type):
        self.seed = seed
        self.position_index = position_index
        self.map_index = map_index
        self.map = copy.deepcopy(game_map)
        self.position_pairs = position_pairs
        self.agent_type = agent_type

def create_tasks():
    if config.CONFIG["seed"] is not None:
        map_seed = config.CONFIG["seed"]
    else:
        map_seed = random.randint(0, 99999)

    maps_to_test = config.CONFIG["maps_to_test"]
    spawns_per_map = config.CONFIG["spawns_per_map"]
    agent_types = config.CONFIG["agent_types"]

    tasks = []
    for current_agent_type in agent_types:
        for map_index in tqdm(range(maps_to_test)):
            seed = map_seed + map_index
            current_map = create_map(seed)
            start_goal_pairs = create_positions(current_map, spawns_per_map)
            for key, pair in start_goal_pairs.items():
                task = TaskSpec(seed=seed, position_index=key, map_index=map_index, game_map=current_map, position_pairs=pair, agent_type=current_agent_type)
                tasks.append(task)

            map_seed += 1

    return tasks

def export_runtime_data(agent_traces, map_traces):
    name = config.CONFIG['experiment_name']

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = os.path.join("outputs", name + "-" + timestamp)
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "agent_output.json"), "w") as f:
        json.dump(agent_traces, f, indent=4)

    with open(os.path.join(output_dir, "map_output.json"), "w") as f:
        json.dump(map_traces, f, indent=4)

    with open(os.path.join(output_dir, "used_config.yaml"), "w") as f:
        yaml.dump(config.CONFIG, f, default_flow_style=False, sort_keys=False)

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

        now = pygame.time.get_ticks()
        game.update(now)
        screen.fill(background_color)
        game.draw(screen)
        pygame.display.flip()
        clock.tick(fps)

        if game.is_task_completed():
            agent_trace, map_trace = game.get_trace()
            map_traces[tasks[index].map_index] = map_trace
            agent_traces.append(agent_trace)
            index += 1
            if index < len(tasks):
                task = tasks[index]

                game = Game(task)
            else:
                running = False

    export_runtime_data(agent_traces, map_traces)

    pygame.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configuration to launch the small game and configure the bot.")
    parser.add_argument("--config", type=str, default="configs/simple_config.yaml", help="Config file to determine the experimentation to run")
    parser.add_argument("--schema", type=str, default="configs/schemas/project_schema.yaml", help="Schema file to validate the config")
    args = parser.parse_args()

    project_config = load_config(args.config, args.schema)

    main(project_config)
