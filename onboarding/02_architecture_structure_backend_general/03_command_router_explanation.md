## 3. Command Router Overview

This sketch shows the **command side** of the backend.

Command routes are used for operations that trigger use cases and usually change state.

The main idea is:

```text id="6wi30h"
A command route receives an HTTP request,
injects the required dependencies,
calls an application orchestration function,
and lets the domain model protect business rules.
```

Commands are more involved than queries because they often modify state, enforce invariants, and commit transactions.

---

## What the Boxes Represent

The sketch shows these module groups:

```text id="tvde1b"
cmd_router
port modules
orchestration modules
domain modules
exception handlers
```

They belong to different layers:

```text id="r4584v"
interface layer:
  cmd_router
  exception handlers

application layer:
  port modules
  orchestration modules

domain layer:
  domain modules
```

The relationship is:

```text id="3y3syj"
cmd_router calls orchestration functions
orchestration functions depend on ports
adapters implement those ports
domain modules contain business behavior and invariants
exception handlers translate domain/port errors to HTTP
```

---

## `cmd_router`

The `cmd_router` module belongs to the interface layer.

It contains HTTP endpoints for command use cases.

Examples:

```text id="zoknme"
create something
update something
delete something
send a message
upload something
trigger processing
```

A command route should receive request data, inject dependencies via `Depends`, call one application use case, and return a response.

Simplified shape:

```python id="2dpj9o"
@router.post("/items/{item_id}/activate")
async def activate_item(
    item_id: str,
    request: ActivateItemRequest,
    uow: ItemUow = Depends(deps.item_uow_factory),
) -> ActivateItemResponse:
    result = activate_item_use_case(
        item_id=item_id,
        reason=request.reason,
        uow=uow,
    )

    return ActivateItemResponse.model_validate(result)
```

The route adapts HTTP into an application call. It should not contain the business workflow itself.

---

## Orchestration Modules

Orchestration modules belong to the application layer.

They contain command use case functions.

A use case function may:

```text id="dg8fl4"
load domain objects through ports
call domain behavior
call external ports if needed
manage Unit of Work boundaries
commit or roll back changes
return simple results or DTOs
```

Example:

```python id="n4qg5a"
def activate_item_use_case(
    item_id: str,
    reason: str,
    uow: ItemUow,
) -> None:
    with uow:
        item = uow.items.get(item_id)
        item.activate(reason)
        uow.items.save(item)
        uow.commit()
```

The orchestration function coordinates the use case. It should not know how the database or external systems are implemented.

---

## Port Modules

Port modules define the dependencies required by orchestration functions.

They may contain:

```text id="rv7h13"
Protocol definitions
port-specific DTOs
port-specific errors
```

The port is the contract. Adapters implementing the port should raise the errors defined by the port, not leak infrastructure-specific exceptions.

Example:

```python id="1gr1oe"
class ItemNotFoundError(Exception):
    pass


class ItemRepository(Protocol):
    def get(self, item_id: str) -> Item: ...

    def save(self, item: Item) -> None: ...


class ItemUow(Protocol):
    @property
    def items(self) -> ItemRepository: ...

    def commit(self) -> None: ...
```

---

## Domain Modules

Domain modules contain the business model and business rules.

They should protect invariants.

Example:

```python id="nxx32h"
@dataclass
class Item:
    status: ItemStatus

    def activate(self, reason: str) -> None:
        if self.status is ItemStatus.ARCHIVED:
            raise ArchivedItemCannotBeActivatedError()

        self.status = ItemStatus.ACTIVE
```

The application orchestration decides when to load, save, and commit.
The domain decides whether the state transition is valid.

---

## Error Handling

Command errors usually come from two places:

```text id="syxtrb"
domain errors
port errors
```

Adapters should translate known technical errors into port errors.

Example:

```text id="vxvxt9"
database row not found
  -> ItemNotFoundError

external provider timeout
  -> ProviderUnavailableError
```

The command route should not know SQLAlchemy, HTTP client, or SDK-specific exceptions.

HTTP translation belongs to exception handlers.

General flow:

```text id="qso6xu"
domain or port error is raised
  -> orchestration lets it bubble up
  -> exception handler catches it
  -> HTTP response is created
```

---

## One Command Router per Context

The sketch notes the general rule:

```text id="g6qwzo"
per context: one command router
```

This keeps command endpoints close to the context that owns the use case.

General shape:

```text id="u9vcmg"
contexts/
  some_context/
    interface/
      http/
        cmd_router.py
    application/
      orchestration/
        use_cases.py
      ports/
        some_port.py
    domain/
      model.py
      errors.py
```

If a command needs data or behavior from another context, it should use an explicit port and DTO contract.

---

## Responsibility Summary

The command router should:

```text id="cdqcx4"
define command endpoints
receive request schemas and parameters
inject dependencies
call application orchestration
return responses
```

The orchestration module should:

```text id="6gpqg5"
coordinate the use case
use ports
call domain behavior
control transaction boundaries
```

The port modules should:

```text id="fzuf0d"
define dependency contracts
define port DTOs
define port errors
avoid infrastructure-specific types
```

The domain modules should:

```text id="e6wloo"
model business concepts
protect invariants
raise domain errors
```

Simplified command flow:

```text id="o3da6x"
HTTP POST/PUT/PATCH/DELETE request
  -> cmd_router endpoint
  -> injected dependencies
  -> orchestration use case
  -> ports and domain model
  -> commit transaction if needed
  -> response schema
  -> HTTP response
```
