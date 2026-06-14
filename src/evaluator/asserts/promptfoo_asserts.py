"""Thin promptfoo assert wrappers over the pure assert functions.

Returns {pass, score, reason} dicts so Promptfoo surfaces failure reasons
in its HTML report without requiring a separate log parse.
"""

from typing import Any

from evaluator.asserts.citation import citation_valid
from evaluator.asserts.match import match_correct
from evaluator.asserts.pii import pii_masked
from evaluator.asserts.risk_tier import risk_tier_correct
from evaluator.providers.promptfoo_provider import _entries
from sut.models import ScreenResult


def _parse(output: str) -> ScreenResult:
    return ScreenResult.model_validate_json(output)


def _to_id_list(v: object) -> list[str]:
    """Promptfoo coerces single-element lists to scalars; normalize back to list."""
    if isinstance(v, str):
        return [v] if v else []
    if isinstance(v, list):
        return v
    return []


def match_assert(output: str, context: dict[str, Any]) -> dict[str, Any]:
    v = context["vars"]
    result = _parse(output)
    found = sorted(m.list_id for m in result.matches)
    expected_ids = _to_id_list(v.get("expected_match_ids", []))
    ok = match_correct(result, expected_ids=expected_ids, kind=v["kind"])
    if ok:
        return {"pass": True, "score": 1.0, "reason": f"correct ({v['kind']}): found={found}"}
    return {
        "pass": False,
        "score": 0.0,
        "reason": f"wrong match ({v['kind']}): expected={expected_ids} got={found}",
    }


def citation_assert(output: str, context: dict[str, Any]) -> dict[str, Any]:
    result = _parse(output)
    valid = {e.list_id for e in _entries()}
    bad = [cid for cid in result.cited_list_ids if cid not in valid]
    ok = citation_valid(result, valid_ids=valid)
    if ok:
        return {"pass": True, "score": 1.0, "reason": "all citations valid"}
    return {"pass": False, "score": 0.0, "reason": f"hallucinated ids: {bad}"}


def pii_assert(output: str, context: dict[str, Any]) -> dict[str, Any]:
    result = _parse(output)
    ok = pii_masked(result)
    if ok:
        return {"pass": True, "score": 1.0, "reason": "no raw PII in rationale"}
    return {"pass": False, "score": 0.0, "reason": "raw PII pattern found in rationale"}


def risk_assert(output: str, context: dict[str, Any]) -> dict[str, Any]:
    result = _parse(output)
    expected = context["vars"]["expected_risk"]
    ok = risk_tier_correct(result, expected_risk=expected)
    if ok:
        return {"pass": True, "score": 1.0, "reason": f"risk={result.risk} matches expected"}
    return {
        "pass": False,
        "score": 0.0,
        "reason": f"risk={result.risk} expected={expected}",
    }
