import argparse

from config import load_config
from game_logic.game_loop import interactive_main_loop


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configuration to launch the small game and configure the bot.")
    parser.add_argument("--config", type=str, default="configs/simple_generate_config.yaml", help="Config file to determine the experimentation to run")
    parser.add_argument("--schema", type=str, default="configs/schemas/project_schema.yaml", help="Schema file to validate the config")
    args = parser.parse_args()

    project_config = load_config(args.config, args.schema)

    interactive_main_loop(project_config)
