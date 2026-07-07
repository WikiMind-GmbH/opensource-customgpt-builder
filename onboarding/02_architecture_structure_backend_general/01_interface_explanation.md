## 1. Interface Layer Overview

This sketch shows the **interface layer** of the backend.

The interface layer is where outside requests enter the system. In this architecture, that usually means FastAPI routes.

The main idea is:

```text
The interface layer receives HTTP requests,
injects dependencies,
calls application use cases or queries,
and translates results/errors back to HTTP.
```

It should stay thin. It connects the outside world to the application, but it should not contain the main business logic.

---

## What the Boxes Represent

The sketch shows several module groups:

```text
app.py
logging.py
exception handler modules
schema modules
command route modules
query route modules
composition.py
bootstrap.py
dependency container
```

Most boxes represent Python modules or small groups of related modules.

The sketch is abstract. It does not show concrete contexts, ports, or adapters. It shows how the interface-side modules generally relate to each other.

---

## `app.py`

`app.py` is the central FastAPI application module.

It typically does things like:

```text
create the FastAPI app
configure logging
include command and query routers
register exception handlers
```

It assembles the HTTP application.

It should not implement use cases or business rules.

---

## Schemas

The schema modules define the HTTP-facing contract.

They usually contain request and response schemas for endpoints.

Their job is to describe what the API receives and returns.

```text
HTTP request schema
  -> route
  -> application call
  -> result
  -> HTTP response schema
```

Schemas belong to the interface layer. They should not become domain models.

---

## Command and Query Routes

The sketch separates command routes from query routes.

### Command routes

Command routes are endpoints that trigger use cases and usually change state.

Examples:

```text
create something
update something
delete something
send a message
upload something
```

A command route should:

```text
receive request data
receive dependencies via FastAPI Depends
call an application orchestration/use-case function
return a response
```

### Query routes

Query routes are endpoints that read data.

Examples:

```text
list items
get details
search
load history
```

A query route should:

```text
receive request parameters
receive a query dependency via Depends
call a query port or query function
return read-optimized DTOs/schemas
```

Queries may be handled more directly than commands, but they should still not expose database rows, ORM models, or infrastructure details as the HTTP response.

---

## Exception Handlers

The sketch shows exception handler modules connected to `app.py`.

These modules translate domain or port errors into HTTP responses.

General flow:

```text
domain or port error is raised
  -> exception handler catches it
  -> HTTP response is created
  -> error may be logged
```

This keeps HTTP-specific error handling out of the domain and application layers.

Domain and application code should raise meaningful domain or port errors, not `HTTPException`.

---

## Logging

The sketch shows logging as a separate setup module.

The idea is simple:

```text
logging is configured centrally
app.py calls the setup once
other modules use the configured logging behavior
```

This avoids spreading logging configuration across many modules.

---

## `composition.py` and the Dependency Container

`composition.py` exposes the configured dependency container to the interface layer.

Routes import this container and use its factories with FastAPI `Depends`.

General shape:

```python
@router.post("/some-action")
async def do_something(
    dependency: SomePort = Depends(deps.some_dependency_factory),
) -> SomeResponse:
    ...
```

Each endpoint should request only the dependencies it needs.

A command endpoint may need a Unit of Work and an external service port.
A query endpoint may only need a query adapter.

The route should not manually construct concrete adapters.

---

## `bootstrap.py`

`bootstrap.py` is where concrete infrastructure is initialized and wired.

It may:

```text
create database engines
create session factories
initialize SDK clients
register ORM mappers
construct adapters
create adapter factories
return the dependency container
```

The important separation is:

```text
bootstrap.py knows concrete infrastructure.
routes receive dependencies through the container.
application services receive dependencies as port types.
```

This keeps construction logic centralized.

---

## Request Flow

A typical request flow looks like this:

```text
HTTP request
  -> FastAPI route
  -> request schema / parameters
  -> dependencies injected via Depends
  -> command use case or query call
  -> result
  -> response schema
  -> HTTP response
```

A typical dependency flow looks like this:

```text
bootstrap.py
  -> dependency container
  -> composition.py
  -> route Depends(...)
  -> endpoint receives the needed port/query dependency
```

---

## Responsibility Summary

The interface layer should do:

```text
define HTTP routes
define request and response schemas
inject dependencies
call application use cases or query ports
translate errors to HTTP responses
configure app-level HTTP setup
```

The interface layer should avoid:

```text
business rules
manual adapter construction inside endpoints
direct database session handling inside endpoint logic
domain model mutation outside application use cases
leaking ORM or SDK objects in responses
```

A useful way to read the sketch is:

```text
app.py assembles the HTTP app.
schemas define the HTTP contract.
routes adapt HTTP calls into application/query calls.
composition.py exposes configured dependencies.
bootstrap.py builds concrete infrastructure.
exception handlers translate internal errors to HTTP.
```
