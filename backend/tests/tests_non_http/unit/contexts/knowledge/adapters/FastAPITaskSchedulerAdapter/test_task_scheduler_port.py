import asyncio

from fastapi import BackgroundTasks

from src.contexts.knowledge.application.ports.task_scheduler_port import (
    TaskSchedulerPort,
)


def test_add_task_schedules_function_with_args_and_kwargs(
    task_scheduler_adapter: TaskSchedulerPort,
    background_tasks: BackgroundTasks,
) -> None:
    calls: list[tuple[str, bool]] = []

    def record_call(value: str, *, enabled: bool) -> None:
        calls.append((value, enabled))

    task_scheduler_adapter.add_task(record_call, "scheduled value", enabled=True)

    assert calls == []

    asyncio.run(background_tasks())

    assert calls == [("scheduled value", True)]
