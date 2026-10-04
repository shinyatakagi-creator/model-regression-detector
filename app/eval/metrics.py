from typing import Dict, List


def compute_run_metrics(example_results: List[Dict]) -> Dict:
    """
    example_results: list of dicts, each with at least
        format_valid: bool, category_correct: bool
    """
    total = len(example_results)
    if total == 0:
        return {"accuracy": 0.0, "format_validity_rate": 0.0, "total": 0}

    correct = sum(1 for r in example_results if r["category_correct"])
    valid = sum(1 for r in example_results if r["format_valid"])

    return {
        "accuracy": correct / total,
        "format_validity_rate": valid / total,
        "total": total,
    }
