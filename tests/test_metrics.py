from app.eval.metrics import compute_run_metrics


def test_all_correct_and_valid():
    results = [
        {"category_correct": True, "format_valid": True},
        {"category_correct": True, "format_valid": True},
    ]
    metrics = compute_run_metrics(results)
    assert metrics["accuracy"] == 1.0
    assert metrics["format_validity_rate"] == 1.0


def test_partial_failures():
    results = [
        {"category_correct": True, "format_valid": True},
        {"category_correct": False, "format_valid": True},
        {"category_correct": False, "format_valid": False},
        {"category_correct": True, "format_valid": True},
    ]
    metrics = compute_run_metrics(results)
    assert metrics["accuracy"] == 0.5
    assert metrics["format_validity_rate"] == 0.75


def test_empty_results():
    metrics = compute_run_metrics([])
    assert metrics["total"] == 0
