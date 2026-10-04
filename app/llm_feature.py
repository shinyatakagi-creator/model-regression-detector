from .prompts import get_prompt_builder


def classify_email(email_text: str, llm_client, prompt_version: str = "v1") -> str:
    """
    Runs the LLM feature under test and returns the raw model output.

    Validation/parsing of that output lives in eval.format_validator, kept
    separate so the feature code and the eval code can change independently -
    exactly the seam a regression pipeline needs.
    """
    build_prompt = get_prompt_builder(prompt_version)
    prompt = build_prompt(email_text)
    return llm_client.complete(prompt)
