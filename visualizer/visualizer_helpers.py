import argparse
import json
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import os.path
import seaborn as sns

from config import load_config
from matplotlib.colors import ListedColormap, BoundaryNorm


def get_count_per_cell(grid, agent_data):
    count_grid = np.zeros_like(grid)

    for agent_trace in agent_data:
        for x, y in agent_trace["agent_visited"]:
            count_grid[y][x] += 1
    return count_grid

def display_heat_map(count_grid, map_id, agent_type):
    plt.figure(figsize=(10, 8))
    sns.heatmap(count_grid, cmap='magma', cbar_kws={'label': 'Visit Count'})
    plt.title(f'Heatmap of Positions Visited\nMap ID: {map_id} | Agent: {agent_type}')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.gca().invert_yaxis()  # Optional: to match the coordinate system
    plt.show()

def display_visited_cells(count_grid, erosion, grid):
    cmap = ListedColormap([
        'white',  # 0 - unvisited
        'lightblue',  # 1 - visited
        'black',  # 2 - obstacle
        'gray'  # 3 - erosion
    ])
    boundaries = [0, 1, 2, 3, 4]  # each value gets a bucket

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