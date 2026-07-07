# Introduction to Hexagonal Architecture

## Purpose

This document introduces **Hexagonal Architecture**, also known as **Ports and Adapters**.

It is intended as an onboarding document for developers who are new to this architecture style. The goal is not to explain every possible variation, but to explain the version we use in this codebase.

Hexagonal Architecture helps us keep business logic independent from technical details such as:

```text id="fzj3w6"
HTTP frameworks
databases
ORMs
external APIs
LLM providers
file systems
message brokers
background workers
```

The central idea is:

```text id="xgq616"
The application defines what it needs.
Infrastructure provides implementations.
```

---

## Why Hexagonal Architecture?

Without clear architectural boundaries, technical details often spread into business logic.

Typical problems are:

```text id="vzhtb6"
application services directly create database sessions
domain logic depends on FastAPI or SQLAlchemy
external SDK types leak through the codebase
tests require real infrastructure even for simple business rules
changing an adapter forces changes in unrelated use cases
```

Hexagonal Architecture helps prevent this by making dependencies point inward.

The inner application does not depend on concrete technical tools.
Instead, it depends on abstractions.

This makes the code easier to:

```text id="1uqtmv"
test
refactor
replace
understand
evolve
```

---

## The Hexagon

The “hexagon” is only a metaphor.

It means the application sits in the center, and different outside systems connect to it through explicit boundaries.

Example:

```text id="ae785d"
          HTTP API
             |
Database -- Application -- External API
             |
        Background Worker
```

The important distinction is:

```text id="5e9xu5"
Inside:
  domain logic
  application use cases
  ports

Outside:
  HTTP
  database
  external APIs
  SDKs
  background workers
  concrete adapters
```

The inside should not know the technical details of the outside.

---

## Ports

A **port** is an interface that describes what the application needs or offers.

In Python, we usually define ports as `Protocol`s.

Example:

```python id="5wfuc2"
from typing import Protocol


class LlmPort(Protocol):
    def get_assistant_text_response(
        self,
        messages: list[MessageForLlmDTO],
    ) -> str: ...
```

The application service can use this port without knowing which LLM provider is behind it.

It does not know whether the implementation uses:

```text id="k1skks"
OpenAI
Anthropic
a local model
a fake test adapter
a cached adapter
```

It only knows the contract.

---

## Adapters

An **adapter** is a concrete implementation of a port.

Example:

```python id="p0k52q"
class OpenAiLlmAdapter:
    def __init__(self, model_name: str) -> None:
        self._model_name = model_name

    def get_assistant_text_response(
        self,
        messages: list[MessageForLlmDTO],
    ) -> str:
        ...
```

The adapter contains the technical details.

It may know about:

```text id="glmydq"
SDK clients
API request formats
authentication
timeouts
retries
provider-specific response objects
```

The application service should not know these things.

The adapter translates between the outside world and the application’s port contract.

---

## Dependency Direction

The most important rule is dependency direction.

```text id="g9i7mr"
Application depends on ports.
Adapters depend on ports.
Ports do not depend on adapters.
Application does not depend on adapters.
```

Bad:

```python id="rihncc"
def continue_conversation(
    openai_adapter: OpenAiLlmAdapter,
) -> str:
    ...
```

Good:

```python id="v7q37y"
def continue_conversation(
    llm: LlmPort,
) -> str:
    ...
```

The service depends on what it needs, not on one concrete way of fulfilling that need.

---

## Our Layer Structure

Inside each bounded context, the usual structure is:

```text id="y42a99"
src/contexts/<context_name>/
    domain/
    application/
    infrastructure/
```

The responsibilities are:

```text id="q8cjv7"
domain/
  domain model and business rules

application/
  use cases, orchestration, ports

infrastructure/
  concrete adapters for databases, external APIs, SDKs, etc.
```

The application layer owns the use cases and the ports needed by those use cases.

The infrastructure layer implements those ports.

---

