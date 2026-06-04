from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ScheduledTask:
    func: Callable[..., None]
    args: tuple[Any, ...]
    kwargs: dict[str, Any]


class FakeTaskScheduler:
    def __init__(self) -> None:
        self.tasks: list[ScheduledTask] = []

    def add_task(
        self,
        func: Callable[..., None],
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.tasks.append(
            ScheduledTask(
                func=func,
                args=args,
                kwargs=kwargs,
            )
        )

    def run_all(self) -> None:
        for task in self.tasks:
            task.func(*task.args, **task.kwargs)
