from pathlib import Path
from typing import Dict, List, Optional


def render_report(
    candidate_metrics: Dict,
    candidate_examples: List[Dict],
    baseline_metrics: Optional[Dict],
    metric_regressions: List[Dict],
    example_regressions: List[Dict],
    output_path: str = "reports/latest.html",
) -> str:
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    def badge(ok: bool) -> str:
        return "PASS" if ok else "FAIL"

    rows = "\n".join(
        f"<tr><td>{ex['id']}</td><td>{ex['expected_category']}</td>"
        f"<td>{ex['actual_category']}</td>"
        f"<td>{badge(ex['format_valid'])}</td>"
        f"<td>{badge(ex['category_correct'])}</td></tr>"
        for ex in candidate_examples
    )

    baseline_row = ""
    if baseline_metrics:
        baseline_row = (
            f"<tr><th>Baseline</th><td>{baseline_metrics['accuracy']:.1%}</td>"
            f"<td>{baseline_metrics['format_validity_rate']:.1%}</td></tr>"
        )

    regressions_html = ""
    if metric_regressions:
        items = "".join(
            f"<li>{r['metric']}: {r['baseline']:.1%} &rarr; {r['candidate']:.1%} (-{r['drop']:.1%})</li>"
            for r in metric_regressions
        )
        regressions_html = f"<h2 style='color:#b00020'>Regressions detected</h2><ul>{items}</ul>"

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Regression report</title>
<style>
body {{ font-family: -apple-system, Segoe UI, sans-serif; margin: 2rem; }}
table {{ border-collapse: collapse; width: 100%; margin-bottom: 1.5rem; }}
th, td {{ border: 1px solid #ddd; padding: 6px 10px; text-align: left; }}
th {{ background: #f4f4f4; }}
</style>
</head>
<body>
<h1>Model regression report</h1>
<table>
<tr><th></th><th>Accuracy</th><th>Format validity</th></tr>
{baseline_row}
<tr><th>Candidate</th><td>{candidate_metrics['accuracy']:.1%}</td>
<td>{candidate_metrics['format_validity_rate']:.1%}</td></tr>
</table>
{regressions_html}
<h2>Per-example results</h2>
<table>
<tr><th>ID</th><th>Expected</th><th>Actual</th><th>Format</th><th>Correct</th></tr>
{rows}
</table>
</body>
</html>
"""
    Path(output_path).write_text(html, encoding="utf-8")
    return output_path
