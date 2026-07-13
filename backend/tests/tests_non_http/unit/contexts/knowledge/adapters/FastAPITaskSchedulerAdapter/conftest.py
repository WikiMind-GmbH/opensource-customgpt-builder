import pytest
from fastapi import BackgroundTasks

from src.contexts.knowledge.application.ports.task_scheduler_port import (
    TaskSchedulerPort,
)
from src.contexts.knowledge.infrastructure.adapters.fastapi_task_scheduler_adapter import (
    FastAPITaskSchedulerAdapter,
)


@pytest.fixture()
def background_tasks() -> BackgroundTasks:
    return BackgroundTasks()


@pytest.fixture()
def task_scheduler_adapter(background_tasks: BackgroundTasks) -> TaskSchedulerPort:
    return FastAPITaskSchedulerAdapter(background_tasks=background_tasks)
