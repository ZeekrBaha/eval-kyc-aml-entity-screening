import json

from sut.models import Candidate, ListEntry


def build_prompt(
    name: str,
    dob: str | None,
    country: str | None,
    candidates: list[Candidate],
    entries: list[ListEntry],
) -> str:
    by_id = {e.list_id: e for e in entries}
    shortlist = [
        {
            "list_id": c.list_id,
            "name": c.matched_name,
            "type": by_id[c.list_id].type,
            "dob": by_id[c.list_id].dob,
            "country": by_id[c.list_id].country,
            "fuzzy_score": round(c.score, 1),
        }
        for c in candidates
    ]
    return (
        "You are a KYC/AML screening assistant. Decide whether the subject matches "
        "any entry on the provided watchlist shortlist.\n"
        "Rules:\n"
        "- Only cite list_ids that appear in the shortlist below.\n"
        "- Never reveal a full date of birth or national id in your rationale;"
        " refer to entries by list_id.\n"
        "- If evidence is insufficient, set risk to MEDIUM and recommend"
        " escalation rather than guessing.\n"
        f"Subject: name={name!r} dob={dob!r} country={country!r}\n"
        f"Shortlist: {json.dumps(shortlist)}\n"
        'Respond ONLY with raw JSON (no markdown, no code fences): '
        '{"matches":[{"list_id","matched_name","score"}],'
        '"risk":"HIGH|MEDIUM|LOW|NONE","rationale":str,"cited_list_ids":[str]}'
    )
