"""Background email scheduler for delayed sending."""

import time
import threading
from typing import List, Callable, Optional, Dict, Any
from datetime import datetime, timezone
from dataclasses import dataclass, field
from uuid import uuid4
import logging

from .models import EmailMessage, EmailStatus
from .sender import EmailSender

logger = logging.getLogger(__name__)


@dataclass
class ScheduledEmail:
    """Task definition for an email awaiting dispatch."""
    id: str = field(default_factory=lambda: str(uuid4()))
    message: EmailMessage = field(default_factory=lambda: None)  # type: ignore
    send_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    attempts: int = 0
    max_attempts: int = 3


class EmailScheduler:
    """Schedules and dispatches emails asynchronously at specified timestamps."""

    def __init__(self, sender: EmailSender, poll_interval: float = 5.0) -> None:
        self.sender = sender
        self.poll_interval = poll_interval
        self._queue: List[ScheduledEmail] = []
        self._lock = threading.Lock()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def schedule(self, message: EmailMessage, send_at: datetime) -> str:
        """Enqueue an email to be sent at a future time."""
        task = ScheduledEmail(message=message, send_at=send_at)
        with self._lock:
            self._queue.append(task)
        logger.info(f"Email '{message.subject}' scheduled for {send_at.isoformat()}")
        return task.id

    def cancel(self, task_id: str) -> bool:
        """Cancel a pending scheduled email."""
        with self._lock:
            initial_len = len(self._queue)
            self._queue = [t for t in self._queue if t.id != task_id]
            return len(self._queue) < initial_len

    def start(self) -> None:
        """Start the background scheduler thread."""
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop the background scheduler."""
        self._stop_event.set()
        if self._thread:
            self._thread.join()

    def _run_loop(self) -> None:
        """Polling loop that checks for due emails."""
        while not self._stop_event.is_set():
            now = datetime.now(timezone.utc)
            ready_tasks: List[ScheduledEmail] = []

            with self._lock:
                remaining_tasks = []
                for task in self._queue:
                    if task.send_at <= now:
                        ready_tasks.append(task)
                    else:
                        remaining_tasks.append(task)
                self._queue = remaining_tasks

            for task in ready_tasks:
                try:
                    task.attempts += 1
                    self.sender.send(task.message)
                    logger.info(f"Successfully sent scheduled email {task.id}")
                except Exception as e:
                    logger.error(f"Error sending scheduled email {task.id}: {e}")
                    if task.attempts < task.max_attempts:
                        with self._lock:
                            self._queue.append(task)

            time.sleep(self.poll_interval)
