from typing import Dict, List


def detect_metric_regressions(baseline_metrics: Dict, candidate_metrics: Dict, tolerance: float = 0.02) -> List[Dict]:
    """Flags any tracked metric that dropped by more than `tolerance`."""
    regressions = []
    for name in ("accuracy", "format_validity_rate"):
        baseline_val = baseline_metrics.get(name, 0.0)
        candidate_val = candidate_metrics.get(name, 0.0)
        drop = baseline_val - candidate_val
        if drop > tolerance:
            regressions.append(
                {
                    "metric": name,
                    "baseline": baseline_val,
                    "candidate": candidate_val,
                    "drop": drop,
                }
            )
    return regressions


def detect_example_regressions(baseline_examples: List[Dict], candidate_examples: List[Dict]) -> List[Dict]:
    """Golden-dataset cases that passed in the baseline but fail in the candidate.

    This is what actually tells an engineer *which* test case broke, not just
    that the aggregate score moved.
    """
    baseline_by_id = {e["id"]: e for e in baseline_examples}
    regressed = []
    for cand in candidate_examples:
        base = baseline_by_id.get(cand["id"])
        if base is None:
            continue
        was_passing = base["category_correct"] and base["format_valid"]
        now_passing = cand["category_correct"] and cand["format_valid"]
        if was_passing and not now_passing:
            regressed.append(
                {
                    "id": cand["id"],
                    "expected_category": cand["expected_category"],
                    "baseline_actual": base["actual_category"],
                    "candidate_actual": cand["actual_category"],
                }
            )
    return regressed
