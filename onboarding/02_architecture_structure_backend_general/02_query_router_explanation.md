## 2. Query Router Overview

This sketch shows the **query side** of the backend.

Query routes are used for read operations. They return data, but they should not change domain state.

The main idea is:

```text id="u6fzf8"
A query route receives an HTTP request,
injects a query dependency,
calls a query port,
and returns read-optimized data.
```

Queries are usually simpler than commands because they do not need to coordinate domain state changes or transactions in the same way.

---

## What the Boxes Represent

The sketch shows three main module groups:

```text id="i3067d"
query_router
query_port
query_adapter
```

They belong to different layers:

```text id="4envxk"
interface layer:
  query_router

application layer:
  query_port

infrastructure layer:
  query_adapter
```

The relationship is:

```text id="thg78c"
query_router depends on the query_port
query_adapter implements the query_port
query_adapter raises errors defined by the query_port
query_adapter is injected into the route through FastAPI Depends
```

The route should know the query contract, not the concrete database implementation.

---

## `query_router`

The `query_router` module belongs to the interface layer.

It contains HTTP endpoints for read use cases.

Examples:

```text id="rfnj5e"
list items
get details
search
load history
show overview data
```

A query route should:

```text id="u76a2j"
receive path or query parameters
receive a query dependency via Depends
call one query method or query function
return a response schema
```

Simplified shape:

```python id="fv8h66"
@router.get("/items/{item_id}")
async def get_item(
    item_id: str,
    query: ItemQueryPort = Depends(deps.item_query_factory),
) -> ItemResponse:
    result = query.get_item(item_id=item_id)
    return ItemResponse.model_validate(result)
```

The route adapts HTTP to the query contract.

It should not contain SQL, ORM logic, or complex data assembly.

---

## `query_port`

The `query_port` module belongs to the application side of the boundary.

It defines the read operations available to the route.

Example:

```python id="y54mpr"
from typing import Protocol


class ItemNotFoundError(Exception):
    pass


class ItemQueryPort(Protocol):
    def get_item(self, item_id: str) -> ItemDTO: ...

    def list_items(self) -> list[ItemSummaryDTO]: ...
```

The port may define:

```text id="h4nzaq"
query methods
query DTOs
input DTOs if needed
query-level errors
```

The query port is a contract.

That contract includes not only the successful return types, but also the expected errors.

For example, if a query can fail because an item does not exist, the query port should define the corresponding `ItemNotFoundError`.

The query router and exception handlers can then react to the port error without knowing anything about the database implementation.

The query port should not expose persistence details such as ORM models, SQLAlchemy sessions, or raw database rows.

---

## `query_adapter`

The `query_adapter` module belongs to the infrastructure layer.

It implements the query port.

It may:

```text id="vj3vqj"
execute SQL
use ORM queries
join tables
load read projections
map database results to DTOs
translate technical errors into query-port errors
```

The adapter must use the errors defined by the query port.

For example:

```python id="6fh9rb"
class SqlItemQueryAdapter:
    def get_item(self, item_id: str) -> ItemDTO:
        row = self._session.execute(...).one_or_none()

        if row is None:
            raise ItemNotFoundError(item_id)

        return map_row_to_item_dto(row)
```

The database-specific situation is translated into the contract-level error.

The route and exception handler only need to know:

```text id="l27jv3"
ItemNotFoundError means the requested item was not found.
```

They do not need to know whether this came from SQLAlchemy, raw SQL, PostgreSQL, SQLite, or anything else.

In a CQRS-light style, query adapters may use optimized read access instead of loading full domain models.

This is intentional.

For queries, we often only need a projection that is useful for the caller.

The important rule is:

```text id="eamr5v"
The adapter may optimize how it reads.
The adapter must still satisfy the query port contract.
The boundary still returns explicit DTOs and raises port-defined errors.
```

---

## Why Queries Can Be More Direct

Commands usually protect invariants and change state.

Queries usually only read data.

That means a query does not always need the full domain model.

