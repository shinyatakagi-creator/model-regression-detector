import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    prompt_version TEXT NOT NULL,
    llm_provider TEXT NOT NULL,
    accuracy REAL NOT NULL,
    format_validity_rate REAL NOT NULL,
    is_baseline INTEGER NOT NULL DEFAULT 0,
    results_json TEXT NOT NULL
);
"""


def init_db(db_path: str) -> None:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(SCHEMA)


def save_run(db_path: str, prompt_version: str, llm_provider: str, metrics: dict, examples: list) -> int:
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        cur = conn.execute(
            """
            INSERT INTO runs (created_at, prompt_version, llm_provider, accuracy, format_validity_rate, results_json)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now(timezone.utc).isoformat(),
                prompt_version,
                llm_provider,
                metrics["accuracy"],
                metrics["format_validity_rate"],
                json.dumps(examples),
            ),
        )
        return cur.lastrowid


def get_baseline(db_path: str) -> Optional[dict]:
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM runs WHERE is_baseline = 1 ORDER BY id DESC LIMIT 1").fetchone()
        return _row_to_dict(row) if row else None


def set_baseline(db_path: str, run_id: int) -> None:
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute("UPDATE runs SET is_baseline = 0")
        conn.execute("UPDATE runs SET is_baseline = 1 WHERE id = ?", (run_id,))


def get_run(db_path: str, run_id: int) -> Optional[dict]:
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
        return _row_to_dict(row) if row else None


def list_runs(db_path: str, limit: int = 20) -> list:
    init_db(db_path)
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [_row_to_dict(r) for r in rows]


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    d["examples"] = json.loads(d.pop("results_json"))
    d["is_baseline"] = bool(d["is_baseline"])
    return d
