# 31. Logging

Date: 2026-06-25

## Status

Accepted

## Created by

Albert

## Decision Maker

Albert

## Scope

Complete backend, including production, development, and pytest-based testing.

## Context

We need a logging setup that is useful in production, development, and tests.

The backend has several internal contexts, currently:

* `customgpts`
* `chat`
* `knowledge`

We want to see detailed logs for our own code when needed, while keeping logs from external libraries less noisy. In pytest, our logs should also be visible and captured correctly without duplicate output.

## Alternatives Considered

### Use module-based logger names with `logging.getLogger(__name__)`

This is the standard Python approach and automatically creates hierarchical logger names based on module paths.

It was not chosen because the resulting names are less readable for our use case. We prefer names based on application context and component responsibility.

### Use fully manual logger names everywhere

This gives readable names, but it is error-prone. A logger can easily be named outside the intended hierarchy and then only receive the root log level, which is meant for external libraries.

### Use context-based logger names created through a helper

This keeps names readable while ensuring all internal loggers are grouped under known context roots.

This was chosen.

## Decision

We use context-based logger names.

Each internal logger must be created through the shared helper:

```python
class LoggerContext(StrEnum):
    CUSTOMGPTS = "customgpts"
    CHAT = "chat"
    KNOWLEDGE = "knowledge"


def get_logger(
    context: LoggerContext,
    component: str,
) -> logging.Logger:
    if not component:
        raise ValueError("Logger component must not be empty")

    return logging.getLogger(f"{context.value}.{component}")
```

Logger names follow this structure:

```text
{context}.{component}
```

Examples:

```text
chat.domain
knowledge.retriever_adapter
customgpts.permission_checker
```

Each context root is configured explicitly:

```python
"loggers": {
    LoggerContext.KNOWLEDGE.value: {
        "level": knowledge_log_level,
        "propagate": True,
    },
    LoggerContext.CHAT.value: {
        "level": chat_log_level,
        "propagate": True,
    },
    LoggerContext.CUSTOMGPTS.value: {
        "level": customgpts_log_level,
        "propagate": True,
    },
}
```

The root logger owns the console handler. Internal context loggers propagate to the root handler but keep their own log levels.

This allows configurations such as:

```text
chat.*        -> DEBUG
knowledge.*   -> DEBUG
customgpts.*  -> DEBUG
external libs -> INFO
```

The root logger level controls external library loggers. Context logger levels control our own backend logs.

## Consequences

This makes internal logs readable, predictable, and easy to configure per backend context.

It avoids orphan internal loggers accidentally falling back to the root log level intended for external libraries.

It also avoids duplicate log output because context loggers propagate to the root handler instead of defining their own handlers.

The trade-off is that developers must use `get_logger(...)` instead of directly calling `logging.getLogger(...)`. This is intentional and should be treated as the project convention.
