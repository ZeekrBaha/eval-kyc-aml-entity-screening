import json

from sut.llm import LLM
from sut.matcher import match_name
from sut.models import ListEntry, ScreenResult
from sut.prompt import build_prompt


def screen(
    name: str,
    dob: str | None,
    country: str | None,
    *,
    entries: list[ListEntry],
    llm: LLM,
    model: str = "gpt-4o",
) -> ScreenResult:
    candidates = match_name(name, entries)
    prompt = build_prompt(name, dob, country, candidates, entries)
    raw = llm.complete(model, prompt)
    result = ScreenResult.model_validate(json.loads(raw))
    # Fail-closed citation validation: strip any id not present in the list.
    valid_ids = {e.list_id for e in entries}
    result.cited_list_ids = [cid for cid in result.cited_list_ids if cid in valid_ids]
    return result
