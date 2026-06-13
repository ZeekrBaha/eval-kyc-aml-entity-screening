from sut.matcher import match_name
from sut.models import ListEntry

LIST = [
    ListEntry(list_id="L1", name="John Smith", dob="1970-05-01", country="US", type="OFAC"),
    ListEntry(list_id="L2", name="Muhammad Ali", dob="1942-01-17", country="US", type="PEP"),
    ListEntry(list_id="L3", name="Maria Garcia", dob="1985-03-22", country="ES", type="PEP"),
]


def test_exact_name_is_top_candidate():
    cands = match_name("John Smith", LIST)
    assert cands[0].list_id == "L1"
    assert cands[0].score >= 95.0


def test_transliteration_variant_matches():
    # "Mohammed" must resolve to sanctioned "Muhammad"
    cands = match_name("Mohammed Ali", LIST, threshold=70.0)
    assert any(c.list_id == "L2" for c in cands)


def test_common_name_decoy_below_threshold_is_excluded():
    # An unrelated common name should not surface high-score matches
    cands = match_name("Robert Johnson", LIST, threshold=80.0)
    assert cands == []


def test_results_sorted_descending_by_score():
    cands = match_name("Maria Garcia", LIST, threshold=10.0)
    scores = [c.score for c in cands]
    assert scores == sorted(scores, reverse=True)
