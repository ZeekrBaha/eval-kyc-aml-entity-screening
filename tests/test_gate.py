import json

import pytest

from evaluator.gate import (
    DEFAULT_THRESHOLDS,
    RowOutcome,
    _injection_from_redteam,
    _load_baseline,
    _rows_from_promptfoo,
    aggregate,
    evaluate_gate,
    main,
)

PROMPTFOO_REPORT = {
    "results": {
        "results": [
            {
                "vars": {"kind": "true_match"},
                "gradingResult": {
                    "componentResults": [
                        {"assertion": {"metric": "match_correct"}, "pass": True},
                        {"assertion": {"metric": "citation_valid"}, "pass": True},
                        {"assertion": {"metric": "pii_masked"}, "pass": True},
                        {"assertion": {"metric": "risk_tier_correct"}, "pass": True},
                    ]
                },
            }
        ]
    }
}


def _rows():
    return [
        RowOutcome(kind="true_match", matched=True, citation_ok=True, pii_ok=True, risk_ok=True),
        RowOutcome(kind="true_match", matched=False, citation_ok=True, pii_ok=True, risk_ok=False),
        RowOutcome(kind="decoy", matched=False, citation_ok=True, pii_ok=True, risk_ok=True),
        RowOutcome(kind="decoy", matched=True, citation_ok=True, pii_ok=True, risk_ok=True),
    ]


def test_aggregate_computes_recall_and_fp_rate():
    sc = aggregate(_rows())
    assert sc.recall == 0.5
    assert sc.false_positive_rate == 0.5
    assert sc.citation_validity == 1.0
    assert sc.pii_masking == 1.0


def test_aggregate_injection_resistance_is_none_by_default():
    sc = aggregate(_rows())
    assert sc.injection_resistance is None


def test_gate_fails_when_recall_below_threshold():
    sc = aggregate(_rows())
    sc.injection_resistance = 1.0  # simulate redteam ran and passed
    res = evaluate_gate(sc, DEFAULT_THRESHOLDS, baseline=None)
    assert res.exit_code == 1
    assert any("recall" in r for r in res.reasons)


def test_gate_passes_clean_run():
    rows = [
        RowOutcome(kind="true_match", matched=True, citation_ok=True, pii_ok=True, risk_ok=True)
    ]
    sc = aggregate(rows)
    sc.injection_resistance = 1.0  # simulate redteam ran and passed
    res = evaluate_gate(sc, DEFAULT_THRESHOLDS, baseline=None)
    assert res.exit_code == 0
    assert res.verdict == "ok"


def test_gate_fails_closed_on_missing_metric():
    sc = aggregate(
        [RowOutcome(kind="true_match", matched=True, citation_ok=True, pii_ok=True, risk_ok=True)]
    )
    # injection_resistance is None by default — no red-team run happened
    res = evaluate_gate(sc, DEFAULT_THRESHOLDS, baseline=None)
    assert res.exit_code == 2
    assert res.verdict == "incomplete"


def test_gate_flags_regression_against_baseline():
    sc = aggregate(
        [
            RowOutcome(
                kind="true_match", matched=True, citation_ok=True, pii_ok=True, risk_ok=True
            ),
            RowOutcome(
                kind="true_match", matched=False, citation_ok=True, pii_ok=True, risk_ok=True
            ),
        ]
    )  # recall 0.5
    sc.injection_resistance = 1.0  # simulate redteam ran and passed
    baseline = {"recall": 0.95}
    res = evaluate_gate(sc, DEFAULT_THRESHOLDS, baseline=baseline)
    assert res.exit_code == 1
    assert any("regress" in r.lower() for r in res.reasons)


def test_rows_from_promptfoo_parses_report(tmp_path):
    p = tmp_path / "report.json"
    p.write_text(json.dumps(PROMPTFOO_REPORT))
    rows = _rows_from_promptfoo(str(p))
    assert len(rows) == 1
    assert rows[0].kind == "true_match"
    assert rows[0].matched is True
    assert rows[0].citation_ok is True
    assert rows[0].pii_ok is True
    assert rows[0].risk_ok is True


def test_rows_from_promptfoo_decoy_assertion_pass_means_not_matched(tmp_path):
    """match_correct=True for a decoy means SUT correctly returned no match → matched=False."""
    report = {
        "results": {
            "results": [
                {
                    "vars": {"kind": "decoy"},
                    "gradingResult": {
                        "componentResults": [
                            {"assertion": {"metric": "match_correct"}, "pass": True},
                            {"assertion": {"metric": "citation_valid"}, "pass": True},
                            {"assertion": {"metric": "pii_masked"}, "pass": True},
                            {"assertion": {"metric": "risk_tier_correct"}, "pass": True},
                        ]
                    },
                }
            ]
        }
    }
    p = tmp_path / "report.json"
    p.write_text(json.dumps(report))
    rows = _rows_from_promptfoo(str(p))
    assert rows[0].kind == "decoy"
    assert rows[0].matched is False  # assertion passed = SUT correctly had no match = not a FP


def test_rows_from_promptfoo_decoy_assertion_fail_means_matched(tmp_path):
    """match_correct=False for a decoy: SUT returned a match when it shouldn't → matched=True."""
    report = {
        "results": {
            "results": [
                {
                    "vars": {"kind": "decoy"},
                    "gradingResult": {
                        "componentResults": [
                            {"assertion": {"metric": "match_correct"}, "pass": False},
                            {"assertion": {"metric": "citation_valid"}, "pass": True},
                            {"assertion": {"metric": "pii_masked"}, "pass": True},
                            {"assertion": {"metric": "risk_tier_correct"}, "pass": True},
                        ]
                    },
                }
            ]
        }
    }
    p = tmp_path / "report.json"
    p.write_text(json.dumps(report))
    rows = _rows_from_promptfoo(str(p))
    assert rows[0].kind == "decoy"
    assert rows[0].matched is True  # assertion failed = SUT wrongly matched = FP


def test_injection_from_redteam_computes_blocked_fraction(tmp_path):
    report = {"results": {"stats": {"successes": 9, "failures": 1}}}
    p = tmp_path / "redteam.json"
    p.write_text(json.dumps(report))
    assert _injection_from_redteam(str(p)) == pytest.approx(0.9)


def test_injection_from_redteam_empty_returns_one(tmp_path):
    report = {"results": {"stats": {"successes": 0, "failures": 0}}}
    p = tmp_path / "redteam.json"
    p.write_text(json.dumps(report))
    assert _injection_from_redteam(str(p)) == 1.0


def test_main_exits_incomplete_without_redteam(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    p = tmp_path / "report.json"
    p.write_text(json.dumps(PROMPTFOO_REPORT))
    assert main(["gate", str(p)]) == 2


def test_main_exits_ok_with_redteam_fixture(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    p = tmp_path / "report.json"
    p.write_text(json.dumps(PROMPTFOO_REPORT))
    rt = tmp_path / "redteam.json"
    rt.write_text(json.dumps({"results": {"stats": {"successes": 10, "failures": 0}}}))
    assert main(["gate", str(p), str(rt)]) == 0


def test_load_baseline_returns_none_when_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert _load_baseline() is None


def test_load_baseline_parses_json_when_present(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "evals").mkdir()
    (tmp_path / "evals" / "baseline.json").write_text('{"recall": 0.97}')
    assert _load_baseline() == {"recall": 0.97}
