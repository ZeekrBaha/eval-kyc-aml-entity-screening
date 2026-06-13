from sut.models import ScreenResult


def citation_valid(result: ScreenResult, *, valid_ids: set[str]) -> bool:
    return all(cid in valid_ids for cid in result.cited_list_ids)
