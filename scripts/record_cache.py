"""Run the live SUT across all queries to populate evals/cache/ for offline replay.
Requires OPENAI_API_KEY and KYCEVAL_OFFLINE=0."""
import json
import os
from pathlib import Path
from sut.llm import LiveLLM
from sut.models import ListEntry
from sut.screen import screen

assert os.environ.get("KYCEVAL_OFFLINE") == "0", "set KYCEVAL_OFFLINE=0 to record live"

entries = [ListEntry.model_validate(e)
           for e in json.loads(Path("evals/data/sanctions_list.json").read_text())]
queries = json.loads(Path("evals/data/queries.json").read_text())
llm = LiveLLM()
for q in queries:
    screen(q["query_name"], q["dob"], q["country"], entries=entries, llm=llm,
           model=os.environ.get("KYCEVAL_MODEL", "gpt-4o"))
print("cache files:", len(list(Path("evals/cache").glob("*.json"))))
