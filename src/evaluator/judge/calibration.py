from __future__ import annotations

import json
from pathlib import Path


def cohen_kappa(a: list[int], b: list[int]) -> float:
    """Cohen's kappa for two binary label sequences."""
    n = len(a)
    if n == 0:
        raise ValueError("empty label sequences")
    agree = sum(1 for x, y in zip(a, b, strict=False) if x == y) / n
    pa1 = sum(a) / n
    pb1 = sum(b) / n
    chance = pa1 * pb1 + (1 - pa1) * (1 - pb1)
    if chance == 1.0:
        return 1.0
    return (agree - chance) / (1 - chance)


def main() -> int:
    """Compute kappa from evals/data/calibration.json (human vs judge labels)."""
    path = Path("evals/data/calibration.json")
    data = json.loads(path.read_text())
    k = cohen_kappa(data["human"], data["judge"])
    print(
        f"[calibrate] cohen_kappa={k:.3f} n={len(data['human'])} "
        f"(single-annotator caveat: see docs)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
