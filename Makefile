.PHONY: test cov check fmt eval eval-offline redteam calibrate debrand

test:
	uv run pytest

cov:
	uv run pytest --cov=src --cov-report=term-missing --cov-fail-under=90

check:
	uv run ruff check .
	uv run ruff format --check .
	uv run mypy

fmt:
	uv run ruff format .
	uv run ruff check --fix .

# Live matrix run — needs OPENAI_API_KEY. Records responses into evals/cache/.
eval:
	KYCEVAL_OFFLINE=0 npx promptfoo@latest eval -c evals/promptfooconfig.yaml -o reports/latest.json
	uv run python -m evaluator.gate reports/latest.json

# Deterministic replay from committed cache — no API key. CI uses this.
eval-offline:
	KYCEVAL_OFFLINE=1 npx promptfoo@latest eval -c evals/promptfooconfig.yaml -o reports/latest.json
	uv run python -m evaluator.gate reports/latest.json

redteam:
	KYCEVAL_OFFLINE=0 npx promptfoo@latest redteam run -c evals/redteam.yaml -o reports/redteam.json

calibrate:
	uv run python -m evaluator.judge.calibration

debrand:
	@! grep -rniEf .debrand-banned.txt . \
		--exclude-dir=.git --exclude-dir=.venv --exclude-dir=node_modules --exclude-dir=reports \
		--exclude=.debrand-banned.txt \
		&& echo "debrand gate: clean"
