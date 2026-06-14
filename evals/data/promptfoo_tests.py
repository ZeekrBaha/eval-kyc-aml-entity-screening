"""Load test cases from queries.json for Promptfoo."""

import json
from pathlib import Path


def load_tests() -> list[dict]:  # type: ignore[type-arg]
    """Return a list of test cases formatted for Promptfoo."""
    path = Path(__file__).parent / "queries.json"
    data = json.loads(path.read_text())

    tests = []
    for q in data:
        test = {
            "vars": {
                "query_name": q["query_name"],
                "dob": q.get("dob"),
                "country": q.get("country"),
                "kind": q["kind"],
                "expected_match_ids": q.get("expected_match_ids", []),
                "expected_risk": q.get("expected_risk", "NONE"),
            }
        }
        tests.append(test)
    return tests
