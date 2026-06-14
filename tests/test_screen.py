import json

from sut.models import ListEntry
from sut.screen import _strip_fences, screen

LIST = [
    ListEntry(list_id="L1", name="John Smith", dob="1970-05-01", country="US", type="OFAC"),
    ListEntry(list_id="L2", name="Maria Garcia", dob="1985-03-22", country="ES", type="PEP"),
]


class FakeLLM:
    def __init__(self, payload: dict) -> None:
        self._payload = payload

    def complete(self, model: str, prompt: str) -> str:
        return json.dumps(self._payload)


def test_strip_fences_removes_markdown_code_block():
    payload = '{"a": 1}'
    assert _strip_fences(f"```json\n{payload}\n```") == payload
    assert _strip_fences(f"```\n{payload}\n```") == payload
    assert _strip_fences(payload) == payload


def test_screen_parses_fenced_json():
    llm_payload = {
        "matches": [],
        "risk": "NONE",
        "rationale": "No match.",
        "cited_list_ids": [],
    }

    class FencedLLM:
        def complete(self, model: str, prompt: str) -> str:
            return f"```json\n{json.dumps(llm_payload)}\n```"

    result = screen("Alice Unknown", None, "US", entries=LIST, llm=FencedLLM(), model="gpt-4o")
    assert result.risk == "NONE"


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


def test_screen_preserves_hallucinated_citations_for_evaluator():
    llm = FakeLLM(
        {
            "matches": [],
            "risk": "LOW",
            "rationale": "No credible match.",
            "cited_list_ids": ["L999"],  # hallucinated — not in LIST
        }
    )
    result = screen("Robert Johnson", None, "US", entries=LIST, llm=llm, model="gpt-4o")
    # Raw model output is preserved so the evaluator (citation_valid) can catch it.
    assert result.cited_list_ids == ["L999"]
