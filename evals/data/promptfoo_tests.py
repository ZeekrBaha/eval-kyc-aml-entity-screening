"""Expand queries.json into promptfoo test rows (vars carry labels for asserts)."""

import json
from pathlib import Path


def load_tests(*args) -> list[dict]:
    cases = json.loads((Path(__file__).parent / "queries.json").read_text())
    return [{"vars": c} for c in cases]
