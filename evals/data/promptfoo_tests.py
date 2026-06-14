"""Load test cases from queries.json for Promptfoo.

Promptfoo validates each test case's `vars`. Null-valued vars (e.g. a query
with no DOB) trip schema warnings, so we omit keys whose value is None. The
provider and asserts read these via `.get(...)`, so absence is equivalent to
null without the warning.
"""

import json
from pathlib import Path
from typing import Any


def load_tests() -> list[dict[str, Any]]:
    """Return a list of test cases formatted for Promptfoo."""
    path = Path(__file__).parent / "queries.json"
    data = json.loads(path.read_text())

    tests: list[dict[str, Any]] = []
    for q in data:
        vars_: dict[str, Any] = {
            "query_name": q["query_name"],
            "kind": q["kind"],
            "expected_match_ids": q.get("expected_match_ids", []),
            "expected_risk": q.get("expected_risk", "NONE"),
        }
        # Only include optional identifiers when present (avoid null-var warnings).
        if q.get("dob") is not None:
            vars_["dob"] = q["dob"]
        if q.get("country") is not None:
            vars_["country"] = q["country"]
        tests.append({"vars": vars_})
    return tests
