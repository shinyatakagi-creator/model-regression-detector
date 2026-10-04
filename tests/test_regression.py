from app.eval.regression import detect_example_regressions, detect_metric_regressions


def test_no_regression_when_metrics_equal():
    baseline = {"accuracy": 0.9, "format_validity_rate": 1.0}
    candidate = {"accuracy": 0.9, "format_validity_rate": 1.0}
    assert detect_metric_regressions(baseline, candidate) == []


def test_regression_flagged_when_drop_exceeds_tolerance():
    baseline = {"accuracy": 0.9, "format_validity_rate": 1.0}
    candidate = {"accuracy": 0.7, "format_validity_rate": 1.0}
    regressions = detect_metric_regressions(baseline, candidate, tolerance=0.02)
    assert len(regressions) == 1
    assert regressions[0]["metric"] == "accuracy"


def test_small_drop_within_tolerance_is_not_flagged():
    baseline = {"accuracy": 0.90, "format_validity_rate": 1.0}
    candidate = {"accuracy": 0.89, "format_validity_rate": 1.0}
    assert detect_metric_regressions(baseline, candidate, tolerance=0.02) == []


def test_example_level_regression_detected():
    baseline_examples = [
        {"id": "e01", "category_correct": True, "format_valid": True, "actual_category": "billing"},
        {"id": "e02", "category_correct": True, "format_valid": True, "actual_category": "technical"},
    ]
    candidate_examples = [
        {
            "id": "e01",
            "category_correct": True,
            "format_valid": True,
            "expected_category": "billing",
            "actual_category": "billing",
        },
        {
            "id": "e02",
            "category_correct": False,
            "format_valid": True,
            "expected_category": "technical",
            "actual_category": "billing",
        },
    ]
    regressed = detect_example_regressions(baseline_examples, candidate_examples)
    assert len(regressed) == 1
    assert regressed[0]["id"] == "e02"
