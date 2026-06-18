import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import List, Optional

from .task import Task

DB_PATH = Path.home() / ".task-scheduler" / "tasks.db"


@contextmanager
def _conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_db() -> None:
    with _conn() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL UNIQUE,
                command     TEXT    NOT NULL,
                cron        TEXT    NOT NULL,
                enabled     INTEGER NOT NULL DEFAULT 1,
                created_at  TEXT    NOT NULL,
                last_run    TEXT,
                last_status TEXT
            )
        """)


def _row_to_task(row: sqlite3.Row) -> Task:
    return Task(
        id=row["id"],
        name=row["name"],
        command=row["command"],
        cron=row["cron"],
        enabled=bool(row["enabled"]),
        created_at=row["created_at"],
        last_run=row["last_run"],
        last_status=row["last_status"],
    )


def add_task(task: Task) -> Task:
    with _conn() as con:
        cur = con.execute(
            "INSERT INTO tasks (name, command, cron, enabled, created_at) VALUES (?, ?, ?, ?, ?)",
            (task.name, task.command, task.cron, int(task.enabled), task.created_at),
        )
        task.id = cur.lastrowid
    return task


def get_task(name: str) -> Optional[Task]:
    with _conn() as con:
        row = con.execute("SELECT * FROM tasks WHERE name = ?", (name,)).fetchone()
    return _row_to_task(row) if row else None


def list_tasks(enabled_only: bool = False) -> List[Task]:
    with _conn() as con:
        query = "SELECT * FROM tasks"
        if enabled_only:
            query += " WHERE enabled = 1"
        rows = con.execute(query + " ORDER BY name").fetchall()
    return [_row_to_task(r) for r in rows]


def update_task(task: Task) -> None:
    with _conn() as con:
        con.execute(
            "UPDATE tasks SET command=?, cron=?, enabled=?, last_run=?, last_status=? WHERE id=?",
            (task.command, task.cron, int(task.enabled), task.last_run, task.last_status, task.id),
        )


def delete_task(name: str) -> bool:
    with _conn() as con:
        cur = con.execute("DELETE FROM tasks WHERE name = ?", (name,))
    return cur.rowcount > 0
