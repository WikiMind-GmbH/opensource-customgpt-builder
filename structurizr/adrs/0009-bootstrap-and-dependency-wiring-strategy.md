# Bootstrap and Dependency Wiring Strategy

Date: 2025-08-04

## Status

OPEN

## Context

As detailed further in ADR-16, the backend follows **hexagonal architecture** principles using **Ports and Adapters**.
The application relies on **dependency inversion**, ensuring that inner layers (the service layer) depend only on abstractions, never on concrete implementations.

### Service Layer and Ports

The service layer exposes functionality exclusively via **Ports**, implemented as Python `Protocol`s.
Service functions are only aware of these port definitions and are completely decoupled from adapter implementations.

Example service function:

```python
def continue_conversation(
    user_message: str,
    conv_id: str,
    conv_uow: ConversationUOW,  # Port
    cgpt_retreiver: CustomGPTInstructionsRetreiver,  # Port
    llm_adapter: LlmPort,  # Port
    use_rag: bool = False,
) -> str:
```

All parameters except primitives are **Ports owned by the service layer**, not concrete adapters.

Example port definitions:

```python
class ConversationUOW(Protocol):
    def __enter__(self) -> Self: ...
    def __exit__(self, exc_type, exc, tb) -> None: ...
    def commit(self) -> None: ...
    def rollback(self) -> None: ...
    @property
    def conversation_repo(self) -> ConversationRepository: ...


class CustomGPTInstructionsRetreiver(Protocol):
    def get_cgpt_sys_prompt(
        self, cgpt_id: str
    ) -> list[MessageDTORetreiver]: ...


class LlmPort(Protocol):
    def get_assistant_text_response(
        self,
        messages_excluding_sys_prompt: list[MessageDTOllm],
        cgpt_systemprompt: list[MessageDTOllm],
    ) -> str: ...
```

### Dependency Injection via the HTTP Layer

The **HTTP layer (FastAPI)** is responsible for injecting concrete implementations of these ports using FastAPI’s `Depends` mechanism.

However, just as the service layer must not depend on concrete adapters, **the HTTP layer must not be responsible for constructing or configuring adapters either**.
Both layers should depend only on service-defined ports.

This creates two additional requirements:

1. A module responsible for **initializing and wiring dependencies** (e.g. DB engines, mappers, adapters).
2. A mechanism to **connect those dependencies to FastAPI**, while preserving:

   * dependency inversion
   * type safety
   * IDE and linter support

### Configuration Requirements

The dependency wiring must be configurable (e.g. DB URLs, model names).
This can be achieved via:

* default parameters,
* environment variables,
* or, in the future, `pydantic_settings`.

For now, configuration is read directly from environment variables.

### Typing Constraints

Returning a raw dictionary of dependencies from a bootstrap function would:

* lose static typing,
* prevent IDE autocompletion,
* weaken linting and refactoring guarantees.

Therefore, dependencies must be represented as a **typed object**.

---

## Decision

We adopt a solution that:

* preserves strict dependency inversion,
* keeps the HTTP layer free of wiring logic,
* maintains strong typing,
* and allows future changes without large-scale refactors.

### Modules Introduced

We introduce three modules:

1. **`bootstrap.py`**
   Responsible for:

   * initializing infrastructure (DB engines, mappers, events),
   * constructing adapters and adapter factories,
   * returning a typed container of dependencies.

2. **`deps.py`**
   Responsible for:

   * reading environment variables,
   * calling the bootstrap function,
   * exporting the resulting dependency container.

3. **HTTP routers**
   Import the dependency container from `deps.py` and use it with `Depends`.

### Bootstrap Function

```python
def bootstrap(
    *,
    db_url_chat: str,
    db_url_cgpt: str,
    model_name: str,
    create_schema: bool = False,
) -> DependenciesContainer:
```

### Dependency Container

To retain type safety and IDE support, the bootstrap function returns a typed container:

```python
@dataclass(frozen=True)
class DependenciesContainer:
    conversation_uow_factory: Factory[ConversationUOW]
    cgpt_uow_factory: Factory[CgptUOW]
    cgpt_retreiver_adapter_factory: Factory[CustomGPTInstructionsRetreiver]
    llm_adapter_factory: Factory[LlmPort]
    cgpt_queries_adapter_factory: Factory[CgptQueries]
    chat_queries_adapter_factory: Factory[ChatQueries]
    conversation_adapter_factory: Factory[ConversationPort]
```

