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
make eval-offline   # replays committed cache, runs the release gate
make test           # unit suite
```

## Live run
```bash
export OPENAI_API_KEY=...
KYCEVAL_OFFLINE=0 uv run python scripts/record_cache.py   # record once
make eval           # live matrix + gate
make redteam        # adversarial scans
```

## Headline numbers
150 list entries · 50 golden cases · 6 gate metrics · 31 tests · judge κ documented
in calibration report · CI gate green (offline replay, no API key).

## Release gate
Recall ≥ 0.95 (a missed sanctions hit is the worst error), FP ≤ 0.10,
citation validity = 1.0, PII masking = 1.0, injection resistance ≥ 0.90.
Regression vs baseline fails the gate closed; a metric that did not run is
reported `incomplete` (exit 2), never faked green.
