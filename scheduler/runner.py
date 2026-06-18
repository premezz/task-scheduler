import subprocess
from datetime import datetime

from . import storage
from .task import Task


def run_task(task: Task) -> tuple[int, str]:
    """Execute the task's shell command. Returns (returncode, output)."""
    try:
        result = subprocess.run(
            task.command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=3600,
        )
        output = result.stdout + result.stderr
        status = "success" if result.returncode == 0 else f"failed (exit {result.returncode})"
    except subprocess.TimeoutExpired:
        output = "Task timed out after 1 hour"
        result = type("R", (), {"returncode": -1})()
        status = "timeout"
    except Exception as exc:
        output = str(exc)
        result = type("R", (), {"returncode": -1})()
        status = "error"

    task.last_run = datetime.now().isoformat()
    task.last_status = status
    storage.update_task(task)
    return result.returncode, output
