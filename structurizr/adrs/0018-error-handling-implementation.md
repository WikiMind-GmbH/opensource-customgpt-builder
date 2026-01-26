# 18. Error handling implementation

Date: 2025-11-20

## Status

Open

Supercedes [ADR-XXX: Error Handling Pattern (Ports Own Errors, Global HTTP Translation)](0010-error-handling-across-layers-and-contexts.md.md)

## Context

In the process of refactoring, testing and working with the ideas of previous adr, a baseline was established that still holds some technical debt.   
The core aspects still hold true:

- Layer specific errors with upper layer translating  (most) errors
- Ports defining errors that the Adapters implement (incl. data layer ports)
- Ports and Domain errors are the only errors that are thrown
- Service layer does not catch/translate nor implement any errors
- http layer catches/translates all port and domain errors to http errors via exception handlers 
- per Port we have one to_http mapper module for exceptions and dataclasses. There, we have one register_handlers function that contains all exception handler functions
```.py
def register_query_exception_handlers_cgpt_query_port(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def _not_found(_, exc: NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": f"Conversation not found: {getattr(exc, 'args', [''])[0]}"
            },
        )

    @app.exception_handler(QueryError)
    async def _query_error(_, exc: QueryError):
    ...
```
- we have one `all_handlers.py` module where we have one function that runs all exception handlers, which we run once in our `app.py`
```.py
def register_all_handlers(app: FastAPI):
    register_query_exception_handlers_queries_port(app)
    register_query_exception_handlers_chat_repo_port(app)
    ...
```

```.py
app = FastAPI(root_path="/api", lifespan=lifespan)
app.include_router(chat_commands_router)
...

register_all_handlers(app)
```
- http layer also implements its own errors (automatically) -e.g. validation errors. Those can also be customized via exception handlers
- all exception handler modules are imported into one

**There is now some nuance!**
Not all exceptions should be caught and translated, some must be passed as is, like control-flow/process exceptions, which should be passed through. See `src/contexts/shared/port_exceptions_decorator.py`
```.py
    KeyboardInterrupt,
    SystemExit,
    GeneratorExit,
    asyncio.CancelledError,
    concurrent.futures.CancelledError,
```
This specific wrapper is not yet implemented.
As of now, we simply do not catch and translate all errors, but those we want the client to know of. Like a missing resource throwing a `NotFound` Error of some kind. This might not be perfect, but the most important errors that the client should know of (after a translation) are.
We must also pay attention to not share too much with the client via error messages due to security reasons!
For example, if a client tries to access a resource that he has insufficient authorization for, we might want to simply return a 404 message instead of a access-not-granted message to not expose the existence of this resource.

Additionally, creating Base Errors which can be inherited to structure the erros better should also be considered



## Decision

We will stick with the current version, maybe implementing the wrapper in the future.   
More fine tuning will be done when we start with implementing logging.

## Consequences

Logging must be put on top of the priority list.   
When working through implementing this, the new knowledge will be used to revisit the open questions here.
