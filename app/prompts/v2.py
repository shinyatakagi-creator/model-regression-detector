"""
v2 - a deliberately "trimmed" version of v1, the kind of edit that happens
in real life when someone shortens a prompt to save tokens without
re-running the eval. It drops:
  - the few-shot examples
  - the explicit "Respond with ONLY a JSON object" instruction

Run `python scripts/run_eval.py --prompt-version v2 --compare-baseline`
after setting a v1 baseline to see this get caught.
"""

SYSTEM_INSTRUCTIONS = """You are a support-ticket triage assistant.
Read the customer email and classify it into billing, technical, account, or general.
Then write a one-sentence summary of the request.

Return the category and a short summary as JSON.
"""

PROMPT_VERSION = "v2"


def build_prompt(email_text: str) -> str:
    return f"{SYSTEM_INSTRUCTIONS}\n--- EMAIL ---\n{email_text}\n--- END EMAIL ---\n"
