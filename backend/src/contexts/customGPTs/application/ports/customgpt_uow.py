from __future__ import annotations

from types import TracebackType
from typing import Protocol, Type

from src.contexts.customGPTs.application.ports.customgpt_repo import CustomGPTRepository


# Below: Not needed if we explicitly inherit Protocols -> better for typechecking
# #@runtime_checkable #So we can  assert isinstance(adapter, port)
class CgptUOW(Protocol):
    # make sure that one session per unit of work
    def __enter__(self) -> CgptUOW: ...
    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ): ...
    def commit(self): ...
    def rollback(self): ...
    @property
    def cgpt_repo(self) -> CustomGPTRepository: ...
