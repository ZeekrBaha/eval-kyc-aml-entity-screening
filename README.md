# KYC/AML Entity Screening — Evaluation Framework

A portfolio-grade **AI QA / evaluation framework** that decides whether a
KYC/AML entity-screening assistant is good enough — and robust enough — to ship.

> I did not just build a screening bot. I built the evaluation and red-team
> infrastructure that decides whether a regulated-domain screening assistant is
> safe to release.

Designed case study; **synthetic, fictional data only** — no real persons.

## Two-repo story
- `eval-financial-risk-research-assistant` (DeepEval): *is this RAG assistant safe to ship?*
- **this repo** (Promptfoo): *which prompt/model screens best, and can it be broken?*

I pick the right eval tool for the question.

## Mental model: SUT vs evaluator
`screen(name, dob, country)` is the **System Under Test** — a fuzzy matcher + an
OpenAI judgment. The **evaluator** (Promptfoo matrix + Python asserts + release
gate + red-team) never reaches inside it.

## Quickstart (no API key)

```bash
uv sync
npm install           # installs pinned Promptfoo (Node >=22.22.0 required)
make test             # 49 unit tests
make cov              # coverage gate (≥90%)
make calibrate        # Cohen's kappa for rationale judge
```

## Offline eval (CI path — no API key)

`make eval-offline` replays Promptfoo's response cache and runs the release gate
against a committed red-team fixture (10/10 attacks blocked).

```bash
make eval-offline     # exits 0 when all thresholds met
```

> **Cache status:** the live Promptfoo cache (`evals/cache/`) is populated by
> running `make eval` with an API key. Until a live run is recorded, `make
> eval-offline` will exit non-zero at the Promptfoo step (no cache files).
> The gate logic itself is fully exercised by `make test`.

## Live run (needs OPENAI_API_KEY)

```bash
export OPENAI_API_KEY=...
KYCEVAL_OFFLINE=0 uv run python scripts/record_cache.py   # record once
make eval           # live matrix + gate
make redteam        # adversarial scans (output → reports/redteam.json)
```

## Headline numbers
150 list entries · 50 golden cases · 6 gate metrics · 49 tests · 95% coverage ·
judge κ documented in calibration report · CI gate green (unit + lint + coverage).

## Release gate
Recall ≥ 0.95 (a missed sanctions hit is the worst error), FP ≤ 0.10,
citation validity = 1.0, PII masking = 1.0, injection resistance ≥ 0.90.
Regression vs baseline fails the gate closed; a metric that did not run is
reported `incomplete` (exit 2), never faked green. Injection resistance requires
a real red-team run (`make redteam`) — without it the gate exits 2.

## Verified commands (2026-06-13)

| Command | Result |
|---------|--------|
| `uv run pytest` | 49 passed |
| `uv run ruff check .` | passed |
| `uv run mypy` | passed |
| `uv run pytest --cov=src --cov-fail-under=90` | 95% — passed |
| `make calibrate` | cohen_kappa printed, exit 0 |
| `make eval-offline` | requires live cache (see note above) |
