"""CLI entry point — all user-facing commands live here."""
import sys

import click
from tabulate import tabulate

from . import storage
from .daemon import start_daemon
from .runner import run_task
from .task import Task


@click.group()
def cli():
    """taskctl — a simple cron-style task scheduler."""
    storage.init_db()


@cli.command()
@click.argument("name")
@click.argument("cron")
@click.argument("command")
def add(name: str, cron: str, command: str):
    """Add a new scheduled task.

    \b
    NAME    Unique identifier for the task
    CRON    Cron expression (e.g. "0 9 * * *" for every day at 9 AM)
    COMMAND Shell command to execute
    """
    from apscheduler.triggers.cron import CronTrigger
    try:
        CronTrigger.from_crontab(cron)
    except Exception:
        click.echo(f"Error: '{cron}' is not a valid cron expression.", err=True)
        sys.exit(1)

    if storage.get_task(name):
        click.echo(f"Error: a task named '{name}' already exists.", err=True)
        sys.exit(1)

    task = Task(name=name, command=command, cron=cron)
    storage.add_task(task)
    click.echo(f"Added task '{name}'  [{cron}]  -> {command}")


@cli.command("list")
@click.option("--all", "show_all", is_flag=True, help="Include disabled tasks")
def list_tasks(show_all: bool):
    """List scheduled tasks."""
    tasks = storage.list_tasks(enabled_only=not show_all)
    if not tasks:
        click.echo("No tasks found.")
        return

    rows = [
        [
            t.id,
            t.name,
            t.cron,
            t.command[:40] + ("…" if len(t.command) > 40 else ""),
            "yes" if t.enabled else "no",
            t.last_run[:19] if t.last_run else "-",
            t.last_status or "-",
        ]
        for t in tasks
    ]
    click.echo(
        tabulate(rows, headers=["ID", "Name", "Cron", "Command", "Enabled", "Last Run", "Status"])
    )


@cli.command()
@click.argument("name")
def remove(name: str):
    """Remove a task by name."""
    if not storage.delete_task(name):
        click.echo(f"Error: no task named '{name}'.", err=True)
        sys.exit(1)
    click.echo(f"Removed task '{name}'.")


@cli.command()
@click.argument("name")
def enable(name: str):
    """Enable a disabled task."""
    task = storage.get_task(name)
    if not task:
        click.echo(f"Error: no task named '{name}'.", err=True)
        sys.exit(1)
    task.enabled = True
    storage.update_task(task)
    click.echo(f"Enabled task '{name}'.")


@cli.command()
@click.argument("name")
def disable(name: str):
    """Disable a task without deleting it."""
    task = storage.get_task(name)
    if not task:
        click.echo(f"Error: no task named '{name}'.", err=True)
        sys.exit(1)
    task.enabled = False
    storage.update_task(task)
    click.echo(f"Disabled task '{name}'.")


@cli.command("run")
@click.argument("name")
def run_now(name: str):
    """Run a task immediately, regardless of its schedule."""
    task = storage.get_task(name)
    if not task:
        click.echo(f"Error: no task named '{name}'.", err=True)
        sys.exit(1)
    click.echo(f"Running '{name}'...")
    code, output = run_task(task)
    if output.strip():
        click.echo(output.strip())
    click.echo(f"Done — {task.last_status}")
    sys.exit(0 if code == 0 else code)


@cli.command()
def start():
    """Start the scheduler daemon (blocking)."""
    start_daemon()
