# 4. Infrastructure Layer

The infrastructure layer contains the concrete technical implementations of application ports.

The main idea is:

```text
The application defines ports.
The infrastructure layer implements those ports.
```

Infrastructure code may know about technical details such as SDKs, SQLAlchemy, HTTP clients, file systems, or external APIs. Domain and application code should not depend on those details directly.

---

## Adapter Modules

An **adapter** is a concrete implementation of a port.

For example, if the application defines a port for an LLM, file storage, embeddings, email, or persistence, the infrastructure layer provides the implementation.

An adapter should:

```text
implement the port contract
call the technical system
map technical data to domain objects or DTOs
raise errors defined by the port for expected failures
hide SDK/ORM/API details from the application
```

The application should only see the port.

It should not need to know whether the adapter uses SQLAlchemy, OpenAI, raw HTTP, local files, or another technical tool.

---

## Simple Adapters

Some adapters are relatively small.

Example categories:

```text
external API adapter
LLM adapter
file storage adapter
embedding adapter
email adapter
```

These often need only:

```text
one adapter class
maybe a mapper
maybe technical error translation
configuration through bootstrap
```

The adapter receives whatever technical client it needs and exposes the port interface to the application.

---

## Persistence Adapters Are More Involved

ORM-mapped database adapters are usually different from simple adapters.

They often need several supporting infrastructure modules, not only one adapter class.

Typical persistence infrastructure can include:

```text
orm.py
  table definitions
  ORM mapping
  mapper startup function

repository.py
  concrete repository implementation

uow.py
  concrete Unit of Work implementation
  session ownership
  commit / rollback handling

events.py
  ORM event listeners
  derived field updates
  persistence-level side effects

engine/session setup
  engine creation
  sessionmaker creation
  database-specific configuration
```

This is still infrastructure.

These modules support the database adapter, but they should not change the dependency direction.

The application still depends on repository and Unit of Work ports.
The infrastructure layer provides the concrete SQLAlchemy implementation.

---

## Why ORM-Mapped Adapters Need Extra Modules

ORM-mapped adapters do more than call an external API.

They may need to define:

```text
how domain objects are mapped to tables
how relationships are loaded
how sessions are created and closed
how transactions are committed or rolled back
how ORM events keep persistence state consistent
how database-specific behavior is configured
```

For example, an `orm.py` module may define SQLAlchemy tables and map them to domain classes.

An `events.py` module may register SQLAlchemy event listeners, such as updating a derived timestamp whenever related rows change.

These are technical persistence concerns.

They belong in infrastructure because they explain **how persistence works**, not **what the business rule is**.

---

## Persistence Ports Stay Small

Even if the SQLAlchemy implementation needs multiple modules, the application-facing port can stay small.

Example:

```text
ConversationUOW
  commit
  rollback
  conversation_repo

ConversationRepository
  get
  create_conversation
  delete
  delete_conversations_with_cgpt
```

The port describes what the application needs.

It does not describe:

```text
SQLAlchemy sessions
table definitions
mapper configuration
event listeners
foreign keys
indexes
flush behavior
```

Those details belong to the infrastructure implementation.

---

## Query Adapters

Query adapters are also infrastructure.

They are used for read paths and may use optimized SQL or ORM queries.

They should still follow the same boundary rules:

```text
return explicit query DTOs
raise errors defined by the query port
do not return raw rows or ORM objects across the boundary
hide database details from the interface layer
```

Queries may be more direct than commands, but they should still be structured around an explicit query port.

---

## Dependency Wiring

Infrastructure adapters are connected through bootstrap and composition.

General flow:

```text
bootstrap.py initializes infrastructure
bootstrap.py creates adapter factories
dependency container exposes those factories
routes receive adapters through Depends
application services receive them as port types
```

This keeps construction logic centralized.

Application services should not import concrete infrastructure adapters directly.

---

## Responsibility Summary

Infrastructure modules should:

```text
implement port contracts
contain technical API/database calls
map technical data to DTOs or domain objects
raise port-defined errors for expected failures
configure persistence and external clients
hide SDK/ORM details from the application
```

Infrastructure modules should avoid:

```text
owning business rules
returning SDK or ORM objects through ports
forcing application services to know technical setup
sharing request-scoped mutable state globally
raising HTTPException
```

Simplified flow:

```text
application use case
  -> calls port
  -> concrete adapter handles technical work
  -> adapter maps result to DTO/domain object
  -> adapter raises port errors for known failures
  -> use case continues without knowing infrastructure details
```
