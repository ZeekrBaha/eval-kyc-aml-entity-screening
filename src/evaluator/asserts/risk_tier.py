from sut.models import ScreenResult


def risk_tier_correct(result: ScreenResult, *, expected_risk: str) -> bool:
    return result.risk == expected_risk
