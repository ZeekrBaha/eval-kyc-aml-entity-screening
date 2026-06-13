import json
from dataclasses import dataclass

from sut.llm import LLM


@dataclass
class Verdict:
    faithful: bool
    reason: str


def judge_faithfulness(*, rationale: str, evidence_ids: list[str], llm: LLM, model: str) -> Verdict:
    prompt = (
        "You are auditing a KYC screening rationale for faithfulness.\n"
        "A rationale is FAITHFUL only if every watchlist id it references is in the evidence set.\n"
        f"Evidence ids: {evidence_ids}\n"
        f"Rationale: {rationale!r}\n"
        'Respond ONLY as JSON: {"faithful": bool, "reason": str}'
    )
    data = json.loads(llm.complete(model, prompt))
    return Verdict(faithful=bool(data["faithful"]), reason=str(data["reason"]))
