import importlib.util
import json
from pathlib import Path
from typing import Any

from sut.models import ListEntry

DATA = Path("evals/data")


def _load_tests() -> list[dict[str, Any]]:
    """Import the Promptfoo test loader by path and return its test cases."""
    spec = importlib.util.spec_from_file_location("promptfoo_tests", DATA / "promptfoo_tests.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return list(module.load_tests())


def test_sanctions_list_parses_and_has_unique_ids():
    raw = json.loads((DATA / "sanctions_list.json").read_text())
    entries = [ListEntry.model_validate(e) for e in raw]
    assert len(entries) >= 160
    ids = [e.list_id for e in entries]
    assert len(ids) == len(set(ids))


def test_queries_cover_all_three_kinds():
    cases = json.loads((DATA / "queries.json").read_text())
    kinds = {c["kind"] for c in cases}
    assert {"true_match", "decoy", "abstain"}.issubset(kinds)


def test_queries_have_enough_hard_true_match_cases():
    cases = json.loads((DATA / "queries.json").read_text())
    true_matches = [c for c in cases if c["kind"] == "true_match"]
    assert len(true_matches) >= 14  # 3 original + 11 hard cases


def test_true_match_cases_reference_real_list_ids():
    entries = {e["list_id"] for e in json.loads((DATA / "sanctions_list.json").read_text())}
    cases = json.loads((DATA / "queries.json").read_text())
    for c in cases:
        if c["kind"] == "true_match":
            assert set(c["expected_match_ids"]).issubset(entries)


def test_loader_produces_one_test_per_query():
    queries = json.loads((DATA / "queries.json").read_text())
    tests = _load_tests()
    assert len(tests) == len(queries)


def test_loader_test_cases_match_promptfoo_schema():
    """Every test case must have a non-empty `vars` dict with required keys."""
    for t in _load_tests():
        assert "vars" in t
        v = t["vars"]
        assert v  # non-empty
        assert "query_name" in v
        assert v["kind"] in {"true_match", "decoy", "abstain"}
        assert isinstance(v["expected_match_ids"], list)
        assert v["expected_risk"] in {"HIGH", "MEDIUM", "LOW", "NONE"}


def test_loader_omits_null_vars():
    """Null dob/country must be omitted, not passed as None (avoids schema warnings)."""
    for t in _load_tests():
        for value in t["vars"].values():
            assert value is not None
