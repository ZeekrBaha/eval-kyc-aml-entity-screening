from evaluator.judge.calibration import cohen_kappa


def test_kappa_perfect_agreement_is_one():
    human = [1, 0, 1, 0]
    judge = [1, 0, 1, 0]
    assert cohen_kappa(human, judge) == 1.0


def test_kappa_no_better_than_chance_is_zero():
    human = [1, 1, 0, 0]
    judge = [1, 0, 1, 0]
    assert abs(cohen_kappa(human, judge)) < 1e-9
