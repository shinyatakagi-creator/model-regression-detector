import json
from typing import Optional, Tuple

ALLOWED_CATEGORIES = {"billing", "technical", "account", "general"}


def validate_classification_output(raw: str) -> Tuple[Optional[dict], bool]:
    """Parse and validate the model's raw output.

    Returns (parsed_dict_or_None, is_valid). A response only counts as valid
    if it's well-formed JSON with a recognised category and a non-empty
    summary string.
    """
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None, False

    if not isinstance(data, dict):
        return None, False

    category = data.get("category")
    summary = data.get("summary")

    if category not in ALLOWED_CATEGORIES:
        return data, False
    if not isinstance(summary, str) or not summary.strip():
        return data, False

    return data, True
