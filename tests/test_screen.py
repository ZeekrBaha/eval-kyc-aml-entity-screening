import json

from sut.models import ListEntry
from sut.screen import screen

LIST = [
    ListEntry(list_id="L1", name="John Smith", dob="1970-05-01", country="US", type="OFAC"),
    ListEntry(list_id="L2", name="Maria Garcia", dob="1985-03-22", country="ES", type="PEP"),
]


class FakeLLM:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def complete(self, model: str, prompt: str) -> str:
        return json.dumps(self._payload)


def test_screen_parses_and_keeps_valid_citation():
    llm = FakeLLM(
        {
            "matches": [{"list_id": "L1", "matched_name": "John Smith", "score": 92.0}],
            "risk": "HIGH",
            "rationale": "Exact name match to OFAC entry L1.",
            "cited_list_ids": ["L1"],
        }
    )
    result = screen("John Smith", "1970-05-01", "US", entries=LIST, llm=llm, model="gpt-4o")
    assert result.risk == "HIGH"
    assert result.cited_list_ids == ["L1"]


def test_screen_drops_hallucinated_citations_not_in_list():
    llm = FakeLLM(
        {
            "matches": [],
            "risk": "LOW",
            "rationale": "No credible match.",
            "cited_list_ids": ["L999"],  # not in LIST
        }
    )
    result = screen("Robert Johnson", None, "US", entries=LIST, llm=llm, model="gpt-4o")
    assert result.cited_list_ids == []  # invalid id stripped, fail-closed
