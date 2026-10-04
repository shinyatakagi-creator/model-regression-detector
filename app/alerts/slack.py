from typing import Dict, List, Optional

import requests


class SlackNotifier:
    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url

    def notify_regression(self, metric_regressions: List[Dict], example_regressions: List[Dict], run_info: Dict) -> None:
        message = self._build_message(metric_regressions, example_regressions, run_info)
        if not self.webhook_url:
            print("[SlackNotifier] SLACK_WEBHOOK_URL not set - printing the alert instead:\n" + message)
            return
        try:
            requests.post(self.webhook_url, json={"text": message}, timeout=5)
        except requests.RequestException as exc:
            print(f"[SlackNotifier] Failed to send Slack alert ({exc}); alert content:\n{message}")

    @staticmethod
    def _build_message(metric_regressions: List[Dict], example_regressions: List[Dict], run_info: Dict) -> str:
        lines = [
            f":rotating_light: Regression detected - prompt `{run_info.get('prompt_version')}`, "
            f"provider `{run_info.get('llm_provider')}` (run #{run_info.get('run_id')})",
        ]
        for reg in metric_regressions:
            lines.append(
                f"- {reg['metric']}: {reg['baseline']:.1%} -> {reg['candidate']:.1%} (-{reg['drop']:.1%})"
            )
        if example_regressions:
            lines.append(f"- {len(example_regressions)} test case(s) newly failing:")
            for ex in example_regressions[:5]:
                lines.append(
                    f"    {ex['id']}: expected `{ex['expected_category']}`, "
                    f"was `{ex['baseline_actual']}`, now `{ex['candidate_actual']}`"
                )
        return "\n".join(lines)
