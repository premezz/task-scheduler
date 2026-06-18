# task-scheduler

A lightweight, cron-style task scheduler with a simple CLI. Tasks are persisted in a local SQLite database and run by a long-lived daemon process.

## Install

```bash
pip install -e .
```

## Usage

### Add a task

```bash
# taskctl add <name> "<cron>" "<command>"
taskctl add daily-backup "0 2 * * *" "tar -czf ~/backup.tar.gz ~/Documents"
taskctl add hourly-ping  "0 * * * *"  "curl -s https://example.com/ping"
```

### List tasks

```bash
taskctl list          # enabled only
taskctl list --all    # include disabled
```

### Run a task immediately

```bash
taskctl run daily-backup
```

### Enable / disable a task

```bash
taskctl disable daily-backup
taskctl enable  daily-backup
```

### Remove a task

```bash
taskctl remove daily-backup
```

### Start the daemon

The daemon reads all enabled tasks from the database and runs them on their cron schedule. It must be running for automatic execution.

```bash
taskctl start
```

To run it in the background on Linux/macOS:

```bash
nohup taskctl start &> ~/.task-scheduler/daemon.log &
```

## Cron expression reference

```
┌───────── minute        (0–59)
│ ┌─────── hour          (0–23)
│ │ ┌───── day of month  (1–31)
│ │ │ ┌─── month         (1–12)
│ │ │ │ ┌─ day of week   (0–6, Sun=0)
│ │ │ │ │
* * * * *
```

Common examples:

| Expression    | Meaning                  |
|---------------|--------------------------|
| `0 * * * *`   | Every hour               |
| `0 9 * * *`   | Every day at 9 AM        |
| `0 9 * * 1`   | Every Monday at 9 AM     |
| `*/15 * * * *`| Every 15 minutes         |
| `0 0 1 * *`   | First day of every month |

## Data storage

Tasks are stored in `~/.task-scheduler/tasks.db` (SQLite). You can back it up or move it freely.
