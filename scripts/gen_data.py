"""Generate synthetic, fictional KYC datasets. No real persons. Deterministic."""
import json
from pathlib import Path

OUT = Path("evals/data")
OUT.mkdir(parents=True, exist_ok=True)

# Seed entries with planted hard cases. Extend to ~150 with the filler loop below.
BASE = [
    {"list_id": "L001", "name": "John Smith", "dob": "1970-05-01", "country": "US", "type": "OFAC"},
    {"list_id": "L002", "name": "Muhammad Ali Hassan", "dob": "1965-09-12", "country": "EG", "type": "PEP"},
    {"list_id": "L003", "name": "Maria Garcia", "dob": "1985-03-22", "country": "ES", "type": "PEP"},
    {"list_id": "L004", "name": "Olena Kovalenko", "dob": "1978-11-03", "country": "UA", "type": "ADVERSE_MEDIA"},
    {"list_id": "L005", "name": "Wei Chen", "dob": "1982-07-19", "country": "CN", "type": "OFAC"},
]
FILLER_NAMES = [
    "Aisha Rahman", "Carlos Mendoza", "Ingrid Larsson", "Tunde Adeyemi", "Sofia Rossi",
    "Dmitri Volkov", "Fatima Zahra", "Liam O'Brien", "Yuki Tanaka", "Pavel Novak",
]
entries = list(BASE)
i = 6
while len(entries) < 150:
    nm = FILLER_NAMES[(i - 6) % len(FILLER_NAMES)]
    entries.append({
        "list_id": f"L{i:03d}", "name": f"{nm} {i}",
        "dob": f"19{50 + i % 40:02d}-0{i % 9 + 1}-1{i % 9}",
        "country": ["US", "GB", "DE", "IN", "BR"][i % 5],
        "type": ["OFAC", "PEP", "ADVERSE_MEDIA"][i % 3],
    })
    i += 1
(OUT / "sanctions_list.json").write_text(json.dumps(entries, indent=2))

queries = [
    # true matches (incl. transliteration / reorder / typo)
    {"query_name": "John Smith", "dob": "1970-05-01", "country": "US",
     "kind": "true_match", "expected_match_ids": ["L001"], "expected_risk": "HIGH"},
    {"query_name": "Mohammed Ali Hassan", "dob": "1965-09-12", "country": "EG",
     "kind": "true_match", "expected_match_ids": ["L002"], "expected_risk": "HIGH"},
    {"query_name": "Garcia, Maria", "dob": "1985-03-22", "country": "ES",
     "kind": "true_match", "expected_match_ids": ["L003"], "expected_risk": "HIGH"},
    # decoys (common names that must NOT match)
    {"query_name": "Robert Johnson", "dob": "1990-02-02", "country": "US",
     "kind": "decoy", "expected_match_ids": [], "expected_risk": "NONE"},
    {"query_name": "Jane Williams", "dob": "1995-06-06", "country": "GB",
     "kind": "decoy", "expected_match_ids": [], "expected_risk": "NONE"},
    # abstain (insufficient data)
    {"query_name": "M. Garcia", "dob": None, "country": None,
     "kind": "abstain", "expected_match_ids": [], "expected_risk": "MEDIUM"},
]
# Pad to >=50 cases by templating more decoys from filler names.
j = 0
while len(queries) < 50:
    nm = FILLER_NAMES[j % len(FILLER_NAMES)]
    queries.append({
        "query_name": f"{nm} Decoy{j}", "dob": "2000-01-01", "country": "US",
        "kind": "decoy", "expected_match_ids": [], "expected_risk": "NONE",
    })
    j += 1
(OUT / "queries.json").write_text(json.dumps(queries, indent=2))

# Hand-labeled calibration set (human vs judge) for kappa. Single-annotator caveat documented.
(OUT / "calibration.json").write_text(json.dumps({
    "human": [1, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1],
    "judge": [1, 0, 1, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1],
}, indent=2))
print("generated:", [p.name for p in OUT.glob("*.json")])
