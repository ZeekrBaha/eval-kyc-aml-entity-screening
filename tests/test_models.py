import pytest
from pydantic import ValidationError

from sut.models import Candidate, ListEntry, ScreenResult


def test_list_entry_requires_known_type():
    with pytest.raises(ValidationError):
        ListEntry(list_id="L1", name="Jane Doe", dob="1980-01-01", country="US", type="BOGUS")


def test_screen_result_round_trips_json():
    r = ScreenResult(
        matches=[Candidate(list_id="L1", matched_name="John Smith", score=91.0)],
        risk="HIGH",
        rationale="Strong name match to an OFAC entry.",
        cited_list_ids=["L1"],
    )
    again = ScreenResult.model_validate_json(r.model_dump_json())
    assert again.risk == "HIGH"
    assert again.matches[0].list_id == "L1"
