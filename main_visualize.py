import argparse
import json
import numpy as np
import os.path

from config import load_config

from visualizer.visualizer_helpers import display_heat_map, get_count_per_cell, display_visited_cells


def main(path, config):
    with open(os.path.join(path, "agent_output.json"), "r") as f:
        agent_data = json.load(f)

    with open(os.path.join(path, "map_output.json"), "r") as f:
        map_data = json.load(f)

    agent_type = config["agent_type"]
    map_id = config["map_id"]
    grid = np.array(map_data[map_id]["grid"])
    erosion = np.array(map_data[map_id]["erosion"])

    count_grid = get_count_per_cell(grid, agent_data)

    display_heat_map(count_grid, map_id, agent_type)
    display_visited_cells(count_grid, erosion, grid)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configuration to visualize recorded games.")
    parser.add_argument("--path", type=str, help="Path to the recorded game data.")
    parser.add_argument("--config", type=str, default="configs/visualize_config.yaml",
                        help="Config file to determine the experimentation to run")
    parser.add_argument("--schema", type=str, default="configs/schemas/visualize_schema.yaml",
                        help="Schema file to validate the config")

    args = parser.parse_args()

    config = load_config(args.config, args.schema)
    path = "outputs/single_map_config-2025-05-16_06-50-17" # TODO just temp

    main(path, config)
