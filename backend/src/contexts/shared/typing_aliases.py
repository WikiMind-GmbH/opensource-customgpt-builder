from typing import Callable, TypeVar

T = TypeVar("T")
Factory = Callable[[], T]
