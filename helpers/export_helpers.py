import json
import os
import yaml

from datetime import datetime

import config


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
