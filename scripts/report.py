"""Generate a structured release report from a promptfoo eval output.

Usage:
    PYTHONPATH=src python scripts/report.py [reports/latest.json]

Prints:
  - Per-kind metrics (true_match / decoy / abstain)
  - Confusion matrix
  - Worst failed cases
  - Gate metric summary
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def _load(path: str) -> list[dict]:  # type: ignore[type-arg]
    data = json.loads(Path(path).read_text())
    return list(data["results"]["results"])


def _kind_metrics(rows: list[dict]) -> dict[str, dict[str, float | int]]:  # type: ignore[type-arg]
    by_kind: dict[str, list[dict]] = {}  # type: ignore[type-arg]
    for r in rows:
        k = r["vars"]["kind"]
        by_kind.setdefault(k, []).append(r)

    result: dict[str, dict[str, float | int]] = {}
    for kind, rs in by_kind.items():
        comps_list = [
            {
                c.get("assertion", {}).get("metric"): c["pass"]
                for c in r.get("gradingResult", {}).get("componentResults", [])
            }
            for r in rs
        ]
        n = len(rs)
        result[kind] = {
            "n": n,
            "match_correct": sum(1 for c in comps_list if c.get("match_correct")) / n,
            "citation_valid": sum(1 for c in comps_list if c.get("citation_valid")) / n,
            "pii_masked": sum(1 for c in comps_list if c.get("pii_masked")) / n,
            "risk_tier_correct": sum(1 for c in comps_list if c.get("risk_tier_correct")) / n,
        }
    return result


def _worst_cases(rows: list[dict], n: int = 5) -> list[dict]:  # type: ignore[type-arg]
    failures = []
    for r in rows:
        comps = {
            c.get("assertion", {}).get("metric"): c
            for c in r.get("gradingResult", {}).get("componentResults", [])
        }
        failed_metrics = [
            f"{m}: {c.get('reason', '')}" for m, c in comps.items() if m and not c.get("pass")
        ]
        if failed_metrics:
            failures.append(
                {
                    "name": r["vars"].get("query_name"),
                    "kind": r["vars"]["kind"],
                    "provider": r.get("provider", {}).get("id", "?"),
                    "prompt": r.get("promptId", "?")[:20],
                    "failures": failed_metrics,
                }
            )
    return failures[:n]


def main(argv: list[str]) -> int:
    path = argv[1] if len(argv) > 1 else "reports/latest.json"
    if not Path(path).exists():
        print(f"[report] {path} not found — run `make eval` or `make eval-offline` first")
        return 1

    rows = _load(path)
    print(f"\n=== Release Report ({path}) — {len(rows)} rows ===\n")

    print("Per-kind metrics:")
    print(f"  {'kind':<14} {'n':>4}  {'match':>6}  {'cite':>6}  {'pii':>6}  {'risk':>6}")
    print("  " + "-" * 50)
    for kind, m in _kind_metrics(rows).items():
        print(
            f"  {kind:<14} {int(m['n']):>4}"
            f"  {m['match_correct']:>6.2%}"
            f"  {m['citation_valid']:>6.2%}"
            f"  {m['pii_masked']:>6.2%}"
            f"  {m['risk_tier_correct']:>6.2%}"
        )

    worst = _worst_cases(rows)
    if worst:
        print(f"\nWorst failed cases (top {len(worst)}):")
        for w in worst:
            print(f"  [{w['kind']}] {w['name']} | {w['provider']} | {w['prompt']}")
            for f in w["failures"]:
                print(f"    ✗ {f}")

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
