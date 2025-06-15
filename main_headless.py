import argparse
import time

from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

from config import load_config
from game import Game
from helpers.export_helpers import export_runtime_data
from helpers.task_helpers import create_tasks


def run_task(task, fps):
    game = Game(task)
    interval = 1.0 / fps
    start_time = time.time()

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

    export_runtime_data(agent_traces, map_traces)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run experiments in headless mode without GUI.")
    parser.add_argument("--config", type=str, default="configs/simple_config.yaml", help="YAML config path")
    parser.add_argument("--schema", type=str, default="configs/schemas/project_schema.yaml", help="YAML schema path")
    parser.add_argument("--workers", type=int, default=8, help="Number of parallel workers")

    args = parser.parse_args()
    project_config = load_config(args.config, args.schema)

    run_experiments_parallel(project_config, max_workers=args.workers)
