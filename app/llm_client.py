import json
import random
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def complete(self, prompt: str) -> str:
        ...


EMAIL_MARKER_START = "--- EMAIL ---"
EMAIL_MARKER_END = "--- END EMAIL ---"

CATEGORY_KEYWORDS = {
    "billing": ["invoice", "charge", "charged", "refund", "payment", "subscription price"],
    "technical": ["error", "bug", "crash", "not working", "exception", "stack trace", "timeout"],
    "account": ["login", "log in", "password", "locked out", "two-factor", "2fa"],
}
ALL_CATEGORIES = list(CATEGORY_KEYWORDS.keys()) + ["general"]

# The mock is otherwise blind to prompt wording (it classifies by keyword, not
# by "reading" the instructions) - that's fine for the error-rate demo, but it
# means two prompt *versions* would always score identically, which makes
# --prompt-version pointless to test offline. This one signal fixes that: a
# real model is noticeably more likely to wrap its answer in a sentence
# ("Sure, here's the classification: {...}") when the prompt doesn't
# explicitly forbid it. The mock reproduces that one failure mode, so a
# prompt version that drops this instruction shows up as a real, local,
# zero-cost regression - see prompts/v2.py for an example.
STRICT_JSON_INSTRUCTION = "Respond with ONLY a JSON object"
MISSING_INSTRUCTION_NOISE_RATE = 0.6


def _extract_email(prompt: str) -> str:
    if EMAIL_MARKER_START in prompt and EMAIL_MARKER_END in prompt:
        return prompt.rsplit(EMAIL_MARKER_START, 1)[1].split(EMAIL_MARKER_END, 1)[0].strip()
    return prompt


def _keyword_classify(email_text: str) -> str:
    text = email_text.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return category
    return "general"


class MockClassifierLLM(LLMProvider):
    """
    Deterministic stand-in for the real model. Classifies by keyword so the
    eval pipeline can be exercised fully offline, at zero cost.

    error_rate: fraction of responses to deliberately corrupt (wrong category
    or truncated/invalid JSON). Use this to simulate a degraded prompt or
    model and verify the regression detector actually catches it - e.g.
    `python scripts/run_eval.py --error-rate 0.3`.
    """

    def __init__(self, error_rate: float = 0.0, seed: int = 42):
        self.error_rate = error_rate
        self._rng = random.Random(seed)

    def complete(self, prompt: str) -> str:
        email_text = _extract_email(prompt)
        category = _keyword_classify(email_text)
        first_line = (email_text.strip().splitlines() or [""])[0]
        summary = first_line[:80]

        if self._rng.random() < self.error_rate:
            if self._rng.random() < 0.5:
                others = [c for c in ALL_CATEGORIES if c != category]
                category = self._rng.choice(others)
            else:
                # Truncate valid JSON into something unparseable.
                return json.dumps({"category": category, "summary": summary})[:-1]

        payload = json.dumps({"category": category, "summary": summary})

        if STRICT_JSON_INSTRUCTION not in prompt and self._rng.random() < MISSING_INSTRUCTION_NOISE_RATE:
            payload = f"Sure, here's the classification:\n{payload}"

        return payload


class OpenAIClient(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        from openai import OpenAI  # local import so the mock path never needs the package configured

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def complete(self, prompt: str) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return resp.choices[0].message.content


def get_llm_client(settings, error_rate: float = 0.0) -> LLMProvider:
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise RuntimeError("LLM_PROVIDER=openai requires OPENAI_API_KEY to be set")
        return OpenAIClient(api_key=settings.openai_api_key, model=settings.openai_model)
    return MockClassifierLLM(error_rate=error_rate)
