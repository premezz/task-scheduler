"""Background scheduler daemon — loads tasks from the DB and runs them on their cron schedule."""
import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from . import storage
from .runner import run_task

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)


def _make_job(task_name: str):
    def _run():
        task = storage.get_task(task_name)
        if task is None or not task.enabled:
            return
        log.info("Running task: %s", task_name)
        code, output = run_task(task)
        if output.strip():
            log.info("Output:\n%s", output.strip())
        log.info("Finished task '%s' — %s", task_name, task.last_status)
    _run.__name__ = task_name
    return _run


def start_daemon() -> None:
    storage.init_db()
    scheduler = BlockingScheduler()

    tasks = storage.list_tasks(enabled_only=True)
    if not tasks:
        log.warning("No enabled tasks found. Add tasks with 'taskctl add' then restart the daemon.")

    for task in tasks:
        try:
            trigger = CronTrigger.from_crontab(task.cron)
            scheduler.add_job(_make_job(task.name), trigger, id=task.name, name=task.name)
            log.info("Scheduled '%s'  cron=%s", task.name, task.cron)
        except Exception as exc:
            log.error("Invalid cron for task '%s': %s", task.name, exc)

    log.info("Daemon started with %d task(s). Press Ctrl+C to stop.", len(tasks))
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("Daemon stopped.")
