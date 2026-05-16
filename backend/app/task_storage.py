import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, Any
import uuid
from logging.handlers import TimedRotatingFileHandler

# Setup cleanup logger with JSON format and daily rotation
cleanup_logger = logging.getLogger("cleanup")
cleanup_logger.setLevel(logging.DEBUG)

# Create cleanup log file handler
CLEANUP_LOG_PATH = Path("./logs/cleanup.log")
CLEANUP_LOG_PATH.parent.mkdir(exist_ok=True)

cleanup_handler = TimedRotatingFileHandler(
    CLEANUP_LOG_PATH,
    when="midnight",
    interval=1,
    backupCount=30,
)
cleanup_handler.setFormatter(logging.Formatter("%(message)s"))
cleanup_logger.addHandler(cleanup_handler)

logger = logging.getLogger(__name__)

TASKS_DIR = Path("./tasks")
TASKS_DIR.mkdir(exist_ok=True)


class TaskStorage:
    """Task storage service for persisting task status to disk."""

    def __init__(self, tasks_dir: Path = None):
        self.tasks_dir = tasks_dir or TASKS_DIR

    def _get_task_path(self, task_id: str) -> Path:
        """Get the file path for a task."""
        return self.tasks_dir / f"{task_id}.json"

    def create_task(
        self,
        source_type: str,
        url: str,
        content: Optional[str] = None,
    ) -> str:
        """
        Create a new task and return its ID.

        Args:
            source_type: Type of source (article/youtube)
            url: Source URL
            content: Optional content for articles

        Returns:
            Task ID string
        """
        task_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        task_data = {
            "task_id": task_id,
            "status": "pending",
            "source_type": source_type,
            "url": url,
            "content": content,
            "created_at": now,
            "completed_at": None,
            "result": None,
            "error": None,
        }

        self._save_task(task_id, task_data)
        logger.info(f"Created task {task_id} for {source_type} source")
        return task_id

    def _save_task(self, task_id: str, task_data: Dict[str, Any]) -> None:
        """Save task data to disk."""
        task_path = self._get_task_path(task_id)
        with open(task_path, "w") as f:
            json.dump(task_data, f, indent=2)

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task data by ID.

        Args:
            task_id: Task ID string

        Returns:
            Task data dict or None if not found
        """
        task_path = self._get_task_path(task_id)
        if not task_path.exists():
            return None

        with open(task_path, "r") as f:
            return json.load(f)

    def update_task(
        self,
        task_id: str,
        status: str = None,
        result: Dict[str, Any] = None,
        error: str = None,
    ) -> None:
        """
        Update task status, result, or error.

        Args:
            task_id: Task ID string
            status: New status value
            result: Result data
            error: Error message
        """
        task_data = self.get_task(task_id)
        if not task_data:
            logger.error(f"Task {task_id} not found for update")
            return

        if status:
            task_data["status"] = status
        if result:
            task_data["result"] = result
        if error:
            task_data["error"] = error
        if status in ("completed", "failed"):
            task_data["completed_at"] = datetime.now(timezone.utc).isoformat()

        self._save_task(task_id, task_data)
        logger.info(f"Updated task {task_id} with status: {status}")

    def delete_task(self, task_id: str) -> bool:
        """
        Delete a task file.

        Args:
            task_id: Task ID string

        Returns:
            True if deleted, False if not found
        """
        task_path = self._get_task_path(task_id)
        if task_path.exists():
            task_path.unlink()
            return True
        return False

    def get_old_tasks(self, days: int = 7) -> list:
        """
        Get tasks older than specified days.

        Args:
            days: Number of days threshold

        Returns:
            List of task IDs older than threshold
        """
        from datetime import timedelta

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        old_tasks = []

        for task_file in self.tasks_dir.glob("*.json"):
            try:
                with open(task_file, "r") as f:
                    task_data = json.load(f)

                created_at = datetime.fromisoformat(task_data["created_at"])
                if created_at < cutoff:
                    old_tasks.append(task_data["task_id"])
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Error reading task file {task_file}: {e}")

        return old_tasks

    def cleanup_old_tasks(self, days: int = 7) -> int:
        """
        Delete tasks older than specified days.

        Args:
            days: Number of days threshold

        Returns:
            Number of tasks deleted
        """
        old_task_ids = self.get_old_tasks(days)
        deleted_count = 0

        for task_id in old_task_ids:
            if self.delete_task(task_id):
                deleted_count += 1

        # Log to cleanup.log in JSON format
        cleanup_logger.debug(json.dumps({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": "cleanup",
            "days_threshold": days,
            "tasks_deleted": deleted_count,
        }))
        
        logger.info(f"Cleaned up {deleted_count} tasks older than {days} days")
        return deleted_count