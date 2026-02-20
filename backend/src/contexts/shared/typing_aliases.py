from typing import Callable, ParamSpec, Protocol, TypeVar

T = TypeVar("T")
Factory = Callable[[], T]

P = ParamSpec("P")
R = TypeVar("R")


class Benchmark(Protocol):
    def __call__(  # https://chatgpt.com/s/t_69971a4c330081918a1ab93f17ea09dc
        self, func: Callable[P, R], *args: P.args, **kwargs: P.kwargs
    ) -> R: ...
