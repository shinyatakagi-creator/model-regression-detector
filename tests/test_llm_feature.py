from app.eval.format_validator import validate_classification_output
from app.llm_client import MockClassifierLLM
from app.llm_feature import classify_email


def test_classify_email_billing_case():
    client = MockClassifierLLM(error_rate=0.0)
    raw = classify_email("I was charged twice for my subscription, please refund me.", client)
    parsed, valid = validate_classification_output(raw)
    assert valid is True
    assert parsed["category"] == "billing"


def test_classify_email_technical_case():
    client = MockClassifierLLM(error_rate=0.0)
    raw = classify_email("The app keeps crashing with a 500 error.", client)
    parsed, valid = validate_classification_output(raw)
    assert valid is True
    assert parsed["category"] == "technical"


def test_classify_email_falls_back_to_general():
    client = MockClassifierLLM(error_rate=0.0)
    raw = classify_email("Just wanted to say thanks for the great product!", client)
    parsed, valid = validate_classification_output(raw)
    assert valid is True
    assert parsed["category"] == "general"
