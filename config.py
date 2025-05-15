import sys

from pathlib import Path
from readtheyaml.exceptions.validation_error import ValidationError
from readtheyaml.schema import Schema

CONFIG = None

def load_config(config_path, schema):
    global CONFIG
    try:
        schema = Schema.from_yaml(schema, Path("./configs/schemas"))
        CONFIG = schema.validate_file(config_path)
    except ValidationError as e:
        print(f"❌ Validation failed: {e}", file=sys.stderr)
        sys.exit(1)

    return CONFIG

