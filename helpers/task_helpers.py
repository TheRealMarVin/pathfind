import numpy as np
import random

from tqdm import tqdm

import config
from environment.map import Map
from game_logic.task_spec import TaskSpec


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

def create_tasks():
    if config.CONFIG["seed"] is not None:
        map_seed = config.CONFIG["seed"]
    else:
        map_seed = random.randint(0, 99999)

    maps_to_test = config.CONFIG["maps_to_test"]
    spawns_per_map = config.CONFIG["spawns_per_map"]
    agent_types = config.CONFIG["agent_types"]

    tasks = []
    for map_index in tqdm(range(maps_to_test)):
        seed = map_seed + map_index
        current_map = create_map(seed)
        start_goal_pairs = create_positions(current_map, spawns_per_map)
        for key, pair in start_goal_pairs.items():
            for current_agent_type in agent_types:
                task = TaskSpec(seed=seed, position_index=key, map_index=map_index, game_map=current_map,
                                position_pairs=pair, agent_type=current_agent_type)
                tasks.append(task)

        map_seed += 1

    return tasks