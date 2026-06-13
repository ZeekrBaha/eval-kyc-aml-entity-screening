from evaluator.gate import aggregate, evaluate_gate, DEFAULT_THRESHOLDS, RowOutcome


def _rows():
    # 2 true matches (1 caught, 1 missed), 2 decoys (1 clean, 1 false positive)
    return [
        RowOutcome(kind="true_match", matched=True, citation_ok=True, pii_ok=True, risk_ok=True),
        RowOutcome(kind="true_match", matched=False, citation_ok=True, pii_ok=True, risk_ok=False),
        RowOutcome(kind="decoy", matched=False, citation_ok=True, pii_ok=True, risk_ok=True),
        RowOutcome(kind="decoy", matched=True, citation_ok=True, pii_ok=True, risk_ok=True),
    ]


def test_aggregate_computes_recall_and_fp_rate():
    sc = aggregate(_rows())
    assert sc.recall == 0.5            # 1 of 2 true matches caught
    assert sc.false_positive_rate == 0.5  # 1 of 2 decoys wrongly matched
    assert sc.citation_validity == 1.0
    assert sc.pii_masking == 1.0


def test_gate_fails_when_recall_below_threshold():
    sc = aggregate(_rows())
    res = evaluate_gate(sc, DEFAULT_THRESHOLDS, baseline=None)
    assert res.exit_code == 1
    assert any("recall" in r for r in res.reasons)


def test_gate_passes_clean_run():
    rows = [RowOutcome(kind="true_match", matched=True, citation_ok=True, pii_ok=True, risk_ok=True)]
    res = evaluate_gate(aggregate(rows), DEFAULT_THRESHOLDS, baseline=None)
    assert res.exit_code == 0
    assert res.verdict == "ok"


def test_gate_fails_closed_on_missing_metric():
    sc = aggregate([RowOutcome(kind="true_match", matched=True, citation_ok=True, pii_ok=True, risk_ok=True)])
    sc.injection_resistance = None  # live red-team metric did not run
    res = evaluate_gate(sc, DEFAULT_THRESHOLDS, baseline=None)
    assert res.exit_code == 2
    assert res.verdict == "incomplete"


def test_gate_flags_regression_against_baseline():
    sc = aggregate([
        RowOutcome(kind="true_match", matched=True, citation_ok=True, pii_ok=True, risk_ok=True),
        RowOutcome(kind="true_match", matched=False, citation_ok=True, pii_ok=True, risk_ok=True),
    ])  # recall 0.5
    baseline = {"recall": 0.95}
    res = evaluate_gate(sc, DEFAULT_THRESHOLDS, baseline=baseline)
    assert res.exit_code == 1
    assert any("regress" in r.lower() for r in res.reasons)
