import argparse
import json
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import os.path
import seaborn as sns

from config import load_config
from matplotlib.colors import ListedColormap, BoundaryNorm


def main(path, config):
    with open(os.path.join(path, "agent_output.json"), "r") as f:
        agent_data = json.load(f)

    with open(os.path.join(path, "map_output.json"), "r") as f:
        map_data = json.load(f)

    agent_type = "a_star" # TODO config
    map_id = "0" # TODO should be in config
    grid = np.array(map_data[map_id]["grid"])
    erosion = np.array(map_data[map_id]["erosion"])
    #y,x = grid.shape

    count_grid = np.zeros_like(grid)

    for agent_trace in agent_data:
        for x, y in agent_trace["agent_visited"]:
            count_grid[y][x] += 1

    # Plotting
    plt.figure(figsize=(10, 8))
    sns.heatmap(count_grid, cmap='magma', cbar_kws={'label': 'Visit Count'})
    plt.title(f'Heatmap of Positions Visited\nMap ID: {map_id} | Agent: {agent_type}')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.gca().invert_yaxis()  # Optional: to match the coordinate system
    plt.show()

    # Define your color map: index corresponds to value in `display`
    cmap = ListedColormap([
        'white',  # 0 - unvisited
        'lightblue',  # 1 - visited
        'black',  # 2 - obstacle
        'gray'  # 3 - erosion
    ])
    # Define boundaries between values: one more than the number of colors
    boundaries = [0, 1, 2, 3, 4]  # each value gets a bucket

    # Create a normalizer that maps values to colormap indices
    norm = BoundaryNorm(boundaries, ncolors=4)

    legend_elements = [
        mpatches.Patch(color='white', label='Unvisited'),
        mpatches.Patch(color='lightblue', label='Visited'),
        mpatches.Patch(color='black', label='Obstacle'),
        mpatches.Patch(color='gray', label='Eroded'),
    ]

    visit_mask = (count_grid > 0).astype(int)
    tata = (erosion.astype(int) - grid)
    display = visit_mask + grid * 2 + (erosion.astype(int) - grid) * 3

    # Plot
    plt.figure(figsize=(8, 8))
    plt.imshow(display, cmap=cmap, interpolation='none', norm=norm)
    plt.title("Map Overview: Obstacles, Visits, Erosion")
    plt.xticks([])
    plt.yticks([])
    plt.grid(False)
    plt.legend(handles=legend_elements, loc='upper right')
    plt.show()

    a = 0


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
