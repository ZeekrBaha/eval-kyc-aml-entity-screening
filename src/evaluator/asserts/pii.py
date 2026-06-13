import re
from sut.models import ScreenResult

# Raw DOB (YYYY-MM-DD) or a 9-digit national-id-like run must not appear in free text.
_PII = re.compile(r"\b\d{4}-\d{2}-\d{2}\b|\b\d{9}\b")


def pii_masked(result: ScreenResult) -> bool:
    return _PII.search(result.rationale) is None
