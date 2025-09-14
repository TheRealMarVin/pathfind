import argparse

from config import load_config
from game_logic.game_loop import run_experiments_parallel


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run experiments in headless mode without GUI.")
    parser.add_argument("--config", type=str, default="configs/simple_generate_config.yaml", help="YAML config path")
    parser.add_argument("--schema", type=str, default="configs/schemas/project_schema.yaml", help="YAML schema path")
    parser.add_argument("--workers", type=int, default=8, help="Number of parallel workers")

    args = parser.parse_args()
    project_config = load_config(args.config, args.schema)

    run_experiments_parallel(project_config, max_workers=args.workers)