## Application Services

An **application service** represents a use case.

It coordinates work, but it should not depend on concrete infrastructure.

Example:

```python id="rdiir7"
def continue_conversation(
    user_message: str,
    conversation_id: str,
    conversation_uow: ConversationUow,
    custom_gpt_reader: CustomGptReader,
    llm: LlmPort,
) -> str:
    with conversation_uow:
        conversation = conversation_uow.conversations.get(conversation_id)

        conversation.add_user_message(user_message)

        custom_gpt_info = custom_gpt_reader.get_custom_gpt_info(
            conversation.custom_gpt_id
        )

        assistant_text = llm.get_assistant_text_response(
            messages=build_llm_messages(
                conversation=conversation,
                custom_gpt_info=custom_gpt_info,
            )
        )

        conversation.add_assistant_message(assistant_text)
        conversation_uow.commit()

        return assistant_text
```

The application service coordinates:

```text id="0lcxun"
loading data
calling domain behavior
using ports
committing transactions
returning a result
```

It does not construct SQLAlchemy sessions.
It does not create OpenAI clients.
It does not know HTTP status codes.

---

## Repositories as Ports

Repositories are a common kind of port.

A repository hides persistence details.

Example:

```python id="6yjmzt"
class ConversationRepository(Protocol):
    def get(self, conversation_id: str) -> Conversation: ...

    def save(self, conversation: Conversation) -> None: ...
```

The application only knows that conversations can be loaded and saved.

It does not know whether persistence uses:

```text id="j58kuv"
SQLAlchemy
raw SQL
PostgreSQL
SQLite
in-memory fake storage
```

A SQLAlchemy adapter can implement the repository port:

```python id="8i10zo"
class SqlAlchemyConversationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get(self, conversation_id: str) -> Conversation:
        ...

    def save(self, conversation: Conversation) -> None:
        ...
```

The ORM belongs in infrastructure, not in the application service.

---

## Unit of Work as a Port

A **Unit of Work** manages transaction boundaries.

It usually exposes repositories and controls commit/rollback.

Example:

```python id="humq9h"
class ConversationUow(Protocol):
    def __enter__(self) -> Self: ...

    def __exit__(self, exc_type, exc, tb) -> None: ...

    def commit(self) -> None: ...

    def rollback(self) -> None: ...
```

The application service uses the Unit of Work abstraction:

```python id="kff4q9"
def rename_conversation(
    conversation_id: str,
    new_title: str,
    uow: ConversationUow,
) -> None:
    with uow:
        conversation = uow.conversations.get(conversation_id)
        conversation.rename(new_title)
        uow.conversations.save(conversation)
        uow.commit()
```

The concrete implementation may use a SQLAlchemy session, but the use case does not need to know that.

---

## External Services as Ports

Ports are not only for databases.

Any external system can be hidden behind a port.

Examples:

```text id="exqwmb"
LLM provider
embedding provider
file storage
email service
payment provider
vector database
background task queue
```

Example:

```python id="6k7mdb"
class EmbeddingPort(Protocol):
    def create_embedding(self, text: str) -> EmbeddingDTO: ...
```

The application defines what it needs:

```text id="xvj07c"
Create an embedding for this text.
```

The adapter decides how:

```text id="rfw6wv"
Call a specific SDK.
Use a specific model.
Handle provider response objects.
Translate errors.
```

---

## DTOs at Port Boundaries

Port boundaries should use explicit DTOs.

A DTO is part of the contract. It should not be an internal domain entity, an ORM model, or a third-party SDK object.

Good:

```python id="4gikbr"
@dataclass(frozen=True)
class MessageForLlmDTO:
    role: str
    content: str


class LlmPort(Protocol):
    def get_assistant_text_response(
        self,
        messages: list[MessageForLlmDTO],
    ) -> str: ...
```

Bad:

```python id="hqqs1y"
class LlmPort(Protocol):
    def get_assistant_text_response(
        self,
        messages: list[OpenAiChatMessageParam],
    ) -> str: ...
```

