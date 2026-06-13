import json
from evaluator.judge.faithfulness import judge_faithfulness


class FakeLLM:
    def __init__(self, verdict): self.verdict = verdict
    def complete(self, model, prompt): return json.dumps(self.verdict)


def test_judge_returns_pass_when_rationale_grounded():
    llm = FakeLLM({"faithful": True, "reason": "rationale only cites L1 which is in evidence"})
    v = judge_faithfulness(rationale="Match to L1.", evidence_ids=["L1"], llm=llm, model="gpt-4o")
    assert v.faithful is True


def test_judge_returns_fail_on_ungrounded_claim():
    llm = FakeLLM({"faithful": False, "reason": "cites L9 not in evidence"})
    v = judge_faithfulness(rationale="Match to L9.", evidence_ids=["L1"], llm=llm, model="gpt-4o")
    assert v.faithful is False
