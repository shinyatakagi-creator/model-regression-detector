"""
Optional dashboard over the run history stored in SQLite.

Run with:
    pip install -r requirements-dashboard.txt
    streamlit run app/report/dashboard.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import streamlit as st

from app.config import settings
from app.storage.db import list_runs

st.set_page_config(page_title="Model Regression Dashboard", layout="wide")
st.title("Model Regression Dashboard")

runs = list_runs(settings.db_path, limit=50)

if not runs:
    st.info("No runs yet. Run `python scripts/run_eval.py` first.")
else:
    runs_oldest_first = list(reversed(runs))

    st.subheader("Accuracy over time")
    st.line_chart(
        {
            "accuracy": [r["accuracy"] for r in runs_oldest_first],
            "format_validity": [r["format_validity_rate"] for r in runs_oldest_first],
        }
    )

    st.subheader("Run history")
    st.dataframe(
        [
            {
                "id": r["id"],
                "created_at": r["created_at"],
                "prompt_version": r["prompt_version"],
                "provider": r["llm_provider"],
                "accuracy": f"{r['accuracy']:.1%}",
                "format_validity": f"{r['format_validity_rate']:.1%}",
                "baseline": "yes" if r["is_baseline"] else "",
            }
            for r in runs
        ]
    )

    latest = runs[0]
    st.subheader(f"Latest run (#{latest['id']}) - per example")
    st.dataframe(latest["examples"])
