#!/usr/bin/env python
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.alerts.slack import SlackNotifier
from app.config import settings
from app.eval.regression import detect_example_regressions, detect_metric_regressions
from app.eval.runner import load_golden_dataset, run_eval
from app.llm_client import get_llm_client
from app.report.html_report import render_report
from app.storage.db import get_baseline, save_run, set_baseline


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the golden-dataset eval and check for regressions.")
    parser.add_argument("--prompt-version", default=settings.prompt_version)
    parser.add_argument(
        "--error-rate",
        type=float,
        default=0.0,
        help="Mock model only: fraction of cases to deliberately corrupt, to demo regression detection.",
    )
    parser.add_argument("--set-baseline", action="store_true", help="Save this run and mark it as the new baseline.")
    parser.add_argument(
        "--compare-baseline",
        action="store_true",
        help="Exit with a non-zero status if a regression is found (CI mode).",
    )
    parser.add_argument("--tolerance", type=float, default=settings.regression_tolerance)
    args = parser.parse_args()

    llm_client = get_llm_client(settings, error_rate=args.error_rate)
    golden_dataset = load_golden_dataset(settings.golden_dataset_path)

    result = run_eval(golden_dataset, llm_client, args.prompt_version)
    metrics, examples = result["metrics"], result["examples"]

    noise_note = f", error_rate={args.error_rate}" if args.error_rate else ""
    print(f"Ran {metrics['total']} golden cases against prompt `{args.prompt_version}` ({settings.llm_provider}{noise_note})")
    print(f"  Accuracy:        {metrics['accuracy']:.1%}")
    print(f"  Format validity: {metrics['format_validity_rate']:.1%}")

    run_id = save_run(settings.db_path, args.prompt_version, settings.llm_provider, metrics, examples)

    if args.set_baseline:
        set_baseline(settings.db_path, run_id)
        print(f"Run #{run_id} saved and marked as the new baseline.")
        return 0

    baseline = get_baseline(settings.db_path)
    metric_regressions, example_regressions = [], []

    if baseline:
        metric_regressions = detect_metric_regressions(baseline, metrics, tolerance=args.tolerance)
        example_regressions = detect_example_regressions(baseline["examples"], examples)
    elif args.compare_baseline:
        print("No baseline set yet - run with --set-baseline first. Failing so CI never passes without a comparison.")
        return 2

    report_path = render_report(metrics, examples, baseline, metric_regressions, example_regressions)
    print(f"Report written to {report_path}")

    if metric_regressions or example_regressions:
        print(f"\n{len(metric_regressions)} metric regression(s), {len(example_regressions)} example regression(s) detected.")
        SlackNotifier(settings.slack_webhook_url).notify_regression(
            metric_regressions,
            example_regressions,
            {"run_id": run_id, "prompt_version": args.prompt_version, "llm_provider": settings.llm_provider},
        )
        if args.compare_baseline:
            return 1
    else:
        print("\nNo regressions detected.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