The second version leaks an external provider type into the port. That couples the application contract to one SDK.

The adapter may use SDK-specific types internally, but it should map to and from the port DTOs.

---

## What Belongs in a Port Module?

A port module is a contract.

It should contain:

```text id="hj2sso"
the Protocol
the DTOs used by the Protocol
contract-level errors
```

Example:

```python id="5ocr5x"
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class CustomGptInfoDTO:
    name: str
    description: str
    instructions: str


class CustomGptNotFoundError(Exception):
    pass


class CustomGptReader(Protocol):
    def get_custom_gpt_info(self, custom_gpt_id: str) -> CustomGptInfoDTO: ...
```

The port module should not import:

```text id="qcku4h"
SQLAlchemy models
FastAPI schemas
OpenAI SDK types
provider domain entities
consumer domain entities from another context
```

Mappers live outside the port module.

---

## Mapping

Mapping is the translation between internal models and boundary DTOs.

Example:

```python id="954vr0"
def map_message_to_llm_dto(message: Message) -> MessageForLlmDTO:
    return MessageForLlmDTO(
        role=message.role.value,
        content=message.content,
    )
```

Mapping code can feel repetitive, but it protects boundaries.

Without mapping, internal models begin to leak into places where they do not belong.

A useful rule:

```text id="kxjy2j"
The adapter may know both sides of a translation.
The port should only know the contract.
The application should only know the port.
```

---

## Inbound and Outbound Adapters

Hexagonal Architecture often distinguishes between inbound and outbound adapters.

### Inbound Adapters

Inbound adapters call into the application.

Examples:

```text id="28zb6r"
HTTP endpoints
CLI commands
background workers
scheduled jobs
message consumers
```

An HTTP route is an inbound adapter.

Its job is to:

```text id="0w18q6"
receive a request
validate request shape
call an application service
translate the result into an HTTP response
```

It should not own the business use case.

---

### Outbound Adapters

Outbound adapters are called by the application through ports.

Examples:

```text id="krxc2x"
database repositories
LLM provider clients
email sender
file storage
vector database
external APIs
```

Their job is to implement technical behavior required by the application.

They should not decide business policy.

---

## HTTP Layer

The HTTP layer is an inbound adapter.

It should be thin.

It may:

```text id="9ipccx"
define routes
receive request DTOs
use FastAPI dependency injection
call application services
return response DTOs
register exception handlers
```

It should avoid:

```text id="4msl1l"
constructing adapters manually
opening database sessions directly inside endpoint logic
containing business rules
depending on concrete infrastructure details
```

Good shape:

```python id="2ox33a"
@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    uow: ConversationUow = Depends(deps.conversation_uow_factory),
    llm: LlmPort = Depends(deps.llm_adapter_factory),
) -> SendMessageResponse:
    assistant_text = continue_conversation(
        conversation_id=conversation_id,
        user_message=request.message,
        conversation_uow=uow,
        llm=llm,
    )

    return SendMessageResponse(assistant_text=assistant_text)
```

The route connects HTTP to the use case. It does not implement the use case itself.

---

## Dependency Wiring

A common mistake is to keep the application independent from adapters, but then construct all adapters directly inside HTTP routes.

That still couples the outer layer too strongly to infrastructure construction.

Our approach separates dependency wiring into dedicated modules:

```text id="yj91qj"
bootstrap.py
  creates infrastructure, adapters, factories, and the typed dependency container

composition.py
  reads configuration and calls bootstrap once

HTTP routers
  use the dependency container with Depends
```

The dependency container is typed.

Example shape:

```python id="7hrcjq"
@dataclass(frozen=True)
class DependenciesContainer:
    conversation_uow_factory: Factory[ConversationUow]
    llm_adapter_factory: Factory[LlmPort]
    custom_gpt_reader_factory: Factory[CustomGptReader]
```

