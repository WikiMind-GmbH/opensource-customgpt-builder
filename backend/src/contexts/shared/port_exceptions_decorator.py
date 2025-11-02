from __future__ import annotations
import asyncio, concurrent.futures, inspect
from functools import wraps
from typing import Callable, Type, Tuple, ParamSpec, TypeVar


P = ParamSpec("P")
R = TypeVar("R")

def port_boundary(
    *,
    port_error_base: Type[BaseException],
    passthrough: Tuple[Type[BaseException], ...] = (
        KeyboardInterrupt,
        SystemExit,
        GeneratorExit,
        asyncio.CancelledError,
        concurrent.futures.CancelledError,
    ),
) : #-> Callable[[Callable[P, R]], Callable[P, R]]
    """Decorator factory for port methods.

    - Lets control-flow/process exceptions pass through.
    - Avoids double-wrapping if it's already a port error.
    - Wraps anything else into a port-specific 'unexpected' error, chaining cause.
    """
    def wrap(fn: Callable[P, R]) -> Callable[P, R]:
        if inspect.iscoroutinefunction(fn):
            @wraps(fn)
            async def inner(*args: P.args, **kwargs: P.kwargs) -> R:
                try:
                    return await fn(*args, **kwargs)
                except passthrough:
                    raise
                except port_error_base:
                    raise
                except Exception as e:
                    raise port_error_base() from e
        else:
            @wraps(fn)
            def inner(*args: P.args, **kwargs: P.kwargs) -> R:
                try:
                    return fn(*args, **kwargs)
                except passthrough:
                    raise
                except port_error_base:
                    raise
                except Exception as e:
                    raise port_error_base() from e
        return inner
    return wrap



# #----------------------ORIGINAL-------------------------
# from __future__ import annotations
# import asyncio, concurrent.futures, inspect
# from functools import wraps
# from typing import Callable, Type, Tuple, ParamSpec, TypeVar

# P = ParamSpec("P")
# R = TypeVar("R")

# def port_boundary(
#     *,
#     unknown_error_factory: Callable[[], Exception],
#     port_error_base: Type[BaseException],
#     passthrough: Tuple[Type[BaseException], ...] = (
#         KeyboardInterrupt,
#         SystemExit,
#         GeneratorExit,
#         asyncio.CancelledError,
#         concurrent.futures.CancelledError,
#     ),
# ) -> Callable[[Callable[P, R]], Callable[P, R]]:
#     """Decorator factory for port methods.

#     - Lets control-flow/process exceptions pass through.
#     - Avoids double-wrapping if it's already a port error.
#     - Wraps anything else into a port-specific 'unexpected' error, chaining cause.
#     """
#     def wrap(fn: Callable[P, R]) -> Callable[P, R]:
#         if inspect.iscoroutinefunction(fn):
#             @wraps(fn)
#             async def inner(*args: P.args, **kwargs: P.kwargs) -> R:
#                 try:
#                     return await fn(*args, **kwargs)
#                 except passthrough:
#                     raise
#                 except port_error_base:
#                     raise
#                 except Exception as e:
#                     raise unknown_error_factory() from e
#         else:
#             @wraps(fn)
#             def inner(*args: P.args, **kwargs: P.kwargs) -> R:
#                 try:
#                     return fn(*args, **kwargs)
#                 except passthrough:
#                     raise
#                 except port_error_base:
#                     raise
#                 except Exception as e:
#                     raise unknown_error_factory() from e
#         return inner
#     return wrap
