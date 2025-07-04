import json
import os
import yaml

from datetime import datetime

import config


def export_runtime_data(agent_traces, map_traces):
    name = config.CONFIG["experiment_name"]
    output_folder = config.CONFIG["output_folder"]

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = os.path.join(output_folder, name + "-" + timestamp)
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "agent_output.json"), "w") as f:
        json.dump(agent_traces, f, indent=4)

    with open(os.path.join(output_dir, "map_output.json"), "w") as f:
        json.dump(map_traces, f, indent=4)

    with open(os.path.join(output_dir, "used_config.yaml"), "w") as f:
        yaml.dump(config.CONFIG, f, default_flow_style=False, sort_keys=False)

def load_json_file(path):
    with open(path, "r") as f:
        return json.load(f)

# ---------- Agent output comparison ----------

def normalize_agent_entry(entry):
    return {
        "agent_type": entry["agent_type"],
        "spawn_index": entry["spawn_index"],
        "map_index": entry["map_index"],
        "agent_visited": entry["agent_visited"],  # order matters
        "agent_explored": sorted(entry["agent_explored"]),  # order doesn't matter
    }

def sort_agent_key(entry):
    return (entry["map_index"], entry["spawn_index"], entry["agent_type"])

def load_and_normalize_agents(path):
    data = load_json_file(path)
    normalized = [normalize_agent_entry(e) for e in data]
    return sorted(normalized, key=sort_agent_key)

def compare_agent_outputs(path1, path2):
    data1 = load_and_normalize_agents(path1)
    data2 = load_and_normalize_agents(path2)
    return data1 == data2

# ---------- Map output comparison ----------

def normalize_map_entry(index, entry):
    return {
        "map_index": int(index),
        "map_seed": entry["seed"],
        "grid": entry["grid"],
        "erosion": entry["erosion"],
        "agent_type": entry["agent_type"],
    }

def load_and_normalize_maps(path):
    data = load_json_file(path)
    normalized = [normalize_map_entry(k, v) for k, v in data.items()]
    return sorted(normalized, key=lambda x: x["map_index"])

def compare_map_outputs(path1, path2):
    data1 = load_and_normalize_maps(path1)
    data2 = load_and_normalize_maps(path2)
    return data1 == data2

# ---------- Final function comparing both folders ----------

def compare_experiment_folders(folder1, folder2):
    agent_equal = compare_agent_outputs(
        os.path.join(folder1, "agent_output.json"),
        os.path.join(folder2, "agent_output.json")
    )
    map_equal = compare_map_outputs(
        os.path.join(folder1, "map_output.json"),
        os.path.join(folder2, "map_output.json")
    )
    return agent_equal and map_equal