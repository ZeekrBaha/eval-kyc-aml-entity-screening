import json
from pathlib import Path

from sut.models import ListEntry

DATA = Path("evals/data")


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