Example:

```text id="j1vm1b"
Command:
  cancel order
  -> load domain model
  -> enforce invariant
  -> save changes

Query:
  show order overview
  -> read projection
  -> return DTO
```

This keeps read paths simple and allows them to be optimized independently.

However, “more direct” does not mean “unstructured”.

Query routes should still depend on query ports, query adapters should still return DTOs, and query adapters should raise the errors defined by the query port.

---

## Dependency Injection Flow

The query adapter is created through the normal bootstrap/composition mechanism.

General flow:

```text id="djf1ox"
bootstrap.py creates query adapter factory
composition.py exposes dependency container
query_router imports dependency container
FastAPI Depends injects query adapter as query port
endpoint calls query method
```

The route should not manually construct the adapter.

Bad:

```python id="6jlsm2"
@router.get("/items/{item_id}")
async def get_item(item_id: str) -> ItemResponse:
    query = SqlItemQueryAdapter(...)
    result = query.get_item(item_id)
    return ItemResponse.model_validate(result)
```

Good:

```python id="meq37n"
@router.get("/items/{item_id}")
async def get_item(
    item_id: str,
    query: ItemQueryPort = Depends(deps.item_query_factory),
) -> ItemResponse:
    result = query.get_item(item_id)
    return ItemResponse.model_validate(result)
```

---

## One Query Router per Context

The sketch notes the general rule:

```text id="xm9k3l"
per context: one query router
```

This keeps read endpoints close to the context that owns the read concept.

General shape:

```text id="az71wo"
contexts/
  some_context/
    interface/
      http/
        query_router.py
    application/
      ports/
        queries.py
    infrastructure/
      queries/
        query_adapter.py
```

The exact module names may vary.

The important idea is:

```text id="o9k1k8"
The context that owns the read concept owns the query route, query port, and query adapter.
```

---

## Query DTOs and Response Schemas

Query ports should return explicit DTOs.

The HTTP route can either return those DTOs directly if they are suitable for the HTTP contract, or map them into response schemas.

General flow:

```text id="dqja8j"
query_adapter
  -> query DTO
  -> query_router
  -> response schema
  -> HTTP response
```

Avoid returning these directly:

```text id="h5nn53"
ORM models
database rows
domain entities
external SDK objects
```

The query response should be a clear contract for the caller.

---

## Error Handling

Query errors are part of the query port contract.

That means:

```text id="6h5fep"
query_port defines the expected query errors
query_adapter raises those errors
exception handlers translate those errors into HTTP responses
```

Example:

```text id="rn7w8t"
database row not found
  -> query-port NotFound error
  -> exception handler
  -> 404 response
```

The query router should not need to know database-specific exceptions.

The query adapter should translate known technical failure cases into the errors defined by the query port.

HTTP translation belongs to the interface layer through exception handlers.

---

## Responsibility Summary

The query router should do:

```text id="d3qrz8"
define read endpoints
receive path/query parameters
inject query dependencies
call query port methods
return response schemas
```

The query port should do:

```text id="6n2262"
define available read operations
define query DTOs
define query-level errors
avoid infrastructure-specific types
```

The query adapter should do:

```text id="5mu375"
implement the query port
perform efficient read access
map results to DTOs
raise errors defined by the query port
hide SQL/ORM/database details from the router
```

A useful way to read the sketch is:

```text id="lapzfx"
query_router is the HTTP entry point for reads.
query_port is the read contract, including DTOs and expected errors.
query_adapter is the concrete read implementation.
bootstrap.py creates the adapter factory.
FastAPI Depends injects the adapter as the port type.
```

Simplified flow:

```text id="0f9ocw"
HTTP GET request
  -> query_router endpoint
  -> injected query dependency
  -> query_adapter reads data
  -> query DTO
  -> response schema
  -> HTTP response
```

Error flow:

```text id="vvabku"
technical read failure or missing data
  -> query_adapter translates to query-port error
  -> exception handler translates to HTTP response
```
