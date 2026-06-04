from collections.abc import Callable
from typing import Any, Protocol


class TaskSchedulerPort(Protocol):
    def add_task(
        self,
        func: Callable[..., None],
        *args: Any,
        **kwargs: Any,
    ) -> None: ...
