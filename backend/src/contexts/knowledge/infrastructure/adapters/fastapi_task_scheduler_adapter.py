from typing import Any, Callable

from fastapi import BackgroundTasks

from src.contexts.knowledge.application.ports.task_scheduler_port import (
    TaskSchedulerPort,
)


class FastAPITaskSchedulerAdapter(TaskSchedulerPort):
    def __init__(self, background_tasks: BackgroundTasks) -> None:
        self._background_tasks = background_tasks

    def add_task(
        self,
        func: Callable[..., None],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self._background_tasks.add_task(func, *args, **kwargs)