This avoids an untyped dictionary of dependencies and keeps IDE/type-checker support useful.

---

## Factories and Singletons

Adapters can have different lifetimes.

The safe default is:

```text id="rsjsc8"
Use factories unless a singleton is clearly safe.
```

Use a factory when the adapter holds:

```text id="w6nilp"
request state
transaction state
database session state
mutable state
per-user credentials
non-thread-safe SDK state
```

Typical factory examples:

```text id="r6xxax"
Unit of Work
repositories wrapping a database session
anything request-scoped
```

A singleton may be acceptable when the adapter is:

```text id="3mbhsz"
stateless
immutable
thread-safe
not tied to a request
not tied to a transaction
```

Typical possible singleton examples:

```text id="h0z2em"
configured LLM client
read-only configuration provider
shared HTTP client with documented thread safety
```

The rule is intentionally conservative:

```text id="le9rge"
Correctness and isolation first.
Performance optimization second.
```

---

## Queries and CQRS-Lite

Commands and queries are handled differently.

### Commands

Commands change state.

They usually go through application services and domain behavior.

Example:

```text id="c0wado"
send message
create conversation
update configuration
upload document
```

Commands use ports such as repositories, Unit of Work, and external service ports.

---

### Queries

Queries read data.

They may use dedicated query adapters and return DTO projections directly.

Example:

```text id="rmy81k"
list conversations
show conversation history
get document metadata
search results
```

Queries do not always need to load full domain models.

In our architecture, query adapters may be used directly from the HTTP layer where appropriate. This is a pragmatic CQRS-lite choice.

The important rule is:

```text id="vp99ny"
Commands protect domain behavior.
Queries return read-optimized DTOs.
```

---

## Cross-Context Ports

The system is a modulith with multiple bounded contexts.

Contexts communicate through explicit boundaries.

In the current first iteration:

```text id="41cd2o"
The consuming context often defines the port it needs.
The providing context may implement that port in its infrastructure layer.
Data crosses the boundary through DTOs.
Mapping happens at the boundary.
```

This keeps communication explicit and avoids direct model sharing.

Example:

```text id="kqecso"
Chat context needs CustomGPT information.

Chat application defines:
  CustomGptReader port

CustomGPT infrastructure provides:
  adapter implementing CustomGptReader

Boundary data:
  CustomGptInfoDTO
```

The provider should not leak its internal domain model.
The consumer should not receive provider ORM models.
The contract should be explicit.

This current approach is pragmatic and works well for a small number of consumers. If cross-context integration grows, the boundary design may become stricter.

---

## Error Handling Across Ports

Ports may define contract-level errors.

Example:

```python id="mt29i8"
class ConversationNotFoundError(Exception):
    pass


class ConversationRepository(Protocol):
    def get(self, conversation_id: str) -> Conversation: ...
```

An adapter should translate infrastructure-specific errors into port-level errors.

For example:

```text id="pxuaie"
SQLAlchemy NoResultFound
  -> ConversationNotFoundError
```

The application service should not need to know SQLAlchemy error types.

The HTTP layer can later translate port or domain errors into HTTP responses.

```text id="dmmmfq"
Infrastructure error -> port error -> HTTP error response
```

The domain and application layers should not raise `HTTPException`.

---

## Testing With Hexagonal Architecture

Hexagonal Architecture makes testing easier because use cases depend on ports.

For application service tests, we can pass fake adapters.

Example:

```python id="tbqbfa"
class FakeLlmAdapter:
    def get_assistant_text_response(
        self,
        messages: list[MessageForLlmDTO],
    ) -> str:
        return "fake assistant response"


class FakeConversationUow:
    ...
```

Then the test can focus on the use case:

```python id="v22l87"
def test_continue_conversation_adds_assistant_message() -> None:
    uow = FakeConversationUow()
    llm = FakeLlmAdapter()

    result = continue_conversation(
        user_message="Hello",
        conversation_id="conv_123",
        conversation_uow=uow,
        llm=llm,
    )

    assert result == "fake assistant response"
    assert uow.committed
```

