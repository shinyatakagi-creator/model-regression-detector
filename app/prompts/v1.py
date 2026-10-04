SYSTEM_INSTRUCTIONS = """You are a support-ticket triage assistant.
Read the customer email and classify it into exactly one category:
billing, technical, account, or general.
Then write a one-sentence summary of the request.

Respond with ONLY a JSON object in this exact shape:
{"category": "<billing|technical|account|general>", "summary": "<one sentence>"}
"""

FEW_SHOT_EXAMPLES = """
Example 1
--- EMAIL ---
I was charged twice for my subscription this month, can you refund the duplicate charge?
--- END EMAIL ---
{"category": "billing", "summary": "Customer was double-charged and wants a refund."}

Example 2
--- EMAIL ---
The app crashes with a 500 error every time I try to export a report.
--- END EMAIL ---
{"category": "technical", "summary": "Exporting a report triggers a 500 error and crash."}

Example 3
--- EMAIL ---
I'm locked out of my account after enabling two-factor authentication.
--- END EMAIL ---
{"category": "account", "summary": "Customer is locked out after enabling 2FA."}
"""

PROMPT_VERSION = "v1"


def build_prompt(email_text: str) -> str:
    return (
        f"{SYSTEM_INSTRUCTIONS}\n"
        f"{FEW_SHOT_EXAMPLES}\n"
        f"Now classify this email.\n"
        f"--- EMAIL ---\n{email_text}\n--- END EMAIL ---\n"
    )
