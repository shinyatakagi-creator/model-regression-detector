from app.eval.format_validator import validate_classification_output


def test_valid_json_passes():
    raw = '{"category": "billing", "summary": "Customer wants a refund."}'
    parsed, valid = validate_classification_output(raw)
    assert valid is True
    assert parsed["category"] == "billing"


def test_unknown_category_fails():
    raw = '{"category": "shipping", "summary": "Where is my package?"}'
    _, valid = validate_classification_output(raw)
    assert valid is False


def test_missing_summary_fails():
    raw = '{"category": "billing"}'
    _, valid = validate_classification_output(raw)
    assert valid is False


def test_malformed_json_fails():
    raw = '{"category": "billing", "summary": "incomplete'
    parsed, valid = validate_classification_output(raw)
    assert valid is False
    assert parsed is None
