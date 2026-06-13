from typing import Literal
from pydantic import BaseModel

ListType = Literal["OFAC", "PEP", "ADVERSE_MEDIA"]
Risk = Literal["HIGH", "MEDIUM", "LOW", "NONE"]


class ListEntry(BaseModel):
    list_id: str
    name: str
    dob: str | None = None
    country: str | None = None
    type: ListType


class Candidate(BaseModel):
    list_id: str
    matched_name: str
    score: float


class ScreenResult(BaseModel):
    matches: list[Candidate]
    risk: Risk
    rationale: str
    cited_list_ids: list[str]
