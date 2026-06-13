import json

from evaluator.providers.promptfoo_provider import call_api


def test_call_api_returns_screen_result_json(monkeypatch):
    monkeypatch.setenv("KYCEVAL_OFFLINE", "1")

    # Use a fake LLM via monkeypatch to avoid cache plumbing in the unit test.
    class FakeLLM:
        def complete(self, model, prompt):
            return json.dumps(
                {"matches": [], "risk": "NONE", "rationale": "no match", "cited_list_ids": []}
            )

    monkeypatch.setattr("evaluator.providers.promptfoo_provider.make_llm", lambda: FakeLLM())
    out = call_api("ignored", {"vars": {"query_name": "Nobody", "dob": None, "country": "US"}}, {})
    parsed = json.loads(out["output"])
    assert parsed["risk"] == "NONE"
