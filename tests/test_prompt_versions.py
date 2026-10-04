from app.eval.format_validator import validate_classification_output
from app.llm_client import MockClassifierLLM
from app.llm_feature import classify_email


def test_v1_keeps_strict_instruction_and_stays_clean():
    client = MockClassifierLLM(error_rate=0.0, seed=1)
    for _ in range(20):
        raw = classify_email("I was charged twice, please refund me.", client, prompt_version="v1")
        _, valid = validate_classification_output(raw)
        assert valid is True


def test_v2_drops_strict_instruction_and_sometimes_breaks_format():
    client = MockClassifierLLM(error_rate=0.0, seed=1)
    invalid_count = 0
    for _ in range(50):
        raw = classify_email("I was charged twice, please refund me.", client, prompt_version="v2")
        _, valid = validate_classification_output(raw)
        if not valid:
            invalid_count += 1
    # v2 drops "Respond with ONLY a JSON object" - the mock reproduces the
    # real-model failure mode of occasionally adding a conversational
    # preamble, which breaks strict JSON parsing.
    assert invalid_count > 0
