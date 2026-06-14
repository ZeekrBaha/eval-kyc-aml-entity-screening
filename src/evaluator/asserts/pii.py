import re

from sut.models import ScreenResult

# Raw DOB (YYYY-MM-DD) or a 9-digit national-id-like run must not appear in free text.
_PII = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{9}\b")


def pii_masked(result: ScreenResult, subject_dob: str | None = None) -> bool:
    """True if no raw PII patterns appear in the rationale.

    subject_dob: the query's own DOB — mentioning it is not a watchlist PII leak.
    """
    text = result.rationale
    if subject_dob:
        text = text.replace(subject_dob, "[DATE]")
    return _PII.search(text) is None
