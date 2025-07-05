import orjson
import os
from functools import partial

import numpy as np
import random

from tqdm import tqdm

import config
from agents.a_star_agent import AStarAgent
from agents.d_star_lite_agent import DStarLiteAgent
from agents.replay_agent import ReplayAgent
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

def _get_generation_agent(agent_type, positions):
    start_pos = positions["start"]
    goal_pos = positions["goal"]

    if agent_type == "astar":
        agent = partial(AStarAgent,start_pos, goal_pos)
    elif agent_type == "dstar":
        agent = partial(DStarLiteAgent, start_pos, goal_pos)
    else:
        raise ValueError(f"Unknown agent type: {agent_type}")

    return agent

def _create_generate_tasks(seed):
    maps_to_test = config.CONFIG["maps_to_test"]
    spawns_per_map = config.CONFIG["spawns_per_map"]
    agent_types = config.CONFIG["agent_types"]

    tasks = []
    for map_index in tqdm(range(maps_to_test)):
        map_seed = seed + map_index
        current_map = create_map(map_seed)
        start_goal_pairs = create_positions(current_map, spawns_per_map)
        for key, position_pairs in start_goal_pairs.items():
            for agent_type in agent_types:
                agent = _get_generation_agent(agent_type, position_pairs)

                task = TaskSpec(seed=map_seed, position_index=key, map_index=map_index, game_map=current_map,
                                agent=agent)
                tasks.append(task)

    return tasks

def _create_replay_tasks(seed):
    replay_folder = config.CONFIG["replay_folder"]

    agent_file = os.path.join(replay_folder, "agent_output.json")
    with open(agent_file, "r") as f:
        agent_data = orjson.loads(f.read())

    map_file = os.path.join(replay_folder, "map_output.json")
    with open(map_file, "r") as f:
        map_data = orjson.loads(f.read())

    tasks = []
    for agent_trace in tqdm(agent_data):
        map_index = agent_trace["map_index"]
        map_seed = map_data[str(map_index)]["seed"]
        spawn_index = agent_trace["spawn_index"]
        positions = agent_trace["agent_visited"]

        current_map = create_map(map_seed)

        if len(positions) < 2:
            raise ValueError(f"Some of the paths are too short")
        agent = partial(ReplayAgent, positions[0], positions[-1], plan=positions)
        task = TaskSpec(seed=map_seed, position_index=spawn_index, map_index=map_index, game_map=current_map,
                        agent=agent)
        tasks.append(task)

    return tasks

def create_tasks():
    if config.CONFIG["seed"] is not None:
        seed = config.CONFIG["seed"]
    else:
        seed = random.randint(0, 99999)

    runtime_type = config.CONFIG["runtime_type"]
    if runtime_type == "Generate":
        tasks = _create_generate_tasks(seed)
    elif runtime_type == "Replay":
        tasks = _create_replay_tasks(seed)

    return tasks