The container exposes **factories** (or singletons) returning objects that satisfy service-layer ports.

### Bootstrap Implementation (Excerpt)

```python
def bootstrap(...):
    chat_start_mappers()
    engine_chat = _make_engine(db_url_chat, chat_prepare_engine)
    sessionMaker_Chat = _make_sessionmaker(engine_chat)

    if create_schema:
        chat_metadata.create_all(engine_chat)

    register_last_message_at_events(sessionMaker_Chat)

    def conversation_uow_factory() -> ConversationUOW:
        return SQLAlchemyConversationUOW(sessionMaker_Chat)

    _llm_adapter = OpenaiAdapter(model_name=model_name)

    def llm_adapter_factory() -> LlmPort:
        return _llm_adapter

    ...

    return DependenciesContainer(
        conversation_uow_factory=conversation_uow_factory,
        cgpt_uow_factory=cgpt_uow_factory,
        cgpt_retreiver_adapter_factory=cgpt_instructions_adapter_factory,
        llm_adapter_factory=llm_adapter_factory,
        cgpt_queries_adapter_factory=cgpt_queries_adapter_factory,
        chat_queries_adapter_factory=chat_queries_adapter_factory,
        conversation_adapter_factory=conversation_adapter_factory,
    )
```

(Decisions regarding singleton vs factory lifetimes are covered in a separate ADR.)

### Connecting to the HTTP Layer

In `deps.py`, the bootstrap function is called exactly once at import time:

```python
from src.bootstrap import bootstrap, DependenciesContainer

deps: DependenciesContainer = bootstrap(
    db_url_chat=require_env("DB_URL_CHAT"),
    db_url_cgpt=require_env("DB_URL_CGPT"),
    model_name=require_env("MODEL_NAME"),
    create_schema=require_env("CREATE_SCHEMA").lower() == "true",  # dev/test only
)
```

Routers then import and use this container:

```python
from src.interface.http.deps import deps

@chat_commands_router.post("/send-user-message")
async def send_user_message(
    request: UserMessageRequest,
    conv_uow: ConversationUOW = Depends(deps.conversation_uow_factory),
    llm_adapter: LlmPort = Depends(deps.llm_adapter_factory),
    cgpt_retreiver: CustomGPTInstructionsRetreiver = Depends(
        deps.cgpt_retreiver_adapter_factory
    ),
):
```

Because Python modules are only executed once per interpreter, this approach ensures:

* mappers are not registered multiple times,
* infrastructure is initialized exactly once per process.

---

## Consequences

### General

* The HTTP layer is fully decoupled from concrete adapters.
* Dependency wiring is centralized and explicit.
* Strong typing enables IDE support, static analysis, and safer refactoring.
* Service-layer testing is straightforward: any adapter implementing a port can be passed directly.
* The structure aligns closely with DDD and hexagonal architecture principles.

### Testing Implications

#### Service-layer tests

* The bootstrap function is **not executed**.
* Fake adapters and mapper setup are provided via `conftest.py`.
* Mapper initialization must still be guarded to run once.

#### Endpoint / E2E tests

* The bootstrap function *does* execute due to module imports. This does restrict us.
* Dependencies can be overridden cleanly using FastAPI’s `dependency_overrides`.

Example:

```python
@pytest.fixture()
def test_client(test_deps: DependenciesContainer):
    from src.interface.http.deps import deps
    from src.interface.http.app import app

    app.dependency_overrides[deps.conversation_uow_factory] = (
        test_deps.conversation_uow_factory
    )

    return TestClient(app)
```

### Known Risks and Future Improvements (according to chatgpt)

* The setup is safe with **Uvicorn** (dev and prod) **without preload**.
* If switching to **Gunicorn with `--preload`** or other pre-fork servers:

  * `bootstrap()` must move into a FastAPI lifespan hook, or
  * engines must be recreated post-fork.
* Mapper and event registration should be made idempotent for resilience.
* Introducing a `settings.py` using `pydantic_settings` is a planned improvement.

This design is inspired by *Cosmic Python*, adapted to:

* a non–message-bus architecture,
* FastAPI dependency injection,
* and stronger typing guarantees.

As such, it is not a 1:1 adaptation and has not yet been validated at scale.
