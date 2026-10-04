import json
from typing import Dict, List

from ..llm_feature import classify_email
from .format_validator import validate_classification_output
from .metrics import compute_run_metrics


def load_golden_dataset(path: str) -> List[Dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_eval(golden_dataset: List[Dict], llm_client, prompt_version: str) -> Dict:
    """
    Runs the feature under test against every golden example.

    Returns {"metrics": {...aggregate...}, "examples": [per-example results]}
    """
    example_results = []
    for case in golden_dataset:
        raw = classify_email(case["email"], llm_client, prompt_version=prompt_version)
        parsed, format_valid = validate_classification_output(raw)
        parsed = parsed or {}
        category_correct = format_valid and parsed.get("category") == case["expected_category"]

        example_results.append(
            {
                "id": case["id"],
                "expected_category": case["expected_category"],
                "actual_category": parsed.get("category"),
                "format_valid": format_valid,
                "category_correct": category_correct,
                "raw": raw,
            }
        )

    metrics = compute_run_metrics(example_results)
    return {"metrics": metrics, "examples": example_results}
