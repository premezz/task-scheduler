from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Task:
    name: str
    command: str
    cron: str
    id: Optional[int] = None
    enabled: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    last_run: Optional[str] = None
    last_status: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "command": self.command,
            "cron": self.cron,
            "enabled": self.enabled,
            "created_at": self.created_at,
            "last_run": self.last_run,
            "last_status": self.last_status,
        }
