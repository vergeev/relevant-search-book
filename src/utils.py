import json
from pathlib import Path
from typing import Any


def read_json(json_path: Path) -> Any:
    with open(json_path) as json_file:
        return json.load(json_file)
