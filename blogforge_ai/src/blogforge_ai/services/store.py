import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from blogforge_ai.config import settings


def _connect() -> sqlite3.Connection:
    Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True) if Path(settings.database_path).parent != Path('.') else None
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
              id TEXT PRIMARY KEY,
              request_json TEXT NOT NULL,
              status TEXT NOT NULL,
              scheduled_for TEXT,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL,
              result_json TEXT,
              error TEXT
            )
            """
        )


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_job(job_id: str, request: dict[str, Any], status: str, scheduled_for: str | None = None) -> None:
    init_db()
    t = now_iso()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO jobs (id, request_json, status, scheduled_for, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
            (job_id, json.dumps(request, default=str), status, scheduled_for, t, t),
        )


def update_job(job_id: str, status: str, result: dict[str, Any] | None = None, error: str | None = None) -> None:
    init_db()
    with _connect() as conn:
        conn.execute(
            "UPDATE jobs SET status=?, result_json=?, error=?, updated_at=? WHERE id=?",
            (status, json.dumps(result, default=str) if result else None, error, now_iso(), job_id),
        )


def get_job(job_id: str) -> dict[str, Any] | None:
    init_db()
    with _connect() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if not row:
        return None
    item = dict(row)
    item["request"] = json.loads(item.pop("request_json"))
    item["result"] = json.loads(item.pop("result_json")) if item.get("result_json") else None
    item.pop("result_json", None)
    return item


def list_jobs(limit: int = 20) -> list[dict[str, Any]]:
    init_db()
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM jobs ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
    jobs = []
    for row in rows:
        item = dict(row)
        item["request"] = json.loads(item.pop("request_json"))
        item["result"] = json.loads(item.pop("result_json")) if item.get("result_json") else None
        item.pop("result_json", None)
        jobs.append(item)
    return jobs


def pending_jobs() -> list[dict[str, Any]]:
    init_db()
    with _connect() as conn:
        rows = conn.execute("SELECT * FROM jobs WHERE status='scheduled'").fetchall()
    items = []
    for row in rows:
        item = dict(row)
        item["request"] = json.loads(item.pop("request_json"))
        item.pop("result_json", None)
        items.append(item)
    return items
