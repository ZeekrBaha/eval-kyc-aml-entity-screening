"""Thin promptfoo assert wrappers over the pure assert functions."""

from typing import Any

from evaluator.asserts.citation import citation_valid
from evaluator.asserts.match import match_correct
from evaluator.asserts.pii import pii_masked
from evaluator.asserts.risk_tier import risk_tier_correct
from evaluator.providers.promptfoo_provider import _entries
from sut.models import ScreenResult


def _parse(output: str) -> ScreenResult:
    return ScreenResult.model_validate_json(output)


def match_assert(output: str, context: dict[str, Any]) -> bool:
    v = context["vars"]
    return match_correct(
        _parse(output), expected_ids=v.get("expected_match_ids", []), kind=v["kind"]
    )


def citation_assert(output: str, context: dict[str, Any]) -> bool:
    valid = {e.list_id for e in _entries()}
    return citation_valid(_parse(output), valid_ids=valid)


def pii_assert(output: str, context: dict[str, Any]) -> bool:
    return pii_masked(_parse(output))


def risk_assert(output: str, context: dict[str, Any]) -> bool:
    return risk_tier_correct(_parse(output), expected_risk=context["vars"]["expected_risk"])
