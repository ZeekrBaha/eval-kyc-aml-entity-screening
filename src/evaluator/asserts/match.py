from sut.models import ScreenResult


def match_correct(result: ScreenResult, *, expected_ids: list[str], kind: str) -> bool:
    found = {m.list_id for m in result.matches}
    if kind == "decoy":
        return len(found) == 0
    if kind == "abstain":
        return result.risk in {"MEDIUM", "NONE"}
    # true_match: every expected id must be surfaced
    return set(expected_ids).issubset(found)
