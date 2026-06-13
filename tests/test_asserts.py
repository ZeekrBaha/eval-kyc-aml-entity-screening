from sut.models import Candidate, ScreenResult
from evaluator.asserts.match import match_correct
from evaluator.asserts.citation import citation_valid
from evaluator.asserts.pii import pii_masked
from evaluator.asserts.risk_tier import risk_tier_correct


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
