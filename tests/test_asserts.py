from unittest.mock import patch

from evaluator.asserts.citation import citation_valid
from evaluator.asserts.match import match_correct
from evaluator.asserts.pii import pii_masked
from evaluator.asserts.promptfoo_asserts import (
    citation_assert,
    match_assert,
    pii_assert,
    risk_assert,
)
from evaluator.asserts.risk_tier import risk_tier_correct
from sut.models import Candidate, ListEntry, ScreenResult


def _result(match_ids, risk="HIGH", rationale="ok", cited=None):
    return ScreenResult(
        matches=[Candidate(list_id=m, matched_name="X", score=90.0) for m in match_ids],
        risk=risk,
        rationale=rationale,
        cited_list_ids=cited if cited is not None else list(match_ids),
    )


def test_true_match_requires_expected_id_present():
    r = _result(["L1"])
    assert match_correct(r, expected_ids=["L1"], kind="true_match") is True
    assert match_correct(_result([]), expected_ids=["L1"], kind="true_match") is False


def test_decoy_must_have_no_matches():
    assert match_correct(_result([]), expected_ids=[], kind="decoy") is True
    assert match_correct(_result(["L1"]), expected_ids=[], kind="decoy") is False


def test_citation_valid_only_when_all_ids_known():
    assert citation_valid(_result(["L1"], cited=["L1"]), valid_ids={"L1", "L2"}) is True
    assert citation_valid(_result(["L1"], cited=["L9"]), valid_ids={"L1", "L2"}) is False


def test_pii_masked_flags_raw_dob_in_rationale():
    assert pii_masked(_result(["L1"], rationale="Refer to entry L1.")) is True
    assert pii_masked(_result(["L1"], rationale="DOB 1970-05-01 matches.")) is False


def test_risk_tier_correct_exact_match():
    assert risk_tier_correct(_result(["L1"], risk="HIGH"), expected_risk="HIGH") is True
    assert risk_tier_correct(_result(["L1"], risk="LOW"), expected_risk="HIGH") is False


def test_match_correct_abstain_escalates_on_medium_or_none():
    assert match_correct(_result([], risk="MEDIUM"), expected_ids=[], kind="abstain") is True
    assert match_correct(_result([], risk="NONE"), expected_ids=[], kind="abstain") is True
    assert match_correct(_result([], risk="HIGH"), expected_ids=[], kind="abstain") is False


# --- promptfoo assert wrappers ---

_ENTRY = ListEntry(list_id="L1", name="John Smith", dob="1970-01-01", country="US", type="OFAC")


def _pf_result(risk: str = "HIGH", cited: list[str] | None = None) -> ScreenResult:
    return ScreenResult(
        matches=[Candidate(list_id="L1", matched_name="John Smith", score=95.0)],
        risk=risk,
        rationale="Exact match to OFAC entry.",
        cited_list_ids=cited if cited is not None else ["L1"],
    )


def test_match_assert_true_match_hit():
    ctx = {"vars": {"kind": "true_match", "expected_match_ids": ["L1"]}}
    assert match_assert(_pf_result().model_dump_json(), ctx) is True


def test_match_assert_decoy_clean():
    r = ScreenResult(matches=[], risk="NONE", rationale="no match", cited_list_ids=[])
    ctx = {"vars": {"kind": "decoy", "expected_match_ids": []}}
    assert match_assert(r.model_dump_json(), ctx) is True


def test_citation_assert_valid():
    with patch("evaluator.asserts.promptfoo_asserts._entries", return_value=(_ENTRY,)):
        assert citation_assert(_pf_result(cited=["L1"]).model_dump_json(), {}) is True


def test_citation_assert_hallucinated_id_fails():
    with patch("evaluator.asserts.promptfoo_asserts._entries", return_value=(_ENTRY,)):
        assert citation_assert(_pf_result(cited=["L999"]).model_dump_json(), {}) is False


def test_pii_assert_clean_rationale():
    assert pii_assert(_pf_result().model_dump_json(), {}) is True


def test_risk_assert_correct_tier():
    ctx = {"vars": {"expected_risk": "HIGH"}}
    assert risk_assert(_pf_result().model_dump_json(), ctx) is True
