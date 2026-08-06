"""
progress.py
-----------
Live progress display for NetOps Automation Suite.
"""

from rich.console import Console
from rich.progress import (
    Progress,
    BarColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)


console = Console()


class ProgressManager:
    """Handles execution progress."""

    @staticmethod
    def create(total_devices: int):

        progress = Progress(
            TextColumn("[cyan]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            TextColumn("[green]✔ {task.fields[success]}"),
            TextColumn("[red]✘ {task.fields[failed]}"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console,
        )

        task = progress.add_task(
            "Executing...",
            total=total_devices,
            success=0,
            failed=0,
        )

        return progress, task

    @staticmethod
    def update(
        progress,
        task,
        hostname: str,
        status: str,
    ):

        task_data = progress.tasks[0]

        success = task_data.fields["success"]
        failed = task_data.fields["failed"]

        if status == "SUCCESS":
            success += 1
        else:
            failed += 1

        progress.update(
            task,
            advance=1,
            description=f"[cyan]{hostname}",
            success=success,
            failed=failed,
        )