Different test levels have different responsibilities:

```text id="n02kgp"
application service tests:
  test use cases with fake ports

adapter tests:
  test concrete infrastructure behavior

mapper tests:
  test DTO translation

E2E tests:
  test important flows through HTTP
```

The point is not to fake everything.
The point is to test each part at the right boundary.

---

## Common Mistakes

### Mistake: Passing Concrete Adapters Into Use Cases

Bad:

```python id="ce2jnp"
def use_case(repo: SqlAlchemyConversationRepository) -> None:
    ...
```

Good:

```python id="b0to70"
def use_case(repo: ConversationRepository) -> None:
    ...
```

The use case should depend on the port.

---

### Mistake: Letting SDK Types Leak Into Ports

Bad:

```python id="ckgpo3"
class LlmPort(Protocol):
    def complete(self, messages: list[OpenAiMessageParam]) -> OpenAiResponse: ...
```

Good:

```python id="umkoyx"
class LlmPort(Protocol):
    def complete(self, messages: list[LlmMessageDTO]) -> LlmResponseDTO: ...
```

SDK types belong inside the adapter.

---

### Mistake: Putting Database Sessions in Port Signatures

Bad:

```python id="io08un"
class ConversationRepository(Protocol):
    def get(self, session: Session, conversation_id: str) -> Conversation: ...
```

Good:

```python id="uq6y3m"
class ConversationRepository(Protocol):
    def get(self, conversation_id: str) -> Conversation: ...
```

The adapter may receive a session through construction.
The port contract should not expose that implementation detail.

---

### Mistake: Business Logic in Adapters

Bad:

```text id="34psyo"
SQLAlchemy adapter decides whether an order may be cancelled.
```

Good:

```text id="nllofp"
Domain model decides whether an order may be cancelled.
Adapter only loads and saves the order.
```

Adapters are technical translators, not owners of business rules.

---

### Mistake: Business Logic in HTTP Routes

Bad:

```text id="scpum8"
Endpoint loads database rows, checks business rules, calls external API, commits transaction.
```

Good:

```text id="qbxdkc"
Endpoint validates request shape, receives dependencies, calls an application service.
```

---

### Mistake: Avoiding Mappers

Avoiding mappers often feels simpler at first.

But it usually causes internal models to leak across boundaries.

Good architecture accepts explicit mapping as the cost of clear contracts.

---

## Practical Checklist

When adding a new dependency or integration, ask:

```text id="hndmqj"
Is this a use case or an adapter detail?
Which application service needs this?
What port should the application depend on?
Which DTOs belong to the port contract?
What errors belong to the port contract?
Where will the concrete adapter live?
Does the adapter need a factory or can it safely be a singleton?
Where does mapping happen?
How can the application service be tested with a fake adapter?
```

When reviewing code, check:

```text id="2pdy4u"
Does application code depend on a Protocol instead of a concrete adapter?
Do port signatures avoid infrastructure objects?
Are DTOs contract-owned?
Are SDK/ORM/FastAPI types kept out of the application core?
Is dependency wiring centralized?
Is request-scoped state created per request?
```

---

## Summary

Hexagonal Architecture keeps the application independent from technical details.

The most important ideas are:

```text id="emy6ep"
application services depend on ports
adapters implement ports
ports are contracts
DTOs protect port boundaries
mappers translate between internal models and contracts
HTTP is an inbound adapter
databases and external APIs are outbound adapters
dependency wiring is centralized
request-scoped dependencies use factories
safe stateless dependencies may be singletons
tests can use fake adapters
```

In short:

```text id="m1nu5y"
The application defines what it needs.
Infrastructure provides it.
The boundary between them is explicit.
```

This gives us a codebase that is easier to test, easier to refactor, and better prepared for future architectural changes.
