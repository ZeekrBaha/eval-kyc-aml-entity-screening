.PHONY: test cov check fmt eval eval-offline redteam calibrate report debrand

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
	PYTHONPATH=src KYCEVAL_OFFLINE=0 npx promptfoo eval -c evals/promptfooconfig.yaml -o reports/latest.json
	PYTHONPATH=src uv run python -m evaluator.gate reports/latest.json

# Deterministic replay from committed cache — no API key. CI uses this.
# Passes the committed redteam fixture so injection_resistance is populated.
eval-offline:
	PYTHONPATH=src KYCEVAL_OFFLINE=1 npx promptfoo eval -c evals/promptfooconfig.yaml -o reports/latest.json
	PYTHONPATH=src uv run python -m evaluator.gate reports/latest.json evals/data/redteam_fixture.json

redteam:
	PYTHONPATH=src KYCEVAL_OFFLINE=0 npx promptfoo redteam run -c evals/redteam.yaml -o reports/redteam.json

calibrate:
	PYTHONPATH=src uv run python -m evaluator.judge.calibration

report:
	PYTHONPATH=src uv run python scripts/report.py reports/latest.json

debrand:
	@! grep -rniEf .debrand-banned.txt . \
		--exclude-dir=.git --exclude-dir=.venv --exclude-dir=node_modules \
		--exclude-dir=reports --exclude-dir=docs \
		--exclude=.debrand-banned.txt \
		&& echo "debrand gate: clean"
