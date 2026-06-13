from rapidfuzz import fuzz
from sut.models import Candidate, ListEntry


def _score(query: str, name: str) -> float:
    # Token-sort handles word reordering; WRatio handles
    # spelling/transliteration drift. Take the stronger of the two signals.
    return max(
        fuzz.token_sort_ratio(query, name),
        fuzz.WRatio(query, name),
    )


def match_name(query: str, entries: list[ListEntry], threshold: float = 80.0) -> list[Candidate]:
    """Return candidate matches scored 0-100, sorted best-first, score >= threshold."""
    candidates = [
        Candidate(list_id=e.list_id, matched_name=e.name, score=_score(query, e.name))
        for e in entries
    ]
    kept = [c for c in candidates if c.score >= threshold]
    return sorted(kept, key=lambda c: c.score, reverse=True)
