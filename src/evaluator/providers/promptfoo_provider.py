"""Promptfoo custom provider bridging to the screen() SUT.
Promptfoo calls call_api(prompt, options, context) and expects {"output": ...}."""

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from sut.llm import make_llm
from sut.models import ListEntry
from sut.screen import screen


@lru_cache(maxsize=1)
def _entries() -> tuple[ListEntry, ...]:
    raw = json.loads(Path("evals/data/sanctions_list.json").read_text())
    return tuple(ListEntry.model_validate(e) for e in raw)


def call_api(prompt: str, options: dict[str, Any], context: dict[str, Any]) -> dict[str, Any]:
    # Promptfoo passes test case vars in context.
    v = context.get("vars", {})
    llm = make_llm()
    result = screen(
        v.get("query_name", ""),
        v.get("dob"),
        v.get("country"),
        entries=list(_entries()),
        llm=llm,
        model=options.get("config", {}).get("model", "gpt-4o"),
    )
    # Emit the structured ScreenResult as the output string for asserts to parse.
    return {"output": result.model_dump_json()}
